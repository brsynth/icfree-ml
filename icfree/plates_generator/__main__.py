import sys
from .plates_generator import (
    input_importer,
    input_processor,
    doe_levels_generator,
    levels_to_concentrations,
    plates_generator,
    save_plates,
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

    # CREATE LOGGER
    logger = create_logger(parser.prog, args.log)

    # READ INPUT FILE
    input_df = input_importer(args.cfps, logger=logger)
    parameters = input_processor(input_df, logger=logger)

    # PROCESS TO THE SAMPLING
    try:
        doe_levels = doe_levels_generator(
            n_variable_parameters=len(parameters['doe']),
            doe_nb_concentrations=args.doe_nb_concentrations,
            doe_concentrations=args.doe_concentrations,
            doe_nb_samples=args.doe_nb_samples,
            seed=args.seed,
            logger=logger
        )
    except KeyError:
        logger.error('There is no \'doe\' status in the input file')
        exit(1)

    # CONVERT INTO CONCENTRATIONS
    # Read the maximum concentration for each variable parameter
    max_conc = [
        v['Maximum concentration']
        for v in parameters['doe'].values()
    ]
    # Convert
    doe_concentrations = levels_to_concentrations(
        doe_levels,
        max_conc,
        logger=logger
    )

    # GENERATE PLATE
    # Read the maximum concentration for each dna parameter
    dna_concentrations = {
        v: dna_param[v]['Maximum concentration']
        for status, dna_param in parameters.items()
        for v in dna_param
        if status.startswith('dna')
    }
    try:
        const_concentrations = {
            k: v['Maximum concentration']
            for k, v in parameters['const'].items()
        }
    except KeyError:
        const_concentrations = {}
    plates = plates_generator(
        doe_concentrations=doe_concentrations,
        const_concentrations=const_concentrations,
        dna_concentrations=dna_concentrations,
        parameters={k: list(v.keys()) for k, v in parameters.items()},
        logger=logger
    )

    # Write to disk
    save_plates(
        plates['initial'],
        plates['normalizer'],
        plates['background'],
        plates['parameters'],
        args.output_folder
    )


if __name__ == "__main__":
    sys.exit(main())
