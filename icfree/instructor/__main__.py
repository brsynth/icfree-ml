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
from .args import build_args_parser
from icfree.utils import save_df
from icfree.plates_generator.plate import Plate


def input_importer(
    source_plates_path: List[str],
    dest_plates_path: List[str],
    logger: Logger = getLogger(__name__)
):
    """
    Create concentrations dataframes from tsv files

    Parameters
    ----------
    source_plates_path : List[str]
        Path to source plates
    dest_plates_path : List[str]
        Path to destination plates

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
    for source_plate_path in source_plates_path:
        source_plates[source_plate_path] = \
            Plate.from_json(source_plate_path, logger=logger)
    logger.debug('SOURCE PLATES')
    for plt in source_plates:
        logger.debug(plt)

    dest_plates = dict()
    for dest_plate_path in dest_plates_path:
        dest_plates[dest_plate_path] = \
            Plate.from_json(dest_plate_path, logger=logger)
    logger.debug('DESTINATION PLATES')
    for plt in dest_plates:
        logger.debug(plt)

    return source_plates, dest_plates


def main():
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
        args.dest_plates,
        logger=logger
    )

    # try:
    #     (volumes,
    #      param_dead_volumes,
    #      warning_volumes_report) = concentrations_to_volumes(
    #         cfps_parameters_df,
    #         concentrations_df,
    #         args.sample_volume,
    #         logger=logger)
    # except ValueError as e:
    #     logger.error(f'{e}\nExiting...')
    #     return -1

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
    warning_volumes_reports = pd_concat(warning_volumes_reports)

    # Save warning volumes
    save_df(
        df=warning_volumes_report,
        outfile='volumes_warnings.tsv',
        output_folder=args.output_folder,
        logger=logger
    )

    echo_instructions = instructions_generator(
            source_plates=source_plates,
            dest_plates=dest_plates,
            robot=args.robot,
            logger=logger
        )

    # Save instructions
    save_df(
        df=echo_instructions,
        outfile='instructions.csv',
        output_folder=args.output_folder,
        logger=logger
    )


if __name__ == "__main__":
    sys.exit(main())
