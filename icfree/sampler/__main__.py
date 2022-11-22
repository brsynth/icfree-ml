import sys
from pandas import (
    read_csv as pd_read_csv,
    DataFrame
)
from logging import (
    Logger,
    getLogger
)
from typing import (
    Dict
)
from math import isnan
from re import findall

from brs_utils import (
    create_logger
)

from .sampler import (
    sampling,
    levels_to_absvalues,
    save_values,
    set_sampling_ratios,
    check_sampling
)
from .args import build_args_parser


def input_importer(
    cfps_parameters,
    logger: Logger = getLogger(__name__)
) -> DataFrame:
    """
    Import tsv input into a dataframe

    Parameters
    ----------
    input_file : tsv file
        tsv with list of cfps parameters and relative features

    Returns
    -------
    cfps_parameters_df : DataFrame
        Pandas dataframe populated with cfps_parameters data
    """
    cfps_parameters_df = pd_read_csv(
                        cfps_parameters,
                        sep='\t')

    logger.debug(f'CFPs parameters dataframe: {cfps_parameters_df}')

    return cfps_parameters_df


def input_processor(
    cfps_parameters_df: DataFrame,
    logger: Logger = getLogger(__name__)
) -> Dict:
    """
    Determine variable and fixed parameters, and maximum concentrations.

    Parameters
    ----------
    input_df: 2d-array
        N-by-samples array where values are uniformly spaced between 0 and 1.

    Returns
    -------
    parameters: dict
        Dictionnary of parameters.
        First level is indexed on 'Status' column.
        Second level is indexed on 'Parameter' column.
    """
    parameters = {}

    for dic in cfps_parameters_df.to_dict('records'):
        parameters[dic['Parameter']] = {
            k: dic[k] for k in dic.keys() - {'Parameter'}
        }
        # Convert list of ratios str into list of float
        # ratio is a list of float
        if isinstance(parameters[dic['Parameter']]['Ratios'], str):
            parameters[dic['Parameter']]['Ratios'] = list(
                map(
                    float,
                    findall(
                        r"(?:\d*\.\d+|\d+)",
                        parameters[dic['Parameter']]['Ratios']
                    )
                )
            )
        # ratio is nan
        elif isnan(parameters[dic['Parameter']]['Ratios']):
            parameters[dic['Parameter']]['Ratios'] = []
        # ratio is a float
        else:
            parameters[dic['Parameter']]['Ratios'] = \
                [parameters[dic['Parameter']]['Ratios']]

    return parameters


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
        for parameter, data in parameters.items()
    }
    sampling_ratios = set_sampling_ratios(
        ratios=ratios,
        all_nb_steps=args.nb_sampling_steps,
        all_ratios=args.sampling_ratios,
        logger=logger
    )

    # PROCESS TO THE SAMPLING
    levels = sampling(
        n_variable_parameters=len(parameters),
        ratios=sampling_ratios,
        nb_samples=args.nb_samples,
        seed=args.seed,
        logger=logger
    )
    # Check sampling
    check_sampling(levels, logger)

    # CONVERT INTO ABSOLUTE VALUES
    # Read the maxValue for each parameter involved in sampling
    max_values = [
        v['maxValue']
        for v in parameters.values()
    ]

    # Convert
    sampling_values = levels_to_absvalues(
        levels,
        max_values,
        logger=logger
    )

    # WRITE TO DISK
    save_values(
        values=sampling_values,
        parameters=list(parameters.keys()),
        output_folder=args.output_folder,
        output_format=args.output_format
    )


if __name__ == "__main__":
    sys.exit(main())
