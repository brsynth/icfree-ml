#!/usr/bin/env python
# coding: utf-8
from pandas import DataFrame
from typing import Dict
from logging import (
    Logger,
    getLogger
)

from .args import (
    DEFAULT_ARGS
)

# def concentrations_to_volumes(
#     cfps_parameters_df: DataFrame,
#     concentrations_df: Dict,
#     sample_volume: int = DEFAULT_ARGS['SAMPLE_VOLUME'],
#     logger: Logger = getLogger(__name__)
# ):
#     """
#     Convert concentrations dataframes into volumes dataframes.
#     Generate warning report of volumes outside the transfer range of Echo.
#     Generate volumes summary for each volumes DataFrame.

#     Parameters
#     ----------
#     cfps_parameters_df : DataFrame
#         Dataframe with cfps_parameters data
#     concentrations_df : Dict
#         Dataframes with concentrations data
#     sample_volume: int
#         Final sample volume in each well. Defaults to 10000 nL

#     Returns
#     -------
#     volumes_df : Dict
#         DataFrames with converted volumes
#         For 'normalizer' key, 0 is assigned to the GOI-DNA column
#     volumes_summary: DataFrame
#         DataFrame with total volume for each factor in
#         initial/normalizer/autofluorescnce_volumes_df
#     warning_volumes_report: DataFrame
#         Report of volumes outside the transfer range of Echo
#     logger: Logger
#         Logger
#     """
#     logger.info('Converting concentrations to volumes...')
#     # Print out parameters
#     logger.debug(f'cfps parameters:\n{cfps_parameters_df}')
#     logger.debug(f'Sample volume: {sample_volume}')

#     # Exract stock concentrations from cfps_parameters_df
#     stock_concentrations = dict(
#         cfps_parameters_df[
#             [
#                 'Parameter',
#                 'Stock concentration'
#             ]
#         ].to_numpy()
#     )
#     logger.debug(f'stock_concentrations: {stock_concentrations}')
#     # stock_concentrations_df = fromiter(
#     #     stock_concentrations_dict.values(),
#     #     dtype=float
#     # )
#     # logger.debug(f'Stock concentrations: {stock_concentrations_df}')

#     # Exract dead plate volumes from cfps_parameters_df
#     param_dead_volumes = dict(
#         cfps_parameters_df[
#             [
#                 'Parameter',
#                 'Parameter deadVolume'
#             ]
#         ].to_numpy()
#     )
#     param_dead_volumes['Water'] = 0
#     logger.debug(f'Parameter deadVolume:{param_dead_volumes}')

#     # Calculate sample volume and stock concentrations ratio for each well
#     sample_volume_stock_ratio = {
#         param: sample_volume / stock_concentrations[param]
#         for param in stock_concentrations
#     }
#     # sample_volume_stock_ratio = \
#     #     sample_volume / stock_concentrations_df
#     logger.debug(f'sample_volume_stock_ratio: {sample_volume_stock_ratio}')
#     sample_volume_stock_ratio_df = Series(
#         sample_volume_stock_ratio
#     )
#     logger.debug(
#         f'sample_volume_stock_ratio_df: {sample_volume_stock_ratio_df}'
#     )
#     # Fit columns order to concentrations
#     first_key = list(concentrations_df.keys())[0]
#     if sample_volume_stock_ratio_df.size != \
#        concentrations_df[first_key].columns.size:
#         msg = (
#             'It seems that the number of parameters is different '
#             'from the number of stock concentrations.'
#         )
#         raise ValueError(msg)
#     sample_volume_stock_ratio_df = sample_volume_stock_ratio_df[
#         concentrations_df[first_key].columns
#     ]
#     logger.debug(
#         f'sample_volume_stock_ratio_df: {sample_volume_stock_ratio_df}'
#     )

#     volumes_df = {}
#     # volumes_summary = {}
#     warning_volumes_report = {
#         'Min Report': {},
#         'Max Report': {}
#     }

#     for volumes_name in concentrations_df.keys():
#         # Print out parameters
#         logger.debug(f'{volumes_name} concentrations:\n'
#                      f'{concentrations_df[volumes_name]}')

