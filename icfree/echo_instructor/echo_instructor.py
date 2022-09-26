#!/usr/bin/env python
# coding: utf-8

from os import (
    path as os_path,
    mkdir as os_mkdir
)
from csv import (
    writer as csv_writer
)
from numpy import (
    multiply,
    array_split
)
from pandas import (
    read_csv,
    concat,
    DataFrame,
    Series
)
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


def input_importer(
    cfps_parameters,
    initial_concentrations,
    normalizer_concentrations,
    autofluorescence_concentrations,
    logger: Logger = getLogger(__name__)
):
    """
    Create concentrations dataframes from tsv files

    Parameters
    ----------
    cfps_parameters : tsv file
        TSV of cfps parameters, status, maximum and stock concentrations
    initial_concentrations : tsv file
        Dataset with concentrations values
    normalizer_concentrations : tsv file
        Copy of initial_concentrations. 0 is assigned to the GOI-DNA column
    autofluorescence_concentrations : tsv file
        Copy of normalizer_concentrations. 0 is assigned to the GFP-DNA column

    Returns
    -------
    cfps_parameters_df : DataFrame
        Dataframe with cfps_parameters data
    initial_volumes_df : DataFrame
        Dataframe with initial_concentrations data
    normalizer_volumes_df : DataFrame
        Dataframe with normalizer_concentrations data
    autofluorescence_volumes_df : DataFrame
        Dataframe with autofluorescence_concentrations data
    """
    cfps_parameters_df = read_csv(
        cfps_parameters,
        sep='\t')
    logger.debug(f'cfps_parameters_df: {cfps_parameters_df}')

    concentrations_df = {}
    concentrations_df['initial'] = read_csv(
        initial_concentrations,
        sep='\t')
    logger.debug(
        f'concentrations_df["initial"]: {concentrations_df["initial"]}'
    )

    concentrations_df['normalizer'] = read_csv(
        normalizer_concentrations,
        sep='\t')
    logger.debug(
        f'concentrations_df["normalizer"]: {concentrations_df["normalizer"]}'
    )

    concentrations_df['autofluorescence'] = read_csv(
        autofluorescence_concentrations,
        sep='\t')
    logger.debug(
        'concentrations_df["autofluorescence"]: '
        f'{concentrations_df["autofluorescence"]}'
    )

    return (cfps_parameters_df,
            concentrations_df)


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
        Dataframes with initial/normalizer/autofluorescence concentrations data
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
                'Parameter dead volume'
            ]
        ].to_numpy()
    )
    param_dead_volumes['Water'] = 0
    logger.debug(f'Parameter dead volume:{param_dead_volumes}')

    # Calculate sample volume and stock concentrations ratio for each well
    sample_volume_stock_ratio = {
        param: sample_volume / stock_concentrations[param]
        for param in stock_concentrations
    }
    # sample_volume_stock_ratio = \
    #     sample_volume / stock_concentrations_df
    logger.debug(f'sample_volume_stock_ratio: {sample_volume_stock_ratio}')
    sample_volume_stock_ratio_df = Series(
        sample_volume_stock_ratio
    )
    logger.debug(
        f'sample_volume_stock_ratio_df: {sample_volume_stock_ratio_df}'
    )
    # Fit columns order to concentrations
    first_key = list(concentrations_df.keys())[0]
    if sample_volume_stock_ratio_df.size != \
       concentrations_df[first_key].columns.size:
        msg = (
            'It seems that the number of parameters is different '
            'from the number of stock concentrations.'
        )
        raise ValueError(msg)
    sample_volume_stock_ratio_df = sample_volume_stock_ratio_df[
        concentrations_df[first_key].columns
    ]
    logger.debug(
        f'sample_volume_stock_ratio_df: {sample_volume_stock_ratio_df}'
    )

    volumes_df = {}
    # volumes_summary = {}
    warning_volumes_report = {
        'Min Report': {},
        'Max Report': {}
    }

    for volumes_name in concentrations_df.keys():
        # Print out parameters
        logger.debug(f'{volumes_name} concentrations:\n'
                     f'{concentrations_df[volumes_name]}')

        # Convert concentrations into volumes
        # and make it a multiple of 2.5 (ECHO specs)
        volumes_df[volumes_name] = round(
            multiply(
                concentrations_df[volumes_name],
                sample_volume_stock_ratio_df
            ) / 2.5, 0
        ) * 2.5
        logger.debug(
            f'concentrations_df[{volumes_name}]:\n'
            f'{concentrations_df[volumes_name]}'
        )
        logger.debug(f'sample_volume_stock_ratio: {sample_volume_stock_ratio}')
        logger.debug(f'{volumes_name} volumes:\n'
                     f'{volumes_df[volumes_name]}')

        # Add Water column
        volumes_df[volumes_name]['Water'] = \
            sample_volume - volumes_df[volumes_name].sum(axis=1)
        # Check volumes
        warning_volumes_report = check_volumes(
                volumes_df[volumes_name],
                lower_bound=10,
                upper_bound=1000,
                warning_volumes=warning_volumes_report,
                logger=logger
            )
        logger.debug(f'{volumes_name} volumes:\n{volumes_df[volumes_name]}')

    # Convert Warning Report Dict to Dataframe
    warning_volumes_report = DataFrame.from_dict(warning_volumes_report)

    return (volumes_df,
            param_dead_volumes,
            warning_volumes_report)


