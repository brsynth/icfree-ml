import sys
from os import path as os_path
from logging import (
    Logger,
    getLogger
)
from pandas import read_csv

from brs_utils import (
    create_logger
)

from .plates_generator import (
    extract_dead_volumes,
    src_plate_generator,
    dst_plate_generator
)
from .args import build_args_parser
from .plate import Plate
from icfree.utils import save_df


def input_importer(
    cfps_parameters,
    volumes,
    logger: Logger = getLogger(__name__)
):
    """
    Create volumes dataframes from tsv files

    Parameters
    ----------
    cfps_parameters : tsv file
        TSV of cfps parameters, status, maximum and stock concentrations
    volumes : tsv file
        Dataset with volumes values

    Returns
    -------
    cfps_parameters_df : DataFrame
        Dataframe with cfps_parameters data
    volumes_df : DataFrame
        Dataframe with volumes data
    """
    cfps_parameters_df = read_csv(
        cfps_parameters,
        sep='[,\t]',
        engine='python'
    )
    logger.debug(f'cfps_parameters_df: {cfps_parameters_df}')

    volumes_df = read_csv(volumes, sep='[,\t]', engine='python')
    logger.debug(f'volumes_df: {volumes_df}')

    return cfps_parameters_df, volumes_df


def main():
    parser = build_args_parser(
        program='echo_instructor',
        description='Generates instructions for the Echo robot'
    )

    args = parser.parse_args()

    # CREATE LOGGER
    logger = create_logger(parser.prog, args.log)

    (cfps_parameters_df,
     values_df) = input_importer(
        args.cfps,
        args.volumes,
        logger=logger
    )

    # # Check if values_f are concentrations or volumes
    # if 'Stock concentration' in values_df.columns:
    #     try:
    #         (values_df,
    #         param_dead_volumes,
    #         warning_volumes_report) = concentrations_to_volumes(
    #             cfps_parameters_df,
    #             values_df,
    #             args.sample_volume,
    #             logger=logger)
    #     except ValueError as e:
    #         logger.error(f'{e}\nExiting...')
    #         return -1

    # Exract dead plate volumes from cfps_parameters_df
    dead_volumes = extract_dead_volumes(cfps_parameters_df)

    values_df['Water'] = \
        args.sample_volume - values_df.sum(axis=1)

    # Generate source plates
    try:
        source_plates = src_plate_generator(
            volumes=values_df,
            plate_dead_volume=args.source_plate_dead_volume,
            plate_well_capacity=args.source_plate_well_capacity,
            param_dead_volumes=dead_volumes,
            starting_well=args.src_starting_well,
            optimize_well_volumes=args.optimize_well_volumes,
            vertical=True,
            plate_dimensions=args.plate_dimensions,
            logger=logger
        )
    except IndexError as e:
        logger.error(e)
        logger.error(
            'Exiting...'
        )
        return -1

    # Generate destination plates
    dest_plates = dst_plate_generator(
        volumes=values_df,
        starting_well=args.dest_starting_well,
        plate_well_capacity=args.dest_plate_well_capacity,
        vertical=True,
        logger=logger
    )

    # Save source plates
    for plt_name, plate in source_plates.items():
        plate.to_json(
            os_path.join(
                args.output_folder,
                f'source_plate_{plt_name}.json'
            )
        )

    # Save destination plates
    for plt_name, plate in dest_plates.items():
        plate.to_json(
            os_path.join(
                args.output_folder,
                f'destination_plate_{plt_name}.json'
            )
        )

    # Save volumes summary
    volumes_summary = Plate.get_volumes_summary(
        list(source_plates.values()),
        'pandas',
        logger=logger
    )
    save_df(
        df=volumes_summary,
        outfile='volumes_summary.tsv',
        output_folder=args.output_folder,
        index=True,
        logger=logger
    )


if __name__ == "__main__":
    sys.exit(main())
