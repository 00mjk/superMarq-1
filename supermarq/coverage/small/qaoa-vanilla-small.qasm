OPENQASM 2.0;
include "qelib1.inc";


// Qubits: [5, 2, 1, 4, 0, 3]
qreg q[6];
creg m0[6];  // Measurement: 0,1,2,3,4,5


h q[4];
h q[2];
h q[1];
h q[5];
h q[3];
h q[0];
cx q[3],q[0];
rz(pi*0.6366197724) q[0];
cx q[3],q[0];
cx q[1],q[0];
cx q[4],q[3];
rz(pi*-0.6366197724) q[0];
rz(pi*0.6366197724) q[3];
cx q[1],q[0];
cx q[4],q[3];
cx q[1],q[3];
cx q[4],q[0];
rz(pi*-0.6366197724) q[3];
rz(pi*-0.6366197724) q[0];
cx q[1],q[3];
cx q[4],q[0];
cx q[1],q[5];
cx q[4],q[2];
rz(pi*0.6366197724) q[5];
rz(pi*0.6366197724) q[2];
cx q[1],q[5];
cx q[4],q[2];
cx q[2],q[5];
rz(pi*-0.6366197724) q[5];
cx q[2],q[5];
cx q[5],q[0];
cx q[2],q[1];
rz(pi*-0.6366197724) q[0];
rz(pi*-0.6366197724) q[1];
cx q[5],q[0];
cx q[2],q[1];
cx q[4],q[5];
cx q[2],q[0];
rz(pi*-0.6366197724) q[5];
rz(pi*0.6366197724) q[0];
cx q[4],q[5];
cx q[2],q[0];
cx q[2],q[3];
cx q[4],q[1];
rx(pi*0.6366197724) q[0];
rz(pi*0.6366197724) q[3];
rz(pi*0.6366197724) q[1];
cx q[2],q[3];
cx q[4],q[1];
cx q[5],q[3];
rx(pi*0.6366197724) q[4];
rx(pi*0.6366197724) q[2];
rx(pi*0.6366197724) q[1];
rz(pi*-0.6366197724) q[3];
cx q[5],q[3];
rx(pi*0.6366197724) q[5];
rx(pi*0.6366197724) q[3];

// Gate: cirq.MeasurementGate(6, '0,1,2,3,4,5', ())
measure q[4] -> m0[0];
measure q[2] -> m0[1];
measure q[1] -> m0[2];
measure q[5] -> m0[3];
measure q[3] -> m0[4];
measure q[0] -> m0[5];
