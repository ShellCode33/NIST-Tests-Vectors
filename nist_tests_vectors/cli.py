#!/usr/bin/env python3
# coding: utf-8

import sys
import argparse
from nist_tests_vectors import RspFile
from nist_tests_vectors.exporter import save_as_json, save_as_c, \
                                        SUPPORTED_EXPORT_FORMATS, \
                                        SUPPORTED_TEMPLATE_FORMATS

class Color:
    GREEN = "\u001b[32m"
    YELLOW = "\u001b[33m"
    RED = "\u001b[31m"
    RESET = "\u001b[0m"


class Logger:

    @staticmethod
    def info(msg: str):
        print(f"{Color.GREEN}[INFO] {Color.RESET}{msg}")

    @staticmethod
    def warning(msg: str):
        print(f"{Color.YELLOW}[WARNING] {Color.RESET}{msg}")

    @staticmethod
    def error(msg: str):
        print(f"{Color.RED}[ERROR] {Color.RESET}{msg}")


def cli_convert(args: argparse.Namespace):

    out_format = args.format

    if out_format is None:
        out_format = args.output.split(".")[-1]

    if out_format not in SUPPORTED_EXPORT_FORMATS:
        Logger.error(f"Support for '{out_format}' format is not implemented")
        sys.exit(1)

    if args.template and out_format not in SUPPORTED_TEMPLATE_FORMATS:
        Logger.error(f"Template parameter is not supported by '{out_format}' format")
        sys.exit(1)

    with RspFile(args.rsp_file) as rsp_file:

        try:
            if out_format == "json":
                save_as_json(rsp_file, args.output)

            elif out_format == "c":
                save_as_c(rsp_file, args.output, args.template)

            else:
                raise NotImplemented
        except FileExistsError as fee:
            Logger.error(str(fee))
            sys.exit(1)

    Logger.info(f"File '{args.output}' has been generated successfully")


def main() -> None:
    parser = argparse.ArgumentParser(description='Welcome to the NIST Tests Vectors '
                                                 'Management Tool !')
    subparsers = parser.add_subparsers(help='The action to perform')

    convert_parser = subparsers.add_parser('convert', help='convert RSP file to specified format')
    convert_parser.add_argument("rsp_file", help="path to the RSP file to convert")
    convert_parser.add_argument("--output", "-o", required=True,
                                help="path to the converted file")
    convert_parser.add_argument("--format", "-f", choices=["json", "c"],
                                help="output format")
    convert_parser.add_argument("--template", "-t",
                                help="template to use for convertion")


    convert_parser.set_defaults(func=cli_convert)

    args = parser.parse_args()

    try:
        args.func(args)
    except AttributeError:
        parser.print_help()

if __name__ == "__main__":
    main()

