'''
Converter module

Converts concentrations into volumes from sampler module
'''
from sys import (
    modules as sys_modules,
    exit as sys_exit
)
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
from icfree._version import __version__

__signature__ = f'{sys_modules[__name__].__package__} {__version__}'


def input_importer(
    parameters,
    values,
    logger: Logger = getLogger(__name__)
):
    """
    Create sampling dataframes from tsv files

    Parameters
    ----------
    parameters : tsv file
        TSV of parameters, status, maximum and stock concentrations
    values : tsv file
        Dataset with concentration values
    logger: Logger
        Logger, default is getLogger(__name__)

    Returns
    -------
    parameters_df : DataFrame
        Dataframe with parameters data
    values_df : DataFrame
        Dataframe with sampling data
    """
    parameters_df = read_csv(
        parameters,
        sep='[,\t]',
        engine='python'
    )
    logger.debug(f'parameters_df:\n{parameters_df}')

    values_df = read_csv(values, sep='[,\t]', engine='python')
    logger.debug(f'values_df:\n{values_df}')

    return parameters_df, values_df


def main(args):
    """
    Main function
    """
    parser = build_args_parser(
        signature=__signature__,
        description='Convert concentrations into volumes'
    )

    args = parser.parse_args(args)

    # CREATE LOGGER
    logger = create_logger(parser.prog, args.log)

    (parameters_df,
     concentrations_df) = input_importer(
        args.parameters,
        args.concentrations,
        logger=logger
    )

    # set the multiple of volumes
    if args.robot == 'echo':
        multiple = 2.5
    else:
        multiple = 1

    try:
        volumes_df = concentrations_to_volumes(
            parameters_df,
            concentrations_df,
            args.sample_volume,
            multiple=multiple,
            logger=logger
        )
    except ValueError as e:
        logger.error(f'{e}\nExiting...')
        sys_exit(-1)

    # Save volumes
    save_df(
        df=volumes_df,
        outfile=args.outfile,
        logger=logger
    )


if __name__ == "__main__":
    import sys
    sys_exit(main(sys.argv[1:]))
