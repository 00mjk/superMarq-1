import collections

import cirq
import numpy as np
import pytest
from supermarq.benchmarks.mermin_bell import MerminBell


def get_ideal_counts(circuit: cirq.Circuit) -> collections.Counter:
    ideal_counts = {}
    for i, amplitude in enumerate(circuit.final_state_vector()):
        bitstring = f"{i:>0{len(circuit.all_qubits())}b}"
        probability = np.abs(amplitude) ** 2
        ideal_counts[bitstring] = probability
    return collections.Counter(ideal_counts)


def test_mermin_bell_circuit() -> None:
    mb = MerminBell(3)
    assert len(mb.circuit().all_qubits()) == 3

    mb = MerminBell(4)
    assert len(mb.circuit().all_qubits()) == 4


def test_mermin_bell_score() -> None:
    mb = MerminBell(3)
    assert mb.score(get_ideal_counts(mb.circuit())) == 1

    mb = MerminBell(4)
    assert mb.score(get_ideal_counts(mb.circuit())) == 1


def test_invalid_size() -> None:
    with pytest.raises(
        ValueError, match="Only 3 and 4 qubit mermin-bell benchmarks are currently supported"
    ):
        MerminBell(5)
