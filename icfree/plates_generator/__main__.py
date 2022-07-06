import sys

from logging import(
    Logger,
    getLogger
)
from typing import (
    Dict
)
from brs_utils import (
    create_logger
)

from .plates_generator import (
    input_importer,
    input_processor,
    doe_levels_generator,
    levels_to_concentrations,
    plates_generator,
    save_plates,
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

    # If status of parameters has to be changed
    if args.all_status is not None:
        parameters = change_status(
            parameters,
            args.all_status,
            logger
        )

    # PROCESS TO THE SAMPLING
    doe_levels = doe_levels_generator(
        n_variable_parameters=len(parameters['doe']),
        doe_nb_concentrations=args.doe_nb_concentrations,
        doe_concentrations=args.doe_concentrations,
        doe_nb_samples=args.doe_nb_samples,
        seed=args.seed,
        logger=logger
    )

    # CONVERT INTO CONCENTRATIONS
    # Read the maximum concentration for each parameter involved in DoE
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
    # Read the maximum concentration for each constant parameter
    try:
        const_concentrations = {
            k: v['Maximum concentration']
            for k, v in parameters['const'].items()
        }
    except KeyError:
        const_concentrations = {}
    # Generate the plates
    plates = plates_generator(
        doe_concentrations=doe_concentrations,
        const_concentrations=const_concentrations,
        dna_concentrations=dna_concentrations,
        parameters={k: list(v.keys()) for k, v in parameters.items()},
        logger=logger
    )

    # WRITE TO DISK
    save_plates(
        plates['initial'],
        plates['normalizer'],
        plates['background'],
        plates['parameters'],
        args.output_folder
    )


def change_status(
    parameters: Dict,
    status: str,
    logger: Logger = getLogger(__name__)
) -> Dict:
    """
    Change status of parameters

    Parameters
    ----------
    parameters : Dict
        Parameters
    status: str
        Status to change parameters status into
    logger: Logger
        Logger

    Returns
    -------
    parameters: Dict
        Parameters with new status
    """
    # Set all status to an empty dict
    _parameters = {
        status: {} for status in parameters.keys()
    }
    # Copy all values under args.all_status key,
    # except for status wich contain 'dna'
    for status, value in parameters.items():
        if 'dna' not in status:
            _parameters[status].update(value)
        else:
            if status not in _parameters:
                _parameters[status] = {}
            _parameters[status].update(value)
    return _parameters


if __name__ == "__main__":
    sys.exit(main())
