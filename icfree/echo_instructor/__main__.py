import sys

from .echo_instructor import (
    input_importer,
    volumes_array_generator,
    save_volumes,
    samples_merger,
    multiple_destination_plate_generator,
    multiple_echo_instructions_generator,
    single_destination_plate_generator,
    single_echo_instructions_generator,
    save_echo_instructions
)

from .args import build_args_parser


def main():
    parser = build_args_parser(
        program='echo_instructor',
        description='Generates instructions for the Echo robot')

    args = parser.parse_args()
    cfps_parameters = args.cfps
    initial_concentrations = args.init_tset
    normalizer_concentrations = args.norm_set
    autofluorescence_concentrations = args.autofluo_set
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

    volumes_array_generator_variables = volumes_array_generator(
        cfps_parameters_df,
        initial_concentrations_df,
        normalizer_concentrations_df,
        autofluorescence_concentrations_df,
        sample_volume)

    initial_volumes_df = volumes_array_generator_variables[0]
    normalizer_volumes_df = volumes_array_generator_variables[1]
    autofluorescence_volumes_df = volumes_array_generator_variables[2]

    save_volumes(
        cfps_parameters_df,
        initial_volumes_df,
        normalizer_volumes_df,
        autofluorescence_volumes_df,
        output_folder)

    samples_merger_variables = samples_merger(
        initial_volumes_df,
        normalizer_volumes_df,
        autofluorescence_volumes_df)

    master_plate_1_final = samples_merger_variables[0]
    master_plate_2_final = samples_merger_variables[1]
    master_plate_3_final = samples_merger_variables[2]

    multiple_destination_plates_dict = multiple_destination_plate_generator(
        initial_volumes_df,
        normalizer_volumes_df,
        autofluorescence_volumes_df,
        starting_well='A1',
        vertical=True)

    multiple_echo_instructions_dict = \
        multiple_echo_instructions_generator(multiple_destination_plates_dict)

    single_destination_plates_dict = single_destination_plate_generator(
        master_plate_1_final,
        master_plate_2_final,
        master_plate_3_final,
        starting_well='A1',
        vertical=True)

    single_echo_instructions_dict = \
        single_echo_instructions_generator(single_destination_plates_dict)

    save_echo_instructions(
        multiple_echo_instructions_dict,
        single_echo_instructions_dict,
        output_folder)


if __name__ == "__main__":
    sys.exit(main())
