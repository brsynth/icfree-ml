#!/usr/bin/env python
# coding: utf-8


from numpy import (
    fromiter,
    multiply,
)

from pandas import (
    read_csv,
    concat,
    DataFrame
)

from string import (
    ascii_uppercase
)

# from typing import (
#     Tuple
# )


def input_importer(
        cfps_parameters,
        initial_set_concentrations,
        normalizer_set_concentrations,
        autofluorescence_set_concentrations):
    """
    Create pandas dataframes from tsv files.

    Parameters
    ----------
    cfps_parameters : tsv file
        Tsv with list of CFPS parameters and relative features.
    initial_set_concentrations : tsv file
        Initial training set with concentrations values.
    normalizer_set_concentrations : tsv file
        Normalizer set with concentrations values.
    autofluorescence_set_concentrations : tsv file
        Autofluorescence set with concentrations values.

    Returns
    -------
    cfps_parameters_df : DataFrame
        Pandas dataframe populated with cfps_parameters data.
    initial_set_volumes_df : DataFrame
        Pandas dataframe with initial_set_concentrations data.
    normalizer_set_volumes_df : DataFrame
        Pandas dataframe with normalizer_set_concentrations data.
    autofluorescence_set_volumes_df : DataFrame
        Pandas dataframe with autofluorescence_set_concentrations data.
    """
    cfps_parameters_df = read_csv(
        cfps_parameters,
        sep='\t')

    initial_set_concentrations_df = read_csv(
        initial_set_concentrations,
        sep='\t')

    normalizer_set_concentrations_df = read_csv(
        normalizer_set_concentrations,
        sep='\t')

    autofluorescence_set_concentrations_df = read_csv(
        autofluorescence_set_concentrations,
        sep='\t')

    return (cfps_parameters_df,
            initial_set_concentrations_df,
            normalizer_set_concentrations_df,
            autofluorescence_set_concentrations_df)


def volumes_array_generator(
        cfps_parameters_df,
        initial_set_concentrations_df,
        normalizer_set_concentrations_df,
        autofluorescence_set_concentrations_df,
        sample_volume):
    """
    Convert concentrations dataframes into volumes dataframes.

    Parameters
    ----------
    cfps_parameters_df : DataFrame
        Pandas dataframe populated with cfps_parameters data.
    initial_set_volumes_df : DataFrame
        Pandas dataframe with initial_set_concentrations data.
    normalizer_set_volumes_df : DataFrame
        Pandas dataframe with normalizer_set_concentrations data.
    autofluorescence_set_volumes_df : DataFrame
        Pandas dataframe with autofluorescence_set_concentrations data.
    sample_volume: int
        Final sample volume in each well.

    Returns
    -------
    initial_set_volumes_df : DataFrame
        Initial set with volumes values.
    normalizer_set_volumes_df : DataFrame
        Normalizer set with volumes values.
    autofluorescence_set_volumes_df : DataFrame
        Autofluorescence set with volumes values.
    """
    stock_concentrations_dict = dict(
        cfps_parameters_df[['Parameter', 'Stock concentration']].to_numpy())

    stock_concentrations_array = fromiter(
        stock_concentrations_dict.values(),
        dtype=float)

    stock_concentrations_array = \
        sample_volume / \
        stock_concentrations_array / \
        0.0025

    intial_set_volumes_df = (multiply(
        initial_set_concentrations_df,
        stock_concentrations_array)) * 0.0025

    normalizer_set_volumes_df = (multiply(
        normalizer_set_concentrations_df,
        stock_concentrations_array)) * 0.0025

    autofluorescence_set_volumes_df = (multiply(
        autofluorescence_set_concentrations_df,
        stock_concentrations_array)) * 0.0025

    return (intial_set_volumes_df,
            normalizer_set_volumes_df,
            autofluorescence_set_volumes_df)


def save_volumes_array(
        cfps_parameters_df,
        intial_set_volumes_df,
        normalizer_set_volumes_df,
        autofluorescence_set_volumes_df):
    """
    Save Pandas dataframes in tsv files.

    Parameters
    ----------
    cfps_parameters_df : DataFrame
        Pandas dataframe populated with cfps_parameters data.
    initial_set_volumes_df : DataFrame
        Initial set with volumes values.
    normalizer_set_volumes_df : DataFrame
        Normalizer set with volumes values.
    autofluorescence_set_volumes_df : DataFrame
        Autofluorescence set with volumes values.

    Returns
    -------
    initial_set_volumes : tsv file
        Initial set with volumes values.
    normalizer_set_volumes : tsv file
        Normalizer set with volumes values.
    autofluorescence_set_volumes : tsv file
        Autofluorescence set with volumes values.
    """
    all_parameters = cfps_parameters_df['Parameter'].tolist()

    initial_set_volumes = intial_set_volumes_df.to_csv(
        'data/volumes_output/intial_set_volumes.tsv',
        sep='\t',
        header=all_parameters,
        index=False)

    normalizer_set_volumes = normalizer_set_volumes_df.to_csv(
        'data/volumes_output/normalizer_set_volumes.tsv',
        sep='\t',
        header=all_parameters)

    autofluorescence_set_volumes = autofluorescence_set_volumes_df.to_csv(
        'data/volumes_output/autofluorescence_set_volumes.tsv',
        sep='\t',
        header=all_parameters,
        index=False)

    return (initial_set_volumes,
            normalizer_set_volumes,
            autofluorescence_set_volumes)


