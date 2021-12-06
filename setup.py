#!/usr/bin/env python3
# coding: utf-8

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='NIST Test Vectors',
    version='0.1',
    description='Convert test vectors from the NIST to any format',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords="nist test vectors crypto block cipher aes signature key derivation drbg",
    license="MIT",
    author='ShellCode',
    author_email='shellcode33@protonmail.ch',
    url='https://github.com/ShellCode33/NIST-Test-Vectors',
    packages=find_packages(),
    python_requires='>=3.6',

    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],

    install_requires=[
        "jinja2"
    ],

    entry_points={
        "console_scripts": [
            "nist-tv = nist_tests_vectors.cli:main",
        ]
    }
)
