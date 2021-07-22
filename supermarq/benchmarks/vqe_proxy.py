import glob
import os
from typing import Counter, List

import cirq
import numpy as np
from cirq.contrib.qasm_import import circuit_from_qasm
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

    def __init__(self, num_qubits: int) -> None:
        if num_qubits != 6 and num_qubits != 10:
            raise ValueError("Only 6 and 10 qubit vqe benchmarks are currently supported")
        self.num_qubits = num_qubits

    def circuit(self) -> List[cirq.Circuit]:
        """For now the VQE proxy benchmark is hardcoded to support only the
        6 and 10 qubit benchmarks. The circuits for these are hardcoded in
        qasm files.

        Returns a list of circuits in the same order that the counts should be
        passed to `score`.
        """
        dir_path = os.path.dirname(os.path.realpath(__file__))
        benchmark_circs = glob.glob(f"{dir_path}/qasm/new_{self.num_qubits}q*.qasm")
        benchmark_circs = sorted(benchmark_circs, key=lambda x: int(x.split("_")[2]))
        benchmark_circs = sorted(
            benchmark_circs, key=lambda x: x.split("_")[-1].strip(".qasm"), reverse=True
        )

        circuits = []
        for fn in benchmark_circs:
            with open(fn, "r") as qasmfile:
                qasm_str = ""
                for line in qasmfile:
                    # The circuits in the qasm files were compiled to the set {u, CX}
                    # (which is what is technically in the paper), but the cirq
                    # function circuit_from_qasm needs uppercase U
                    if line[0] == "u":
                        line = "U" + line[1:]
                    qasm_str += line

            circuit = circuit_from_qasm(qasm_str)

            # circuit_from_qasm yields NamedQubits but we need LineQubits
            qubits = cirq.LineQubit.range(self.num_qubits)
            qubit_map = {cirq.NamedQubit(f"q_{i}"): qubits[i] for i in range(self.num_qubits)}

            new_circuit = circuit.transform_qubits(qubit_map)
            new_circuit += cirq.measure(*qubits)  # also add in measurements on all qubits

            circuits.append(new_circuit)

        return circuits

    def _parity_ones(self, bitstr: str) -> int:
        one_count = 0
        for i in bitstr:
            if i == "1":
                one_count += 1
        return one_count % 2

    def _calc(self, key_list: List[str], key: str, H: int, counts: Counter) -> int:
        for item in key_list:
            if self._parity_ones(item) == 0:
                H += counts.get(key, 0)
            else:
                H -= counts.get(key, 0)
        return H

    def _get_H_val(self, counts_Z: Counter, counts_X: Counter) -> float:
        H = 0
        key_list_Z = []
        key_list_X = []

        # 6 qubit, the key list corresponds to the terms in the Hamiltonian:
        #    XIIIII + IXIIII + IIXIII + IIIXII + IIIIXI + IIIIIX + ZZIIII
        #     + IZZIII + IIZZII + IIIZZI + IIIIZZ + ZIIIIZ
        # NOTE: After HPCA submission, generalize this code
        if self.num_qubits == 6:
            for key in counts_X.keys():
                key_list_X = [key[0], key[1], key[2], key[3], key[4], key[5]]
                H = self._calc(key_list_X, key, H, counts_X)
            for key in counts_Z.keys():
                key_list_Z = [key[0:2], key[1:3], key[2:4], key[3:5], key[4:6], (key[0] + key[5])]
                H = self._calc(key_list_Z, key, H, counts_Z)

        # 10 qubit
        if self.num_qubits == 10:
            for key in counts_X.keys():
                key_list_X = [
                    key[0],
                    key[1],
                    key[2],
                    key[3],
                    key[4],
                    key[5],
                    key[6],
                    key[7],
                    key[8],
                    key[9],
                ]
                H = self._calc(key_list_X, key, H, counts_X)
            for key in counts_Z.keys():
                key_list_Z = [
                    key[0:2],
                    key[1:3],
                    key[2:4],
                    key[3:5],
                    key[4:6],
                    key[5:7],
                    key[6:8],
                    key[7:9],
                    key[8:10],
                    (key[0] + key[9]),
                ]
                H = self._calc(key_list_Z, key, H, counts_Z)

        shots = sum(counts_Z.values())
        return H / shots

    def score(self, counts: List[Counter]) -> float:
        """Compare the average energy measured by the experiments to the ideal
        value obtained via noiseless simulation. In principle the ideal value
        can be obtained through efficient classical means since the 1D TFIM
        is analytically solvable.
        """
        counts_Z1, counts_Z2, counts_Z3, counts_X1, counts_X2, counts_X3 = counts

        if self.num_qubits == 6:
            ideal_H = -7.42
        elif self.num_qubits == 10:
            ideal_H = -12.43

        experimental_H_val1 = self._get_H_val(counts_Z1, counts_X1)
        experimental_H_val2 = self._get_H_val(counts_Z2, counts_X2)
        experimental_H_val3 = self._get_H_val(counts_Z3, counts_X3)

        experimental_H = np.mean([experimental_H_val1, experimental_H_val2, experimental_H_val3])

        return float(1.0 - abs(ideal_H - experimental_H) / abs(2 * ideal_H))
