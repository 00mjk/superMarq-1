import collections
import pytest

import cirq
import numpy as np
from supermarq.benchmarks.vqe_proxy import VQEProxy


def get_ideal_counts(circuit: cirq.Circuit) -> collections.Counter:
    ideal_counts = {}
    for i, amplitude in enumerate(circuit.final_state_vector()):
        bitstring = f"{i:>0{len(circuit.all_qubits())}b}"
        probability = np.abs(amplitude) ** 2
        ideal_counts[bitstring] = probability
    return collections.Counter(ideal_counts)


def test_vqe_circuit() -> None:
    vqe = VQEProxy(6)
    assert len(vqe.circuit()) == 6
    assert len(vqe.circuit()[0].all_qubits()) == 6

    vqe = VQEProxy(10)
    assert len(vqe.circuit()) == 6
    assert len(vqe.circuit()[0].all_qubits()) == 10


def test_vqe_score() -> None:
    vqe = VQEProxy(6)
    circuits = vqe.circuit()
    counts = [get_ideal_counts(circ) for circ in circuits]
    assert vqe.score(counts) > 0.99

    vqe = VQEProxy(10)
    circuits = vqe.circuit()
    counts = [get_ideal_counts(circ) for circ in circuits]
    assert vqe.score(counts) > 0.99


def test_invalid_size() -> None:
    with pytest.raises(
        ValueError, match="Only 6 and 10 qubit vqe benchmarks are currently supported"
    ):
        VQEProxy(3)
