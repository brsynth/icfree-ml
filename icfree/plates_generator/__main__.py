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

# from brs_utils import (
#     create_logger
# )

from .args import build_args_parser

# from typing import *

# from logging import (
#     Logger,
#     getLogger
# )

# def check_results(
#     result_files: Dict,
#     logger: Logger = getLogger(__name__)
# ) -> int:
#     logger.info('lblblb')
#     logger.debug(f'lblblb{[i for i in result_files]}')


def main():

    parser = build_args_parser(
        program='initial_set_generator',
        description='Generate the initial plates for active learning'
    )

    args = parser.parse_args()

    # Create logger
    # logger = create_logger(parser.prog, args.log)
    # check_results(gg, logger=logger)

    input_file = args.cfps
    input_df = input_importer(input_file)

    input_processor_variables = input_processor(input_df)
    n_variable_parameters = input_processor_variables[0]

    levels_array = levels_array_generator(
        n_variable_parameters,
        args.doe_ratios,
        seed=args.seed)

    maximum_variable_concentrations = input_processor_variables[3]
    variable_concentrations_array = variable_concentrations_array_generator(
                                    levels_array,
                                    maximum_variable_concentrations)

    maximum_fixed_concentrations = input_processor_variables[1]
    fixed_concentrations_array = fixed_concentrations_array_generator(
                                variable_concentrations_array,
                                maximum_fixed_concentrations)

    # maximum_concentrations_sample = maximum_concentrations_sample_generator(
    #                             input_df)[0]

    initial_plates_generator_variables = initial_plates_generator(
        variable_concentrations_array,
        fixed_concentrations_array,
        input_df)

    initial_set = initial_plates_generator_variables[0]
    normalizer_set = initial_plates_generator_variables[1]
    autofluorescence_set = initial_plates_generator_variables[2]
    all_parameters = initial_plates_generator_variables[3]

    save_intial_plates(
        initial_set,
        normalizer_set,
        autofluorescence_set,
        all_parameters,
        args.output_folder)


if __name__ == "__main__":
    sys.exit(main())
