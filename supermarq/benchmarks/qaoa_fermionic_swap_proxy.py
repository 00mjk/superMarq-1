import collections
from typing import List, Tuple

import cirq
import numpy as np
import scipy
from supermarq.benchmarks.benchmark import Benchmark


class QAOAFermionicSwapProxy(Benchmark):
    """Proxy of a full Quantum Approximate Optimization Algorithm
    (QAOA) benchmark. The benchmark targets MaxCut on a Sherrington-Kirkpatrick model.

    Device performance is given by the Hellinger fidelity between the experimental
    output distribution and the true distribution obtained via scalable, classical
    simulation.
    """

    def __init__(self, num_qubits: int) -> None:
        self.num_qubits = num_qubits
        # Intialize the benchmark parameters
        #   1. Generate a random instance of an SK graph
        #   2. Find approximately optimal angles (rather than random values)
        self.Hamiltonian = self._gen_sk_Hamiltonian()
        self.params = self._gen_angles()

    def _gen_sk_Hamiltonian(self) -> List:
        """randomly pick +1 or -1 for each edge weight"""
        random_weights = list(
            2
            * np.random.randint(
                low=0, high=1 + 1, size=int(self.num_qubits * (self.num_qubits - 1) / 2)
            )
            - 1
        )

        H = []
        for i in range(self.num_qubits):
            for j in range(i + 1, self.num_qubits):
                H.append([i, j, random_weights.pop()])

        np.random.shuffle(H)

        return H

    def _gen_swap_network(self, gamma: float, beta: float) -> cirq.Circuit:
        qubits = cirq.LineQubit.range(self.num_qubits)
        circuit = cirq.Circuit()

        # initialize |++++>
        for i in range(self.num_qubits):
            circuit.append(cirq.H(qubits[i]))

        # Implement the phase-separator unitary with a swap network
        # The covers indicate which qubits will be swapped at each layer
        cover_a = [(idx - 1, idx) for idx in range(1, self.num_qubits, 2)]
        cover_b = [(idx - 1, idx) for idx in range(2, self.num_qubits, 2)]

        # The indices of the virtual map correspond to physical qubits,
        # the value at that index corresponds to the virtual qubit residing there
        virtual_map = np.arange(self.num_qubits)

        for layer in range(self.num_qubits):
            cover = [cover_a, cover_b][layer % 2]
            for pair in cover:
                i, j = pair  # swap physical qubits i and j

                # Get the corresponding weight between the virtual qubits
                v_i = virtual_map[i]
                v_j = virtual_map[j]
                for edge in self.Hamiltonian:
                    if v_i == edge[0] and v_j == edge[1]:
                        weight = edge[2]
                phi = gamma * weight

                # Perform the ZZ+SWAP operation
                circuit.append(cirq.CNOT(qubits[i], qubits[j]))
                circuit.append(cirq.rz(2 * phi)(qubits[j]))
                circuit.append(cirq.CNOT(qubits[j], qubits[i]))
                circuit.append(cirq.CNOT(qubits[i], qubits[j]))

                # update the virtual map
                virtual_map[j], virtual_map[i] = virtual_map[i], virtual_map[j]

        # Implement the mixing unitary
        for i in range(self.num_qubits):
            circuit.append(cirq.rx(beta)(qubits[i]))

        # Measure all qubits
        circuit.append(cirq.measure(*qubits))

        # NOTE: the final qubits in this circuit are in REVERSED order due to the swap network
        return circuit

    def _get_energy_for_bitstring(self, bitstring: str) -> float:
        H_val = 0
        for i, j, weight in self.Hamiltonian:
            if bitstring[i] == bitstring[j]:
                H_val -= weight  # if edge is UNCUT, weight counts against objective
            else:
                H_val += weight  # if edge is CUT, weight counts towards objective
        return H_val

    def _get_expected_H_from_probs(self, probabilities: collections.Counter) -> float:
        H_expectation = 0.0
        for bitstring, probability in probabilities.items():
            H_expectation += probability * self._get_energy_for_bitstring(bitstring)
        return H_expectation

    def _get_ideal_counts(self, circuit: cirq.Circuit) -> collections.Counter:
        n = len(circuit.all_qubits())
        ideal_counts = {}
        for i, amplitude in enumerate(circuit.final_state_vector()):
            bitstring = f"{i:>0{n}b}"
            probability = np.abs(amplitude) ** 2
            ideal_counts[
                bitstring[::-1]
            ] = probability  # reverse the bitstring order due to Fermionic SWAP network
        return collections.Counter(ideal_counts)

    def _get_opt_angles(self) -> Tuple[List, float]:
        def f(params: List) -> float:
            gamma, beta = params
            circ = self._gen_swap_network(gamma, beta)
            probs = self._get_ideal_counts(circ)
            H_expect = self._get_expected_H_from_probs(probs)

            return -H_expect  # because we are minimizing instead of maximizing

        init_params = [np.random.uniform() * 2 * np.pi, np.random.uniform() * 2 * np.pi]
        out = scipy.optimize.minimize(f, init_params, method="COBYLA")

        return out["x"], out["fun"]

    def _gen_angles(self) -> List:
        # Classically simulate the variational optimization 5 times,
        # return the parameters from the best performing simulation
        best_params, best_cost = [], 0.0
        for _ in range(5):
            params, cost = self._get_opt_angles()
            if cost < best_cost:
                best_params = params
                best_cost = cost
        return best_params

    def circuit(self) -> cirq.Circuit:
        """Generate a QAOA circuit for the Sherrington-Kirkpatrick model using
        the fermionic swap network ansatz structure. We restrict the depth of
        this proxy benchmark to p=1 to keep the classical simulation scalable.
        """
        gamma, beta = self.params
        return self._gen_swap_network(gamma, beta)

    def score(self, counts: collections.Counter) -> float:
        """Compare the experimental output to the output of noiseless simulation.

        The implementation here has exponential runtime and would not scale.
        However, it could in principle be done efficiently via
        https://arxiv.org/abs/1706.02998, so we're good.
        """
        ideal_counts = self._get_ideal_counts(self.circuit())
        total_shots = sum(counts.values())
        # Reverse the order of the bitstrings due to the fermionic swap ansatz
        experimental_counts = collections.Counter(
            {k[::-1]: v / total_shots for k, v in counts.items()}
        )

        H_ideal = self._get_expected_H_from_probs(ideal_counts)
        H_experimental = self._get_expected_H_from_probs(experimental_counts)

        return 1 - abs(H_ideal - H_experimental) / (2 * H_ideal)
