import collections
from typing import Dict, List

import cirq
from qiskit.quantum_info import hellinger_fidelity
from supermarq.benchmarks.benchmark import Benchmark


class PhaseCode(Benchmark):
    """
    Creates a circuit for syndrome measurement in a phase-flip error
    correcting code.

    Args:
    - num_data: The number of data qubits
    - num_rounds: The number of measurement rounds
    - phase_state: A list denoting the state to initialize each data
                   qubit to. Currently just + or - states. 0 -> +, 1 -> -

    returns a cirq circuit for the phase-flip error correcting code

    """

    def __init__(
        self, num_data_qubits: int, num_rounds: int, phase_state: List[int] = [0, 1, 0]
    ) -> None:
        if len(phase_state) != num_data_qubits:
            raise ValueError("The length of `phase_state` must match the number of data qubits")
        self.num_data_qubits = num_data_qubits
        self.num_rounds = num_rounds
        self.phase_state = phase_state

    def _measurement_round_cirq(self, qubits: List[cirq.LineQubit]) -> None:
        """
        Generates cirq ops for a single measurement round

        Args:
        - qubits: Circuit qubits - assumed data on even indices and
                  measurement on odd indices
        """
        yield [cirq.ops.reset(qubits[i]) for i in range(1, len(qubits), 2)]
        yield [cirq.H(q) for q in qubits]
        for i in range(1, len(qubits), 2):
            yield cirq.CZ(qubits[i - 1], qubits[i])
            yield cirq.CZ(qubits[i + 1], qubits[i])
        yield [cirq.H(q) for q in qubits]

    def circuit(self) -> cirq.Circuit:
        num_qubits = 2 * self.num_data_qubits - 1
        qubits = cirq.LineQubit.range(num_qubits)
        circuit = cirq.Circuit()

        # Initialize the data qubits
        for i in range(self.num_data_qubits):
            if self.phase_state[i] == 1:
                circuit.append(cirq.X(qubits[2 * i]))
            circuit.append(cirq.H(qubits[2 * i]))

        # Apply measurement rounds
        circuit.append(self._measurement_round_cirq(qubits) for _ in range(self.num_rounds))

        circuit.append(cirq.measure(*qubits))

        return circuit

    def _get_dist(self, circuit: cirq.Circuit) -> collections.Counter:
        shots = 5000
        result = cirq.Simulator().run(circuit, repetitions=shots)

        num_measured_qubits = []
        for _, op in circuit.findall_operations(cirq.is_measurement):
            num_measured_qubits.append(len(op.qubits))
        raw_counts = result.multi_measurement_histogram(keys=result.measurements.keys())

        # cirq.Result.multi_measurement_histogram returns a collection.Counter object
        # where the keys are tuples of integers and the values are the shot counts.
        # The integers in the keys indicate the bitstring result of each set of measurement tags.
        counts: Dict[str, int] = collections.defaultdict(int)
        for key, val in raw_counts.items():
            bit_list = []
            for int_tag, num_bits in zip(key, num_measured_qubits):
                bit_list.extend(cirq.value.big_endian_int_to_bits(int_tag, bit_count=num_bits))
            counts["".join([str(b) for b in bit_list])] = val / shots

        return collections.Counter(counts)

    def score(self, counts: collections.Counter) -> float:
        """Device performance is given by the Hellinger fidelity between
        the experimental results and the ideal distribution. The ideal
        is known based on the bit_state parameter.
        """
        ideal_dist = self._get_dist(self.circuit())
        total_shots = sum(counts.values())
        experimental_dist = {bitstr: shots / total_shots for bitstr, shots in counts.items()}
        return hellinger_fidelity(ideal_dist, experimental_dist)
