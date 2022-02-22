import sys

from .echo_instructor import (
    input_importer,
    volumes_array_generator,
    save_volumes_array,
    destination_plate_generator,
    echo_instructions_generator,
    save_echo_instructions
)


from .args import build_args_parser


def main():
    parser = build_args_parser(
        program='echo_instructor',
        description='Generates instructions for the Echo robot')

    args = parser.parse_args()
    cfps_parameters = args.input
    initial_set_concentrations = args.input1
    normalizer_set_concentrations = args.input2
    autofluorescence_set_concentrations = args.input3
    # sample_volume = args.sample_volume
    sample_volume = 10

    cfps_parameters_df = input_importer(
        cfps_parameters,
        initial_set_concentrations,
        normalizer_set_concentrations,
        autofluorescence_set_concentrations)[0]

    initial_set_concentrations_df = input_importer(
        cfps_parameters,
        initial_set_concentrations,
        normalizer_set_concentrations,
        autofluorescence_set_concentrations)[1]

    normalizer_set_concentrations_df = input_importer(
        cfps_parameters,
        initial_set_concentrations,
        normalizer_set_concentrations,
        autofluorescence_set_concentrations)[2]

    autofluorescence_set_concentrations_df = input_importer(
        cfps_parameters,
        initial_set_concentrations,
        normalizer_set_concentrations,
        autofluorescence_set_concentrations)[3]

    initial_set_volumes_df = volumes_array_generator(
        cfps_parameters_df,
        initial_set_concentrations_df,
        normalizer_set_concentrations_df,
        autofluorescence_set_concentrations_df,
        sample_volume)[0]

    normalizer_set_volumes_df = volumes_array_generator(
        cfps_parameters_df,
        initial_set_concentrations_df,
        normalizer_set_concentrations_df,
        autofluorescence_set_concentrations_df,
        sample_volume)[1]

    autofluorescence_set_volumes_df = volumes_array_generator(
        cfps_parameters_df,
        initial_set_concentrations_df,
        normalizer_set_concentrations_df,
        autofluorescence_set_concentrations_df,
        sample_volume)[2]

    save_volumes_array(
        cfps_parameters_df,
        initial_set_volumes_df,
        normalizer_set_volumes_df,
        autofluorescence_set_volumes_df)

    destination_plates_dict = destination_plate_generator(
        initial_set_volumes_df,
        normalizer_set_volumes_df,
        autofluorescence_set_volumes_df,
        starting_well='A1',
        vertical=True)

    echo_instructions_dict = echo_instructions_generator(
        destination_plates_dict)

    save_echo_instructions(echo_instructions_dict)


if __name__ == "__main__":
    sys.exit(main())
