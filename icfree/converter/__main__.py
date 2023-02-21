'''
Converter module

Converts concentrations into volumes from sampler module
'''
import sys
from logging import (
    Logger,
    getLogger
)
from pandas import read_csv

from brs_utils import (
    create_logger
)

from .converter import concentrations_to_volumes
from .args import build_args_parser
from icfree.utils import save_df


def input_importer(
    cfps_parameters,
    values,
    logger: Logger = getLogger(__name__)
):
    """
    Create sampling dataframes from tsv files

    Parameters
    ----------
    cfps_parameters : tsv file
        TSV of cfps parameters, status, maximum and stock concentrations
    values : tsv file
        Dataset with concentration values
    logger: Logger
        Logger, default is getLogger(__name__)

    Returns
    -------
    cfps_parameters_df : DataFrame
        Dataframe with cfps_parameters data
    values_df : DataFrame
        Dataframe with sampling data
    """
    cfps_parameters_df = read_csv(
        cfps_parameters,
        sep='[,\t]',
        engine='python'
    )
    logger.debug(f'cfps_parameters_df:\n{cfps_parameters_df}')

    values_df = read_csv(values, sep='[,\t]', engine='python')
    logger.debug(f'values_df:\n{values_df}')

    return cfps_parameters_df, values_df


def main():
    """
    Main function
    """
    parser = build_args_parser(
        program='converter',
        description='Convert concentrations into volumes'
    )

    args = parser.parse_args()

    # CREATE LOGGER
    logger = create_logger(parser.prog, args.log)

    (cfps_parameters_df,
     concentrations_df) = input_importer(
        args.cfps,
        args.concentrations,
        logger=logger
    )

    try:
        volumes_df = concentrations_to_volumes(
            cfps_parameters_df,
            concentrations_df,
            args.sample_volume,
            logger=logger
        )
    except ValueError as e:
        logger.error(f'{e}\nExiting...')
        return -1

    # Save volumes
    save_df(
        df=volumes_df,
        outfile='sampling_volumes.tsv',
        output_folder=args.output_folder,
        logger=logger
    )


if __name__ == "__main__":
    sys.exit(main())
