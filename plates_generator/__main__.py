import sys
from .plates_generator import (
    input_importer,
    input_processor,
    levels_array_generator,
    variable_concentrations_array_generator,
    fixed_concentrations_array_generator,
    initial_plates_generator,
    save_intial_plates,
)

from .args import build_args_parser


def main():

    parser = build_args_parser(
        program='initial_set_generator',
        description='Generate the initial plates for active learning')

    args = parser.parse_args()

    input_file = args.input
    input_df = input_importer(input_file)

    n_variable_parameters = input_processor(input_df)[0]
    n_ratios = 5
    levels_array = levels_array_generator(n_variable_parameters, n_ratios)

    maximum_variable_concentrations = input_processor(input_df)[3]
    variable_concentrations_array = variable_concentrations_array_generator(
                                    levels_array,
                                    maximum_variable_concentrations)

    maximum_fixed_concentrations = input_processor(input_df)[1]
    fixed_concentrations_array = fixed_concentrations_array_generator(
                                variable_concentrations_array,
                                maximum_fixed_concentrations)

    # maximum_concentrations_sample = maximum_concentrations_sample_generator(
    #                             input_df)[0]

    initial_set = initial_plates_generator(
        variable_concentrations_array,
        fixed_concentrations_array,
        input_df)[0]

    normalizer_set = initial_plates_generator(
        variable_concentrations_array,
        fixed_concentrations_array,
        input_df)[1]

    autolfuorescence_set = initial_plates_generator(
        variable_concentrations_array,
        fixed_concentrations_array,
        input_df)[2]

    all_parameters = initial_plates_generator(
        variable_concentrations_array,
        fixed_concentrations_array,
        input_df)[3]

    save_intial_plates(
        initial_set,
        normalizer_set,
        autolfuorescence_set,
        all_parameters)


if __name__ == "__main__":
    sys.exit(main())
