from argparse import (
    ArgumentParser
    )

from random import (
    randint
)
from os import getcwd as os_getcwd

DEFAULT_SEED = randint(0, 1)
DEFAULT_OUTPUT_FOLDER = os_getcwd()

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
        'cfps',
        type=str,
        help='Path to a .tsv file containing cfps parameters and features',
    )

    parser.add_argument(
        '-of', '--output-folder',
        type=str,
        default=DEFAULT_OUTPUT_FOLDER,
        help='Output folder to write output files',
    )

    parser.add_argument(
        '-s', '--seed',
        type=int,
        default=DEFAULT_SEED,
        help='Seed to reproduce results',
    )

    return parser
