# NIST Test Vectors

This tool allows you to download, parse and export to any format test vectors from the NIST.

It can be useful if you're planning to implement your own crypto algorithms and want to validate it.

## Installation

It's as simple as `pip install nist-test-vectors`.

## Usage

You can use this tool both in your CLI and in your Python scripts.

### Command Line Interface

```
$ ntv --help

```

### Using Python

```python
import nist_test_vectors as ntv

def my_function():
    ntv.download(ntv.aes, "/tmp/aes_test_vectors.rsp")
    rsp = ntv.parse("/tmp/aes_test_vectors.rsp")

    for test_vector in rsp:
        ntv.export(test_vector, "/tmp/aes_test_vectors.json")
```