def check_volumes(
    volumes_df: DataFrame,
    lower_bound: float,
    upper_bound: float,
    warning_volumes: Dict,
    logger: Logger = getLogger(__name__)
) -> Dict:
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
    warning_volumes : Dict
        Dictionnary with volumes outside of bounds
    """
    # WARNING: < 10 nL (ECHO min volume transfer limit) --> dilute stock
    for factor in volumes_df.columns:
        # Check lower bound
        for vol in volumes_df[factor].sort_values():
            # Pass all 0 since it is a correct value
            if vol != 0:
                # Exit the loop at the first non-0 value
                break
        # Warn if the value is < 10 nL
        if 0 < vol < lower_bound:
            warning_volumes['Min Report'][factor] = vol
            logger.warning(
                f'One volume of {factor} = {vol} nL (< 10 nL). '
                'Stock have to be more diluted.'
            )
        # Check upper bound
        # Warn if the value is > 1000 nL
        v_max = volumes_df[factor].max()
        if v_max > upper_bound:
            warning_volumes['Max Report'][factor] = v_max
            logger.warning(
                f'One volume of {factor} = {v_max} nL (> 1000 nL). '
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
            warning_volumes['Min Report']['Water'] = vol_min_w
            for factor in under_conc_fac:
                logger.warning(
                    f'*** {factor}\nFactor seems to be under-concentrated '
                    '(volume of added water < 0).\n'
                )

    return warning_volumes


def save_volumes(
    volumes_df: Dict,
    volumes_summary: Dict,
    warning_volumes_report: DataFrame,
    echo_wells: Dict,
    output_folder: str = DEFAULT_ARGS['OUTPUT_FOLDER'],
    logger: Logger = getLogger(__name__)
):
    """
    Save volumes dataframes in TSV files

    Parameters
    ----------
    volumes_df : Dict
        DataFrames with converted volumes
        For 'normalizer' key, 0 is assigned to GOI-DNA column
        For 'autofluorescence' key, 0 is assigned to GFP-DNA & GOI-DNA columns
    volumes_summary: Dict
        DataFrame with total volume for each factor in
        initial/normalizer/autofluorescence_volumes_df
    warning_volumes_report: DataFrame
        Report of volumes outside the transfer range of Echo.
    echo_wells: Dict
        Source plate
    output_folder: str
        Path to storage folder for output files. Defaults to working directory.
    """
    logger.debug(f'volumes_df: {volumes_df}')

    # Create output folder if it doesn't exist
    if not os_path.exists(output_folder):
        os_mkdir(output_folder)

    # Create subfolder for volumes
    output_subfolder = os_path.join(output_folder, 'volumes_output')
    if not os_path.exists(output_subfolder):
        os_mkdir(output_subfolder)

    # Save volumes dataframes in TSV files
    for key, value in volumes_df.items():
        value.to_csv(
            os_path.join(
                output_subfolder,
                f'{key}_volumes.tsv'),
            sep='\t',
            header=volumes_df[key].columns,
            index=False)

    # Save volumes summary series in TSV files
    with open(
        os_path.join(
            output_subfolder,
            'volumes_summary.tsv'
        ), 'w'
    ) as csv_file:
        writer = csv_writer(
            csv_file,
            delimiter='\t'
        )
        writer.writerow(['', 'Sample + Dead Volumes'])
        for row in volumes_summary.items():
            writer.writerow(row)

    # Save volumes warning report in TSV file
    warning_volumes_report.to_csv(
        os_path.join(
            output_subfolder,
            'warning_volumes_report.tsv'),
        sep='\t')

    # Save source plates
    for plate_id, plate in echo_wells.items():
        with open(
            os_path.join(
                output_folder,
                f'source_plate_{plate_id}.tsv'
            ), 'w'
        ) as fp:
            header = 'WELL\tPARAMETER\tVOLUME_PER_WELL\n'
            fp.write(header)
            for param, param_values in plate.items():
                row = \
                    f'{param_values["wells"]}\t' \
                    f'{param}\t' \
                    f'{param_values["volume_per_well"]}\n'
                fp.write(row)


def samples_merger(
    volumes: Dict,
    nplicate: int = DEFAULT_ARGS['NPLICATE'],
    logger: Logger = getLogger(__name__)
) -> Dict:
    """
    Merge and triplicate samples into a single dataframe

    Parameters
    ----------
    volumes: Dict
        DataFrames with converted volumes
        For 'normalizer' key, 0 is assigned to GOI-DNA column
        For 'autofluorescence' key, 0 is assigned to GFP-DNA & GOI-DNA columns
    nplicate: int
        Number of copies
    logger: Logger
        Logger

    Returns
    -------
    merged_plates_final: List[DataFrame]
        DataFrames with merged samples
    """
    n_split = len(volumes)

    # Split volumes dataframes into three subsets
    volumes_list = {}
    for key in volumes.keys():
        sublst_len = len(volumes[key]) // n_split
        volumes_list[key] = array_split(
            volumes[key],
            range(sublst_len, len(volumes[key]), sublst_len)
        )
        # vsplit(
        #     volumes[key],
        #     n_split)

    merged_plates_final = {}
    for i_split in range(n_split):
        # Put together each (i_split)th of volumes_list
        merged_plates = concat(
            [
                _volumes[i_split]
                for _volumes in volumes_list.values()
            ],
            axis=0
        )
        # Nplicate merged subsets
        merged_plates_final[f'merged_plate_{i_split+1}'] = concat(
            [merged_plates]*nplicate,
            ignore_index=True
        )

    return merged_plates_final


def init_plate(
    starting_well: str = DEFAULT_ARGS['SRC_STARTING_WELL'],
    vertical: str = True,
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
    vertical : str, optional
        Reading/writing direction, by default True
    dimensions : str, optional
        Dimensions, by default '16x24'
    dead_volume : int, optional
        Plate dead volume per well, by default 15000
    well_capacity : float, optional
        Capacity of each well, by default 60000
    logger : Logger, optional
        Logger, by default getLogger(__name__)

    Returns
    -------
    Plate
        _description_
    """
    nb_rows, nb_cols = map(int, dimensions.split('x'))
    plate = Plate(
        nb_cols=nb_cols,
        nb_rows=nb_rows,
        dead_volume=dead_volume,
        well_capacity=well_capacity,
        vertical=vertical,
        logger=logger
    )
    plate.set_current_well(starting_well)
    return plate


