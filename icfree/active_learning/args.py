from argparse import (
    ArgumentParser
    )

from brs_utils import add_logger_args
from icfree._version import __version__


def build_args_parser(
        program,
        description):

    parser = ArgumentParser(
        program,
        description,
    )

    parser = add_arguments(parser)

    return parser


def add_arguments(parser):

    parser.add_argument(
        'data_folder',
        type=str,
        help='Path to a folder with experimental data',
    )

    parser.add_argument(
        'files_number',
        type=int,
        help='Number of files in the data folder',
    )

    # Add logger arguments
    parser = add_logger_args(parser)

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {}'.format(__version__),
        help='show the version number and exit'
    )

    return parser
