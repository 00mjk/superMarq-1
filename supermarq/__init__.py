from .benchmarks import benchmark
from .benchmarks import bit_code
from .benchmarks import ghz
from .benchmarks import hamiltonian_simulation
from .benchmarks import mermin_bell
from .benchmarks import phase_code
from .benchmarks import qaoa_fermionic_swap_proxy
from .benchmarks import qaoa_vanilla_proxy
from .benchmarks import vqe_proxy

__all__ = [
    "benchmark",
    "bit_code",
    "ghz",
    "hamiltonian_simulation",
    "mermin_bell",
    "phase_code",
    "qaoa_fermionic_swap_proxy",
    "qaoa_vanilla_proxy",
    "vqe_proxy",
]