def dst_plate_generator(
    volumes: Dict,
    plate_dimensions: str = DEFAULT_ARGS['PLATE_DIMENSIONS'],
    starting_well: str = DEFAULT_ARGS['DEST_STARTING_WELL'],
    plate_dead_volume: int = DEFAULT_ARGS['SOURCE_PLATE_DEAD_VOLUME'],
    plate_well_capacity: float = DEFAULT_ARGS['SOURCE_PLATE_WELL_CAPACITY'],
    vertical: str = True,
    logger: Logger = getLogger(__name__)
) -> Dict:
    """
    Generate destination plates dataframe

    Parameters
    ----------
    volumes: Dict
        DataFrames with samples
    starting_well : str
        Starter well to begin filling the 384 well-plate. Defaults to 'A1'
    vertical: bool
        - True: plate is filled column by column from top to bottom
        - False: plate is filled row by row from left to right
    logger: Logger
        Logger

    Returns
    -------
    plates: Dict
        Dict with destination plates dataframes
    """
    plates = {}
    plate = init_plate(
        starting_well=starting_well,
        dead_volume=plate_dead_volume,
        dimensions=plate_dimensions,
        well_capacity=plate_well_capacity,
        vertical=vertical,
        logger=logger
    )

    for set, volumes_df in volumes.items():
        plate.set_current_well(starting_well)
        names = []
        for i, row in volumes_df.iterrows():
            names.append(plate.get_current_well())
            try:
                plate.next_well()
            except ValueError:  # Out of plate
                # Store current plate
                plates[set] = deepcopy(plate)
                # Create new plate
                logger.warning('A new destination plate is created')
                plate = Plate(
                    nb_cols=plate.get_nb_cols(),
                    nb_rows=plate.get_nb_rows(),
                    dead_volume=plate_dead_volume,
                    well_capacity=plate_well_capacity,
                    vertical=vertical,
                    logger=logger
                )

        plates[set] = volumes_df.copy()
        plates[set]['well_name'] = names

    return plates


