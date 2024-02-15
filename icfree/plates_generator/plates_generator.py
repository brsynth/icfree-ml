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
    dimensions: str,
    start_well: str = DEFAULT_ARGS['SRC_PLT_START_WELL'],
    vertical: bool = True,
    dead_volume: int = DEFAULT_ARGS['SRC_PLT_DEAD_VOLUME'],
    well_capacity: float = DEFAULT_ARGS['SRC_PLT_WELL_CAPACITY'],
    logger: Logger = getLogger(__name__)
) -> Plate:
    """Initialize a Plate object

    Parameters
    ----------
    start_well : str, optional
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
    plate.set_current_well(start_well)
    return plate


def dst_plate_generator(
    volumes: DataFrame,
    dimensions: str = DEFAULT_ARGS['DST_PLT_DIM'],
    start_well: str = DEFAULT_ARGS['DST_PLT_START_WELL'],
    well_capacity: float = DEFAULT_ARGS['DST_PLT_WELL_CAPACITY'],
    plate_dead_volume: int = DEFAULT_ARGS['DST_PLT_DEAD_VOLUME'],
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
    dimensions: str
        Plate dimensions, by default '16x24'
    start_well : str
        Starter well to begin filling the 384 well-plate. Defaults to 'A1'
    well_capacity: float
        Plate well capacity, by default 60000
    plate_dead_volume: int
        Plate deadVolume, by default 15000
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
            dimensions=dimensions,
            start_well=start_well,
            well_capacity=well_capacity,
            plate_dead_volume=plate_dead_volume,
            vertical=vertical,
            logger=logger
        )

    if nplicates > 1:
        # Merge plates
        return Plate.merge(plates)

    return plates


def __dst_plate_generator(
    volumes: DataFrame,
    dimensions: str = DEFAULT_ARGS['DST_PLT_DIM'],
    start_well: str = DEFAULT_ARGS['DST_PLT_START_WELL'],
    well_capacity: float = DEFAULT_ARGS['DST_PLT_WELL_CAPACITY'],
    plate_dead_volume: int = DEFAULT_ARGS['DST_PLT_DEAD_VOLUME'],
    vertical: bool = True,
    logger: Logger = getLogger(__name__)
) -> List:
    """
    Generate destination plates dataframe

    Parameters
    ----------
    volumes: DataFrame
        DataFrames with samples
    dimensions: str
        Plate dimensions, by default '16x24'
    start_well : str
        Starter well to begin filling the 384 well-plate. Defaults to 'A1'
    well_capacity: float
        Plate well capacity, by default 60000
    plate_dead_volume: int
        Plate deadVolume, by default 15000
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
    plates = []
    plate = init_plate(
        start_well=start_well,
        dead_volume=plate_dead_volume,
        dimensions=dimensions,
        well_capacity=well_capacity,
        vertical=vertical,
        logger=logger
    )

    for _, row in volumes.iterrows():
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
            plates.append(deepcopy(plate))
            # Create new plate
            logger.warning('A new destination plate is created')
            plate = Plate(
                dimensions=plate.get_dimensions(),
                dead_volume=plate_dead_volume,
                well_capacity=well_capacity,
                vertical=vertical,
                logger=logger
            )

    plates.append(deepcopy(plate))

    return plates