def volumes_dispatcher(
        volumes_array,
        starting_well,
        vertical):
    """
    Make a dataframe as a 384 well plate for each metabolite.

    Parameters
    ----------
    volumes_array : DataFrame
        Add description.
    starting_well : str
        Name of the starter well to begin filling the 384 well-plate.
    vertical: bool
        -True: plate is filled column by column from top to bottom.
        -False: plate is filled row by row from left to right.

    Returns
    -------
    all_dataframe:
        add description

    volumes_wells: DataFrame
        add description
    """
    all_dataframe = {}
    plate_rows = ascii_uppercase
    plate_rows = list(plate_rows[0:16])

    if vertical:
        from_well = plate_rows.index(starting_well[0]) + \
            (int(starting_well[1:]) - 1) * 16

        for parameter_name in volumes_array.columns:
            dataframe = DataFrame(0.0, index=plate_rows, columns=range(1, 25))

            for index, value in enumerate(volumes_array[parameter_name]):
                index += from_well
                dataframe.iloc[index % 16, index // 16] = value

            all_dataframe[parameter_name] = dataframe

        echo_instructions = volumes_array.copy()
        names = ['{}{}'.format(
            plate_rows[(index + from_well) % 16],
            (index + from_well) // 16 + 1)
                for index in echo_instructions.index]

        echo_instructions['well_name'] = names

    if not vertical:
        from_well = plate_rows.index(starting_well[0]) * 24 + \
            int(starting_well[1:]) - 1

        for parameter_name in volumes_array.columns:
            dataframe = DataFrame(0.0, index=plate_rows, columns=range(1, 25))

            for index, value in enumerate(volumes_array[parameter_name]):
                index += from_well
                dataframe.iloc[index // 24, index % 24] = value

            all_dataframe[parameter_name] = dataframe

        volumes_wells = volumes_array.copy()
        names = ['{}{}'.format(
            plate_rows[index // 24],
            index % 24 + 1) for index in volumes_wells.index]
        volumes_wells['well_name'] = names

    return all_dataframe, volumes_wells


def source_to_destination(
        volumes_wells,
        desired_order=None,
        reset_index=True,
        check_zero=False):
    """
    _summary_

    Parameters
    ----------
        volumes_wells: _type_
            _description_
        desired_order: _type_
            _description_
        reset_index: _type_
            _description_
        check_zero: _type_
            _description_

    Returns
    -------
        all_sources: _type_
            _description_
        echo_instructions: _type_
            _description_
    """
    all_sources = {}
    for parameter_name in volumes_wells.drop(columns=['well_name']):
        transfers = {
            'Source_Plate_Barcode': [],
            'Source_Well': [],
            'Destination_Plate_Barcode': [],
            'Destination_Well': [],
            'Transfer_Volume': []}

        for index in range(len(volumes_wells)):
            if volumes_wells.loc[index, parameter_name] > 0 or check_zero == False:
                transfers['Source_Plate_Barcode'].append('Plate1')
                transfers['Source_Well'].append(
                    '{} well'.format(parameter_name))
                transfers['Destination_Plate_Barcode'].append('destPlate1')
                transfers['Destination_Well'].append(
                    volumes_wells.loc[index, 'well_name'])
                transfers['Transfer_Volume'].append(
                    volumes_wells.loc[index, parameter_name])
        transfers = DataFrame(transfers)
        all_sources[parameter_name] = transfers

    echo_instructions = concat(all_sources.values())

    if desired_order:
        echo_instructions = concat([all_sources[i] for i in desired_order])

    if reset_index:
        echo_instructions = echo_instructions.reset_index(drop=True)

    return all_sources, echo_instructions


def save_echo_instructions(
    echo_instructions
):
    """
    Save echo_instructions into a tsv file

    Parameters
    ----------
        echo_instructions: _type_
            _description_
    """

    echo_instructions = echo_instructions.to_csv(
        'data/echo_instructions/echo_instructions.tsv',
        sep='\t',
        index=False)
