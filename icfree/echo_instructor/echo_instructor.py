#!/usr/bin/env python
# coding: utf-8

from os import (
    path as os_path,
    mkdir as os_mkdir
)

from numpy import (
    fromiter as np_fromiter,
    multiply as np_multiply,
    vsplit as np_vsplit
)

from pandas import (
    read_csv as pd_read_csv,
    concat as pd_concat,
    DataFrame
)

from string import (
    ascii_uppercase as string_ascii_uppercase
)

from typing import (
    Dict
)

from logging import (
    Logger,
    getLogger
)

from .args import (
    DEFAULT_OUTPUT_FOLDER,
    DEFAULT_SAMPLE_VOLUME,
    DEFAULT_SOURCE_PLATE_DEAD_VOLUME,
    DEFAULT_STARTING_WELL,
    DEFAULT_NPLICATE
)


def input_importer(
        cfps_parameters,
        initial_concentrations,
        normalizer_concentrations,
        autofluorescence_concentrations):
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
    cfps_parameters_df = pd_read_csv(
        cfps_parameters,
        sep='\t')

    concentrations_df = {}
    concentrations_df['initial'] = pd_read_csv(
        initial_concentrations,
        sep='\t')

    concentrations_df['normalizer'] = pd_read_csv(
        normalizer_concentrations,
        sep='\t')

    concentrations_df['autofluorescence'] = pd_read_csv(
        autofluorescence_concentrations,
        sep='\t')

    return (cfps_parameters_df,
            concentrations_df)


