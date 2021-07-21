#!/usr/bin/env python
import cirq
import cirq_superstaq
import supermarq as sm
import time


def main():
    service = cirq_superstaq.Service(
            remote_host="https://127.0.0.1:5000",
            api_key="""Paste your SuperstaQ token here""",
            ibmq_token="Paste your IBM Token here",
            ibmq_hub="ibm-q-startup",
            ibmq_group="super-tech-labs",
            ibmq_project="default",
            ibmq_pulse='false',
            verbose=True,
    )


    nq = 3
    ghz = sm.benchmarks.ghz.GHZ(nq)

    print(ghz.circuit())

    job = service.create_job(circuit=ghz.circuit(), repetitions=1000, target="ibmq_qasm_simulator")
    print("Created job:", job)
    print("Current status:", job.status())

    while job.status() != "Done":
        time.sleep(5)

    print("Job status:", job.status())
    print('Counts:', job.counts())
    print("Benchmark score:", ghz.score(job.counts()))
    print('Job_id:', job.job_id())
    print("Service.get_job:",service.get_job(job.job_id()))


if __name__=='__main__':
    main()