#         # Convert concentrations into volumes
#         # and make it a multiple of 2.5 (ECHO specs)
#         volumes_df[volumes_name] = round(
#             multiply(
#                 concentrations_df[volumes_name],
#                 sample_volume_stock_ratio_df
#             ) / 2.5, 0
#         ) * 2.5
#         logger.debug(
#             f'concentrations_df[{volumes_name}]:\n'
#             f'{concentrations_df[volumes_name]}'
#         )
#         logger.debug(f'sample_volume_stock_ratio: \
#           {sample_volume_stock_ratio}')
#         logger.debug(f'{volumes_name} volumes:\n'
#                      f'{volumes_df[volumes_name]}')

#         # Add Water column
#         volumes_df[volumes_name]['Water'] = \
#             sample_volume - volumes_df[volumes_name].sum(axis=1)
#         # Check volumes
#         warning_volumes_report = check_volumes(
#                 volumes_df[volumes_name],
#                 lower_bound=10,
#                 upper_bound=1000,
#                 warning_volumes=warning_volumes_report,
#                 logger=logger
#             )
#         logger.debug(f'{volumes_name} volumes:\n{volumes_df[volumes_name]}')

#     # Convert Warning Report Dict to Dataframe
#     warning_volumes_report = DataFrame.from_dict(warning_volumes_report)

#     return (volumes_df,
#             param_dead_volumes,
#             warning_volumes_report)


def check_volumes(
    plate: Dict,
    lower_bound: float,
    upper_bound: float,
    logger: Logger = getLogger(__name__)
) -> DataFrame:
    """
    Checks if volumes are between lower and upper bounds.
    Checks if a factor stock concentration is low (Vwater < 0).

    Parameters
    ----------
    volumes_df : DataFrame
        Volumes to check
    lower_bound: float
        Lower bound
    upper_bound: float
        Upper bound
    logger: Logger
        Logger

    Returns
    -------
    warning_volumes : DataFrame
        Volumes outside of bounds
    """
    # Put plate volumes into a DataFrame
    volumes_df = DataFrame.from_dict(plate['Wells'], orient='index')
    warning_volumes = dict()
    logger.debug(volumes_df)
    # WARNING: < 10 nL (ECHO min volume transfer limit) --> dilute stock
    for factor in volumes_df.columns:
        logger.debug(f'Checking {factor} volumes...')
        # Check lower bound
        for vol in volumes_df[factor].sort_values():
            # Pass all 0 since it is a correct value
            if vol != 0:
                # Exit the loop at the first non-0 value
                break
        # Warn if the value is < 10 nL
        if 0 < vol < lower_bound:
            logger.debug(f'{factor} volume is < {lower_bound} nL')
            # if factor not in warning_volumes:
            warning_volumes[factor] = {
                'min': vol,
                'max': '',
            }
            # else:
            #     warning_volumes[factor]['min'] = vol
            logger.warning(
                f'One volume of {factor} = {vol} nL (< {lower_bound} nL). '
                'Stock have to be more diluted.'
            )
        # Check upper bound
        # Warn if the value is > 1000 nL
        v_max = volumes_df[factor].max()
        if v_max > upper_bound:
            logger.debug(f'{factor} volume is > {upper_bound} nL')
            # if factor not in warning_volumes:
            warning_volumes[factor] = {
                'min': '',
                'max': v_max,
            }
            # else:
            #     warning_volumes[factor]['max'] = v_max
            logger.warning(
                f'One volume of {factor} = {v_max} nL (> {upper_bound} nL). '
                'Stock have to be more concentrated or pipetting '
                'has to be done manually.'
            )

    # Check if a factor stock is not concentrated enough,
    # WARNING: Vwater < 0 --> increase stock concentration
    if 'Water' in volumes_df:
        vol_min_w = volumes_df['Water'].min()
        if vol_min_w < 0:
            # Get factor with max value in each line (sample) where Vwater < 0
            under_conc_fac = list(set(
                DataFrame(
                    volumes_df.drop(
                        volumes_df[volumes_df['Water'] >= 0].index
                    ).astype('float64'),
                    dtype='float64'
                ).idxmax(axis=1)
            ))
            factor = 'Water'
            # if factor not in warning_volumes:
            warning_volumes[factor] = {
                'min': vol_min_w,
                'max': '',
            }
            # else:
            #     warning_volumes[factor]['min'] = vol_min_w
            for factor in under_conc_fac:
                logger.warning(
                    f'*** {factor}\nFactor seems to be under-concentrated '
                    '(volume of added water < 0).\n'
                )

    # Convert Warning Report Dict to Dataframe
    warning_volumes_df = DataFrame(
        columns=['Parameter', 'Min', 'Max']
    )
    for param in warning_volumes:
        warning_volumes_df.loc[len(warning_volumes_df.index)] = [
            param,
            warning_volumes[param]['min'],
            warning_volumes[param]['max']
        ]

    return warning_volumes_df


