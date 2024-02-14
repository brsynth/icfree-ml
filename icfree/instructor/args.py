from argparse import (
    ArgumentParser,
    # BooleanOptionalAction
)
from os import getcwd as os_getcwd

from brs_utils import add_logger_args
from icfree._version import __version__

DEFAULT_ARGS = {
    'OUTPUT_FOLDER': os_getcwd(),
    'ROBOT': 'echo',
    'SRC_PLATE_TYPE': '384PP_AQ_GP3',
    'SPLIT_COMPONENTS': [''],
    'SPLIT_UPPER_VOL': [0],
    'SPLIT_LOWER_VOL': [0]
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
        '--source_plates',
        nargs='+',  # 1 or more
        type=str,
        help='Path to .json files containing source plates information'
    )

    parser.add_argument(
        '--source_wells',
        nargs='+',  # 1 or more
        type=str,
        help='Path to .csv/tsv files containing source wells content. '
        'If set, overwrite "Wells" entry in .json file.'
    )

    parser.add_argument(
        '--dest_plates',
        nargs='+',  # 1 or more
        type=str,
        help='Path to .json files containing destination plates information',
    )

    parser.add_argument(
        '--dest_wells',
        nargs='+',  # 1 or more
        type=str,
        help='Path to .csv/tsv files containing dest wells content. '
        'If set, overwrite "Wells" entry in .json file.'
    )

    parser.add_argument(
        '--robot',
        type=str,
        default=DEFAULT_ARGS['ROBOT'],
        help='Name of the robot to use'
        f' (default: {DEFAULT_ARGS["ROBOT"]})',
    )

    parser.add_argument(
        '-of', '--output-folder',
        type=str,
        default=DEFAULT_ARGS['OUTPUT_FOLDER'],
        help=('Output folder to write output files'
              f' (default: {DEFAULT_ARGS["OUTPUT_FOLDER"]})')
    )

    parser.add_argument(
        '-spt', '--src-plate-type',
        type=str,
        nargs='+',
        default=DEFAULT_ARGS['SRC_PLATE_TYPE'],
        help=(
            'Source plate type (for ECHO robot). If number of args is odd, '
            'the first arg is the plate type by default. '
            'Then, each pair of args is a sample ID and a plate type.'
            f' (default: {DEFAULT_ARGS["SRC_PLATE_TYPE"]})'
        )
    )

    parser.add_argument(
        '-sc', '--split-components',
        nargs='+',
        type=str,
        default=DEFAULT_ARGS['SPLIT_COMPONENTS'],
        help=(
            'List of components (separated by blanks) to apply'
            ' pick limits given by \'--split-upper-vol\''
            ' and \'--split-lower-vol\' options.'
            f' (default: {DEFAULT_ARGS["SPLIT_COMPONENTS"]})'
        )
    )
    parser.add_argument(
        '-suv', '--split-upper-vol',
        nargs='+',
        type=int,
        default=DEFAULT_ARGS['SPLIT_UPPER_VOL'],
        help=(
            'List of maximum volumes (nL) (separated by blanks)'
            ' of components to pick in the source plate wells, applied'
            ' to the components given by \'--split-upper-vol\''
            ' option. Applied to all if one single value is specified.'
            f' (default: {DEFAULT_ARGS["SPLIT_UPPER_VOL"]})'
        )
    )
    parser.add_argument(
        '-slv', '--split-lower-vol',
        nargs='+',
        type=int,
        default=DEFAULT_ARGS['SPLIT_LOWER_VOL'],
        help=(
            'List of minimum volumes (nL) (separated by blanks) of components'
            ' to pick in the source plate wells, applied to the components'
            ' given by \'--split-upper-vol\' option.'
            ' Applied to all if one single value is specified.'
            f' (default: {DEFAULT_ARGS["SPLIT_LOWER_VOL"]})'
        )
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
