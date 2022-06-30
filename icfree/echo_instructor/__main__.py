import sys

from brs_utils import (
    create_logger
)

from .echo_instructor import (
    input_importer,
    concentrations_to_volumes,
    save_volumes,
    samples_merger,
    distribute_destination_plate_generator,
    distribute_echo_instructions_generator,
    merge_destination_plate_generator,
    merge_echo_instructions_generator,
    save_echo_instructions
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
    cfps_parameters = args.cfps
    initial_concentrations = args.init_set
    normalizer_concentrations = args.norm_set
    autofluorescence_concentrations = args.autofluo_set
    starting_well = args.starting_well
    sample_volume = args.sample_volume
    source_plate_dead_volume = args.source_plate_dead_volume
    output_folder = args.output_folder

    (cfps_parameters_df,
    concentrations_df) = input_importer(
        cfps_parameters,
        initial_concentrations,
        normalizer_concentrations,
        autofluorescence_concentrations)

    try:
        (volumes_df,
        volumes_summary,
        warning_volumes_report) = concentrations_to_volumes(
            cfps_parameters_df,
            concentrations_df,
            sample_volume,
            source_plate_dead_volume,
            logger=logger)
    except ValueError:
        exit(1)

    save_volumes(
        cfps_parameters_df,
        volumes_df,
        volumes_summary,
        warning_volumes_report,
        output_folder)

    merged_plates = samples_merger(volumes_df)

    distribute_destination_plates_dict = \
        distribute_destination_plate_generator(
            volumes_df,
            starting_well,
            vertical=True)

    distribute_echo_instructions_dict = \
        distribute_echo_instructions_generator(
            distribute_destination_plates_dict)

    merge_destination_plates_dict = merge_destination_plate_generator(
        merged_plates,
        starting_well,
        vertical=True)

    merge_echo_instructions_dict = \
        merge_echo_instructions_generator(
            merge_destination_plates_dict)

    save_echo_instructions(
        distribute_echo_instructions_dict,
        merge_echo_instructions_dict,
        output_folder)


if __name__ == "__main__":
    sys.exit(main())