def instructions_generator(
    source_plates: Dict,
    dest_plates: Dict,
    robot: str = DEFAULT_ARGS['ROBOT'],
    logger: Logger = getLogger(__name__)
) -> DataFrame:
    """
    Generate and dispatch instructions on multiple plates

    Parameters
    ----------
    source_plates: Dict
        Source plates distribution
    dest_plates: Dict
        Destination plates distribution
    robot: str
        Robot name

    Returns
    -------
    instructions: Dict
        Dict with instructions dataframes
    """
    return globals()[f'{robot.lower()}_instructions_generator'](
        source_plates,
        dest_plates,
        logger=logger
    )


def echo_instructions_generator(
    source_plates: Dict,
    dest_plates: Dict,
    logger: Logger = getLogger(__name__)
) -> DataFrame:
    """
    Generate and dispatch Echo® instructions on multiple plates

    Parameters
    ----------
    source_plates: Dict
        Source plates distribution
    dest_plates: Dict
        Destination plates distribution

    Returns
    -------
    echo_instructions: Dict
        Dict with echo instructions dataframes
    """
    logger.debug('Generating Echo® instructions')
    logger.debug('Source plates: %s', source_plates)
    logger.debug('Destination plates: %s', dest_plates)

    # Reindex plates by factors ID
    # SRC
    src_plates_by_factor = {}
    for i, src_plt in enumerate(source_plates.values()):
        for well_id, well in src_plt.get_wells().items():
            for factor in well.keys():
                if factor not in src_plates_by_factor:
                    src_plates_by_factor[factor] = {
                        'wells': list(),
                        'volumes': list()
                    }
                src_plates_by_factor[factor]['plt_id'] = i+1
                src_plates_by_factor[factor]['wells'].append(well_id)
                src_plates_by_factor[factor]['volumes'].append(well[factor])
    # DST
    dst_plates_by_factor = {}
    for i, dst_plt in enumerate(dest_plates.values()):
        for well_id, well in dst_plt.get_wells().items():
            for factor, vol in well.items():
                if factor not in dst_plates_by_factor:
                    dst_plates_by_factor[factor] = {
                        'wells': dict()
                    }
                dst_plates_by_factor[factor]['plt_id'] = i+1
                dst_plates_by_factor[factor]['wells'][well_id] = vol

    # Build the instructions
    instructions = DataFrame(
        columns=[
            'Source Plate Name',
            'Source Plate Type',
            'Source Well',
            'Destination Plate Name',
            'Destination Well',
            'Transfer Volume',
            'Sample ID'
        ]
    )
    for factor in dst_plates_by_factor:
        src_plt_id = src_plates_by_factor[factor]['plt_id']
        src_wells = src_plates_by_factor[factor]['wells']
        if len(src_wells) > 1:
            src_well_ids = \
                f'{{{"-".join(src_plates_by_factor[factor]["wells"])}}}'
        else:
            src_well_ids = src_plates_by_factor[factor]['wells'][0]
        dst_plt_id = dst_plates_by_factor[factor]['plt_id']
        for dst_well in dst_plates_by_factor[factor]['wells'].items():
            dst_well_id = dst_well[0]
            dst_well_vol = dst_well[1]
            instructions.loc[len(instructions.index)] = [
                f'Source[{src_plt_id}]', '384PP_AQ_GP3', src_well_ids,
                f'Destination[{dst_plt_id}]', dst_well_id, dst_well_vol,
                factor
            ]

    logger.debug(f'INSTRUCTIONS:\n{instructions}')

    return instructions
