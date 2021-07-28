#!/usr/bin/env python
import glob, sys, os
import argparse
import scipy
import qiskit
import numpy as np
import supermarq as sm


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vecs', type=str, default=None,
                        help='name of the feature vectors')
    args = parser.parse_args()
    return args


def compute_features():
    benchmarks = ['small', 'medium', 'large']

    feature_vecs = []

    for bmark_fn in benchmarks:
        print('Loading:', bmark_fn)
        bmarks = glob.glob(bmark_fn + '/*')
        print('\tFound {} circuits'.format(len(bmarks)))
        for qasm in bmarks:
            name = qasm.split('/')[-1].strip('.qasm')
            print('\t', name)
            try:
                circ = qiskit.QuantumCircuit().from_qasm_file(qasm)
            except qiskit.qasm.QasmError as err:
                print('\t\tSkipping due to QasmError:\n\t\t', err)
                continue
            print('\t\tqubits: {},'.format(circ.num_qubits), *['{}: {},'.format(key, val) for key, val in circ.count_ops().items()])
            feature_vecs.append([sm.features.compute_connectivity(circ),
                                 sm.features.compute_liveness(circ),
                                 sm.features.compute_parallelism(circ),
                                 sm.features.compute_measurement(circ),
                                 sm.features.compute_entanglement(circ),
                                 sm.features.compute_depth(circ)
                                ])

    feature_vecs.append(np.zeros(6))
    # save feature vector to file
    with open('supermarq_feature_vector.npy', 'wb') as fn:
        np.save(fn, np.array(feature_vecs))

    return np.array(feature_vecs)


def compute_volume(points):
    print(points)
    hull = scipy.spatial.ConvexHull(points)
    volume = hull.volume
    print('SupermarQ volume:', volume)


def main():
    args = parse_args()

    if args.vecs is None:
        points = compute_features()
    else:
        points = np.load(args.vecs)

    compute_volume(points)


if __name__ == '__main__':
    main()