def src_plate_generator(
    dest_plates: List,
    param_dead_volumes: Dict,
    plate_dead_volume: int = DEFAULT_ARGS['SRC_PLT_DEAD_VOLUME'],
    well_capacity: float = DEFAULT_ARGS['SRC_PLT_WELL_CAPACITY'],
    start_well: str = DEFAULT_ARGS['SRC_PLT_START_WELL'],
    new_col_comp: str = DEFAULT_ARGS['NEW_COL_COMP'],
    opt_well_vol: List = DEFAULT_ARGS['OPTIMIZE_WELL_VOLUMES'],
    vertical: bool = True,
    dimensions: str = DEFAULT_ARGS['SRC_PLT_DIM'],
    logger: Logger = getLogger(__name__)
) -> List:
    """
    Generate source plate dataframe

    Parameters
    ----------
    dest_plates: List
        List of destination plates
    param_dead_volumes: Dict
        deadVolumes of parameters
    plate_dead_volume: int
        Source plate deadVolume. Defaults to 15000 nL
    well_capacity: float
        Source plate well capacity. Defaults to 60000 nL
    start_well : str
        Starter well to begin filling the 384 well-plate. Defaults to 'A1'
    new_col_comp: str
        Start component at a new column. Defaults to None
    opt_well_vol: List
        List of parameters to optimize. set to [] if none
    vertical: bool
        - True: plate is filled column by column from top to bottom
        - False: plate is filled row by row from left to right
    dimensions: str
        Dimensions of the plate given as a string with nb_rows
        and nb_cols separated by 'x'
    logger: Logger
        Logger

    Returns
    -------
    plate: List
        List with source plate dataframe
    """
    logger.debug(f'dest_plates:\n{dest_plates}')
    logger.debug(f'param_dead_volumes: {param_dead_volumes}')
    logger.debug(f'plate_dead_volume: {plate_dead_volume}')
    logger.debug(f'plate_well_capacity: {well_capacity}')
    logger.debug(f'starting_well: {start_well}')
    logger.debug(f'optimize_well_volumes: {opt_well_vol}')
    logger.debug(f'vertical: {vertical}')
    logger.debug(f'plate_dimensions: {dimensions}')
    logger.debug(f'new_col_comp: {new_col_comp}')

    plates = []
    plate = init_plate(
        start_well=start_well,
        dead_volume=plate_dead_volume,
        dimensions=dimensions,
        well_capacity=well_capacity,
        vertical=vertical,
        logger=logger
    )

    # Sum volumes for each factor
    vol_sums = Plate.get_volumes_summary(dest_plates)
    logger.debug(f'vol_sums: {vol_sums}')

    if new_col_comp == []:
        new_col_comp = vol_sums.keys()

    # Set number of wells needed
    for param, volume in vol_sums.items():
        logger.debug(f'param: {param}, volume: {volume}')
        # If volume = 0, then nothing to do
        if volume == 0:
            logger.warning(
                f'{param} has a volume = 0. '
                'Please check if is expected or because '
                f'sample volume is too low '
                f'or the stock concentration is too high.'
            )
            continue
        nb_wells, volume_per_well = nb_wells_needed(
            param=param,
            volume=volume,
            param_dead_volume=param_dead_volumes[param],
            opt_well_vol=opt_well_vol,
            plate=plate,
            logger=logger
        )

        try:
            # Start at a new column if requested
            if new_col_comp and param in new_col_comp:
                plate.next_col()

            # Fill wells
            for _ in range(nb_wells):
                plate.fill_well(param, volume_per_well)
                plate.next_well()

        except ValueError:  # Out of plate
            # Store current plate
            plates.append(deepcopy(plate))
            # Create new plate
            logger.warning('A new source plate is created')
            plate = Plate(
                dimensions=plate.get_dimensions(),
                dead_volume=plate_dead_volume,
                well_capacity=well_capacity,
                vertical=vertical,
                logger=logger
            )

    plates.append(deepcopy(plate))

    for plate in plates:
        logger.debug(f'{plate}')

    return plates


def nb_wells_needed(
    param: str,
    volume: float,
    param_dead_volume: float,
    opt_well_vol: List,
    plate: Plate,
    logger: Logger = getLogger(__name__)
) -> int:
    """
    Calculate the number of wells needed to store the volume

    Parameters
    ----------
    param : str
        Parameter name
    volume : float
        Volume to store
    param_dead_volume: float
        DeadVolume of parameter
    opt_well_vol: List
        List of parameters to optimize. set to [] if none
    plate : Plate
        Plate to store the volume
    logger : Logger
        Logger

    Returns
    -------
    nb_wells : int
        Number of wells needed
    volume_per_well : float
        Volume per well
    """
    logger.debug(f'param: {param}, volume: {volume}')
    logger.debug(f'plate: {plate}')

    # Take account of deadVolumes
    # Multiple of 2.5 (ECHO)
    dead_volume = max(
        plate.get_dead_volume(),
        param_dead_volume
    )
    well_net_capacity = floor(
        (
            plate.get_well_capacity()
            - dead_volume
        ) / 2.5
    ) * 2.5
    logger.debug(f'well_net_capacity: {well_net_capacity}')
    # Volume w/o deadVolumes
    nb_wells = ceil(volume / well_net_capacity)
    logger.debug(f'nb_wells: {nb_wells}')
    # Raw volume per well
    # Multiple of 2.5 (ECHO)
    net_volume_per_well = ceil(
        volume / nb_wells / 2.5
    ) * 2.5
    logger.debug(f'net_volume_per_well: {net_volume_per_well}')
    logger.debug(f'optmize_well_volumes: {opt_well_vol}')
    # Optimize well volume
    if (
        param in opt_well_vol
        or opt_well_vol == ['all']
    ):
        # Net volume per well
        volume_per_well = (
            net_volume_per_well
            + dead_volume
        )
    else:
        volume_per_well = plate.get_well_capacity()

    return nb_wells, volume_per_well
