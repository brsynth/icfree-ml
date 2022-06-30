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
    DEFAULT_STARTING_WELL
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

    initial_concentrations_df = pd_read_csv(
        initial_concentrations,
        sep='\t')

    normalizer_concentrations_df = pd_read_csv(
        normalizer_concentrations,
        sep='\t')

    autofluorescence_concentrations_df = pd_read_csv(
        autofluorescence_concentrations,
        sep='\t')

    return (cfps_parameters_df,
            initial_concentrations_df,
            normalizer_concentrations_df,
            autofluorescence_concentrations_df)


def concentrations_to_volumes(
    cfps_parameters_df: DataFrame,
    initial_concentrations_df: DataFrame,
    normalizer_concentrations_df: DataFrame,
    autofluorescence_concentrations_df: DataFrame,
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
    initial_volumes_df : DataFrame
        Dataframe with initial_concentrations data
    normalizer_volumes_df : DataFrame
        Dataframe with normalizer_concentrations data
    autofluorescence_volumes_df : DataFrame
        Dataframe with autofluorescence_concentrations data
    sample_volume: int
        Final sample volume in each well. Defaults to 10000 nL
    source_plate_dead_volume: int
        Source plate dead volume. Defaults to 15000 nL

    Returns
    -------
    initial_volumes_df : DataFrame
        DataFrame with converted volumes
    normalizer_volumes_df : DataFrame
        DataFrame with converted volumes. 0 is assigned to the GOI-DNA column
    autofluorescence_volumes_df : DataFrame
        DataFrame with converted volumes. 0 is assigned to the GFP-DNA column
    initial_volumes_summary: DataFrame
        Series with total volume for each factor in initial_volumes_df
    normalizer_volumes_summary: DataFrame
        Series with total volume for each factor in normalizer_volumes_df
    autofluorescence_volumes_summary: DataFrame
        Series with total volume for each factor in autofluorescence_volumes_df
    warning_volumes_report: DataFrame
        Report of volumes outside the transfer range of Echo
    """
    # Print out parameters
    logger.info('Converting concentrations to volumes...')
    logger.debug(
        'cfps parameters:\n%s',
        cfps_parameters_df
    )
    logger.debug(
        'initial concentrations:\n%s',
        initial_concentrations_df
    )
    logger.debug(
        'normalizer concentrations:\n%s',
        normalizer_concentrations_df
    )
    logger.debug(
        'autofluorescence concentrations:\n%s',
        autofluorescence_concentrations_df
    )
    logger.debug('Sample volume:\n%s', sample_volume)

    # Warning volumes
    warning_volumes_report = {
        'Min Report': {},
        'Max Report': {}
    }

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

    # Convert concentrations into volumes
    # and make it a multiple of 2.5 (ECHO specs)
    try:
        initial_volumes_df = round(
            np_multiply(
                initial_concentrations_df,
                sample_volume_stock_ratio
            ) / 2.5,
            0
        ) * 2.5
        logger.debug(
            'initial volumes:\n%s',
            initial_volumes_df
        )

        normalizer_volumes_df = round(np_multiply(
            normalizer_concentrations_df,
            sample_volume_stock_ratio
            ) / 2.5,
            0
        ) * 2.5
        logger.debug(
            'normalizer volumes:\n%s',
            normalizer_volumes_df
        )

        autofluorescence_volumes_df = round(np_multiply(
            autofluorescence_concentrations_df,
            sample_volume_stock_ratio
            ) / 2.5,
            0
        ) * 2.5
        logger.debug(
            'autofluorescence volumes:\n%s',
            autofluorescence_volumes_df
        )
    except ValueError as e:
        logger.error(f'*** {e}')
        logger.error(
            'It seems that the number of parameters is different '
            'from the number of stock concentrations. Exiting...'
        )
        raise(e)

    # WARNING: < 10 nL (ECHO min volume transfer limit) --> dilute stock
    for volumes in [
        initial_volumes_df,
        normalizer_volumes_df,
        autofluorescence_volumes_df
    ]:
        for factor in volumes.columns:
            # Check lower bound
            for vol in volumes[factor].sort_values():
                # Pass all 0 since it is a correct value
                if vol != 0:
                    # Exit the loop at the first non-0 value
                    break
            # Warn if the value is < 10 nL
            if 0 < vol < 10:
                warning_volumes_report['Min Report'][factor] = vol
                logger.warning(
                    f'*** {factor}\nOne volume = {vol} nL (< 10 nL). '
                    'Stock have to be more diluted.\n'
                )
            # Check upper bound
            # Warn if the value is > 1000 nL
            v_max = volumes[factor].max()
            if v_max > 1000:
                warning_volumes_report['Max Report'][factor] = v_max
                logger.warning(
                    f'*** {factor}\nOne volume = {v_max} nL (> 1000 nL). '
                    'Stock have to be more concentrated or pipetting '
                    'has to be done manually.\n'
                )

    # Add Water column
    initial_volumes_df['Water'] = \
        sample_volume - initial_volumes_df.sum(axis=1)
    logger.debug('initial volumes:\n%s', initial_volumes_df)

    normalizer_volumes_df['Water'] = \
        sample_volume - normalizer_volumes_df.sum(axis=1)
    logger.debug('normalizer volumes:\n%s', normalizer_volumes_df)

    autofluorescence_volumes_df['Water'] = \
        sample_volume - autofluorescence_volumes_df.sum(axis=1)
    logger.debug('autofluorescence volumes:\n%s', autofluorescence_volumes_df)

    # Check water added volume
    for water_volumes in [
        initial_volumes_df['Water'],
        normalizer_volumes_df['Water'],
        autofluorescence_volumes_df['Water']
    ]:
        # Check if a factor stock is not concentrated enough,
        # WARNING: Vwater < 0 --> increase stock concentration
        vol_min = water_volumes.min()
        vol_max = water_volumes.max()
        if vol_min < 0:
            warning_volumes_report['Min Report']['Water'] = vol_min
            logger.warning(
                f'*** Water\nVolume of added water = {vol_min} (< 0). '
                'It seems that at least a factor stock '
                'is not concentrated enough.\n'
            )
        # WARNING: Vwater > 1000 nL
        elif vol_max > 1000:
            warning_volumes_report['Max Report']['Water'] = vol_max
            logger.warning(
                f'*** Water\nVolume of added water = {vol_max} (> 1000 nL). '
                'Pipetting has to be done manually.\n'
            )

    # Convert Warning Report Dict to Dataframe
    warning_volumes_report = DataFrame.from_dict(warning_volumes_report)

    # Sum of volumes for each parameter
    initial_volumes_summary = (initial_volumes_df.sum()).to_frame()
    normalizer_volumes_summary = (normalizer_volumes_df.sum()).to_frame()
    autofluorescence_volumes_summary = \
        (autofluorescence_volumes_df.sum()).to_frame()

    # Add source plate dead volume to sum of volumes for each parameter
    initial_volumes_summary = initial_volumes_summary.add(
        source_plate_dead_volume)
    normalizer_volumes_summary = normalizer_volumes_summary.add(
        source_plate_dead_volume)
    autofluorescence_volumes_summary = autofluorescence_volumes_summary.add(
        source_plate_dead_volume)

    return (initial_volumes_df,
            normalizer_volumes_df,
            autofluorescence_volumes_df,
            initial_volumes_summary,
            normalizer_volumes_summary,
            autofluorescence_volumes_summary,
            warning_volumes_report)


def save_volumes(
        cfps_parameters_df: DataFrame,
        initial_volumes_df: DataFrame,
        normalizer_volumes_df: DataFrame,
        autofluorescence_volumes_df: DataFrame,
        initial_volumes_summary: DataFrame,
        normalizer_volumes_summary: DataFrame,
        autofluorescence_volumes_summary: DataFrame,
        warning_volumes_report: DataFrame,
        output_folder: str = DEFAULT_OUTPUT_FOLDER):
    """
    Save volumes dataframes in TSV files

    Parameters
    ----------
    cfps_parameters_df : DataFrame
        Dataframe with cfps_parameters data.
    initial_volumes_df : DataFrame
        DataFrame with converted volumes
    normalizer_volumes_df : DataFrame
        DataFrame with converted volumes. 0 is assigned to the GOI-DNA column
    autofluorescence_volumes_df : DataFrame
        DataFrame with converted volumes. 0 is assigned to the GFP-DNA column
    initial_volumes_summary: DataFrame
        Series with total volume for each factor in initial_volumes_df
    normalizer_volumes_summary: DataFrame
        Series with total volume for each factor in normalizer_volumes_df
    autofluorescence_volumes_summary: DataFrame
        Series with total volume for each factor in autofluorescence_volumes_df
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
    initial_volumes_df.to_csv(
        os_path.join(
            output_subfolder,
            'initial_volumes.tsv'),
        sep='\t',
        header=all_parameters,
        index=False)

    normalizer_volumes_df.to_csv(
        os_path.join(
            output_subfolder,
            'normalizer_volumes.tsv'),
        sep='\t',
        header=all_parameters,
        index=False)

    autofluorescence_volumes_df.to_csv(
        os_path.join(
            output_subfolder,
            'autofluorescence_volumes.tsv'),
        sep='\t',
        header=all_parameters,
        index=False)

    # Save volumes summary series in TSV files
    initial_volumes_summary.to_csv(
        os_path.join(
            output_subfolder,
            'initial_volumes_summary.tsv'),
        sep='\t',
        header=['Sample + Dead Volumes'])

    normalizer_volumes_summary.to_csv(
        os_path.join(
            output_subfolder,
            'normalizer_volumes_summary.tsv'),
        sep='\t',
        header=['Sample + Dead Volumes'])

    autofluorescence_volumes_summary.to_csv(
        os_path.join(
            output_subfolder,
            'autofluorescence_volumes_summary.tsv'),
        sep='\t',
        header=['Sample + Dead Volumes'])

    # Save volumes warning report in TSV file
    warning_volumes_report.to_csv(
        os_path.join(
            output_subfolder,
            'warning_volumes_report.tsv'),
        sep='\t')


def samples_merger(
        initial_volumes_df: DataFrame,
        normalizer_volumes_df: DataFrame,
        autofluorescence_volumes_df: DataFrame):
    """
    Merge and triplicate samples into a single dataframe

    Parameters
    ----------
    initial_volumes_df : DataFrame
        DataFrame with converted volumes
    normalizer_volumes_df : DataFrame
        DataFrame with converted volumes. 0 is assigned to the GOI-DNA column
    autofluorescence_volumes_df : DataFrame
        DataFrame with converted volumes. 0 is assigned to the GFP-DNA column

    Returns
    -------
    merged_plate_1_final: DataFrame
        First DataFrame with merged samples
    merged_plate_2_final: DataFrame
        Second DataFrame with merged samples
    merged_plate_3_final: DataFrame
        Third DataFrame with merged samples
    """
    # Split volumes dataframes into three subsets
    initial_volumes_df_list = np_vsplit(
        initial_volumes_df,
        3)

    normalizer_volumes_df_list = np_vsplit(
        normalizer_volumes_df,
        3)

    autofluorescence_volumes_df_list = np_vsplit(
        autofluorescence_volumes_df,
        3)

    # Merge first subsets from each list
    merged_plate_1 = pd_concat((
        initial_volumes_df_list[0],
        normalizer_volumes_df_list[0],
        autofluorescence_volumes_df_list[0]),
        axis=0)

    # Triplicate merged subsets
    merged_plate_1_duplicate = merged_plate_1.copy()
    merged_plate_1_triplicate = merged_plate_1.copy()
    merged_plate_1_final = pd_concat((
        merged_plate_1,
        merged_plate_1_duplicate,
        merged_plate_1_triplicate),
        axis=0,
        ignore_index=True)

    # Merge second subsets from each list
    merged_plate_2 = pd_concat((
        initial_volumes_df_list[1],
        normalizer_volumes_df_list[1],
        autofluorescence_volumes_df_list[1]),
        axis=0)

    # Triplicate merged subsets
    merged_plate_2_duplicate = merged_plate_2.copy()
    merged_plate_2_triplicate = merged_plate_2.copy()
    merged_plate_2_final = pd_concat((
        merged_plate_2,
        merged_plate_2_duplicate,
        merged_plate_2_triplicate),
        axis=0,
        ignore_index=True)

    # Merge third subsets from each list
    merged_plate_3 = pd_concat((
        initial_volumes_df_list[2],
        normalizer_volumes_df_list[2],
        autofluorescence_volumes_df_list[2]),
        axis=0)

    # Triplicate merged subsets
    merged_plate_3_duplicate = merged_plate_3.copy()
    merged_plate_3_triplicate = merged_plate_3.copy()
    merged_plate_3_final = pd_concat((
        merged_plate_3,
        merged_plate_3_duplicate,
        merged_plate_3_triplicate),
        axis=0,
        ignore_index=True)

    return (merged_plate_1_final,
            merged_plate_2_final,
            merged_plate_3_final)


def distribute_destination_plate_generator(
        initial_volumes_df: DataFrame,
        normalizer_volumes_df: DataFrame,
        autofluorescence_volumes_df: DataFrame,
        starting_well: str = DEFAULT_STARTING_WELL,
        vertical: str = True):
    """
    Generate an ensemble of destination plates dataframes

    Parameters
    ----------
    initial_volumes_df : DataFrame
        DataFrame with converted volumes.
    normalizer_volumes_df : DataFrame
        DataFrame with converted volumes. 0 is assigned to the GOI-DNA column
    autofluorescence_volumes_df : DataFrame
        DataFrame with converted volumes. 0 is assigned to the GFP-DNA column
    starting_well : str
        Starter well to begin filling the 384 well-plate. Defaults to 'A1'
    vertical: bool
        -True: plate is filled column by column from top to bottom
        -False: plate is filled row by row from left to right

    Returns
    -------
    distribute_destination_plates_dict: Dict
        Dict with ditributed destination plates dataframes
    """
    volumes_df_dict = {
        'initial_volumes_df': initial_volumes_df,
        'normalizer_volumes_df': normalizer_volumes_df,
        'autofluorescence_volumes_df': autofluorescence_volumes_df}

    volumes_wells_keys = [
        'initial_volumes_wells',
        'normalizer_volumes_wells',
        'autofluorescence_volumes_wells']

    plate_rows = string_ascii_uppercase
    plate_rows = list(plate_rows[0:16])

    volumes_wells_list = []
    all_dataframe = {}

    for volumes_df in volumes_df_dict.values():
        # Fill destination plates column by column
        if vertical:
            from_well = plate_rows.index(starting_well[0]) + \
                (int(starting_well[1:]) - 1) * 16

            for parameter_name in volumes_df.columns:
                dataframe = DataFrame(
                    0.0,
                    index=plate_rows,
                    columns=range(1, 25))

                for index, value in enumerate(volumes_df[parameter_name]):
                    index += from_well
                    dataframe.iloc[index % 16, index // 16] = value

                all_dataframe[parameter_name] = dataframe

            volumes_wells = volumes_df.copy()
            names = ['{}{}'.format(
                plate_rows[(index + from_well) % 16],
                (index + from_well) // 16 + 1)
                    for index in volumes_df.index]

            volumes_wells['well_name'] = names
            volumes_wells_list.append(volumes_wells)

        # Fill destination plates row by row
        if not vertical:
            from_well = plate_rows.index(starting_well[0]) * 24 + \
                int(starting_well[1:]) - 1

            for parameter_name in volumes_df.columns:
                dataframe = DataFrame(
                    0.0,
                    index=plate_rows,
                    columns=range(1, 25))

                for index, value in enumerate(volumes_df[parameter_name]):
                    index += from_well
                    dataframe.iloc[index // 24, index % 24] = value

                all_dataframe[parameter_name] = dataframe

            volumes_wells = volumes_df.copy()
            names = ['{}{}'.format(
                plate_rows[index // 24],
                index % 24 + 1) for index in volumes_wells.index]
            volumes_wells['well_name'] = names
            volumes_wells_list.append(volumes_wells)

    distribute_destination_plates_dict = dict(zip(
        volumes_wells_keys,
        volumes_wells_list))

    return distribute_destination_plates_dict


def merge_destination_plate_generator(
        merged_plate_1_final: DataFrame,
        merged_plate_2_final: DataFrame,
        merged_plate_3_final: DataFrame,
        starting_well: str = DEFAULT_STARTING_WELL,
        vertical=True):
    """
    Generate merged destination plates dataframe

    Parameters
    ----------
    merged_plate_1_final: DataFrame
        First DataFrame with merged samples
    merged_plate_2_final: DataFrame
        Second DataFrame with merged samples
    merged_plate_3_final: DataFrame
        Third DataFrame with merged samples
    starting_well : str
        Starter well to begin filling the 384 well-plate. Defaults to 'A1'
    vertical: bool
        -True: plate is filled column by column from top to bottom
        -False: plate is filled row by row from left to right

    Returns
    -------
    merge_destination_plates_dict: Dict
        Dict with merged destination plates dataframes
    """
    volumes_df_dict = {
        'merged_plate_1_final': merged_plate_1_final,
        'merged_plate_2_final': merged_plate_2_final,
        'merged_plate_3_final': merged_plate_3_final}

    volumes_wells_keys = [
        'merged_plate_1_volumes_wells',
        'merged_plate_2_volumes_wells',
        'merged_plate_3_volumes_wells']

    plate_rows = string_ascii_uppercase
    plate_rows = list(plate_rows[0:16])

    volumes_wells_list = []
    all_dataframe = {}

    for volumes_df in volumes_df_dict.values():
        # Fill destination plates column by column
        if vertical:
            from_well = plate_rows.index(starting_well[0]) + \
                (int(starting_well[1:]) - 1) * 16

            for parameter_name in volumes_df.columns:
                dataframe = DataFrame(
                    0.0,
                    index=plate_rows,
                    columns=range(1, 25))

                for index, value in enumerate(volumes_df[parameter_name]):
                    index += from_well
                    dataframe.iloc[index % 16, index // 16] = value

                all_dataframe[parameter_name] = dataframe

            volumes_wells = volumes_df.copy()
            names = ['{}{}'.format(
                plate_rows[(index + from_well) % 16],
                (index + from_well) // 16 + 1)
                    for index in volumes_df.index]

            volumes_wells['well_name'] = names
            volumes_wells_list.append(volumes_wells)

        # Fill destination plates row by row
        if not vertical:
            from_well = plate_rows.index(starting_well[0]) * 24 + \
                int(starting_well[1:]) - 1

            for parameter_name in volumes_df.columns:
                dataframe = DataFrame(
                    0.0,
                    index=plate_rows,
                    columns=range(1, 25))

                for index, value in enumerate(volumes_df[parameter_name]):
                    index += from_well
                    dataframe.iloc[index // 24, index % 24] = value

                all_dataframe[parameter_name] = dataframe

            volumes_wells = volumes_df.copy()
            names = ['{}{}'.format(
                plate_rows[index // 24],
                index % 24 + 1) for index in volumes_wells.index]
            volumes_wells['well_name'] = names
            volumes_wells_list.append(volumes_wells)

    merge_destination_plates_dict = dict(zip(
        volumes_wells_keys,
        volumes_wells_list))

    return merge_destination_plates_dict


def distribute_echo_instructions_generator(
        distribute_destination_plates_dict: Dict):
    """
    Generate and dispatch Echo® instructions on multiple plates

    Parameters
    ----------
        distribute_destination_plates_dict: Dict
            Dict with distributed destination plates dataframes

    Returns
    -------
        distribute_echo_instructions_dict: Dict
            Dict with distributed echo instructions dataframes
    """
    all_sources = {}
    distribute_echo_instructions_dict = {}
    distribute_echo_instructions_list = []
    distribute_echo_instructions_dict_keys = [
        'initial_instructions',
        'normalizer_instructions',
        'autofluorescence_instructions']

    for destination_plate in distribute_destination_plates_dict.values():

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
            echo_instructions = pd_concat(
                all_sources.values()).reset_index(drop=True)

        distribute_echo_instructions_list.append(echo_instructions)
        distribute_echo_instructions_dict = dict(
            zip(distribute_echo_instructions_dict_keys,
                distribute_echo_instructions_list))

    return distribute_echo_instructions_dict


def merge_echo_instructions_generator(
        merge_destination_plates_dict: Dict):
    """
    Generate and merge Echo® instructions a single triplicated plate

    Parameters
    ----------
        merge_destination_plates_dict: Dict
            Dict with merged destination plates dataframes

    Returns
    -------
        merge_echo_instructions_dict: Dict
            Dict with merged echo instructions dataframes
    """
    all_sources = {}
    merge_echo_instructions_dict = {}
    merge_echo_instructions_list = []
    merge_echo_instructions_dict_keys = [
        'merged_plate_1_final',
        'merged_plate_2_final',
        'merged_plate_3_final']

    for destination_plate in merge_destination_plates_dict.values():

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
            echo_instructions = pd_concat(
                all_sources.values()).reset_index(drop=True)

        merge_echo_instructions_list.append(echo_instructions)
        merge_echo_instructions_dict = dict(
            zip(merge_echo_instructions_dict_keys,
                merge_echo_instructions_list))

    return merge_echo_instructions_dict


def save_echo_instructions(
        distribute_echo_instructions_dict: Dict,
        merge_echo_instructions_dict: Dict,
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
    for key, value in distribute_echo_instructions_dict.items():
        value.to_csv(
            os_path.join(
                output_subfolder_distributed,
                f'distributed_{str(key)}.csv'
            ),
            sep=',',
            index=False,
            encoding='utf-8')

    # Save merged Echo instructions in csv files
    for key, value in merge_echo_instructions_dict.items():
        value.to_csv(
            os_path.join(
                output_subfolder_merged,
                f'{str(key)}_instructions.csv'
            ),
            sep=',',
            index=False,
            encoding='utf-8')
