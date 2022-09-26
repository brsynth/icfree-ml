from argparse import (
    ArgumentParser
    )

from random import (
    randint
)

from os import getcwd as os_getcwd
from brs_utils import add_logger_args
from icfree._version import __version__

DEFAULT_OUTPUT_FOLDER = os_getcwd()
DEFAULT_DOE_NB_CONCENTRATIONS = 5
DEFAULT_DOE_NB_SAMPLES = 99


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
        help=('Output folder to write output files'
              f' (default: {DEFAULT_OUTPUT_FOLDER})')
    )

    parser.add_argument(
        '--doe-nb-concentrations',
        type=int,
        default=DEFAULT_DOE_NB_CONCENTRATIONS,
        help=('Number of concentration values for all factors when performing'
              f' the DoE (default: {DEFAULT_DOE_NB_CONCENTRATIONS})')
    )

    parser.add_argument(
        '--doe-concentration-ratios',
        nargs='+',
        type=float,
        help=('Concentration rations (between 0.0 and 1.0)'
              ' for all factors when performing the DoE')
    )

    parser.add_argument(
        '--doe-nb-samples',
        type=int,
        default=DEFAULT_DOE_NB_SAMPLES,
        help=('Number of samples to generate for all factors'
              f' when performing the DoE (default: {DEFAULT_DOE_NB_SAMPLES})')
    )

    parser.add_argument(
        '--seed',
        type=int,
        help=f'Seed to reproduce results',
    )

    parser.add_argument(
        '--all-status',
        type=str,
        choices=['doe', 'const'],
        help='Change status of all parameters (but DNA)',
    )

    # Add arguments related to the logger
    parser = add_logger_args(parser)

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {}'.format(__version__),
        help='show the version number and exit'
    )

    return parser
