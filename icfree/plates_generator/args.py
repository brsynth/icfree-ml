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
    'SOURCE_PLATE_DEAD_VOLUME': 15000,
    'DEST_PLATE_DEAD_VOLUME': 15000,
    'DEST_STARTING_WELL': 'A1',
    'SRC_STARTING_WELL': 'A1',
    'NPLICATE': 3,
    'KEEP_NIL_VOL': False,
    'SOURCE_PLATE_WELL_CAPACITY': 60000,
    'DEST_PLATE_WELL_CAPACITY': 60000,
    'PLATE_DIMENSIONS': '16x24',
    'OPTIMIZE_WELL_VOLUMES': [],
    'OUTPUT_FORMAT': 'csv'
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
        'volumes',
        type=str,
        help='Path to a .tsv file containing volumes',
    )

    parser.add_argument(
        '-v', '--sample_volume',
        type=int,
        default=DEFAULT_ARGS['SAMPLE_VOLUME'],
        help=('Final sample volume in each well in nL'
              f' (default: {DEFAULT_ARGS["SAMPLE_VOLUME"]})')
    )

    parser.add_argument(
        '-sdv', '--source_plate_dead_volume',
        type=int,
        default=DEFAULT_ARGS['SOURCE_PLATE_DEAD_VOLUME'],
        help=('deadVolume to add in the source plate in nL'
              f' (default: {DEFAULT_ARGS["SOURCE_PLATE_DEAD_VOLUME"]})')
    )

    parser.add_argument(
        '-ddv', '--dest_plate_dead_volume',
        type=int,
        default=DEFAULT_ARGS['DEST_PLATE_DEAD_VOLUME'],
        help=('deadVolume to add in the dest plate in nL'
              f' (default: {DEFAULT_ARGS["DEST_PLATE_DEAD_VOLUME"]})')
    )

    parser.add_argument(
        '-dsw', '--dest-starting_well',
        type=str,
        default=DEFAULT_ARGS['DEST_STARTING_WELL'],
        help=('Starter well of destination plate to begin '
              'filling the 384 well-plate.'
              f' (default: {DEFAULT_ARGS["DEST_STARTING_WELL"]})')
    )

    parser.add_argument(
        '-ssw', '--src-starting_well',
        type=str,
        default=DEFAULT_ARGS['SRC_STARTING_WELL'],
        help=('Starter well of source plate to begin '
              'filling the 384 well-plate.'
              f' (default: {DEFAULT_ARGS["SRC_STARTING_WELL"]})')
    )

    parser.add_argument(
        '-of', '--output-folder',
        type=str,
        default=DEFAULT_ARGS['OUTPUT_FOLDER'],
        help=('Output folder to write output files'
              f' (default: {DEFAULT_ARGS["OUTPUT_FOLDER"]})')
    )

    parser.add_argument(
        '-ofmt', '--output-format',
        type=str,
        choices=['csv', 'tsv', 'json'],
        default=DEFAULT_ARGS['OUTPUT_FORMAT'],
        help=('Output file format'
              f' (default: {DEFAULT_ARGS["OUTPUT_FORMAT"]})')
    )

    parser.add_argument(
        '--nplicate',
        type=int,
        default=DEFAULT_ARGS['NPLICATE'],
        help=('Numbers of copies of volume sets'
              f' (default: {DEFAULT_ARGS["NPLICATE"]})')
    )

    parser.add_argument(
        '--keep-nil-vol',
        type=bool,
        # action=BooleanOptionalAction,
        default=DEFAULT_ARGS['KEEP_NIL_VOL'],
        help='Keep nil volumes in instructions or not (default: yes)'
    )

    parser.add_argument(
        '-spwc', '--source_plate_well_capacity',
        type=int,
        default=DEFAULT_ARGS['SOURCE_PLATE_WELL_CAPACITY'],
        help=('Maximum volume capacity of the source plate in nL'
              f' (default: {DEFAULT_ARGS["SOURCE_PLATE_WELL_CAPACITY"]})')
    )

    parser.add_argument(
        '-dpwc', '--dest_plate_well_capacity',
        type=int,
        default=DEFAULT_ARGS['DEST_PLATE_WELL_CAPACITY'],
        help=('Maximum volume capacity of the dest plate in nL'
              f' (default: {DEFAULT_ARGS["DEST_PLATE_WELL_CAPACITY"]})')
    )

    parser.add_argument(
        '--optimize-well-volumes',
        nargs='*',
        default=DEFAULT_ARGS["OPTIMIZE_WELL_VOLUMES"],
        help=('Save volumes in source plate for all factors. '
              'It may trigger more volume pipetting warnings. '
              'If list of factors is given (separated by blanks), '
              'save only for these ones '
              f'(default: {DEFAULT_ARGS["OPTIMIZE_WELL_VOLUMES"]}).')
    )

    parser.add_argument(
        '--plate-dimensions',
        type=str,
        default=DEFAULT_ARGS['PLATE_DIMENSIONS'],
        help=(f'Dimensions of plate separated by a \'x\', '
              'e.g. <nb_rows>x<nb_cols>'
              f'(default: {DEFAULT_ARGS["PLATE_DIMENSIONS"]}).')
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
