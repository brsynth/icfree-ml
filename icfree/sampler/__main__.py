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
    save_values,
    set_sampling_ratios,
    check_sampling,
    convert
)
from .args import build_args_parser
from icfree._version import __version__

__signature__ = f'{sys.modules[__name__].__package__} {__version__}'


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
        signature=__signature__,
        description='Sample values'
    )

    args = parser.parse_args()

    print(__signature__)
    print()

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

    # PRINT INFOS
    logger.info('List of parameters')
    # Compute the number of combinations,
    # i.e. the maximum number of samples
    nb_combinations = 1
    for param, _ratios in sampling_ratios.items():
        nb_ratios = len(_ratios)
        logger.info(f'   {param}\t({nb_ratios} possible values)')
        nb_combinations *= nb_ratios
    logger.info('')
    logger.info(f'Maximum number of unique samples: {nb_combinations}')
    logger.info('')

    # PROCESS TO THE SAMPLING
    try:
        sampling_values = sampling(
            nb_parameters=len(parameters),
            ratios=sampling_ratios,
            nb_samples=args.nb_samples,
            seed=args.seed,
            logger=logger
        )
    except ValueError as e:
        logger.error(e)
        logger.error('Exiting...')
        sys.exit(1)

    # import matplotlib.pyplot as plt
    # plt.scatter(*zip(*sampling_values))
    # plt.show()

    # CONVERT RATIOS INTO VALUES
    max_values = [
        v['maxValue']
        for v in parameters.values()
    ]
    sampling_values = convert(sampling_values, max_values, logger=logger)

    # Get the min and max values for each parameter
    min_max = []
    for i in range(len(sampling_ratios.values())):
        _sampling = list(sampling_ratios.values())[i]
        min_max += [
            (min(_sampling)*max_values[i], max(_sampling)*max_values[i])
        ]
    # Check sampling
    check_sampling(
        sampling_values,
        min_max,
        logger
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
