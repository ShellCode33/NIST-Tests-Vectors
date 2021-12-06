#!/usr/bin/env python3
# coding: utf-8

import argparse
from nist_tests_vectors.downloader import download


def cli_download(args: argparse.Namespace):
    download("block cipher", "/tmp")


def cli_list(args: argparse.Namespace):
    pass


def main() -> None:
    parser = argparse.ArgumentParser(description='Welcome to the NIST Test Vectors '
                                                 'Management Tool !')
    subparsers = parser.add_subparsers(help='The mode to run')

    download_parser = subparsers.add_parser('download',
                                            help='download given test vectors')

    list_parser = subparsers.add_parser('list',
                                        help='list available test vectors')

    download_parser.set_defaults(func=cli_download)
    list_parser.set_defaults(func=cli_list)

    parser.parse_args()

if __name__ == "__main__":
    main()

