import io
from setuptools import find_packages, setup

# This reads the __version__ variable from superstaq/_version.py
__version__ = ""
exec(open("superstaq/_version.py").read())

name = "SuperstaQ"

description = "SuperstaQ accelerates quantum computers by optimizing across the entire stack"

# README file as long_description.
long_description = io.open("README.md", encoding="utf-8").read()


# Read in requirements
requirements = open("requirements.txt").readlines()
requirements = [r.strip() for r in requirements]
dev_requirements = open("dev-requirements.txt").readlines()
dev_requirements = [r.strip() for r in dev_requirements]

superstaq_packages = ["superstaq"] + [
    "superstaq." + package for package in find_packages(where="superstaq")
]

# Sanity check
assert __version__, "Version string cannot be empty"

setup(
    name=name,
    version=__version__,
    url="https://github.com/SupertechLabs/SuperstaQ",
    author="Super.tech",
    author_email="pranav@super.tech",
    python_requires=(">=3.8.0"),
    install_requires=requirements,
    extras_require={
        "dev_env": dev_requirements,
    },
    license="N/A",
    description=description,
    long_description=long_description,
    packages=superstaq_packages,
    package_data={"superstaq": ["py.typed"]},
)
