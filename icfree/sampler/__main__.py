import sys

from logging import (
    Logger,
    getLogger
)
from typing import (
    Dict
)
from brs_utils import (
    create_logger
)

from .concentrations_sampler import (
    input_importer,
    input_processor,
    doe_levels_generator,
    levels_to_concentrations,
    assemble_concentrations,
    save_concentrations,
    set_concentration_ratios,
    check_sampling
)
from .args import build_args_parser


def main():

    parser = build_args_parser(
        program='concenrations_sampler',
        description='Sample concentrations for DNA and protein'
    )

    args = parser.parse_args()

    # CREATE LOGGER
    logger = create_logger(parser.prog, args.log)

    # READ INPUT FILE
    input_df = input_importer(args.cfps, logger=logger)
    parameters = input_processor(input_df, logger=logger)

    # Set the concentration ratios for each parameter
    doe_concentration_ratios = {
        parameter: data['Concentration ratios']
        for parameter, data in parameters['doe'].items()
    }
    concentration_ratios = set_concentration_ratios(
        concentration_ratios=doe_concentration_ratios,
        all_doe_nb_concentrations=args.doe_nb_concentrations,
        all_doe_concentration_ratios=args.doe_concentration_ratios,
        logger=logger
    )

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
        concentration_ratios=concentration_ratios,
        doe_nb_samples=args.doe_nb_samples,
        seed=args.seed,
        logger=logger
    )

    # Check sampling
    check_sampling(doe_levels, logger)

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
    # Generate the concentrations
    concentrations = assemble_concentrations(
        doe_concentrations=doe_concentrations,
        const_concentrations=const_concentrations,
        dna_concentrations=dna_concentrations,
        parameters={k: list(v.keys()) for k, v in parameters.items()},
        logger=logger
    )

    # WRITE TO DISK
    save_concentrations(
        concentrations['initial'],
        concentrations['normalizer'],
        concentrations['background'],
        concentrations['parameters'],
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
    for _status, _value in parameters.items():
        if 'dna' not in _status:
            _parameters[status].update(_value)
        else:
            if _status not in _parameters:
                _parameters[_status] = {}
            _parameters[_status].update(_value)
    return _parameters


if __name__ == "__main__":
    sys.exit(main())
