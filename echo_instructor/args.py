from argparse import (
    ArgumentParser
    )


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
        help='Path to a .tsv file containing CFPS parameters and features',
    )

    parser.add_argument(
        'input1',
        type=str,
        help='Path to a .tsv file containing initial training set',
    )

    parser.add_argument(
        'input2',
        type=str,
        help='Path to a .tsv file containing normalizer set',
    )

    parser.add_argument(
        'input3',
        type=str,
        help='Path to a .tsv file containing autofluorescence set',
    )

    # parser.add_argument(
    #     'sample_volume',
    #     type=int,
    #     help='Final sample volume in each well',
    # )

    # parser.add_argument(
    #     'output',
    #     type=str,
    #     help='Path to the csv output',
    # )

    return parser
