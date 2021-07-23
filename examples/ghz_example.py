#!/usr/bin/env python
import cirq
import cirq_superstaq
import supermarq as sm
import time


def main():
    service = cirq_superstaq.Service(
        remote_host="https://127.0.0.1:5000",
        api_key="""ya29.a0ARrdaM8taiSjj8IUgpQaeBmKdgYRfPiZeCRGGDKZxeiaFeZ3driSTUGn-hvAVMzs8iTuWAa08lb4d4KhMa5aRDmtN7LIAXF-o9MuXOMX9KbUmxOKLgEBYJ5Kr51Sm4LDlVKEUJIJLEVRyBIez_4znsYfetpEAw""",
        ibmq_token="70c3bf3be7eed9265577858ab058697602b7b831f742556d83594f3655fcd192de2160c2469f3432f1ac54263eb8eb38bf7b4d10519eaf2f420f72e0e3ec7f72",
        ibmq_hub="ibm-q-startup",
        ibmq_group="super-tech-labs",
        ibmq_project="default",
        verbose=True,
    )


    nq = 3
    ghz = sm.benchmarks.ghz.GHZ(nq)

    print(ghz.circuit())

    ibm_job = service.create_job(circuit=ghz.circuit(), repetitions=100, target="ibmq_qasm_simulator")
    print("Created IBM job:", ibm_job)
    print("Current IBM status:", ibm_job.status())

    while ibm_job.status() != "Done":
        time.sleep(10)

    print("IBM Job status:", ibm_job.status())
    print('IBM Counts:', ibm_job.counts())
    print("IBM Benchmark score:", ghz.score(ibm_job.counts()))
    print('IBM Job_id:', ibm_job.job_id())
    ibm_job = service.get_job(ibm_job.job_id())
    print('IBM Counts:', ibm_job.counts())


    aws_job = service.create_job(circuit=ghz.circuit(), repetitions=100, target="aws_sv1_simulator")
    print("Created AWS job:", aws_job)
    print("Current AWS status:", aws_job.status())

    time.sleep(10)
    while aws_job.status() != "Done":
        time.sleep(10)

    print("AWS Job status:", aws_job.status())
    print('AWS Counts:', aws_job.counts())
    print("AWS Benchmark score:", ghz.score(aws_job.counts()))
    print('AWS Job_id:', aws_job.job_id())
    print("AWS Service.get_job:",service.get_job(aws_job.job_id()))


if __name__=='__main__':
    main()
