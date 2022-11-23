from argparse import (
    ArgumentParser,
    # BooleanOptionalAction
)
from os import getcwd as os_getcwd

from brs_utils import add_logger_args
from icfree._version import __version__

DEFAULT_ARGS = {
    'OUTPUT_FOLDER': os_getcwd(),
    'SAMPLE_VOLUME': 1000,
}


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
        help='Path to a .tsv file containing CFPS parameters and features',
    )

    parser.add_argument(
        'concentrations',
        type=str,
        help='Path to file containing concentrations to convert'
    )

    parser.add_argument(
        '-v', '--sample_volume',
        type=int,
        default=DEFAULT_ARGS['SAMPLE_VOLUME'],
        help=('Final sample volume in each well in nL'
              f' (default: {DEFAULT_ARGS["SAMPLE_VOLUME"]})')
    )

    parser.add_argument(
        '-of', '--output-folder',
        type=str,
        default=DEFAULT_ARGS['OUTPUT_FOLDER'],
        help=('Output folder to write output files'
              f' (default: {DEFAULT_ARGS["OUTPUT_FOLDER"]})')
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
