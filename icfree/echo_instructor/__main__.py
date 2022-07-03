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
    dst_plate_generator
)
from .args import build_args_parser


def main():
    parser = build_args_parser(
        program='echo_instructor',
        description='Generates instructions for the Echo robot')

    args = parser.parse_args()

    # CREATE LOGGER
    logger = create_logger(parser.prog, args.log)

    args = parser.parse_args()
    optimize_well_volumes = args.optimize_well_volumes
    plate_well_capacity = args.source_plate_well_capacity
    keep_nil_vol = args.keep_nil_vol
    cfps_parameters = args.cfps
    initial_concentrations = args.init_set
    normalizer_concentrations = args.norm_set
    autofluorescence_concentrations = args.autofluo_set
    dest_starting_well = args.dest_starting_well
    src_starting_well = args.src_starting_well
    sample_volume = args.sample_volume
    source_plate_dead_volume = args.source_plate_dead_volume
    output_folder = args.output_folder
    nplicate = args.nplicate
    nb_wells_plate = args.nb_wells_plate

    (cfps_parameters_df,
     concentrations_df) = input_importer(
        cfps_parameters,
        initial_concentrations,
        normalizer_concentrations,
        autofluorescence_concentrations)

    try:
        (volumes,
        #  volumes_summary,
         param_dead_volumes,
         warning_volumes_report) = concentrations_to_volumes(
            cfps_parameters_df,
            concentrations_df,
            sample_volume,
            logger=logger)
    except ValueError:
        exit(1)

    # print(param_dead_volumes)
    # print(dict(zip(cfps_parameters_df['Parameter'], cfps_parameters_df['Parameter dead volume'])))
    # exit()
    source_plate = src_plate_generator(
        volumes=volumes,
        plate_dead_volume=source_plate_dead_volume,
        plate_well_capacity=plate_well_capacity,
        param_dead_volumes=param_dead_volumes,
        starting_well=src_starting_well,
        optimize_well_volumes=optimize_well_volumes,
        vertical=True,
        nb_wells_plate=nb_wells_plate,
        logger=logger
    )

    distribute_echo_instructions = \
        echo_instructions_generator(
            volumes=volumes,
            source_plate=source_plate,
            starting_well=dest_starting_well,
            keep_nil_vol=keep_nil_vol,
            logger=logger
        )

    merged_plates = samples_merger(volumes, nplicate)

    merge_echo_instructions = \
        echo_instructions_generator(
            volumes=merged_plates,
            source_plate=source_plate,
            starting_well=dest_starting_well,
            keep_nil_vol=keep_nil_vol,
            logger=logger
        )

    save_echo_instructions(
        distribute_echo_instructions,
        merge_echo_instructions,
        output_folder)

    volumes_summary = {
        param: volume['nb_wells'] * volume['volume_per_well']
        for param, volume in source_plate.items()
    }

    save_volumes(
        cfps_parameters_df,
        volumes,
        volumes_summary,
        warning_volumes_report,
        output_folder
    )


if __name__ == "__main__":
    sys.exit(main())
