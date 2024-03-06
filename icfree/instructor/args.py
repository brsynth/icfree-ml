from numpy import (
    iinfo as np_iinfo,
    int32 as np_int32,
)
from argparse import ArgumentParser
from os import getcwd as os_getcwd

from brs_utils import add_logger_args
from icfree._version import __version__

DEFAULT_ARGS = {
    'OUTPUT_FOLDER': os_getcwd(),
    # 'ROBOT': 'echo',
    'SRC_PLATE_TYPE': 'ALL:384PP_AQ_GP3',
    # 'SPLIT_COMPONENTS': [''],
    'SPLIT_UPPER_VOL': np_iinfo(np_int32).max,
    'SPLIT_LOWER_VOL': 0,
    'SPLIT_OUTFILE_COMPONENTS': [''],
}


def build_args_parser(signature, description):

    parser = ArgumentParser(
        signature.split(' ')[0],
        description,
    )

    parser = add_arguments(parser, signature)

    return parser


def add_arguments(parser, signature):

    # Required arguments
    parser.add_argument(
        "--source-plates", nargs='+', required=True,
        help="Paths to the source plate CSV files."
    )
    parser.add_argument(
        "--destination-plates", nargs='+', required=True,
        help="Paths to the destination plate CSV files."
    )
    parser.add_argument(
        "-of", "--output-file", required=True,
        help="Base path for the generated instructions CSV file."
    )

    # Optional arguments
    parser.add_argument(
        "-suv", "--split-upper-vol", type=int,
        default=DEFAULT_ARGS['SPLIT_UPPER_VOL'],
        help="Upper volume threshold for splitting instructions."
        " Default is max int value."
    )
    parser.add_argument(
        "-slv", "--split-lower-vol", type=int,
        default=DEFAULT_ARGS['SPLIT_LOWER_VOL'],
        help="Lower volume threshold for integrating "
        "remaining volume into penultimate instruction. Default is 0."
    )
    parser.add_argument(
        "-soc", "--split-outfile-components", type=str,
        help="Specification for splitting output files by components."
        " Separate groups with spaces and components "
        "within groups with commas."
    )
    parser.add_argument(
        "-spt", "--src-plate-type", type=str,
        default=DEFAULT_ARGS['SRC_PLATE_TYPE'],
        help="Specification for source plate types "
        "(choices: '384PP_AQ_GP3', '384_AQ_CP')."
        " Format as component:plate_type or ALL:plate_type."
        " Separate multiple specifications with semicolons."
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
