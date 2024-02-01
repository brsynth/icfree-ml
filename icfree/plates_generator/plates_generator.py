"""Plates generator module"""
from pandas import DataFrame
from math import (
    ceil,
    floor
)
from typing import (
    Dict,
    List
)
from logging import (
    Logger,
    getLogger
)
from copy import deepcopy

from .args import (
    DEFAULT_ARGS
)
from .plate import Plate


def extract_dead_volumes(
    parameters_df: DataFrame,
    logger: Logger = getLogger(__name__)
) -> DataFrame:
    """
    Extract deadVolumes from cfps_parameters_df and volumes_df

    Parameters
    ----------
    cfps_parameters_df : DataFrame
        Dataframe with cfps_parameters data
    logger: Logger
        Logger, default is getLogger(__name__)

    Returns
    -------
    dead_volumes : Dict
        Dict with deadVolumes data
    """
    logger.debug(f'parameters_df:\n{parameters_df}')

    dead_volumes = dict(
        parameters_df[
            [
                'Component',
                'deadVolume'
            ]
        ].to_numpy()
    )
    dead_volumes['Water'] = 0
    logger.debug(f'deadVolume:{dead_volumes}')
    return dead_volumes


def init_plate(
    starting_well: str = DEFAULT_ARGS['SRC_STARTING_WELL'],
    vertical: bool = True,
    dimensions: str = DEFAULT_ARGS['PLATE_DIMENSIONS'],
    dead_volume: int = DEFAULT_ARGS['SOURCE_PLATE_DEAD_VOLUME'],
    well_capacity: float = DEFAULT_ARGS['SOURCE_PLATE_WELL_CAPACITY'],
    logger: Logger = getLogger(__name__)
) -> Plate:
    """Initialize a Plate object

    Parameters
    ----------
    starting_well : str, optional
        Well to fill first, by default 'A1'
    vertical : bool, optional
        Reading/writing direction, by default True
    dimensions : str, optional
        Dimensions, by default '16x24'
    dead_volume : int, optional
        Plate deadVolume per well, by default 15000
    well_capacity : float, optional
        Capacity of each well, by default 60000
    logger : Logger, optional
        Logger, by default getLogger(__name__)

    Returns
    -------
    Plate
        _description_
    """
    plate = Plate(
        dimensions=dimensions,
        dead_volume=dead_volume,
        well_capacity=well_capacity,
        vertical=vertical,
        logger=logger
    )
    plate.set_current_well(starting_well)
    return plate


def dst_plate_generator(
    volumes: DataFrame,
    plt_dim: str = DEFAULT_ARGS['PLATE_DIMENSIONS'],
    starting_well: str = DEFAULT_ARGS['DEST_STARTING_WELL'],
    plate_well_capacity: float = DEFAULT_ARGS['SOURCE_PLATE_WELL_CAPACITY'],
    vertical: bool = True,
    nplicates: int = DEFAULT_ARGS['NPLICATES'],
    logger: Logger = getLogger(__name__)
) -> List:
    """
    Generate destination plates dataframe

    Parameters
    ----------
    volumes: DataFrame
        DataFrames with samples
    plt_dim: str
        Plate dimensions, by default '16x24'
    starting_well : str
        Starter well to begin filling the 384 well-plate. Defaults to 'A1'
    plate_well_capacity: float
        Plate well capacity, by default 60000
    vertical: bool
        - True: plate is filled column by column from top to bottom
        - False: plate is filled row by row from left to right
    nplicates: int
        Number of plates to generate, by default 1
    logger: Logger
        Logger

    Returns
    -------
    plates: List
        List with destination plates dataframes
    """

    plates = []

    for i in range(nplicates):
        # Generate destination plate(s)
        plates += __dst_plate_generator(
            volumes=volumes,
            plt_dim=plt_dim,
            starting_well=starting_well,
            plate_well_capacity=plate_well_capacity,
            vertical=vertical,
            logger=logger
        )

    if nplicates > 1:
        # Merge plates
        return Plate.merge(plates)

    return plates


def __dst_plate_generator(
    volumes: DataFrame,
    plt_dim: str = DEFAULT_ARGS['PLATE_DIMENSIONS'],
    starting_well: str = DEFAULT_ARGS['DEST_STARTING_WELL'],
    plate_well_capacity: float = DEFAULT_ARGS['SOURCE_PLATE_WELL_CAPACITY'],
    vertical: bool = True,
    logger: Logger = getLogger(__name__)
) -> List:
    """
    Generate destination plates dataframe

    Parameters
    ----------
    volumes: DataFrame
        DataFrames with samples
    plt_dim: str
        Plate dimensions, by default '16x24'
    starting_well : str
        Starter well to begin filling the 384 well-plate. Defaults to 'A1'
    plate_well_capacity: float
        Plate well capacity, by default 60000
    vertical: bool
        - True: plate is filled column by column from top to bottom
        - False: plate is filled row by row from left to right
    logger: Logger
        Logger

    Returns
    -------
    plates: List
        List with destination plates dataframes
    """
    # No deadVolume for destination plates
    plate_dead_volume = 0
    # plt_idx = 1
    plates = []
    plate = init_plate(
        starting_well=starting_well,
        dead_volume=plate_dead_volume,
        dimensions=plt_dim,
        well_capacity=plate_well_capacity,
        vertical=vertical,
        logger=logger
    )

    for index, row in volumes.iterrows():
        # For all parameters
        for param in volumes.columns:
            logger.debug(f'param: {param}, volume: {row[param]}')
            plate.fill_well(
                parameter=param,
                volume=row[param]
            )
        try:
            plate.next_well()
        except ValueError:  # Out of plate
            # Store current plate
            # plates[str(plt_idx)] = deepcopy(plate)
            plates.append(deepcopy(plate))
            # plt_idx += 1
            # Create new plate
            logger.warning('A new destination plate is created')
            plate = Plate(
                dimensions=plate.get_dimensions(),
                dead_volume=plate_dead_volume,
                well_capacity=plate_well_capacity,
                vertical=vertical,
                logger=logger
            )

    # Store last plate
    # plates[str(plt_idx)] = deepcopy(plate)
    plates.append(deepcopy(plate))

    return plates


