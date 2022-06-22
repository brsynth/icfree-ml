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
    output_folder = args.output_folder

    input_importer_variables = input_importer(
        cfps_parameters,
        initial_concentrations,
        normalizer_concentrations,
        autofluorescence_concentrations)

    cfps_parameters_df = input_importer_variables[0]
    initial_concentrations_df = input_importer_variables[1]
    normalizer_concentrations_df = input_importer_variables[2]
    autofluorescence_concentrations_df = input_importer_variables[3]

    try:
        concentrations_to_volumes_dfs = concentrations_to_volumes(
            cfps_parameters_df,
            initial_concentrations_df,
            normalizer_concentrations_df,
            autofluorescence_concentrations_df,
            sample_volume,
            logger=logger)
    except ValueError:
        exit(1)

    initial_volumes_df = concentrations_to_volumes_dfs[0]
    normalizer_volumes_df = concentrations_to_volumes_dfs[1]
    autofluorescence_volumes_df = concentrations_to_volumes_dfs[2]

    save_volumes(
        cfps_parameters_df,
        initial_volumes_df,
        normalizer_volumes_df,
        autofluorescence_volumes_df,
        output_folder)

    samples_merger_dfs = samples_merger(
        initial_volumes_df,
        normalizer_volumes_df,
        autofluorescence_volumes_df)

    merged_plate_1_final = samples_merger_dfs[0]
    merged_plate_2_final = samples_merger_dfs[1]
    merged_plate_3_final = samples_merger_dfs[2]

    distribute_destination_plates_dict = \
        distribute_destination_plate_generator(
            initial_volumes_df,
            normalizer_volumes_df,
            autofluorescence_volumes_df,
            starting_well,
            vertical=True)

    distribute_echo_instructions_dict = \
        distribute_echo_instructions_generator(
            distribute_destination_plates_dict)

    merge_destination_plates_dict = merge_destination_plate_generator(
        merged_plate_1_final,
        merged_plate_2_final,
        merged_plate_3_final,
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
