#!/usr/bin/env python
from sys import exit

from setuptools import find_packages, setup

long_description = u'\n\n'.join((
    open('README.rst').read(),
))

setup(
    name='pip-check',
    version='2.1.1',
    description='Display installed pip packages and their update status..',
    long_description=long_description,
    author='Martin Mahner',
    author_email='martin@mahner.org',
    url='https://github.com/bartTC/pip-check/',
    classifiers=[
    ],
    packages=find_packages(),
    package_data={},
    include_package_data=True,
    scripts = ['pip-check'],
    install_requires=[
        'terminaltables',
        'colorclass',
    ],
    tests_require=[
    ],
    cmdclass={
    },
)
