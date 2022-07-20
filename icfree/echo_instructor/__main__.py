import sys

from brs_utils import (
    create_logger
)

from .echo_instructor import (
    input_importer,
    concentrations_to_volumes,
    save_volumes,
    samples_merger,
    echo_instructions_generator,
    save_echo_instructions,
    src_plate_generator,
    echo_wells
)
from .args import build_args_parser


def main():
    parser = build_args_parser(
        program='echo_instructor',
        description='Generates instructions for the Echo robot')

    args = parser.parse_args()

    # CREATE LOGGER
    logger = create_logger(parser.prog, args.log)

    (cfps_parameters_df,
     concentrations_df) = input_importer(
        args.cfps,
        args.init_set,
        args.norm_set,
        args.autofluo_set,
        logger=logger)

    try:
        (volumes,
         param_dead_volumes,
         warning_volumes_report) = concentrations_to_volumes(
            cfps_parameters_df,
            concentrations_df,
            args.sample_volume,
            logger=logger)
    except ValueError as e:
        logger.error(f'{e}\nExiting...')
        return -1

    try:
        source_plates = src_plate_generator(
            volumes=volumes,
            plate_dead_volume=args.source_plate_dead_volume,
            plate_well_capacity=args.source_plate_well_capacity,
            param_dead_volumes=param_dead_volumes,
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

    _echo_wells = {}
    for plate_id, plate in source_plates.items():
        _echo_wells[plate_id] = echo_wells(plate)

    distribute_echo_instructions = \
        echo_instructions_generator(
            volumes=volumes,
            echo_wells=_echo_wells,
            plate_dead_volume=args.dest_plate_dead_volume,
            plate_well_capacity=args.dest_plate_well_capacity,
            starting_well=args.dest_starting_well,
            keep_nil_vol=args.keep_nil_vol,
            logger=logger
        )

    merged_plates = samples_merger(volumes, args.nplicate)

    merge_echo_instructions = \
        echo_instructions_generator(
            volumes=merged_plates,
            echo_wells=_echo_wells,
            plate_dead_volume=args.dest_plate_dead_volume,
            plate_well_capacity=args.dest_plate_well_capacity,
            starting_well=args.dest_starting_well,
            keep_nil_vol=args.keep_nil_vol,
            logger=logger
        )

    save_echo_instructions(
        distribute_echo_instructions,
        merge_echo_instructions,
        args.output_folder)

    volumes_summary = {
        param: well['nb_wells'] * well['volume_per_well']
        for wells in _echo_wells.values()
        for param, well in wells.items()
    }

    save_volumes(
        volumes,
        volumes_summary,
        warning_volumes_report,
        _echo_wells,
        args.output_folder,
        logger=logger
    )


if __name__ == "__main__":
    sys.exit(main())
