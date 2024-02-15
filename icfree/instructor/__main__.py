"""
Instructor module

This module is used to create instructions for the robot from
source and destination plates given from plates_generator module
"""
import sys
from pandas import concat as pd_concat
from typing import List
from logging import (
    Logger,
    getLogger
)

from brs_utils import (
    create_logger
)

from .instructor import (
    check_volumes,
    instructions_generator,
)
from .args import (
    build_args_parser,
    DEFAULT_ARGS
)
from icfree.utils import save_df
from icfree.plates_generator.plate import Plate


def input_importer(
    source_plates_path: List[str],
    source_wells_path: List[str],
    dest_plates_path: List[str],
    dest_wells_path: List[str],
    logger: Logger = getLogger(__name__)
):
    """
    Create concentrations dataframes from tsv files

    Parameters
    ----------
    source_plates_path : List[str]
        Path to source plates
    source_wells_path : List[str]
        Path to source wells
    dest_plates_path : List[str]
        Path to destination plates
    dest_wells_path : List[str]
        Path to destination wells
    logger: Logger
        Logger

    Returns
    -------
    source_plates : Dict[Plate]
        Source plates
    dest_plates : Dict[Plate]
        Destination plates
    """
    logger.debug(f'source_plates_path: {source_plates_path}')
    logger.debug(f'dest_plates_path: {dest_plates_path}')

    source_plates = dict()
    if not source_wells_path:
        source_wells_path = [None] * len(source_plates_path)
    for i in range(len(source_plates_path)):
        source_plates[source_plates_path[i]] = \
            Plate.from_file(
                source_plates_path[i],
                source_wells_path[i],
                logger=logger
            )
    logger.debug('SOURCE PLATES')
    for plt in source_plates:
        logger.debug(plt)

    dest_plates = dict()
    if not dest_wells_path:
        dest_wells_path = [None] * len(dest_plates_path)
    for i in range(len(dest_plates_path)):
        dest_plates[dest_plates_path[i]] = \
            Plate.from_file(
                dest_plates_path[i],
                dest_wells_path[i],
                logger=logger
            )
    logger.debug('DESTINATION PLATES')
    for plt in dest_plates:
        logger.debug(plt)

    return source_plates, dest_plates


def main():
    '''main function'''
    parser = build_args_parser(
        program='instructor',
        description='Generates instructions for robots'
    )

    args = parser.parse_args()

    # CREATE LOGGER
    logger = create_logger(parser.prog, args.log)

    (source_plates,
     dest_plates) = input_importer(
        args.source_plates,
        args.source_wells,
        args.dest_plates,
        args.dest_wells,
        logger=logger
    )

    # Check volumes
    warning_volumes_reports = list()
    for plt_n, plt in dest_plates.items():
        warning_volumes_report = check_volumes(
            plt.to_dict(),
            lower_bound=10,
            upper_bound=1000,
            logger=logger
        )
        warning_volumes_report['Plate'] = plt_n
        warning_volumes_reports.append(warning_volumes_report)
    warning_volumes_report = pd_concat(warning_volumes_reports)

    # Save warning volumes
    save_df(
        df=warning_volumes_report,
        outfile='volumes_warnings.tsv',
        output_folder=args.output_folder,
        logger=logger
    )

    split_components = dict()
    for i in range(len(args.split_components)):
        split_components[args.split_components[i]] = {
            'upper': args.split_upper_vol[i],
            'lower': args.split_lower_vol[i]
        }

    # Generate instructions
    echo_instructions = instructions_generator(
            source_plates=source_plates,
            dest_plates=dest_plates,
            split_components=split_components,
            robot=args.robot,
            src_plate_type=args.src_plate_type,
            logger=logger
        )

    # Save instructions
    if (
        args.split_outfile_components !=
        DEFAULT_ARGS['SPLIT_OUTFILE_COMPONENTS']
    ):
        # If list of split_outfile_components is empty
        # i.e. no components are listed but the optipn is activated,
        # save each component in a separate file
        if args.split_outfile_components == []:
            args.split_outfile_components = \
                echo_instructions['Sample ID'].unique()
        # save each listed component in a separate file
        for component in args.split_outfile_components:
            # Extract instructions where 'Sample ID' == component
            echo_instructions_component = echo_instructions[
                echo_instructions['Sample ID'] == component
            ]
            save_df(
                df=echo_instructions_component,
                outfile=f'instructions_{component}.csv',
                output_folder=args.output_folder,
                logger=logger
            )
            echo_instructions = echo_instructions[
                echo_instructions['Sample ID'] != component
            ]
    # For each remained components,
    # or if list of split_outfile_components is unchanged,
    # save all instructions in a single file
    save_df(
        df=echo_instructions,
        outfile='instructions.csv',
        output_folder=args.output_folder,
        logger=logger
    )


if __name__ == "__main__":
    sys.exit(main())
