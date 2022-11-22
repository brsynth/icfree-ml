#!/usr/bin/env python
# coding: utf-8
from pandas import (
    DataFrame,
    Series,
)
from typing import Dict
from logging import (
    Logger,
    getLogger
)

from .args import (
    DEFAULT_ARGS
)


def concentrations_to_volumes(
    cfps_parameters_df: DataFrame,
    concentrations_df: Dict,
    sample_volume: int = DEFAULT_ARGS['SAMPLE_VOLUME'],
    logger: Logger = getLogger(__name__)
):
    """
    Convert concentrations dataframes into volumes dataframes.
    Generate warning report of volumes outside the transfer range of Echo.
    Generate volumes summary for each volumes DataFrame.

    Parameters
    ----------
    cfps_parameters_df : DataFrame
        Dataframe with cfps_parameters data
    concentrations_df : Dict
        Dataframes with concentrations data
    sample_volume: int
        Final sample volume in each well. Defaults to 10000 nL

    Returns
    -------
    volumes_df : Dict
        DataFrames with converted volumes
        For 'normalizer' key, 0 is assigned to the GOI-DNA column
    volumes_summary: DataFrame
        DataFrame with total volume for each factor in
        initial/normalizer/autofluorescnce_volumes_df
    warning_volumes_report: DataFrame
        Report of volumes outside the transfer range of Echo
    logger: Logger
        Logger
    """
    logger.info('Converting concentrations to volumes...')
    # Print out parameters
    logger.debug(f'cfps parameters:\n{cfps_parameters_df}')
    logger.debug(f'concentrations:\n{concentrations_df}')
    logger.debug(f'Sample volume: {sample_volume}')

    # Exract stock concentrations from cfps_parameters_df
    stock_concentrations = dict(
        cfps_parameters_df[
            [
                'Parameter',
                'Stock concentration'
            ]
        ].to_numpy()
    )
    logger.debug(f'stock_concentrations: {stock_concentrations}')
    # stock_concentrations_df = fromiter(
    #     stock_concentrations_dict.values(),
    #     dtype=float
    # )
    # logger.debug(f'Stock concentrations: {stock_concentrations_df}')

    # Exract dead plate volumes from cfps_parameters_df
    param_dead_volumes = dict(
        cfps_parameters_df[
            [
                'Parameter',
                'deadVolume'
            ]
        ].to_numpy()
    )
    param_dead_volumes['Water'] = 0
    logger.debug(f'Parameter deadVolume:{param_dead_volumes}')

    # Calculate sample volume and stock concentrations ratio for each well
    sample_volume_stock_ratio = {
        param: sample_volume / stock_concentrations[param]
        for param in stock_concentrations
    }
    # sample_volume_stock_ratio = \
    #     sample_volume / stock_concentrations_df
    # logger.debug(f'sample_volume_stock_ratio: {sample_volume_stock_ratio}')
    sample_volume_stock_ratio_df = Series(
        sample_volume_stock_ratio
    )
    logger.debug(
        f'sample_volume_stock_ratio_df: {sample_volume_stock_ratio_df}'
    )
    # # Fit columns order to concentrations
    # first_key = list(concentrations_df.keys())[0]
    # if sample_volume_stock_ratio_df.size != \
    #    concentrations_df.columns.size:
    #     msg = (
    #         'It seems that the number of parameters is different '
    #         'from the number of stock concentrations.'
    #     )
    #     raise ValueError(msg)
    # sample_volume_stock_ratio_df = sample_volume_stock_ratio_df[
    #     concentrations_df.columns
    # ]
    # logger.debug(
    #     f'sample_volume_stock_ratio_df: {sample_volume_stock_ratio_df}'
    # )

    volumes_df = {}
    # volumes_summary = {}
    # warning_volumes_report = {
    #     'Min Report': {},
    #     'Max Report': {}
    # }

    # Convert concentrations into volumes
    # and make it a multiple of 2.5 (ECHO specs)
    volumes_df = round(
        concentrations_df
        * sample_volume_stock_ratio_df
        / 2.5, 1
    ) * 2.5

    # # Add Water column
    # volumes_df['Water'] = sample_volume - volumes_df.sum(axis=1)

    logger.debug(
        f'volumes_df:\n{volumes_df}'
    )

    #     # Check volumes
    #     warning_volumes_report = check_volumes(
    #             volumes_df[volumes_name],
    #             lower_bound=10,
    #             upper_bound=1000,
    #             warning_volumes=warning_volumes_report,
    #             logger=logger
    #         )
    #     logger.debug(f'{volumes_name} volumes:\n{volumes_df[volumes_name]}')

    # # Convert Warning Report Dict to Dataframe
    # warning_volumes_report = DataFrame.from_dict(warning_volumes_report)

    return volumes_df