def concentrations_to_volumes(
    cfps_parameters_df: DataFrame,
    concentrations_df: Dict,
    sample_volume: int = DEFAULT_SAMPLE_VOLUME,
    source_plate_dead_volume: int = DEFAULT_SOURCE_PLATE_DEAD_VOLUME,
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
    source_plate_dead_volume: int
        Source plate dead volume. Defaults to 15000 nL

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
    logger.debug('Sample volume:\n%s', sample_volume)

    # Exract stock conecentrations from cfps_parameters_df
    stock_concentrations_dict = dict(
        cfps_parameters_df[
            [
                'Parameter',
                'Stock concentration'
            ]
        ].to_numpy()
    )
    stock_concentrations_df = np_fromiter(
        stock_concentrations_dict.values(),
        dtype=float
    )
    logger.debug('Stock concentrations:\n%s', stock_concentrations_df)

    # Calculate sample volume and stock concentrations ratio for each well
    sample_volume_stock_ratio = \
        sample_volume / stock_concentrations_df

    volumes_df = {}
    volumes_summary = {}
    warning_volumes_report = {
        'Min Report': {},
        'Max Report': {}
    }

    for volumes_name in concentrations_df.keys():
        # Print out parameters
        logger.debug(f'{volumes_name} volumes:\n'
                     '{concentrations_df[volumes_name]}')

        # Convert concentrations into volumes
        # and make it a multiple of 2.5 (ECHO specs)
        try:
            volumes_df[volumes_name] = round(
                np_multiply(
                    concentrations_df[volumes_name],
                    sample_volume_stock_ratio
                ) / 2.5, 0
            ) * 2.5
            logger.debug(f'{volumes_name} volumes:\n'
                         '{volumes_df[volumes_name]}')
        except ValueError as e:
            logger.error(f'*** {e}')
            logger.error(
                'It seems that the number of parameters is different '
                'from the number of stock concentrations. Exiting...'
            )
            raise(e)

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

        # Sum of volumes for each parameter
        volumes_summary[volumes_name] = \
            volumes_df[volumes_name].sum().to_frame()

        # Add source plate dead volume to sum of volumes for each parameter
        volumes_summary[volumes_name] = \
            volumes_summary[volumes_name].add(source_plate_dead_volume)

    # Convert Warning Report Dict to Dataframe
    warning_volumes_report = DataFrame.from_dict(warning_volumes_report)

    return (volumes_df,
            volumes_summary,
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
                f'*** {factor}\nOne volume = {vol} nL (< 10 nL). '
                'Stock have to be more diluted.\n'
            )
        # Check upper bound
        # Warn if the value is > 1000 nL
        v_max = volumes_df[factor].max()
        if v_max > upper_bound:
            warning_volumes['Max Report'][factor] = v_max
            logger.warning(
                f'*** {factor}\nOne volume = {v_max} nL (> 1000 nL). '
                'Stock have to be more concentrated or pipetting '
                'has to be done manually.\n'
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
        cfps_parameters_df: DataFrame,
        volumes_df: Dict,
        volumes_summary: Dict,
        warning_volumes_report: DataFrame,
        output_folder: str = DEFAULT_OUTPUT_FOLDER):
    """
    Save volumes dataframes in TSV files

    Parameters
    ----------
    cfps_parameters_df : DataFrame
        Dataframe with cfps_parameters data.
    volumes_df : Dict
        DataFrames with converted volumes
        For 'normalizer' key, 0 is assigned to GOI-DNA column
        For 'autofluorescence' key, 0 is assigned to GFP-DNA & GOI-DNA columns
    volumes_summary: Dict
        DataFrame with total volume for each factor in
        initial/normalizer/autofluorescence_volumes_df
    warning_volumes_report: DataFrame
        Report of volumes outside the transfer range of Echo.
    output_folder: str
        Path to storage folder for output files. Defaults to working directory.
    """
    # Create output folder if it doesn't exist
    if not os_path.exists(output_folder):
        os_mkdir(output_folder)

    # Create subfolder for volumes
    output_subfolder = os_path.join(output_folder, 'volumes_output')
    if not os_path.exists(output_subfolder):
        os_mkdir(output_subfolder)

    # Get list of cfps parameters and add water
    all_parameters = cfps_parameters_df['Parameter'].tolist()
    all_parameters.append('Water')

    # Save volumes dataframes in TSV files
    for key, value in volumes_df.items():
        value.to_csv(
            os_path.join(
                output_subfolder,
                f'{key}_volumes.tsv'),
            sep='\t',
            header=all_parameters,
            index=False)

    # Save volumes summary series in TSV files
    for key, value in volumes_summary.items():
        value.to_csv(
            os_path.join(
                output_subfolder,
                f'{key}_volumes_summary.tsv'),
            sep='\t',
            header=['Sample + Dead Volumes'])

    # Save volumes warning report in TSV file
    warning_volumes_report.to_csv(
        os_path.join(
            output_subfolder,
            'warning_volumes_report.tsv'),
        sep='\t')


def samples_merger(
    volumes_df: Dict,
    nplicate: int = DEFAULT_NPLICATE,
    logger: Logger = getLogger(__name__)
) -> Dict:
    """
    Merge and triplicate samples into a single dataframe

    Parameters
    ----------
    volumes_df: Dict
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
    n_split = len(volumes_df)

    # Split volumes dataframes into three subsets
    volumes_df_list = {}
    for key in volumes_df.keys():
        volumes_df_list[key] = np_vsplit(
            volumes_df[key],
            n_split)

    merged_plates_final = {}
    for i_split in range(n_split):
        # Put together each (i_split)th of volumes_df_list
        merged_plates = pd_concat(
            [
                volumes_df[i_split]
                for volumes_df in volumes_df_list.values()
            ],
            axis=0
        )
        # Nplicate merged subsets
        merged_plates_final[f'merged_plate_{i_split+1}'] = pd_concat(
            [merged_plates]*nplicate,
            ignore_index=True
        )

    return merged_plates_final


def destination_plate_generator(
    wells: Dict,
    starting_well: str = DEFAULT_STARTING_WELL,
    vertical: str = True,
    logger: Logger = getLogger(__name__)
) -> Dict:
    """
    Generate merged destination plates dataframe

    Parameters
    ----------
    wells: Dict
        DataFrames with merged samples
    starting_well : str
        Starter well to begin filling the 384 well-plate. Defaults to 'A1'
    vertical: bool
        - True: plate is filled column by column from top to bottom
        - False: plate is filled row by row from left to right
    logger: Logger
        Logger

    Returns
    -------
    destination_plates: Dict
        Dict with destination plates dataframes
    """
    plate_rows = string_ascii_uppercase
    plate_rows = list(plate_rows[0:16])

    destination_plates = {}

    for well, volumes_df in wells.items():
        # Fill destination plates column by column
        if vertical:
            from_well = plate_rows.index(starting_well[0]) + \
                (int(starting_well[1:]) - 1) * 16
            names = ['{}{}'.format(
                plate_rows[(index + from_well) % 16],
                (index + from_well) // 16 + 1)
                    for index in volumes_df.index]
        # Fill destination plates row by row
        else:
            names = ['{}{}'.format(
                plate_rows[index // 24],
                index % 24 + 1) for index in volumes_df.index]

        destination_plates[well] = volumes_df.copy()
        destination_plates[well]['well_name'] = names

    return destination_plates


def echo_instructions_generator(
    volumes: Dict,
    starting_well: str = DEFAULT_STARTING_WELL,
    vertical: str = True,
    logger: Logger = getLogger(__name__)
) -> Dict:
    """
    Generate and dispatch Echo® instructions on multiple plates

    Parameters
    ----------
    volumes: Dict
        DataFrames with merged samples
    starting_well : str
        Starter well to begin filling the 384 well-plate. Defaults to 'A1'
    vertical: bool
        - True: plate is filled column by column from top to bottom
        - False: plate is filled row by row from left to right

    Returns
    -------
        echo_instructions: Dict
            Dict with echo instructions dataframes
    """
    destination_plates = destination_plate_generator(
        volumes,
        starting_well,
        vertical,
        logger
    )

    all_sources = {}
    echo_instructions = {}

    for key, destination_plate in destination_plates.items():

        for parameter_name in destination_plate.drop(columns=['well_name']):
            worklist = {
                'Source Plate Name': [],
                'Source Plate Type': [],
                'Source Well': [],
                'Destination Plate Name': [],
                'Destination Well': [],
                'Transfer Volume': [],
                'Sample ID': []}

            for index in range(len(destination_plate)):
                worklist['Source Plate Name'].append('Source[1]')
                worklist['Source Plate Type'].append('384PP_AQ_GP3')
                worklist['Source Well'].append(parameter_name)
                worklist['Destination Plate Name'].append('Destination[1]')
                worklist['Destination Well'].append(
                        destination_plate.loc[index, 'well_name'])
                worklist['Transfer Volume'].append(
                        destination_plate.loc[index, parameter_name])
                worklist['Sample ID'].append(parameter_name)

            worklist = DataFrame(worklist)
            all_sources[parameter_name] = worklist
            instructions = pd_concat(
                all_sources.values()
            ).reset_index(drop=True)

        echo_instructions[key] = instructions

    return echo_instructions


def save_echo_instructions(
        distribute_echo_instructions: Dict,
        merge_echo_instructions: Dict,
        output_folder: str = DEFAULT_OUTPUT_FOLDER):
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
