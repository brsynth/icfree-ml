#!/usr/bin/env python
# coding: utf-8

from os import (
    path as os_path,
    mkdir as os_mkdir
)

from numpy import (
    fromiter,
    multiply,
    vsplit
)

from pandas import (
    read_csv,
    concat,
    DataFrame
)

from string import (
    ascii_uppercase
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
        Tsv with list of cfps parameters and relative features.
    initial_concentrations : tsv file
        Dataset with concentrations values.
    normalizer_concentrations : tsv file
        Copy of initial_concentrations. 0 is assigned to the GOI-DNA column.
    autofluorescence_concentrations : tsv file
        Copy of normalizer_concentrations. 0 is assigned to the GFP-DNA column.

    Returns
    -------
    cfps_parameters_df : DataFrame
        Dataframe with cfps_parameters data.
    initial_volumes_df : DataFrame
        Dataframe with initial_set_concentrations data.
    normalizer_volumes_df : DataFrame
        Dataframe with normalizer_set_concentrations data.
    autofluorescence_volumes_df : DataFrame
        Dataframe with autofluorescence_set_concentrations data.
    """
    cfps_parameters_df = read_csv(
        cfps_parameters,
        sep='\t')

    initial_concentrations_df = read_csv(
        initial_concentrations,
        sep='\t')

    normalizer_concentrations_df = read_csv(
        normalizer_concentrations,
        sep='\t')

    autofluorescence_concentrations_df = read_csv(
        autofluorescence_concentrations,
        sep='\t')

    return (cfps_parameters_df,
            initial_concentrations_df,
            normalizer_concentrations_df,
            autofluorescence_concentrations_df)


def volumes_array_generator(
    cfps_parameters_df: DataFrame,
    initial_concentrations_df: DataFrame,
    normalizer_concentrations_df: DataFrame,
    autofluorescence_concentrations_df: DataFrame,
    sample_volume: int = DEFAULT_SAMPLE_VOLUME,
    logger: Logger = getLogger(__name__)
):
    """
    Convert concentrations dataframes into volumes dataframes

    Parameters
    ----------
    cfps_parameters_df : DataFrame
        Dataframe with cfps_parameters data.
    initial_volumes_df : DataFrame
        Dataframe with initial_concentrations data.
    normalizer_volumes_df : DataFrame
        Dataframe with normalizer_concentrations data.
    autofluorescence_volumes_df : DataFrame
        Dataframe with autofluorescence_concentrations data.
    sample_volume: int
        Final sample volume in each well. Defaults to 10000 nL.

    Returns
    -------
    initial_volumes_df : DataFrame
        DataFrame with converted volumes.
    normalizer_volumes_df : DataFrame
        DataFrame with converted volumes. 0 is assigned to the GOI-DNA column.
    autofluorescence_volumes_df : DataFrame
        DataFrame with converted volumes. 0 is assigned to the GFP-DNA column.
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

    # Exract stock conecentrations from cfps_parameters_df
    stock_concentrations_dict = dict(
        cfps_parameters_df[['Parameter', 'Stock concentration']].to_numpy())
    stock_concentrations_df = fromiter(
        stock_concentrations_dict.values(),
        dtype=float)
    logger.debug('Stock concentrations:\n%s', stock_concentrations_df)

    # Calculate coeff for each well
    coeff = \
        sample_volume / stock_concentrations_df

    # Convert concentrations to volumes
    try:
        initial_volumes_df = round(multiply(
            initial_concentrations_df,
            coeff) / 2.5, 0) * 2.5
        logger.debug(
            'initial volumes:\n%s',
            initial_volumes_df
        )

        normalizer_volumes_df = round(multiply(
            normalizer_concentrations_df,
            coeff) / 2.5, 0) * 2.5
        logger.debug(
            'normalizer volumes:\n%s',
            normalizer_volumes_df
        )

        autofluorescence_volumes_df = round(multiply(
            autofluorescence_concentrations_df,
            coeff) / 2.5, 0) * 2.5
        logger.debug(
            'autofluorescence volumes:\n%s',
            autofluorescence_volumes_df
        )
    except ValueError as e:
        logger.error(f'*** {e}')
        logger.error(
            'It seems that the number of parameters is different '
            'than the number of stock concentrations. Exiting...'
        )
        raise(e)

    # WARNING: < 10 nL (echo specs) --> have to dilute stock
    for volumes in [
        initial_volumes_df,
        normalizer_volumes_df,
        autofluorescence_volumes_df
    ]:
        for factor in volumes.columns:
            for value in volumes[factor].sort_values():
                if value != 0:
                    break
            if 0 < value < 10:
                logger.warning(
                    f'There are {factor} volume(s) < 10 nL. '
                    'Stock have to be more diluted.'
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

    # WARNING: Vwater < 0 --> have to increase stock conentration
    # Check if a factor stock is not concentrated enough,
    # i.e. Vwater < 0
    for water_volumes in [
        initial_volumes_df['Water'],
        normalizer_volumes_df['Water'],
        autofluorescence_volumes_df['Water']
    ]:
        if water_volumes.min() < 0:
            logger.warning('*** Volume of added water < 0')
            logger.warning(
                'It seems that at least a factor stock '
                'is not concentrated enough.'
            )

    return (initial_volumes_df,
            normalizer_volumes_df,
            autofluorescence_volumes_df)


def save_volumes(
        cfps_parameters_df: DataFrame,
        initial_volumes_df: DataFrame,
        normalizer_volumes_df: DataFrame,
        autofluorescence_volumes_df: DataFrame,
        output_folder: str = DEFAULT_OUTPUT_FOLDER):
    """
    Save volumes dataframes in tsv files

    Parameters
    ----------
    cfps_parameters_df : DataFrame
        Dataframe with cfps_parameters data.
    initial_volumes_df : DataFrame
        DataFrame with converted volumes.
    normalizer_volumes_df : DataFrame
        Copy of initial_volumes_df. 0 is assigned to the GOI-DNA column.
    autofluorescence_volumes_df : DataFrame
        Copy of normalizer_volumes_df. 0 is assigned to the GFP-DNA column.
    output_folder: str
        Path to storage folder for output files. Defaults to working directory.
    """
    # Create output folder if it doesn't exist
    if not os_path.exists(output_folder):
        os_mkdir(output_folder)

    # Store files in user-provided output folder
    output_subfolder = os_path.join(output_folder, 'volumes_output')
    if not os_path.exists(output_subfolder):
        os_mkdir(output_subfolder)

    all_parameters = cfps_parameters_df['Parameter'].tolist()
    all_parameters.append('Water')

    initial_volumes_df.to_csv(
        os_path.join(output_subfolder, 'initial_volumes.tsv'),
        sep='\t',
        header=all_parameters,
        index=False)

    normalizer_volumes_df.to_csv(
        os_path.join(output_subfolder, 'normalizer_volumes.tsv'),
        sep='\t',
        header=all_parameters,
        index=False)

    autofluorescence_volumes_df.to_csv(
        os_path.join(output_subfolder, 'autofluorescence_volumes.tsv'),
        sep='\t',
        header=all_parameters,
        index=False)


def samples_merger(
        initial_volumes_df: DataFrame,
        normalizer_volumes_df: DataFrame,
        autofluorescence_volumes_df: DataFrame):
    """
    Merge and triplicate samples into a single dataframe

    Parameters
    ----------
    initial_volumes_df : DataFrame
        DataFrame with converted volumes.
    normalizer_volumes_df : DataFrame
        DataFrame with converted volumes. 0 is assigned to the GOI-DNA column.
    autofluorescence_volumes_df : DataFrame
        DataFrame with converted volumes. 0 is assigned to the GFP-DNA column.

    Returns
    -------
    master_plate_1_final: DataFrame
        First DataFrame with merged samples.
    master_plate_2_final: DataFrame
        Second DataFrame with merged samples.
    master_plate_3_final: DataFrame
        Third DataFrame with merged samples.
    """
    # Split volumes dataframes into three subsets
    initial_volumes_df_list = vsplit(
        initial_volumes_df,
        3)

    normalizer_volumes_df_list = vsplit(
        normalizer_volumes_df,
        3)

    autofluorescence_volumes_df_list = vsplit(
        autofluorescence_volumes_df,
        3)

    # Merge first subsets from each list
    master_plate_1 = concat((
        initial_volumes_df_list[0],
        normalizer_volumes_df_list[0],
        autofluorescence_volumes_df_list[0]),
        axis=0)

    # Triplicate merged subsets
    master_plate_1_duplicate = master_plate_1.copy()
    master_plate_1_triplicate = master_plate_1.copy()
    master_plate_1_final = concat((
        master_plate_1,
        master_plate_1_duplicate,
        master_plate_1_triplicate),
        axis=0,
        ignore_index=True)

    # Merge second subsets from each list
    master_plate_2 = concat((
        initial_volumes_df_list[1],
        normalizer_volumes_df_list[1],
        autofluorescence_volumes_df_list[1]),
        axis=0)

    # Triplicate merged subsets
    master_plate_2_duplicate = master_plate_2.copy()
    master_plate_2_triplicate = master_plate_2.copy()
    master_plate_2_final = concat((
        master_plate_2,
        master_plate_2_duplicate,
        master_plate_2_triplicate),
        axis=0,
        ignore_index=True)

    # Merge third subsets from each list
    master_plate_3 = concat((
        initial_volumes_df_list[2],
        normalizer_volumes_df_list[2],
        autofluorescence_volumes_df_list[2]),
        axis=0)

    # Triplicate merged subsets
    master_plate_3_duplicate = master_plate_3.copy()
    master_plate_3_triplicate = master_plate_3.copy()
    master_plate_3_final = concat((
        master_plate_3,
        master_plate_3_duplicate,
        master_plate_3_triplicate),
        axis=0,
        ignore_index=True)

    return (master_plate_1_final,
            master_plate_2_final,
            master_plate_3_final)


def multiple_destination_plate_generator(
        initial_volumes_df: DataFrame,
        normalizer_volumes_df: DataFrame,
        autofluorescence_volumes_df: DataFrame,
        starting_well: str = DEFAULT_STARTING_WELL,
        vertical=True):
    """
    Generate an ensemble of destination plates dataframes

    Parameters
    ----------
    initial_volumes_df : DataFrame
        DataFrame with converted volumes.
    normalizer_volumes_df : DataFrame
        DataFrame with converted volumes. 0 is assigned to the GOI-DNA column.
    autofluorescence_volumes_df : DataFrame
        DataFrame with converted volumes. 0 is assigned to the GFP-DNA column.
    starting_well : str
        Starter well to begin filling the 384 well-plate. Defaults to 'A1'.
    vertical: bool
        -True: plate is filled column by column from top to bottom.
        -False: plate is filled row by row from left to right.

    Returns
    -------
    multiple_destination_plates_dict: Dict
        Dict with destination plates dataframes.
    """
    volumes_df_dict = {
        'initial_volumes_df': initial_volumes_df,
        'normalizer_volumes_df': normalizer_volumes_df,
        'autofluorescence_volumes_df': autofluorescence_volumes_df}

    volumes_wells_keys = [
        'initial_volumes_wells',
        'normalizer_volumes_wells',
        'autofluorescence_volumes_wells']

    plate_rows = ascii_uppercase
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

    multiple_destination_plates_dict = dict(zip(
        volumes_wells_keys,
        volumes_wells_list))

    return multiple_destination_plates_dict


def single_destination_plate_generator(
        master_plate_1_final: DataFrame,
        master_plate_2_final: DataFrame,
        master_plate_3_final: DataFrame,
        starting_well: str = DEFAULT_STARTING_WELL,
        vertical=True):
    """
    Generate a single destination plates dataframe

    Parameters
    ----------
    master_plate_1_final: DataFrame
        First DataFrame with merged samples.
    master_plate_2_final: DataFrame
        Second DataFrame with merged samples.
    master_plate_3_final: DataFrame
        Third DataFrame with merged samples.
    starting_well : str
        Starter well to begin filling the 384 well-plate. Defaults to 'A1'.
    vertical: bool
        -True: plate is filled column by column from top to bottom.
        -False: plate is filled row by row from left to right.

    Returns
    -------
    single_destination_plates_dict: Dict
        Dict with destination plates dataframes.
    """
    volumes_df_dict = {
        'master_plate_1_final': master_plate_1_final,
        'master_plate_2_final': master_plate_2_final,
        'master_plate_3_final': master_plate_3_final}

    volumes_wells_keys = [
        'master_plate_1_volumes_wells',
        'master_plate_2_volumes_wells',
        'master_plate_3_volumes_wells']

    plate_rows = ascii_uppercase
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

    single_destination_plates_dict = dict(zip(
        volumes_wells_keys,
        volumes_wells_list))

    return single_destination_plates_dict


def multiple_echo_instructions_generator(
        multiple_destination_plates_dict: Dict):
    """
    Generate and dispatch Echo® instructions on multiple plates

    Parameters
    ----------
        multiple_destination_plates_dict: Dict
            Dict with destination plates dataframes.
        desired_order: _type_
            _description_
        reset_index: _type_
            _description_

    Returns
    -------
        multiple_echo_instructions_dict: Dict
            Dict with echo instructions dataframes.
    """
    all_sources = {}
    multiple_echo_instructions_dict = {}
    multiple_echo_instructions_list = []
    multiple_echo_instructions_dict_keys = [
        'initial_instructions',
        'normalizer_instructions',
        'autofluorescence_instructions']

    for destination_plate in multiple_destination_plates_dict.values():

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
            echo_instructions = concat(all_sources.values())

        multiple_echo_instructions_list.append(echo_instructions)
        multiple_echo_instructions_dict = dict(
            zip(multiple_echo_instructions_dict_keys,
                multiple_echo_instructions_list))

    return multiple_echo_instructions_dict


def single_echo_instructions_generator(
        single_destination_plates_dict: Dict):
    """
    Generate and merge Echo® instructions a single triplicated plate

    Parameters
    ----------
        single_destination_plates_dict: Dict
            Dict with destination plates dataframes.
        desired_order: _type_
            _description_
        reset_index: _type_
            _description_

    Returns
    -------
        single_echo_instructions_dict: Dict
            Dict with echo instructions dataframes.
    """
    all_sources = {}
    single_echo_instructions_dict = {}
    single_echo_instructions_list = []
    single_echo_instructions_dict_keys = [
        'master_plate_1_final',
        'master_plate_2_final',
        'master_plate_3_final']

    for destination_plate in single_destination_plates_dict.values():

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
            echo_instructions = concat(all_sources.values())

        single_echo_instructions_list.append(echo_instructions)
        single_echo_instructions_dict = dict(
            zip(single_echo_instructions_dict_keys,
                single_echo_instructions_list))

    return single_echo_instructions_dict


def save_echo_instructions(
        multiple_echo_instructions_dict: Dict,
        single_echo_instructions_dict: Dict,
        output_folder: str = DEFAULT_OUTPUT_FOLDER):
    """
    Save Echo instructions in csv files

    Parameters
    ----------
        single_echo_instructions_dict: Dict
            Dict with echo instructions dataframes.

        multiple_echo_instructions_dict: Dict
            Dict with echo instructions dataframes.

        output_folder: str
            Path to output storage folder
    """
    if not os_path.exists(output_folder):
        os_mkdir(output_folder)
    output_subfolder = os_path.join(output_folder, 'echo_instructions')

    if not os_path.exists(output_subfolder):
        os_mkdir(output_subfolder)
    output_subfolder_mul = os_path.join(
        output_folder, 'echo_instructions', 'multiple'
    )

    if not os_path.exists(output_subfolder_mul):
        os_mkdir(output_subfolder_mul)
    output_subfolder_sin = os_path.join(
        output_folder, 'echo_instructions', 'single'
    )

    if not os_path.exists(output_subfolder_sin):
        os_mkdir(output_subfolder_sin)

    for key, value in multiple_echo_instructions_dict.items():
        value.to_csv(
            os_path.join(
                output_subfolder_mul,
                f'{str(key)}.csv'
            ),
            sep=',',
            index=False,
            encoding='utf-8')

    for key, value in single_echo_instructions_dict.items():
        value.to_csv(
            os_path.join(
                output_subfolder_sin,
                f'{str(key)}_instructions.csv'
            ),
            sep=',',
            index=False,
            encoding='utf-8')