def src_plate_generator(
    volumes: Dict,
    param_dead_volumes: List[float],
    plate_dead_volume: int = DEFAULT_ARGS['SOURCE_PLATE_DEAD_VOLUME'],
    plate_well_capacity: float = DEFAULT_ARGS['SOURCE_PLATE_WELL_CAPACITY'],
    starting_well: str = DEFAULT_ARGS['SRC_STARTING_WELL'],
    optimize_well_volumes: List = [],
    vertical: str = True,
    plate_dimensions: str = DEFAULT_ARGS['PLATE_DIMENSIONS'],
    logger: Logger = getLogger(__name__)
) -> Dict:
    """
    Generate source plate dataframe

    Parameters
    ----------
    volumes: Dict
        DataFrames with factors
    param_dead_volumes: List
        Dead volumes of parameters
    plate_dead_volume
        Source plate dead volume. Defaults to 15000 nL
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
    plate: Dict
        Dict with source plate dataframe
    """
    logger.debug(f'volumes: {volumes}')

    plates = {}
    nb_plates = 1
    plate = init_plate(
        starting_well=starting_well,
        dead_volume=plate_dead_volume,
        dimensions=plate_dimensions,
        well_capacity=plate_well_capacity,
        vertical=vertical,
        logger=logger
    )

    vol_sums = {}

    # Sum volumes for each factor
    for vol_set in volumes.values():
        for factor in list(vol_set):
            if factor not in vol_sums:
                vol_sums[factor] = 0
            vol_sums[factor] += vol_set[factor].sum()

    # Set number of wells needed
    for factor in param_dead_volumes:
        # If volume = 0, then nothing to do
        if vol_sums[factor] == 0:
            logger.warning(
                f'{factor} has a volume = 0. '
                'Please check if is expected or because '
                f'sample volume is too low '
                f'or the stock concentration is too high.'
            )
            continue
        # Take account of dead volumes
        # Multiple of 2.5 (ECHO)
        well_net_capacity = floor(
            (
                plate.get_well_capacity()
                - plate.get_dead_volume()
                - param_dead_volumes[factor]
            ) / 2.5
        ) * 2.5
        logger.debug(f'well_net_capacity: {well_net_capacity}')
        # Volume w/o dead volumes
        nb_wells = ceil(vol_sums[factor] / well_net_capacity)
        logger.debug(f'nb_wells: {nb_wells}')
        # Raw volume per well
        # Multiple of 2.5 (ECHO)
        raw_volume_per_well = ceil(
            vol_sums[factor] / nb_wells / 2.5
        ) * 2.5
        logger.debug(f'raw_volume_per_well: {raw_volume_per_well}')
        # Optimize well volume
        if (
            factor in optimize_well_volumes
            or optimize_well_volumes == ['all']
        ):
            # Net volume per well
            volume_per_well = (
                raw_volume_per_well
                + plate.get_dead_volume()
                + param_dead_volumes[factor]
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
                plates[f'{nb_plates}'] = deepcopy(plate)
                nb_plates += 1
                # Create new plate
                logger.warning('A new source plate is created')
                plate = Plate(
                    nb_cols=plate.get_nb_cols(),
                    nb_rows=plate.get_nb_rows(),
                    dead_volume=plate_dead_volume,
                    well_capacity=plate_well_capacity,
                    vertical=vertical,
                    logger=logger
                )

    plates[f'{nb_plates}'] = deepcopy(plate)

    for plate_id, plate in plates.items():
        logger.debug(f'PLATE_ID: {plate_id}\n{plate}')

    return plates


def echo_instructions_generator(
    volumes: Dict,
    echo_wells: Dict,
    starting_well: str = DEFAULT_ARGS['DEST_STARTING_WELL'],
    plate_dead_volume: int = DEFAULT_ARGS['SOURCE_PLATE_DEAD_VOLUME'],
    plate_well_capacity: float = DEFAULT_ARGS['SOURCE_PLATE_WELL_CAPACITY'],
    keep_nil_vol: bool = DEFAULT_ARGS['KEEP_NIL_VOL'],
    logger: Logger = getLogger(__name__)
) -> Dict:
    """
    Generate and dispatch Echo® instructions on multiple plates

    Parameters
    ----------
    volumes: Dict
        DataFrames with merged samples
    source_plates: Dict
        Source plates distribution
    starting_well : str
        Starter well to begin filling the 384 well-plate. Defaults to 'A1'
    vertical: bool
        - True: plate is filled column by column from top to bottom
        - False: plate is filled row by row from left to right
    keep_nil_vol: bool
        If False, remove transfer volumes = 0 in instructions.
        Otherwise keep them (default: False)

    Returns
    -------
    echo_instructions: Dict
        Dict with echo instructions dataframes
    """

    dest_plates = dst_plate_generator(
        volumes=volumes,
        starting_well=starting_well,
        plate_dead_volume=plate_dead_volume,
        plate_well_capacity=plate_well_capacity,
        vertical=True,
        logger=logger
    )

    all_sources = {}
    echo_instructions = {}

    for key, destination_plate in dest_plates.items():
        # Iterate over all source plates
        for source_plate_id, wells in echo_wells.items():
            # Iterate over all parameters
            for parameter in wells:
                worklist = {
                    'Source Plate Name': [],
                    'Source Plate Type': [],
                    'Source Well': [],
                    'Destination Plate Name': [],
                    'Destination Well': [],
                    'Transfer Volume': [],
                    'Sample ID': []}

                for index in range(len(destination_plate)):
                    worklist['Source Plate Name'].append(
                        f'Source[{source_plate_id}]'
                    )
                    worklist['Source Plate Type'].append('384PP_AQ_GP3')
                    worklist['Source Well'].append(
                        wells[parameter]['wells']
                    )
                    worklist['Destination Plate Name'].append('Destination[1]')
                    worklist['Destination Well'].append(
                            destination_plate.loc[index, 'well_name']
                    )
                    worklist['Transfer Volume'].append(
                            destination_plate.loc[index, parameter])
                    worklist['Sample ID'].append(parameter)

                worklist = DataFrame(worklist)
                all_sources[parameter] = worklist
                instructions = concat(
                    all_sources.values()
                ).reset_index(drop=True)

            if not keep_nil_vol:
                # Remove instructions where transfer volume = 0
                instructions = instructions[
                    instructions['Transfer Volume'] != 0
                ]
                # Re-index
                instructions.reset_index(drop=True, inplace=True)
            echo_instructions[key] = instructions

    logger.debug(f'echo_instructions: {echo_instructions}')
    return echo_instructions


def echo_wells(
    plate: Plate,
    logger: Logger = getLogger(__name__)
) -> Dict:
    """Generate Echo® plate sorted by parameter

    Parameters
    ----------
    plate: Plate
        Plate
    logger: Logger
        Logger

    Returns
    -------
    echo_plate: Dict
        Dict sorted by parameter
    """
    echo_wells = {}
    parameter = old_parameter = None

    for well_name, well in plate.get_wells().items():
        for parameter, volume in well.items():
            if parameter not in echo_wells:
                echo_wells[parameter] = {
                    'first': well_name,
                    'last': well_name,
                    'volume': volume,
                    'nb_wells': 1
                }
            else:
                if old_parameter != parameter:
                    echo_wells[parameter] = {
                        'first': well_name,
                        'last': well_name,
                        'volume': volume,
                        'nb_wells': 1
                    }
                else:
                    echo_wells[parameter]['last'] = well_name
                    echo_wells[parameter]['nb_wells'] += 1
            old_parameter = parameter

    # Write with Echo format
    for parameter in echo_wells:
        if echo_wells[parameter]['first'] == echo_wells[parameter]['last']:
            echo_wells[parameter] = {
                'wells': f'{echo_wells[parameter]["first"]}',
                'volume_per_well': echo_wells[parameter]['volume'],
                'nb_wells': echo_wells[parameter]['nb_wells']
            }
        else:
            echo_wells[parameter] = {
                'wells':
                    f'{{{echo_wells[parameter]["first"]}:'
                    f'{echo_wells[parameter]["last"]}}}',
                'volume_per_well': echo_wells[parameter]['volume'],
                'nb_wells': echo_wells[parameter]['nb_wells']
            }

    return echo_wells


def save_echo_instructions(
    distribute_echo_instructions: Dict,
    merge_echo_instructions: Dict,
    output_folder: str = DEFAULT_ARGS['OUTPUT_FOLDER']
):
    """
    Save Echo instructions in csv files

    Parameters
    ----------
        distribute_echo_instructions_dict: Dict
            Dict with echo distributed instructions dataframes

        merge_echo_instructions_dict: Dict
            Dict with echo merged instructions dataframes

        output_folder: str
            Path to output storage folder
    """
    # Create output folder if it doesn't exist
    if not os_path.exists(output_folder):
        os_mkdir(output_folder)

    # Create output subfolders if they don't exist
    output_subfolder = os_path.join(output_folder, 'echo_instructions')
    if not os_path.exists(output_subfolder):
        os_mkdir(output_subfolder)

    output_subfolder_distributed = os_path.join(
        output_folder, 'echo_instructions', 'distributed')
    if not os_path.exists(output_subfolder_distributed):
        os_mkdir(output_subfolder_distributed)

    output_subfolder_merged = os_path.join(
        output_folder, 'echo_instructions', 'merged')
    if not os_path.exists(output_subfolder_merged):
        os_mkdir(output_subfolder_merged)

    # Save distributed Echo instructions in csv files
    for key, value in distribute_echo_instructions.items():
        value.to_csv(
            os_path.join(
                output_subfolder_distributed,
                f'distributed_{str(key)}_instructions.csv'
            ),
            sep=',',
            index=False,
            encoding='utf-8')

    # Save merged Echo instructions in csv files
    i = 1
    for key, value in merge_echo_instructions.items():
        value.to_csv(
            os_path.join(
                output_subfolder_merged,
                f'merged_plate_{i}_final_instructions.csv'
            ),
            sep=',',
            index=False,
            encoding='utf-8')
        i += 1
