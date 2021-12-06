# coding: utf-8

import os
import itertools
from collections.abc import Iterable
from typing import Union, List

import json
from json.encoder import JSONEncoder

from jinja2 import Template

from nist_tests_vectors.parser import RspFile, Profile, TestVector, TestVectors, TestVectorsIterator

SUPPORTED_EXPORT_FORMATS = ["json", "c"]
SUPPORTED_TEMPLATE_FORMATS = ["c"]

_THIS_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

_DEFAULT_RSP_FILE_TEMPLATE = f"{_THIS_SCRIPT_DIR}/templates/rsp_file.c.jinja"
_DEFAULT_PROFILE_TEMPLATE = f"{_THIS_SCRIPT_DIR}/templates/profile.c.jinja"
_DEFAULT_TESTS_VECTORS_TEMPLATE = f"{_THIS_SCRIPT_DIR}/templates/tests_vectors.c.jinja"

class RspJsonEncoder(JSONEncoder):

    # Hack from https://stackoverflow.com/questions/12670395/json-encoding-very-long-iterators
    class FakeListIterator(list):
        def __init__(self, iterable):
            self.iterable = iter(iterable)
            try:
                self.firstitem = next(self.iterable)
                self.truthy = True
            except StopIteration:
                self.truthy = False

        def __iter__(self):
            if not self.truthy:
                return iter([])
            return itertools.chain([self.firstitem], self.iterable)

        def __bool__(self):
            return self.truthy

    def default(self, obj):
        if isinstance(obj, RspFile):
            return RspJsonEncoder.rspfile_to_json(obj)
        elif isinstance(obj, Profile):
            return RspJsonEncoder.profile_to_json(obj)
        elif isinstance(obj, TestVectors):
            return obj.__dict__()
        elif isinstance(obj, bytearray):
            return obj.hex()
        elif isinstance(obj, Iterable):
            return type(self).FakeListIterator(obj)

        return json.JSONEncoder.default(self, obj)

    @staticmethod
    def rspfile_to_json(rsp_file: RspFile):
        return {"metadata": rsp_file.metadata, "profiles": rsp_file.profiles}

    @staticmethod
    def profile_to_json(profile: Profile):
        return {"attributes": profile.attributes, "vectors": profile.vectors}


def save_as_json(rsp_iterator: Union[RspFile, Profile, List[TestVector]], output_file: str):

    if os.path.exists(output_file):
        raise FileExistsError(f"File '{output_file}' already exists")

    with open(output_file, "w", encoding="utf-8") as out_fd:
        json.dump(rsp_iterator, out_fd, indent=4, cls=RspJsonEncoder)


def _save_rsp_file_as_c(rsp_file: RspFile, output_file: str, jinja_template_path: str):
    tests_vectors_keys = next(rsp_file.profiles[0].vectors).keys()

    with open(jinja_template_path, "r", encoding="utf-8") as template_fd:
        template = Template(template_fd.read())

    profile_attributes_values = {}

    for profile in rsp_file:
        for key, value in profile.attributes.items():
            if key in profile_attributes_values:
                profile_attributes_values[key].add(value)
            else:
                profile_attributes_values[key] = set([value])

    with open(output_file, "w") as output_fd:
        output_fd.write(template.render(
            rsp_file=rsp_file,
            tests_vectors_keys=tests_vectors_keys,
            profile_attributes_values=profile_attributes_values
        ))

def _save_profile_as_c(profile: Profile, output_file: str, jinja_template_path: str):
    tests_vectors_keys = next(profile.vectors).keys()

    with open(jinja_template_path, "r", encoding="utf-8") as template_fd:
        template = Template(template_fd.read())

    profile_attributes_values = {}

    for key, value in profile.attributes.items():
        if key in profile_attributes_values:
            profile_attributes_values[key].add(value)
        else:
            profile_attributes_values[key] = set([value])

    with open(output_file, "w") as output_fd:
        output_fd.write(template.render(
            rsp_file=profile,
            tests_vectors_keys=tests_vectors_keys,
            profile_attributes_values=profile_attributes_values
        ))

def _save_test_vectors_as_c(tests_vectors: TestVectorsIterator, output_file: str, jinja_template_path: str):
    tests_vectors_keys = next(tests_vectors).keys()

    with open(jinja_template_path, "r", encoding="utf-8") as template_fd:
        template = Template(template_fd.read())

    with open(output_file, "w") as output_fd:
        output_fd.write(template.render(
            tests_vectors=tests_vectors,
            tests_vectors_keys=tests_vectors_keys
        ))

def save_as_c(rsp_iterator: Union[RspFile, Profile, TestVectorsIterator], output_file: str, jinja_template_path: Union[str, None] = None):

    if os.path.exists(output_file):
        raise FileExistsError(f"File '{output_file}' already exists")

    if isinstance(rsp_iterator, RspFile):
        _save_rsp_file_as_c(rsp_iterator, output_file, jinja_template_path or _DEFAULT_RSP_FILE_TEMPLATE)

    elif isinstance(rsp_iterator, Profile):
        _save_profile_as_c(rsp_iterator, output_file, jinja_template_path or _DEFAULT_PROFILE_TEMPLATE)

    elif isinstance(rsp_iterator, list) and isinstance(rsp_iterator[0], TestVector):
        _save_test_vectors_as_c(rsp_iterator, output_file, jinja_template_path or _DEFAULT_TESTS_VECTORS_TEMPLATE)

    else:
        raise NotImplemented
