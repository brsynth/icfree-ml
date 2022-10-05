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

from .sampler import (
    input_importer,
    input_processor,
    sampling,
    levels_to_absvalues,
    assemble_values,
    save_values,
    set_sampling_ratios,
    check_sampling
)
from .args import build_args_parser


def main():

    parser = build_args_parser(
        program='sampler',
        description='Sample values'
    )

    args = parser.parse_args()

    # CREATE LOGGER
    logger = create_logger(parser.prog, args.log)

    # READ INPUT FILE
    input_df = input_importer(args.cfps, logger=logger)
    parameters = input_processor(input_df, logger=logger)

    # Set the ratios for each parameter
    ratios = {
        parameter: data['Ratios']
        for parameter, data in parameters['doe'].items()
    }
    sampling_ratios = set_sampling_ratios(
        ratios=ratios,
        all_nb_steps=args.nb_sampling_steps,
        all_ratios=args.sampling_ratios,
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
    levels = sampling(
        n_variable_parameters=len(parameters['doe']),
        ratios=sampling_ratios,
        nb_samples=args.nb_samples,
        seed=args.seed,
        logger=logger
    )
    # Check sampling
    check_sampling(levels, logger)

    # CONVERT INTO ABSOLUTE VALUES
    # Read the maximum value for each parameter involved in DoE
    max_values = [
        v['Maximum']
        for v in parameters['doe'].values()
    ]
    # Convert
    sampling_values = levels_to_absvalues(
        levels,
        max_values,
        logger=logger
    )

    # GENERATE PLATE
    # Read the maximum value for each dna parameter
    dna_values = {
        v: dna_param[v]['Maximum']
        for status, dna_param in parameters.items()
        for v in dna_param
        if status.startswith('dna')
    }
    # Read the maximum for each constant parameter
    try:
        const_values = {
            k: v['Maximum']
            for k, v in parameters['const'].items()
        }
    except KeyError:
        const_values = {}
    # Generate the absolute values
    abs_values = assemble_values(
        sampling_values=sampling_values,
        const_values=const_values,
        dna_values=dna_values,
        parameters={k: list(v.keys()) for k, v in parameters.items()},
        logger=logger
    )

    # WRITE TO DISK
    save_values(
        abs_values['initial'],
        abs_values['normalizer'],
        abs_values['background'],
        abs_values['parameters'],
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
