from argparse import ArgumentParser

from brs_utils import add_logger_args
from icfree._version import __version__


DEFAULT_ARGS = {
    'SAMPLE_VOLUME': 1000,
    'ROBOT': 'echo',
}


def build_args_parser(signature, description):

    parser = ArgumentParser(
        signature.split(' ')[0],
        description,
    )

    parser = add_arguments(parser, signature)

    return parser


def add_arguments(parser, signature):

    parser.add_argument(
        'parameters',
        type=str,
        help='Path to the file (.tsv) containing component parameters',
    )

    parser.add_argument(
        'concentrations',
        type=str,
        help='Path to file (.tsv) containing concentrations to convert'
    )

    parser.add_argument(
        '-v', '--sample_volume',
        type=int,
        default=DEFAULT_ARGS['SAMPLE_VOLUME'],
        help=('Final sample volume in each well in nL'
              f' (default: {DEFAULT_ARGS["SAMPLE_VOLUME"]})')
    )

    parser.add_argument(
        '-o', '--outfile',
        type=str,
        required=True,
        help=('Output file to write the converted volumes')
    )

    parser.add_argument(
        '-r', '--robot',
        type=str,
        default=DEFAULT_ARGS['ROBOT'],
        help='Name of the robot to use (activate 2.5 multiple for volumes)'
        f' (default: {DEFAULT_ARGS["ROBOT"]})',
    )

    # Add logger arguments
    parser = add_logger_args(parser)

    parser.add_argument(
        '--version',
        action='version',
        version=signature,
        help='show the version number and exit'
    )

    return parser
