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
    # plt_idx = 1
    plates = []
    plate = init_plate(
        start_well=start_well,
        dead_volume=plate_dead_volume,
        dimensions=dimensions,
        well_capacity=well_capacity,
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
                well_capacity=well_capacity,
                vertical=vertical,
                logger=logger
            )

    # Store last plate
    # plates[str(plt_idx)] = deepcopy(plate)
    plates.append(deepcopy(plate))

    return plates


def src_plate_generator(
    dest_plates: List,
    param_dead_volumes: Dict,
    plate_dead_volume: int = DEFAULT_ARGS['SRC_PLT_DEAD_VOLUME'],
    well_capacity: float = DEFAULT_ARGS['SRC_PLT_WELL_CAPACITY'],
    start_well: str = DEFAULT_ARGS['SRC_PLT_START_WELL'],
    opt_well_vol: List = DEFAULT_ARGS['OPTIMIZE_WELL_VOLUMES'],
    vertical: bool = True,
    dimensions: str = DEFAULT_ARGS['SRC_PLT_DIM'],
    lower_volumes: Dict = {},
    upper_volumes: Dict = {},
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
    opt_well_vol: List
        List of parameters to optimize. set to [] if none
    vertical: bool
        - True: plate is filled column by column from top to bottom
        - False: plate is filled row by row from left to right
    dimensions: str
        Dimensions of the plate given as a string with nb_rows
        and nb_cols separated by 'x'
    lower_volumes: Dict
        Minimum volume (nL) of each component in the source plate wells
    upper_volumes: Dict
        Maximum volume (nL) of each component in the source plate wells
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
    logger.debug(f'lower_volumes: {lower_volumes}')
    logger.debug(f'upper_volumes: {upper_volumes}')

    plates = []
    nb_plates = 1
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

    # Split components according to lower_volumes and upper_volumes
    split_comp = {}
    for component in upper_volumes.keys():
        spread = split(
            vol_sums[component],
            upper_volumes[component],
            lower_volumes[component]
        )
        # Remove the original entry if it has been split into multiple parts
        if spread['nb_bins'] > 0:
            del vol_sums[component]
            # Split the volume into the number of bins + remainder
            for i in range(spread['nb_bins']):
                vol_sums[f'{component}_{i+1}'] = upper_volumes[component]
            if spread['remainder'] > 0:
                index = f'{component}_{spread["nb_bins"]+1}'
                vol_sums[index] = spread['remainder']
            split_comp[component] = spread
            split_comp[component]['upper_vol'] = upper_volumes[component]
            split_comp[component]['lower_vol'] = lower_volumes[component]
        elif spread['remainder'] > 0:
            vol_sums[component] = spread['remainder']

    # Extend 'param_dead_volumes' and 'opt_well_vol'
    # with new parameters in 'vol_sums'.
    # For each extended parameter ('Component_1_1', 'Component_1_2', ...),
    # set the deadVolume to the one of
    # the original parameter (e.g. 'Component_1').
    # Not needed to remove the original component, it will never been called
    for param in vol_sums.keys():
        _name = param.split('_')[0]
        if param not in param_dead_volumes:
            param_dead_volumes[param] = param_dead_volumes[_name]
        # Check if the original component
        # is in the list of components to optimize volumes for
        if _name in opt_well_vol:
            # If so, add the new component to the list
            opt_well_vol.append(param)

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

        for _ in range(nb_wells):
            plate.fill_well(param, volume_per_well)
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
                    well_capacity=well_capacity,
                    vertical=vertical,
                    logger=logger
                )

    plates.append(deepcopy(plate))

    for plate in plates:
        logger.debug(f'{plate}')

    return plates, split_comp


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


def dst_plate_split_volumes(
    dest_plates: List,
    split_comp: Dict,
    logger: Logger = getLogger(__name__)
) -> List:
    """
    Split volumes of destination plates

    Parameters
    ----------
    dest_plates: List
        List of destination plates
    split_comp: Dict
        Dict of splitted_comp with
        number of splits and upper/lower volumes
    logger: Logger
        Logger

    Returns
    -------
    dest_plates: List
        List of destination plates with split volumes
    """

    # For each component of each plate,
    # split volumes according to split_comp
    for plate in dest_plates:
        for comp in plate.get_list_of_parameters():
            if comp in split_comp:
                # In each well, rename the original component
                # by one of the splitted components
                # and update the volume
                i = 1
                for well, content in plate.get_wells().items():
                    i = i % split_comp[comp]['nb_bins']
                    spread = split(
                        content.pop(comp),  # removing the original component
                        split_comp[comp]['upper_vol'],
                        split_comp[comp]['lower_vol']
                    )
                    # Split the original component
                    # into the nb of bins + remainder
                    for _ in range(spread['nb_bins']):
                        # Fill the bin with the max volume
                        content[f'{comp}_{i}'] = split_comp[comp]['upper_vol']
                        # Update the index,
                        # it should never be greater than the number of splits
                        i += 1
                    # Fill the remainder with the remaining volume
                    if spread['remainder'] > 0:
                        content[f'{comp}_{i}'] = spread['remainder']
                        i += 1

    return dest_plates


def split(vol, max, min):
    """
    Split a volume into a number of bins and a remainder

    Parameters
    ----------
    vol : float
        Volume to split
    max : float
        Maximum volume per bin
    min : float
        Minimum volume per bin

    Returns
    -------
    Dict
        Number of bins fully filled + remainder
    """
    if vol < min:
        # If the volume is less than the minimum, nothing can be filled.
        return {'nb_bins': 0, 'remainder': vol}
    elif vol < max:
        # If the volume is less than the max, it all goes into the remainder.
        return {'nb_bins': 0, 'remainder': vol}
    else:
        # Calculate the number of full bins and the remainder.
        nb_bins = vol // max
        remainder = vol - nb_bins * max
        # Ensure remainder is not below the minimum unless it's zero.
        if remainder < min and remainder != 0:
            nb_bins -= 1
            remainder += max
        return {'nb_bins': int(nb_bins), 'remainder': remainder}
