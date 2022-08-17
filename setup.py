import io
from setuptools import find_packages, setup

# This reads the __version__ variable from supermarq/_version.py
__version__ = ""
exec(open("supermarq/_version.py").read())

name = "SupermarQ"

description = "SupermarQ is a scalable, application-centric quantum benchmarking suite."

# README file as long_description.
long_description = io.open("README.md", encoding="utf-8").read()


# Read in requirements
requirements = open("requirements.txt").readlines()
requirements = [r.strip() for r in requirements]

supermarq_packages = ["supermarq"] + [
    "supermarq." + package for package in find_packages(where="supermarq")
]

# Sanity check
assert __version__, "Version string cannot be empty"

setup(
    name=name,
    version=__version__,
    url="https://github.com/SupertechLabs/SupermarQ",
    author="Super.tech",
    author_email="pranav@super.tech",
    python_requires=(">=3.8.0"),
    install_requires=requirements,
    extras_require={},
    license="N/A",
    description=description,
    long_description=long_description,
    packages=supermarq_packages,
    package_data={"supermarq": ["py.typed"]},
)
