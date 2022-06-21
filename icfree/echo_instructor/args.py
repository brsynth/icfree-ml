from argparse import (
    ArgumentParser
    )
from os import getcwd as os_getcwd

from brs_utils import add_logger_args
from icfree._version import __version__

DEFAULT_OUTPUT_FOLDER = os_getcwd()
DEFAULT_SAMPLE_VOLUME = 10000
DEFAULT_STARTING_WELL = 'A1'


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
        'init_set',
        type=str,
        help='Path to a .tsv file containing initial training set',
    )

    parser.add_argument(
        'norm_set',
        type=str,
        help='Path to a .tsv file containing normalizer set',
    )

    parser.add_argument(
        'autofluo_set',
        type=str,
        help='Path to a .tsv file containing autofluorescence set',
    )

    parser.add_argument(
        '-v', '--sample_volume',
        type=int,
        default=DEFAULT_SAMPLE_VOLUME,
        help=('Final sample volume in each well in nL'
              f' (default: {DEFAULT_SAMPLE_VOLUME})')
    )

    parser.add_argument(
        '-sw', '--starting_well',
        type=str,
        default=DEFAULT_STARTING_WELL,
        help=('Starter well to begin filling the 384 well-plate.'
              f' (default: {DEFAULT_STARTING_WELL})')
    )

    parser.add_argument(
        '-of', '--output-folder',
        type=str,
        default=DEFAULT_OUTPUT_FOLDER,
        help=('Output folder to write output files'
              f' (default: {DEFAULT_OUTPUT_FOLDER})')
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
