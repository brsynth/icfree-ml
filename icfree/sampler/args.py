from argparse import ArgumentParser

from brs_utils import add_logger_args


DEFAULTS = {
    'OUTPUT_FILE': "",
    'RATIOS': None,
    'NB_STEPS': None,
    'NB_BINS': None,
    'NB_SAMPLES': 100,
    'OUTPUT_FORMAT': 'tsv',
    'method': 'auto',
}


def build_args_parser(
    signature: str,
    description: str
):

    parser = ArgumentParser(
        signature.split(' ')[0],
        description,
    )

    parser = add_arguments(parser, signature)

    return parser


def add_arguments(parser, signature):

    parser.add_argument(
        "input_file",
        type=str,
        help="Path to the input CSV file."
    )
    parser.add_argument(
        "--output-file", "-o",
        type=str,
        default=DEFAULTS['OUTPUT_FILE'],
        help="Path where the output CSV file will be saved."
    )
    parser.add_argument(
        "--nb-samples", "-n",
        type=int,
        default=DEFAULTS['NB_SAMPLES'],
        help="Number of samples to generate "
        f"(default: {DEFAULTS['NB_SAMPLES']})."
    )
    parser.add_argument(
        "--method", "-m",
        type=str,
        choices=['lhs', 'random', 'all', 'auto'],
        default=DEFAULTS['method'],
        help=f"Sampling method (default: '{DEFAULTS['method']}')."
    )
    # Step size for creating discrete ranges
    parser.add_argument(
        "--step", "-p",
        type=int,
        default=DEFAULTS['NB_STEPS'],
        help="Step size for creating discrete ranges for all component."
        f" (default: {DEFAULTS['NB_STEPS']})."
    )
    # Ratios for creating discrete ranges
    parser.add_argument(
        "--ratios", "-r",
        nargs='+',
        type=float,
        help="Ratios for creating discrete ranges."
        " Must be a list of floats between 0.0 and 1.0 (separated by blanks)."
        f" (default: {DEFAULTS['RATIOS']})."
    )
    # Number of bins for creating discrete ranges
    parser.add_argument(
        "--nb-bins", "-b",
        type=int,
        help="Number of bins for creating discrete ranges."
        f" (default: {DEFAULTS['NB_BINS']})."
    )
    parser.add_argument(
        "--seed", "-S",
        type=int,
        default=None,
        help="Seed value for random number generation (default: None)."
    )

    # parser.add_argument(
    #     'cfps',
    #     type=str,
    #     help='Path to a .tsv file containing cfps parameters and features',
    # )

    # parser.add_argument(
    #     '-of', '--output-folder',
    #     type=str,
    #     default=DEFAULTS['OUTPUT_FOLDER'],
    #     help=('Output folder to write output files'
    #           f' (default: {DEFAULTS["OUTPUT_FOLDER"]})')
    # )

    # parser.add_argument(
    #     '-ofmt', '--output-format',
    #     type=str,
    #     choices=['csv', 'tsv'],
    #     default=DEFAULTS['OUTPUT_FORMAT'],
    #     help=('Output file format'
    #           f' (default: {DEFAULTS["OUTPUT_FORMAT"]})')
    # )

    # parser.add_argument(
    #     '--nb-sampling-steps',
    #     type=int,
    #     default=DEFAULTS['NB_SAMPLING_STEPS'],
    #     help=('Number of uniform sampling steps for all factors'
    #           f' (default: {DEFAULTS["NB_SAMPLING_STEPS"]})')
    # )

    # parser.add_argument(
    #     '--sampling-ratios',
    #     nargs='+',
    #     type=float,
    #     help=('Sampling ratios (between 0.0 and 1.0)'
    #           ' for all factors.')
    # )

    # parser.add_argument(
    #     '--nb-samples',
    #     type=int,
    #     # type=arg_range(1, 100),
    #     default=DEFAULTS['NB_SAMPLES'],
    #     help=('Number of samples to generate for all factors'
    #           f' (default: {DEFAULTS["NB_SAMPLES"]})')
    # )

    # parser.add_argument(
    #     '--seed',
    #     type=int,
    #     help='Seed to reproduce results'
    # )

    # Add arguments related to the logger
    parser = add_logger_args(parser)

    parser.add_argument(
        '--version',
        action='version',
        version=signature,
        help='show the version number and exit'
    )

    return parser