def src_plate_generator(
    # volumes: DataFrame,
    dest_plates: List,
    param_dead_volumes: Dict,
    plate_dead_volume: int = DEFAULT_ARGS['SOURCE_PLATE_DEAD_VOLUME'],
    plate_well_capacity: float = DEFAULT_ARGS['SOURCE_PLATE_WELL_CAPACITY'],
    starting_well: str = DEFAULT_ARGS['SRC_STARTING_WELL'],
    optimize_well_volumes: List = DEFAULT_ARGS['OPTIMIZE_WELL_VOLUMES'],
    vertical: bool = True,
    plate_dimensions: str = DEFAULT_ARGS['PLATE_DIMENSIONS'],
    logger: Logger = getLogger(__name__)
) -> List:
    """
    Generate source plate dataframe

    Parameters
    ----------
    # volumes: DataFrame
    #     DataFrames with factors
    dest_plates: List
        List of destination plates
    param_dead_volumes: Dict
        deadVolumes of parameters
    plate_dead_volume: int
        Source plate deadVolume. Defaults to 15000 nL
    plate_well_capacity: float
        Source plate well capacity. Defaults to 60000 nL
    starting_well : str
        Starter well to begin filling the 384 well-plate. Defaults to 'A1'
    optimize_well_volumes: List
        List of parameters to optimize. set to [] if none
    vertical: bool
        - True: plate is filled column by column from top to bottom
        - False: plate is filled row by row from left to right
    plate_dimensions: str
        Dimensions of the plate given as a string with nb_rows
        and nb_cols separated by 'x'
    logger: Logger
        Logger

    Returns
    -------
    plate: List
        List with source plate dataframe
    """
    # logger.debug(f'volumes:\n{volumes}')
    logger.debug(f'dest_plates:\n{dest_plates}')
    logger.debug(f'param_dead_volumes: {param_dead_volumes}')
    logger.debug(f'plate_dead_volume: {plate_dead_volume}')
    logger.debug(f'plate_well_capacity: {plate_well_capacity}')
    logger.debug(f'starting_well: {starting_well}')
    logger.debug(f'optimize_well_volumes: {optimize_well_volumes}')
    logger.debug(f'vertical: {vertical}')
    logger.debug(f'plate_dimensions: {plate_dimensions}')

    plates = []
    nb_plates = 1
    plate = init_plate(
        starting_well=starting_well,
        dead_volume=plate_dead_volume,
        dimensions=plate_dimensions,
        well_capacity=plate_well_capacity,
        vertical=vertical,
        logger=logger
    )

    # Sum volumes for each factor
    # vol_sums = volumes.sum(axis=0)
    vol_sums = Plate.get_volumes_summary(dest_plates)
    logger.debug(f'vol_sums: {vol_sums}')

    # Set number of wells needed
    for factor in param_dead_volumes:
        logger.debug(f'factor: {factor}, vol_sums: {vol_sums[factor]}')
        # If volume = 0, then nothing to do
        if vol_sums[factor] == 0:
            logger.warning(
                f'{factor} has a volume = 0. '
                'Please check if is expected or because '
                f'sample volume is too low '
                f'or the stock concentration is too high.'
            )
            continue
        # Take account of deadVolumes
        # Multiple of 2.5 (ECHO)
        dead_volume = max(
            plate.get_dead_volume(),
            param_dead_volumes[factor]
        )
        well_net_capacity = floor(
            (
                plate.get_well_capacity()
                - dead_volume
            ) / 2.5
        ) * 2.5
        logger.debug(f'well_net_capacity: {well_net_capacity}')
        # Volume w/o deadVolumes
        nb_wells = ceil(vol_sums[factor] / well_net_capacity)
        logger.debug(f'nb_wells: {nb_wells}')
        # Raw volume per well
        # Multiple of 2.5 (ECHO)
        net_volume_per_well = ceil(
            vol_sums[factor] / nb_wells / 2.5
        ) * 2.5
        logger.debug(f'net_volume_per_well: {net_volume_per_well}')
        logger.debug(f'optmize_well_volumes: {optimize_well_volumes}')
        # Optimize well volume
        if (
            factor in optimize_well_volumes
            or optimize_well_volumes == ['all']
        ):
            # Net volume per well
            volume_per_well = (
                net_volume_per_well
                + dead_volume
            )
        else:
            volume_per_well = plate.get_well_capacity()
        logger.debug(f'volume_per_well: {volume_per_well}')
        for i in range(nb_wells):
            plate.fill_well(factor, volume_per_well)
            try:
                plate.next_well()
            except ValueError:  # Out of plate
                # Store current plate
                # plates[f'{nb_plates}'] = deepcopy(plate)
                plates.append(deepcopy(plate))
                nb_plates += 1
                # Create new plate
                logger.warning('A new source plate is created')
                plate = Plate(
                    dimensions=plate.get_dimensions(),
                    dead_volume=plate_dead_volume,
                    well_capacity=plate_well_capacity,
                    vertical=vertical,
                    logger=logger
                )

    # plates[f'{nb_plates}'] = deepcopy(plate)
    plates.append(deepcopy(plate))

    # for plate_id, plate in plates.items():
    #     logger.debug(f'PLATE_ID: {plate_id}\n{plate}')
    for plate in plates:
        logger.debug(f'{plate}')

    return plates
