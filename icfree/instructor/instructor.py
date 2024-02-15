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
    split_components: Dict = {},
    robot: str = DEFAULT_ARGS['ROBOT'],
    src_plate_type: str = DEFAULT_ARGS['SRC_PLATE_TYPE'],
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
    split_components: Dict
        Volume bounds for picking components in the source plates
    robot: str
        Robot name
    src_plate_type: str
        Source plate type (for ECHO only)

    Returns
    -------
    instructions: Dict
        Dict with instructions dataframes
    """
    return globals()[f'{robot.lower()}_instructions_generator'](
        source_plates,
        dest_plates,
        split_components,
        src_plate_type,
        logger=logger
    )


def echo_instructions_generator(
    source_plates: Dict,
    dest_plates: Dict,
    split_components: Dict = {},
    src_plate_type: str = DEFAULT_ARGS['SRC_PLATE_TYPE'],
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
    split_components: Dict
        Volume bounds for picking components in the source plates
    src_plate_type: str
        Source plate type

    Returns
    -------
    echo_instructions: Dict
        Dict with echo instructions dataframes
    """
    logger.debug('Generating Echo® instructions')
    logger.debug(f'Source plates: {source_plates}')
    logger.debug(f'Destination plates: {dest_plates}')
    logger.debug(f'Split components: {split_components}')
    logger.debug(f'Source plate type: {src_plate_type}')

    # Reindex plates by factors ID
    src_plates_by_factor = reindex_plates_by_factor(source_plates, logger)
    dst_plates_by_factor = reindex_plates_by_factor(dest_plates, logger)

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

    # Get source plate type
    def_src_plate_type = DEFAULT_ARGS['SRC_PLATE_TYPE']
    if len(src_plate_type) % 2 == 1:
        def_src_plate_type = src_plate_type.pop(0)
    # Put src_plate_type in a dict
    src_plate_type_dict = {}
    for i in range(0, len(src_plate_type), 2):
        src_plate_type_dict[src_plate_type[i]] = src_plate_type[i+1]
    # Set plate type for each parameter
    for factor in src_plates_by_factor:
        if factor in src_plate_type_dict:
            src_plates_by_factor[factor]['plt_type'] = \
                src_plate_type_dict[factor]
        else:
            src_plates_by_factor[factor]['plt_type'] = def_src_plate_type

    # Generate instructions
    for factor in dst_plates_by_factor:
        src_plt_id = src_plates_by_factor[factor]['plt_id']
        src_plt_type = src_plates_by_factor[factor]['plt_type']
        src_well_ids = \
            f'{{{";".join(src_plates_by_factor[factor]["wells"].keys())}}}'
        dst_plt_id = dst_plates_by_factor[factor]['plt_id']
        for dst_well in dst_plates_by_factor[factor]['wells'].items():
            dst_well_id = dst_well[0]
            dst_well_vol = dst_well[1]
            # If the volume to drop in the destination well
            # is greater than the upper bound (given by ),
            # split the volume in several instructions
            if (
                factor in split_components and
                dst_well_vol > split_components[factor]['upper']
            ):
                logger.debug(
                    f'Volume to drop in {dst_well_id} > '
                    f'{split_components[factor]["upper"]} nL'
                )
                # Get the number of times the volume has to be split
                n_splits = int(
                    dst_well_vol / split_components[factor]['upper']
                )
                # Get the volume to drop in the last instruction
                last_vol = dst_well_vol % split_components[factor]['upper']
                # Get the volume to drop in each instruction
                split_vol = split_components[factor]['upper']
                for _ in range(n_splits):
                    instructions.loc[len(instructions.index)] = [
                        f'Source[{src_plt_id}]', src_plt_type, src_well_ids,
                        f'Destination[{dst_plt_id}]', dst_well_id, split_vol,
                        factor
                    ]
                # Add the last instruction
                # If the last volume is less than the lower bound,
                # add it to the last instruction
                if last_vol < split_components[factor]['lower']:
                    split_vol += last_vol
                    instructions.loc[len(instructions.index)-1] = [
                        f'Source[{src_plt_id}]', src_plt_type, src_well_ids,
                        f'Destination[{dst_plt_id}]', dst_well_id, split_vol,
                        factor
                    ]
                else:
                    instructions.loc[len(instructions.index)] = [
                        f'Source[{src_plt_id}]', src_plt_type, src_well_ids,
                        f'Destination[{dst_plt_id}]', dst_well_id, last_vol,
                        factor
                    ]
            else:
                instructions.loc[len(instructions.index)] = [
                    f'Source[{src_plt_id}]', src_plt_type, src_well_ids,
                    f'Destination[{dst_plt_id}]', dst_well_id, dst_well_vol,
                    factor
                ]

    logger.debug(f'INSTRUCTIONS:\n{instructions}')

    return instructions


def reindex_plates_by_factor(
    plates: Dict,
    logger: Logger = getLogger(__name__)
) -> Dict:
    """
    Reindex plates by factor ID

    Parameters
    ----------
    plates: Dict
        Plates to reindex

    Returns
    -------
    plates_by_factor: Dict
        Plates reindexed by factor ID
    """

    plates_by_factor = {}

    for i, src_plt in enumerate(plates.values()):
        for well_id, well in src_plt.get_wells().items():
            for factor in well.keys():
                if factor not in plates_by_factor:
                    plates_by_factor[factor] = {
                        'plt_id': i+1,
                        'wells': {}
                    }
                plates_by_factor[factor]['wells'][well_id] = well[factor]

    logger.debug(f'Plates by factor: {plates_by_factor}')

    return plates_by_factor
