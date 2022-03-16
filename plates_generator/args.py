from argparse import (
    ArgumentParser
    )

from random import (
    randint
)

DEFAULT_SEED = randint(0, 1)


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
        'input',
        type=str,
        help='Path to a .tsv file containing cfps parameters and features',
    )

    parser.add_argument(
        '--seed',
        type=int,
        default=DEFAULT_SEED,
        help='Seed to reproduce results',
    )

    # parser.add_argument(
    #     'output',
    #     type=str,
    #     help='Path to the csv output',
    # )

    return parser
