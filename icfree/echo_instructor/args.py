from argparse import (
    ArgumentParser
    )
from os import getcwd as os_getcwd

DEFAULT_OUTPUT_FOLDER = os_getcwd()
DEFAULT_SAMPLE_VOLUME = 10000

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
        'init_tset',
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
        help=f'Final sample volume in each well in nL (default: {DEFAULT_SAMPLE_VOLUME})',
    )

    parser.add_argument(
        '-of', '--output-folder',
        type=str,
        default=DEFAULT_OUTPUT_FOLDER,
        help=f'Output folder to write output files (default: {DEFAULT_OUTPUT_FOLDER})',
    )

    return parser
