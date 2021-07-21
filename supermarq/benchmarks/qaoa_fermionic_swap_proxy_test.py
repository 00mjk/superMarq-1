import collections

import cirq
from supermarq.benchmarks.qaoa_fermionic_swap_proxy import QAOAFermionicSwapProxy


def test_qaoa_circuit() -> None:
    qaoa = QAOAFermionicSwapProxy(4)
    assert len(qaoa.circuit().all_qubits()) == 4
    assert (
        len(
            list(qaoa.circuit().findall_operations(lambda op: isinstance(op.gate, type(cirq.CNOT))))
        )
        == 18
    )


def test_qaoa_score() -> None:
    qaoa = QAOAFermionicSwapProxy(4)
    ideal_counts = qaoa.get_ideal_counts(qaoa.circuit())
    assert qaoa.score(collections.Counter({k[::-1]: v for k, v in ideal_counts.items()})) > 0.99
