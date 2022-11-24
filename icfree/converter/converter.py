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
                'stockConcentration'
            ]
        ].to_numpy()
    )
    logger.debug(f'stock_concentrations: {stock_concentrations}')

    # Calculate sample volume and stock concentrations ratio for each well
    sample_volume_stock_ratio_df = Series(
        {
            param: sample_volume / stock_concentrations[param]
            for param in stock_concentrations
        }
    )
    logger.debug(
        f'sample_volume_stock_ratio_df: {sample_volume_stock_ratio_df}'
    )

    volumes_df = {}

    # Convert concentrations into volumes
    # and make it a multiple of 2.5 (ECHO specs)
    multiple = 2.5
    volumes_df = round(
        concentrations_df
        * sample_volume_stock_ratio_df
        / multiple, 0
    ) * multiple

    # If a parameter has all values equal to 0,
    # assign 'multiple' value
    for param in volumes_df:
        if volumes_df[param].sum() == 0:
            volumes_df[param] = multiple

    logger.debug(
        f'volumes_df:\n{volumes_df}'
    )

    return volumes_df
