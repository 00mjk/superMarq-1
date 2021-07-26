import collections
from typing import List, Tuple

import cirq
import numpy as np
import sympy
from supermarq.benchmarks.benchmark import Benchmark


class MerminBell(Benchmark):
    """The Mermin-Bell benchmark is a test of a quantum computer's ability
    to exploit purely quantum phenomemna such as superposition and entanglement.
    It is based on the famous Bell-inequality tests of locality.

    Performance is based on a QPU's ability to prepare a GHZ state and measure
    the Mermin operator.
    """

    def __init__(self, num_qubits: int) -> None:
        if num_qubits != 3 and num_qubits != 4:
            raise ValueError("Only 3 and 4 qubit mermin-bell benchmarks are currently supported")
        self.num_qubits = num_qubits

    def circuit(self) -> cirq.Circuit:
        qubits = cirq.LineQubit.range(self.num_qubits)

        if self.num_qubits == 3:
            ops = [
                cirq.rx(-np.pi / 2).on(qubits[0]),
                cirq.CNOT(qubits[0], qubits[1]),
                cirq.CNOT(qubits[1], qubits[2]),
                cirq.H(qubits[1]),
                cirq.H(qubits[2]),
                cirq.CNOT(qubits[0], qubits[2]),
                cirq.CNOT(qubits[1], qubits[2]),
                cirq.CNOT(qubits[2], qubits[0]),
                cirq.CNOT(qubits[1], qubits[0]),
                cirq.S(qubits[2]),
                cirq.S(qubits[0]),
                cirq.H(qubits[2]),
                cirq.CZ(qubits[0], qubits[1]),
                cirq.H(qubits[0]),
                cirq.S(qubits[1]),
                cirq.H(qubits[1]),
                cirq.measure(*qubits),
            ]

        if self.num_qubits == 4:
            ops = [
                cirq.rx(-np.pi / 2).on(qubits[0]),
                cirq.CNOT(qubits[0], qubits[1]),
                cirq.CNOT(qubits[1], qubits[2]),
                cirq.CNOT(qubits[2], qubits[3]),
                cirq.H(qubits[1]),
                cirq.H(qubits[2]),
                cirq.H(qubits[3]),
                cirq.CNOT(qubits[0], qubits[3]),
                cirq.SWAP(qubits[1], qubits[2]),
                cirq.CNOT(qubits[1], qubits[3]),
                cirq.CNOT(qubits[2], qubits[3]),
                cirq.CNOT(qubits[3], qubits[0]),
                cirq.CNOT(qubits[2], qubits[0]),
                cirq.CNOT(qubits[1], qubits[0]),
                cirq.S(qubits[3]),
                cirq.H(qubits[3]),
                cirq.S(qubits[0]),
                cirq.CZ(qubits[0], qubits[1]),
                cirq.S(qubits[1]),
                cirq.CZ(qubits[0], qubits[2]),
                cirq.CZ(qubits[1], qubits[2]),
                cirq.H(qubits[0]),
                cirq.H(qubits[1]),
                cirq.S(qubits[2]),
                cirq.H(qubits[2]),
                cirq.measure(*qubits),
            ]

        return cirq.Circuit(ops)

    def score(self, counts: collections.Counter) -> float:
        if self.num_qubits == 3:
            return self._mermin_score_N3(counts)
        else:
            return self._mermin_score_N4(counts)

    def _mermin_operator(self, n: int) -> List[Tuple[float, str]]:
        """
        Generate the Mermin operator (https://journals.aps.org/prl/pdf/10.1103/PhysRevLett.65.1838),
        or M_n (Eq. 2.8) in https://arxiv.org/pdf/2005.11271.pdf
        """
        x = sympy.symbols("x_1:{}".format(n + 1))
        y = sympy.symbols("y_1:{}".format(n + 1))

        term1 = 1
        term2 = 1
        for j in range(n):
            term1 = term1 * (x[j] + sympy.I * y[j])
            term2 = term2 * (x[j] - sympy.I * y[j])
        term1 = sympy.expand(term1)
        term2 = sympy.expand(term2)

        M_n = (1 / (2 * sympy.I)) * (term1 - term2)
        M_n = sympy.simplify(M_n)

        variables = M_n.as_terms()[1]
        mermin_op = []
        for term in M_n.as_terms()[0]:
            coef = term[1][0][0]
            pauli = [""] * n
            for i, v in enumerate(term[1][1]):
                if v == 1:
                    char, idx = str(variables[i]).split("_")
                    pauli[int(idx) - 1] = char.upper()

            mermin_op.append((coef, "".join(pauli)))

        return mermin_op

    def _mermin_score_N3(self, counts: collections.Counter) -> float:
        """
        Compute the score for the 3-qubit Mermin-Bell benchmark.

        This function assumes the regular big endian ordering of bitstring results
        """
        mermin_op = self._mermin_operator(3)
        count_dict = {
            "XXY": {"counts": counts, "qubits": [0], "coef": 1},
            "XYX": {"counts": counts, "qubits": [1], "coef": 1},
            "YXX": {"counts": counts, "qubits": [2], "coef": -1},
            "YYY": {"counts": counts, "qubits": [0, 1, 2], "coef": 1},
        }

        expect_val = 0.0
        for term in mermin_op:
            coef, pauli = term

            cur_counts = count_dict[pauli]["counts"]
            meas_qb = count_dict[pauli]["qubits"]
            meas_coef = count_dict[pauli]["coef"]

            numerator = 0
            for bitstr, count in cur_counts.items():
                parity = meas_coef * 1
                for qb in meas_qb:
                    if bitstr[qb] == "1":  # Qubit order is big endian
                        parity = -1 * parity

                numerator += coef * parity * count

            expect_val += numerator / sum(list(cur_counts.values()))

        print("<mermin_op> =", expect_val)
        # so expect_val of 4 gives score of 1.0 and expect_val of -4 gives score of 0
        return (expect_val + 4) / 8

    def _mermin_score_N4(self, counts: collections.Counter) -> float:
        """
        Compute the score for the 4-qubit Mermin-Bell benchmark.

        This function assumes the regular big endian ordering of bitstring results
        """
        mermin_op = self._mermin_operator(4)
        count_dict = {
            "XXXY": {"counts": counts, "qubits": [0], "coef": 1},
            "XXYX": {"counts": counts, "qubits": [1], "coef": 1},
            "XYXX": {"counts": counts, "qubits": [2], "coef": 1},
            "YXXX": {"counts": counts, "qubits": [3], "coef": -1},
            "XYYY": {"counts": counts, "qubits": [0, 1, 2], "coef": -1},
            "YXYY": {"counts": counts, "qubits": [0, 1, 3], "coef": 1},
            "YYXY": {"counts": counts, "qubits": [0, 2, 3], "coef": 1},
            "YYYX": {"counts": counts, "qubits": [1, 2, 3], "coef": 1},
        }

        expect_val = 0.0
        for term in mermin_op:
            coef, pauli = term

            cur_counts = count_dict[pauli]["counts"]
            meas_qb = count_dict[pauli]["qubits"]
            meas_coef = count_dict[pauli]["coef"]

            numerator = 0
            for bitstr, count in cur_counts.items():
                parity = meas_coef * 1
                for qb in meas_qb:
                    if bitstr[qb] == "1":  # Qubit order is big endian
                        parity = -1 * parity

                numerator += coef * parity * count

            expect_val += numerator / sum(list(cur_counts.values()))

        print("<mermin_op> =", expect_val)
        # so expect_val of 8 gives score of 1.0 and expect_val of -8 gives score of 0
        return (expect_val + 8) / 16
