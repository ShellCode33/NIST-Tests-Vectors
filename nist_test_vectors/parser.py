# coding: utf-8

from typing import List, Set, Union, Iterator, Dict
from io import TextIOWrapper
from dataclasses import dataclass
from collections.abc import Iterable


class RspParsingError(Exception):
    """
    Raised when parsing the RSP file fails due to unexpected data.
    """

@dataclass(frozen=True)
class TestVector:
    key: str
    value: Union[int, bytearray]

    @staticmethod
    def parse_vector_value(value: str) -> Union[int, bytearray]:
        """
        Some test vector values are base 10 compatible but are in fact bytes string.
        This static method tries to guess whether the test vector value should be a
        bytes array or a raw integer.

        Raises ValueError if given parameter is invalid.
        """

        # Only base 16 values can start with 0.
        # (except 0 itself but 0 is the same in base 10 and base 16)
        if value.startswith("00"):
            return bytearray.fromhex(value)

        try:
            value_as_int = int(value, 10)

            # If an integer is more than 4 bytes wide it's probably an hexstring
            if value_as_int > 2**32 - 1:
                return bytearray.fromhex(value)

            else:
                return value_as_int

        except ValueError:
            return bytearray.fromhex(value)


class TestVectors(Iterable):
    """
    """

    def __init__(self):
        self._test_vectors: List[TestVector] = []

    def keys(self) -> Set[str]:
        return set([v.key for v in self._test_vectors])

    def __iter__(self) -> Iterator[TestVector]:
        return self._test_vectors.__iter__()

    def __dict__(self) -> Dict[str, Union[str, int, bytearray]]:
        return {vec.key: vec.value for vec in self._test_vectors}

    def __getitem__(self, key: str):
        for vec in self._test_vectors:
            if vec.key == key:
                return vec.value

        raise KeyError(f"Key '{key}' not found")

    def __len__(self):
        return len(self._test_vectors)

    def append(self, item: TestVector):
        self._test_vectors.append(item)


class TestVectorsIterator:

    """
    """

    def __init__(self, rsp_fd: TextIOWrapper):
        self._rsp_fd = rsp_fd

        # Not that much of an overhead and allows us to detect missing fields in vectors
        self._expected_fields: Set[str] = set()

    def __iter__(self):
        return self

    def __next__(self) -> TestVectors:
        vectors = self._read_vectors()
        vectors_keys = vectors.keys()

        if "COUNT" not in vectors_keys:
            raise RspParsingError("Invalid test vector: missing field COUNT")

        if len(vectors) == 1:
            raise RspParsingError("Invalid test vector: COUNT is the only field")

        if not self._expected_fields:
            self._expected_fields = vectors_keys

        elif vectors_keys != self._expected_fields:
            raise RspParsingError("Invalid test vector: fields inconsistency")

        return vectors

    def _read_vectors(self) -> TestVectors:
        vectors = TestVectors()

        line = self._rsp_fd.readline()

        # Skip potentially empty lines
        while line == "\n":
            line = self._rsp_fd.readline()

        # End of file
        if not line:
            raise StopIteration

        # Beginning of new profile detected = must stop iterating
        if line.startswith("["):
            # Cancel the reading of this line so that it can be 
            # parsed by the ProfileIterator instead
            self._rsp_fd.seek(self._rsp_fd.tell() - len(line) - 1)
            raise StopIteration

        # Keep reading lines while there's data to parse
        while line and line != "\n" and not line.startswith("["):
            key, value = line.split("=")
            key = key.strip()

            if key in vectors.keys():
                raise RspParsingError(f"Duplicated key: {key}")

            try:
                value = TestVector.parse_vector_value(value)
            except ValueError:
                raise RspParsingError(f"Expected integer or hexstring, got: {value}") from None

            vectors.append(TestVector(key, value))
            line = self._rsp_fd.readline()

        # Beginning of new profile detected = we will stop iterating next call
        # But we must still return the vector we parsed
        if line.startswith("["):
            # Cancel the reading of this line
            self._rsp_fd.seek(self._rsp_fd.tell() - len(line) - 1)

        return vectors

class Profile:

    """
    """

    def __init__(self, rsp_fd: TextIOWrapper):
        self._rsp_fd = rsp_fd
        self._file_ptr_after_profile: int

        self.attributes: Dict[str, Union[str, int, bytearray]]
        self._read_profile_attributes()

    def __repr__(self) -> str:
        return f"Profile({self.attributes})"

    def __eq__(self, other) -> bool:

        if not isinstance(other, Profile):
            return NotImplemented

        return self.attributes == other.attributes

    def _read_profile_attributes(self) -> None:
        self.attributes = {}
        line = self._rsp_fd.readline()

        # Keep reading lines until we find a profile
        while line and not line.startswith("["):
            line = self._rsp_fd.readline()

        # End of file
        if not line:
            raise StopIteration

        # Parse the profile
        while line.startswith("["):
            tokens = line[1:-2].split("=")

            if len(tokens) == 0 or len(tokens) > 2:
                raise RspParsingError(f"Invalid profile attribute: {tokens}")

            key = tokens[0].strip()
            value = tokens[1].strip() if len(tokens) == 2 else ""

            if key in self.attributes:
                raise RspParsingError(f"Duplicated attribute: {key}")

            self.attributes[key] = value

            line = self._rsp_fd.readline()

        self._file_ptr_after_profile = self._rsp_fd.tell() - len(line) - 1

        # Cancel the reading of the last line as its processing does not belong here
        self._rsp_fd.seek(self._file_ptr_after_profile)


    @property
    def vectors(self) -> TestVectorsIterator:
        self._rsp_fd.seek(self._file_ptr_after_profile)
        return TestVectorsIterator(self._rsp_fd)


class RspFile:

    """
    """

    def __init__(self, path: str):
        self.path = path

        self.metadata: List[str]

        # Private attributes
        self._rsp_fd: TextIOWrapper
        self._file_ptr_after_metadata: int

        # Not that much of an overhead and allows us to detect duplicates
        self._seen_profiles: List[Profile] = []

        self._rsp_fd = open(self.path, "r")
        self._read_meta_data()

    def close(self):
        if self._rsp_fd:
            self._rsp_fd.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def __iter__(self):
        # Set file pointer after the metadata
        self._rsp_fd.seek(self._file_ptr_after_metadata)

        # Reset seen profiles
        self._seen_profiles.clear()
        return self

    def __next__(self):
        p = Profile(self._rsp_fd)

        if p in self._seen_profiles:
            raise RspParsingError(f"Duplicated profile: {p}")

        self._seen_profiles.append(p)
        return p

    def _read_meta_data(self):
        self.metadata = []

        line = self._rsp_fd.readline()

        # Skip potentially empty first lines
        while line == "\n":
            line = self._rsp_fd.readline()

        while line.startswith("#"):
            self.metadata.append(line[1:].strip())
            line = self._rsp_fd.readline()

        self._file_ptr_after_metadata = self._rsp_fd.tell() - len(line) - 1

        # Cancel the reading of the last line to let the iterators parse it instead
        self._rsp_fd.seek(self._file_ptr_after_metadata)

    @property
    def profiles(self) -> List[Profile]:
        return [p for p in self]

