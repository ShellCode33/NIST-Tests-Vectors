# coding: utf-8

import os
import json
from unittest import TestCase
from tempfile import TemporaryDirectory

from nist_tests_vectors import RspFile
from nist_tests_vectors.exporter import save_as_json, save_as_c

THIS_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

class TestRspExporter(TestCase):

    def test_json_export(self):
        with RspFile(f"{THIS_SCRIPT_DIR}/data/test_export.rsp") as rsp_file:
            with TemporaryDirectory() as tmp_dir:
                generated_json_path = f"{tmp_dir}/test_export.json"
                expected_json_path = f"{THIS_SCRIPT_DIR}/data/expected_exports/rsp_file.json"

                save_as_json(rsp_file, generated_json_path)

                with open(generated_json_path, "r") as generated_fd:
                    generated_json = json.load(generated_fd)

                with open(expected_json_path, "r") as expected_fd:
                    expected_json = json.load(expected_fd)

                self.assertEqual(generated_json, expected_json)


    def test_c_export(self):
        with RspFile(f"{THIS_SCRIPT_DIR}/data/test_export.rsp") as rsp_file:
            with TemporaryDirectory() as tmp_dir:
                generated_c_path = f"{tmp_dir}/test_export.c"
                expected_c_path = f"{THIS_SCRIPT_DIR}/data/expected_exports/rsp_file.c"

                save_as_c(rsp_file, generated_c_path)

                with open(generated_c_path, "r") as generated_fd:
                    generated_lines = [line.strip() for line in generated_fd.readlines()]

                with open(expected_c_path, "r") as expected_fd:
                    expected_lines = [line.strip() for line in expected_fd.readlines()]

                # Not comparing content directly because some lines could be shuffled
                # because of unordered dicts.
                # Just making sure each line is in the other file.
                for line in generated_lines:
                    self.assertIn(line, expected_lines)

    def test_file_already_exists(self):
        with RspFile(f"{THIS_SCRIPT_DIR}/data/XTSGenAES128.rsp") as rsp_file:
            with TemporaryDirectory() as tmp_dir:
                generated_json_path = f"{tmp_dir}/XTSGenAES128.json"
                generated_c_path = f"{tmp_dir}/XTSGenAES128.c"
                save_as_json(rsp_file, generated_json_path)
                save_as_c(rsp_file, generated_c_path)

                with self.assertRaisesRegex(FileExistsError, "already exists"):
                    save_as_json(rsp_file, generated_json_path)

                with self.assertRaisesRegex(FileExistsError, "already exists"):
                    save_as_c(rsp_file, generated_c_path)
