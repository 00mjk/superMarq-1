import collections

import cirq
import supermarq
from supermarq.benchmarks.benchmark import Benchmark
from qiskit.quantum_info import hellinger_fidelity


class GHZ(Benchmark):
    """Represents the GHZ state preparation benchmark parameterized
    by the number of qubits n.

    Device performance is based on the Hellinger fidelity between
    the experimental and ideal probability distributions.
    """

    def __init__(self, n: int) -> None:
        self.n = n

    def circuit(self) -> cirq.Circuit:
        """Generate an n-qubit GHZ circuit"""
        qubits = cirq.LineQubit.range(self.n)
        circuit = cirq.Circuit()
        circuit.append(cirq.H(qubits[0]))
        for i in range(self.n - 1):
            circuit.append(cirq.CNOT(qubits[i], qubits[i + 1]))
        circuit.append(cirq.measure(*qubits))
        return circuit

    def score(self, counts: collections.Counter) -> float:
        """Compute the Hellinger fidelity between the experimental and ideal
        results, i.e., 50% probabilty of measuring the all-zero state and 50%
        probability of measuring the all-one state.

        The formula for the Hellinger fidelity between two distributions p and q
        is given by $(\sum_i{p_i q_i})^2$.
        """
        # Create an equal weighted distribution between the all-0 and all-1 states
        ideal_dist = {b * self.n: 0.5 for b in ["0", "1"]}
        total_shots = sum(counts.values())
        device_dist = {bitstr: count / total_shots for bitstr, count in counts.items()}
        return hellinger_fidelity(ideal_dist, device_dist)
