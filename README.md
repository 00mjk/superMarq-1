# SupermarQ HPCA Artifact

## Artifact Evaluation

The artifact evaluation is contained within the `HPCA_Artifact.ipynb` jupyter notebook.

This notebook was created to serve as the reproducibility artifact for the paper "SupermarQ: A Scalable Quantum Benchmark Suite" accepted in the 28th IEEE International Symposium on High-Performance Computer Architecture (HPCA-28). The main contribution of this paper includes a quantum benchmark suite comprised of a number of different quantum applications. The software provided within this artifact includes the circuit generators and score functions for each benchmark application. This notebook provides an example of each benchmark: generating the quantum circuits with the provided parameters, simulating their execution via noisy density matrix simulation provided through Cirq (more on this in the following section), and finally computing the performance score of those executions.

This notebook is meant to serve as an overview of the process used to generate and collect the benchmark results that were presented in the above paper. Each benchmark is defined within a file found in the `supermarq/benchmarks/` directory. This file defines a benchmark class that includes a function for generating the quantum circuits, and a function for evaluating the benchmark score.

The first section of this notebook, **Benchmarks**, provides an overview of the benchmarks within the SupermarQ suite. The second section, **Features**, contains examples showing how the feature plots in Figure 1 were created (the corresponding code for the feature plots is contained in `supermarq/features.py`). Finally, the last section **Correlations** shows how the benchmark scores and application features (stored as Pandas dataframes within the `data/` directory) are used to create Figures 4 and 5. The `plotting_function.py` file contains the functions used to generate the correlation plots.

### Simulation vs. Hardware Execution

The benchmark results included in the SupermarQ paper were evaluated on real quantum computers including both superconducting and trapped ion processors. These systems were accessed over the cloud via services provided by IBM Quantum and Braket (Amazon). Access to some of these systems is restricted to certain users and the cost of running quantum programs varies among them. Because of these reasons, it would be impractical to exactly reproduce the results within the SupermarQ paper. Instead, we substitute the hardware executions with circuit simulations conducted via the Cirq SDK.

### Installation Guide

This artifact was generated using Python 3.8. We recommend creating a fresh python virtual environment. Then, the supermarq software package and all of its dependencies can be installed via:

```
cd SupermarQ_HPCA_Artifact
pip install -r requirements.txt
pip install -e .
```

The jupyter lab can be started with:
```
jupyter lab
```
