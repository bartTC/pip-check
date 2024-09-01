#!/usr/bin/env python
from sys import exit

from setuptools import find_packages, setup

long_description = u"\n\n".join((open("README.rst").read(),))

setup(
    name="pip-check",
    version="2.9",
    description="Display installed pip packages and their update status..",
    long_description=long_description,
    author="Martin Mahner",
    author_email="martin@mahner.org",
    url="https://github.com/bartTC/pip-check/",
    classifiers=[],
    package_dir={"": "src"},
    packages=find_packages(
        where="src",
    ),
    package_data={},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "pip-check = pip_check:main",
        ]
    },
    python_requires=">=3.6",
    install_requires=[
        "terminaltables",
        "packaging",
        "pip>=9",
    ],
)
