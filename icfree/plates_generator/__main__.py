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

from brs_utils import (
    create_logger
)

from .args import build_args_parser

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
    logger = create_logger(parser.prog, args.log)

    ## Read input file
    input_df = input_importer(args.cfps)
    parameters = input_processor(input_df, logger=logger)

    ## Process to the sampling
    levels_array = levels_array_generator(
        n_variable_parameters=len(parameters['variable']),
        doe_nb_concentrations=args.doe_nb_concentrations,
        doe_concentrations=args.doe_concentrations,
        doe_nb_samples=args.doe_nb_samples,
        seed=args.seed,
        logger=logger
    )

    ## Convert into concentrations
    # read the maximum concentration for each variable parameter
    max_variable_con = [
        v['Maximum concentration']
        for v in parameters['variable'].values()
    ]
    # convert
    variable_concentrations_array = variable_concentrations_array_generator(
        levels_array,
        max_variable_con
    )
    # read the maximum concentration for each fixed parameter
    max_fixed_conc = [
        v['Maximum concentration']
        for v in parameters['fixed'].values()
    ]
    # convert
    fixed_concentrations_array = fixed_concentrations_array_generator(
        variable_concentrations_array,
        max_fixed_conc
    )

    ## Generate plate
    plates_generator = initial_plates_generator(
        variable_concentrations_array,
        fixed_concentrations_array,
        input_df,
        logger=logger
    )

    ## Write to disk
    save_intial_plates(
        plates_generator['initial'],
        plates_generator['normalizer'],
        plates_generator['background'],
        plates_generator['parameters'],
        args.output_folder
    )


if __name__ == "__main__":
    sys.exit(main())
