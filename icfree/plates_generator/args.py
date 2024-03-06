from argparse import (
    ArgumentParser,
    # BooleanOptionalAction
)
from os import getcwd as os_getcwd

from brs_utils import add_logger_args

DEFAULT_ARGS = {
    'OUTPUT_FOLDER': os_getcwd(),
    'SRC_PLT_DEAD_VOLUME': 15000,
    'SRC_PLT_WELL_CAPACITY': 60000,
    'SRC_PLT_DIM': '16x24',
    'SRC_PLT_START_WELL': 'A1',
    'DST_PLT_DEAD_VOLUME': 15000,
    'DST_PLT_START_WELL': 'A1',
    'DST_PLT_WELL_CAPACITY': 60000,
    'DST_PLT_DIM': '16x24',
    'NPLICATES': 1,
    'NEW_COL_COMP': [],
    # 'KEEP_NIL_VOL': False,
    # 'OPTIMIZE_WELL_VOLUMES': ['none'],
    'OUTPUT_FORMAT': 'csv'
}


def build_args_parser(signature, description):

    parser = ArgumentParser(
        signature.split(' ')[0],
        description,
    )

    parser = add_arguments(parser, signature)

    return parser


def add_arguments(parser, signature):

    # parser.add_argument(
    #     'parameters',
    #     type=str,
    #     help='Path to a .csv file containing component parameters',
    # )

    parser.add_argument(
        'volumes_file',
        type=str,
        help='Path to a .tsv file containing volumes',
    )
    parser.add_argument(
        '-v', '--sample-volume',
        type=float,
        required=True,
        help=('Final sample volume in each well in nL.')
    )

    src_plates_group = parser.add_argument_group("Source Plates")
    src_plates_group.add_argument(
        '-sdv', '--src-plt-dead-volume',
        type=int,
        default=DEFAULT_ARGS['SRC_PLT_DEAD_VOLUME'],
        help=('deadVolume to add in the source plate in nL'
              f' (default: {DEFAULT_ARGS["SRC_PLT_DEAD_VOLUME"]})')
    )
    src_plates_group.add_argument(
        '-ssw', '--src-start-well',
        type=str,
        default=DEFAULT_ARGS['SRC_PLT_START_WELL'],
        help=('Starter well of source plate to begin '
              'filling the 384 well-plate.'
              f' (default: {DEFAULT_ARGS["SRC_PLT_START_WELL"]})')
    )
    src_plates_group.add_argument(
        '-spd', '--src-plt-dim',
        type=str,
        default=DEFAULT_ARGS['SRC_PLT_DIM'],
        help=(f'Dimensions of source plates separated by a \'x\', '
              'e.g. <nb_rows>x<nb_cols>'
              f' (default: {DEFAULT_ARGS["SRC_PLT_DIM"]}).')
    )
    src_plates_group.add_argument(
        '-spwc', '--src-plt-well-capacity',
        type=int,
        default=DEFAULT_ARGS['SRC_PLT_WELL_CAPACITY'],
        help=('Maximum volume capacity of the source plate in nL'
              f' (default: {DEFAULT_ARGS["SRC_PLT_WELL_CAPACITY"]})')
    )
    src_plates_group.add_argument(
        '-ncc', '--new-col-comp',
        nargs='*',
        type=str,
        default=DEFAULT_ARGS["NEW_COL_COMP"],
        help=('Start wells at a new column for each listed component.'
              ' If empty, start wells at a new column for each component. '
              f' (default: {DEFAULT_ARGS["NEW_COL_COMP"]}).')
    )

    dst_plates_group = parser.add_argument_group("Destination Plates")
    dst_plates_group.add_argument(
        '-dsw', '--dst-start-well',
        type=str,
        default=DEFAULT_ARGS['DST_PLT_START_WELL'],
        help=('Starter well of destination plate to begin '
              'filling the 384 well-plate.'
              f' (default: {DEFAULT_ARGS["DST_PLT_START_WELL"]})')
    )
    dst_plates_group.add_argument(
        '-dpd', '--dst-plt-dim',
        type=str,
        default=DEFAULT_ARGS['DST_PLT_DIM'],
        help=(f'Dimensions of destination plates separated by a \'x\', '
              'e.g. <nb_rows>x<nb_cols>'
              f' (default: {DEFAULT_ARGS["DST_PLT_DIM"]}).')
    )
    dst_plates_group.add_argument(
        '-dpwc', '--dst-plt-well-capacity',
        type=int,
        default=DEFAULT_ARGS['DST_PLT_WELL_CAPACITY'],
        help=('Maximum volume capacity of the dest plate in nL'
              f' (default: {DEFAULT_ARGS["DST_PLT_WELL_CAPACITY"]})')
    )

    # vol_group = parser.add_argument_group("Volumes")
    # vol_group.add_argument(
    #     '-knv', '--keep-nil-vol',
    #     type=bool,
    #     # action=BooleanOptionalAction,
    #     default=DEFAULT_ARGS['KEEP_NIL_VOL'],
    #     help='Keep nil volumes in instructions or not (default: yes)'
    # )

    # vol_group.add_argument(
    #     '-owv', '--opt-well-vol',
    #     nargs='*',
    #     type=str,
    #     default=DEFAULT_ARGS["OPTIMIZE_WELL_VOLUMES"],
    #     help=('Save volumes in source plate for all factors. '
    #           'It may trigger more volume pipetting warnings. '
    #           'If list of factors is given (separated by blanks), '
    #           'save only for these ones '
    #           f' (default: {DEFAULT_ARGS["OPTIMIZE_WELL_VOLUMES"]}).')
    # )
    parser.add_argument(
        '--nplicates',
        type=int,
        default=DEFAULT_ARGS['NPLICATES'],
        help=('Numbers of copies of volume sets in the destination plate'
              f' (default: {DEFAULT_ARGS["NPLICATES"]})')
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
        choices=['csv', 'tsv'],
        default=DEFAULT_ARGS['OUTPUT_FORMAT'],
        help=('Output file format'
              f' (default: {DEFAULT_ARGS["OUTPUT_FORMAT"]})')
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
