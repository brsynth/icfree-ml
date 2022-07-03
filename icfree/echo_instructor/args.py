from argparse import (
    ArgumentParser,
    BooleanOptionalAction
)
from os import getcwd as os_getcwd

from brs_utils import add_logger_args
from icfree._version import __version__

DEFAULT_ARGS = {
    'DEFAULT_OUTPUT_FOLDER': os_getcwd(),
    'DEFAULT_SAMPLE_VOLUME': 10000,
    'DEFAULT_SOURCE_PLATE_DEAD_VOLUME': 15000,
    'DEFAULT_DEST_STARTING_WELL': 'A1',
    'DEFAULT_SRC_STARTING_WELL': 'A1',
    'DEFAULT_NPLICATE': 3,
    'DEFAULT_KEEP_NIL_VOL': False,
    'DEFAULT_SOURCE_PLATE_WELL_CAPACITY': 60000,
    'DEFAULT_PLATE_NB_WELLS': 384,
    'DEFAULT_OPTIMIZE_VOLUMES': []
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
        default=DEFAULT_ARGS['DEFAULT_SAMPLE_VOLUME'],
        help=('Final sample volume in each well in nL'
              f' (default: {DEFAULT_ARGS["DEFAULT_SAMPLE_VOLUME"]})')
    )

    parser.add_argument(
        '-sdv', '--source_plate_dead_volume',
        type=int,
        default=DEFAULT_ARGS['DEFAULT_SOURCE_PLATE_DEAD_VOLUME'],
        help=('Dead volume to add in the source plate in nL'
              f' (default: {DEFAULT_ARGS["DEFAULT_SOURCE_PLATE_DEAD_VOLUME"]})')
    )

    parser.add_argument(
        '-dsw', '--dest-starting_well',
        type=str,
        default=DEFAULT_ARGS['DEFAULT_DEST_STARTING_WELL'],
        help=('Starter well of destination plate to begin filling the 384 well-plate.'
              f' (default: {DEFAULT_ARGS["DEFAULT_DEST_STARTING_WELL"]})')
    )

    parser.add_argument(
        '-ssw', '--src-starting_well',
        type=str,
        default=DEFAULT_ARGS['DEFAULT_SRC_STARTING_WELL'],
        help=('Starter well of source plate to begin filling the 384 well-plate.'
              f' (default: {DEFAULT_ARGS["DEFAULT_SRC_STARTING_WELL"]})')
    )

    parser.add_argument(
        '-of', '--output-folder',
        type=str,
        default=DEFAULT_ARGS['DEFAULT_OUTPUT_FOLDER'],
        help=('Output folder to write output files'
              f' (default: {DEFAULT_ARGS["DEFAULT_OUTPUT_FOLDER"]})')
    )

    parser.add_argument(
        '--nplicate',
        type=int,
        default=DEFAULT_ARGS['DEFAULT_NPLICATE'],
        help=('Numbers of copies of volume sets'
              f' (default: {DEFAULT_ARGS["DEFAULT_NPLICATE"]})')
    )

    parser.add_argument(
        '--keep-nil-vol',
        action=BooleanOptionalAction,
        default=DEFAULT_ARGS['DEFAULT_KEEP_NIL_VOL'],
        help='Keep nil volumes in instructions or not (default: yes)'
    )

    parser.add_argument(
        '-spwc', '--source_plate_well_capacity',
        type=int,
        default=DEFAULT_ARGS['DEFAULT_SOURCE_PLATE_WELL_CAPACITY'],
        help=('Maximum volume capacity of the source plate in nL'
              f' (default: {DEFAULT_ARGS["DEFAULT_SOURCE_PLATE_WELL_CAPACITY"]})')
    )

    parser.add_argument(
        '--optimize-well-volumes',
        nargs='*',
        default=DEFAULT_ARGS["DEFAULT_OPTIMIZE_VOLUMES"],
        help=('Save volumes in source plate for all factors.'
              'It may trigger more volume pipetting warnings.'
              'If list of factors is given (separated by blanks), '
              f'save only for these ones (default: {DEFAULT_ARGS["DEFAULT_OPTIMIZE_VOLUMES"]}).')
    )

    parser.add_argument(
        '--nb-wells-plate',
        type=int,
        default=DEFAULT_ARGS['DEFAULT_PLATE_NB_WELLS'],
        help=(f'Number of wells on the plate '
              f'(default: {DEFAULT_ARGS["DEFAULT_PLATE_NB_WELLS"]}).')
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
