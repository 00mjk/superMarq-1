import collections
import copy
from typing import Counter, List, Tuple

import cirq
import numpy as np
import scipy
from supermarq.benchmarks.benchmark import Benchmark


class VQEProxy(Benchmark):
    """Proxy benchmark of a full VQE application that targets a single iteration
    of the whole variational optimization.

    The benchmark is parameterized by the number of qubits, n. For each value of
    n, we classically optimize the ansatz, sample 3 iterations near convergence,
    and use the sampled parameters to execute the corresponding circuits on the
    QPU. We take the measured energies from these experiments and average their
    values and compute a score based on how closely the experimental results are
    to the noiseless values.
    """

    def __init__(self, num_qubits: int, num_layers: int = 1) -> None:
        self.num_qubits = num_qubits
        self.num_layers = num_layers
        self.Hamiltonian = self._gen_tfim_Hamiltonian()
        self._params = self._gen_angles()

    def _gen_tfim_Hamiltonian(self) -> List:
        r"""Generate an n-qubit Hamiltonian for a transverse-field Ising model (TFIM).

            $H = \sum_i^n(X_i) + \sum_i^n(Z_i Z_{i+1})$

        Example of a 6-qubit TFIM Hamiltonian:

            $H_6 = XIIIII + IXIIII + IIXIII + IIIXII + IIIIXI + IIIIIX + ZZIIII
                  + IZZIII + IIZZII + IIIZZI + IIIIZZ + ZIIIIZ$
        """
        H = []
        for i in range(self.num_qubits):
            H.append(["X", i, 1])  # [Pauli type, qubit idx, weight]
        for i in range(self.num_qubits - 1):
            H.append(["ZZ", (i, i + 1), 1])
        H.append(["ZZ", (self.num_qubits - 1, 0), 1])
        return H

    def _gen_ansatz(self, params: List[float]) -> List[cirq.Circuit]:
        qubits = cirq.LineQubit.range(self.num_qubits)
        z_circuit = cirq.Circuit()

        param_counter = 0
        for _ in range(self.num_layers):
            # Ry rotation block
            for i in range(self.num_qubits):
                z_circuit.append(cirq.Ry(rads=2 * params[param_counter])(qubits[i]))
                param_counter += 1
            # Rz rotation block
            for i in range(self.num_qubits):
                z_circuit.append(cirq.Rz(rads=2 * params[param_counter])(qubits[i]))
                param_counter += 1
            # Entanglement block
            for i in range(self.num_qubits - 1):
                z_circuit.append(cirq.CX(qubits[i], qubits[i + 1]))
            # Ry rotation block
            for i in range(self.num_qubits):
                z_circuit.append(cirq.Ry(rads=2 * params[param_counter])(qubits[i]))
                param_counter += 1
            # Rz rotation block
            for i in range(self.num_qubits):
                z_circuit.append(cirq.Rz(rads=2 * params[param_counter])(qubits[i]))
                param_counter += 1

        x_circuit = copy.deepcopy(z_circuit)
        x_circuit.append(cirq.H(q) for q in qubits)

        # Measure all qubits
        z_circuit.append(cirq.measure(*qubits))
        x_circuit.append(cirq.measure(*qubits))

        return [z_circuit, x_circuit]

    def _parity_ones(self, bitstr: str) -> int:
        one_count = 0
        for i in bitstr:
            if i == "1":
                one_count += 1
        return one_count % 2

    def _calc(self, bit_list: List[str], bitstr: str, probs: Counter) -> float:
        energy = 0.0
        for item in bit_list:
            if self._parity_ones(item) == 0:
                energy += probs.get(bitstr, 0)
            else:
                energy -= probs.get(bitstr, 0)
        return energy

    def _get_expected_H_from_probs(self, probs_Z: Counter, probs_X: Counter) -> float:
        avg_energy = 0.0

        # Find the contribution to the energy from the X-terms: \sum_i{X_i}
        for bitstr in probs_X.keys():
            bit_list_X = [bitstr[i] for i in range(len(bitstr))]
            avg_energy += self._calc(bit_list_X, bitstr, probs_X)

        # Find the contribution to the energy from the Z-terms: \sum_i{Z_i Z_{i+1}}
        for bitstr in probs_Z.keys():
            bit_list_Z = [bitstr[i - 1 : i + 1] for i in range(1, len(bitstr))]
            bit_list_Z.append(bitstr[0] + bitstr[-1])  # Add the wrap-around term manually
            avg_energy += self._calc(bit_list_Z, bitstr, probs_Z)

        return avg_energy

    def _get_ideal_probs(self, circuit: cirq.Circuit) -> collections.Counter:
        n = len(circuit.all_qubits())
        ideal_counts = {}
        for i, amplitude in enumerate(circuit.final_state_vector()):
            bitstring = f"{i:>0{n}b}"
            probability = np.abs(amplitude) ** 2
            ideal_counts[bitstring] = probability
        return collections.Counter(ideal_counts)

    def _get_opt_angles(self) -> Tuple[List, float]:
        def f(params: List) -> float:
            z_circuit, x_circuit = self._gen_ansatz(params)
            z_probs = self._get_ideal_probs(z_circuit)
            x_probs = self._get_ideal_probs(x_circuit)
            H_expect = self._get_expected_H_from_probs(z_probs, x_probs)

            return -H_expect  # because we are minimizing instead of maximizing

        init_params = [
            np.random.uniform() * 2 * np.pi for _ in range(self.num_layers * 4 * self.num_qubits)
        ]
        out = scipy.optimize.minimize(f, init_params, method="COBYLA")

        return out["x"], out["fun"]

    def _gen_angles(self) -> List:
        """Classically simulate the variational optimization and return
        the final parameters.
        """
        params, _ = self._get_opt_angles()
        return params

    def circuit(self) -> List[cirq.Circuit]:
        """Construct a parameterized ansatz.

        Returns a list of circuits: the ansatz measured in the Z basis, and the
        ansatz measured in the X basis. The counts obtained from evaluated these
        two circuits should be passed to `score` in the same order they are
        returned here.
        """
        return self._gen_ansatz(self._params)

    def score(self, counts: List[Counter]) -> float:
        """Compare the average energy measured by the experiments to the ideal
        value obtained via noiseless simulation. In principle the ideal value
        can be obtained through efficient classical means since the 1D TFIM
        is analytically solvable.
        """
        counts_Z, counts_X = counts
        shots_Z = sum(counts_Z.values())
        probs_Z = {bitstr: count / shots_Z for bitstr, count in counts_Z.items()}
        shots_X = sum(counts_X.values())
        probs_X = {bitstr: count / shots_X for bitstr, count in counts_X.items()}
        experimental_H = self._get_expected_H_from_probs(
            collections.Counter(probs_Z),
            collections.Counter(probs_X),
        )

        circuit_Z, circuit_X = self.circuit()
        ideal_H = self._get_expected_H_from_probs(
            self._get_ideal_probs(circuit_Z),
            self._get_ideal_probs(circuit_X),
        )

        return float(1.0 - abs(ideal_H - experimental_H) / abs(2 * ideal_H))
