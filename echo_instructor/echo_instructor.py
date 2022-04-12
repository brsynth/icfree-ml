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


def samples_dispatcher(
        initial_set_volumes_df,
        normalizer_set_volumes_df,
        autofluorescence_set_volumes_df):

    """
    """
    initial_set_volumes_df_list = vsplit(
        initial_set_volumes_df,
        3)

    normalizer_set_volumes_df_list = vsplit(
        normalizer_set_volumes_df,
        3)

    autofluorescence_set_volumes_df_list = vsplit(
        autofluorescence_set_volumes_df,
        3)

    master_plate_1 = concat((
        initial_set_volumes_df_list[0],
        normalizer_set_volumes_df_list[0],
        autofluorescence_set_volumes_df_list[0]),
        axis=0)

    master_plate_1_duplicate = master_plate_1.copy()
    master_plate_1_triplicate = master_plate_1.copy()
    master_plate_1_final = concat((
        master_plate_1,
        master_plate_1_duplicate,
        master_plate_1_triplicate),
        axis=0)

    master_plate_2 = concat((
        initial_set_volumes_df_list[1],
        normalizer_set_volumes_df_list[1],
        autofluorescence_set_volumes_df_list[1]),
        axis=0)

    master_plate_2_duplicate = master_plate_2.copy()
    master_plate_2_triplicate = master_plate_2.copy()
    master_plate_2_final = concat((
        master_plate_2,
        master_plate_2_duplicate,
        master_plate_2_triplicate),
        axis=0)

    master_plate_3 = concat((
        initial_set_volumes_df_list[2],
        normalizer_set_volumes_df_list[2],
        autofluorescence_set_volumes_df_list[2]),
        axis=0)

    master_plate_3_duplicate = master_plate_3.copy()
    master_plate_3_triplicate = master_plate_3.copy()
    master_plate_3_final = concat((
        master_plate_3,
        master_plate_3_duplicate,
        master_plate_3_triplicate),
        axis=0)

    return (master_plate_1_final,
            master_plate_2_final,
            master_plate_3_final)


def multiple_destination_plate_generator(
        initial_set_volumes_df,
        normalizer_set_volumes_df,
        autofluorescence_set_volumes_df,
        starting_well='A1',
        vertical=True):
    """
    Generate an ensemble of destination plates as matrices
    Parameters
    ----------
    initial_set_volumes_df: DataFrame
        _description_
    normalizer_set_volumes_df: DataFrame
        _description_
    autofluorescence_set_volumes_df: DataFrame
        _description_
    starting_well : str
        Name of the starter well to begin filling the 384 well-plate.
    vertical: bool
        -True: plate is filled column by column from top to bottom.
        -False: plate is filled row by row from left to right.

    Returns
    -------
    destination_plates_dict: Dict
        _description_
    """
    volumes_df_dict = {
        'initial_set_volumes_df': initial_set_volumes_df,
        'normalizer_set_volumes_df': normalizer_set_volumes_df,
        'autofluorescence_set_volumes_df': autofluorescence_set_volumes_df}

    volumes_wells_keys = [
        'initial_volumes_wells',
        'normalizer_volumes_wells',
        'autofluorescence_volumes_wells']

    plate_rows = ascii_uppercase
    plate_rows = list(plate_rows[0:16])

    volumes_wells_list = []
    all_dataframe = {}

    for volumes_df in volumes_df_dict.values():
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
        master_plate_1_final,
        master_plate_2_final,
        master_plate_3_final,
        starting_well='A1',
        vertical=True):
    """
    Generate an ensemble of destination plates as matrices

    Parameters
    ----------
    master_plate_1_final: DataFrame
        _description_
    master_plate_2_final: DataFrame
        _description_
    master_plate_3_final: DataFrame
        _description_
    starting_well : str
        Name of the starter well to begin filling the 384 well-plate.
    vertical: bool
        -True: plate is filled column by column from top to bottom.
        -False: plate is filled row by row from left to right.

    Returns
    -------
    single_destination_plates_dict: Dict
        _description_
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

    # single_destination_plates_dict = dict(zip(
    #     volumes_wells_keys,
    #     volumes_wells_list))

    single_destination_plates_dict = {}
    for label, df in zip(volumes_wells_keys, volumes_wells_list):
        df.reset_index(inplace=True)
        single_destination_plates_dict[label] = df

    return single_destination_plates_dict


def multiple_echo_instructions_generator(
        multiple_destination_plates_dict,
        desired_order=None,
        reset_index=True):
    """
    Generate instructions matrices for the Echo robot.
    Dispatches instructions on a multiple plate.

    Parameters
    ----------
        multiple_destination_plates_dict: Dict
            _description_
        desired_order: _type_
            _description_
        reset_index: _type_
            _description_

    Returns
    -------
        multiple_echo_instructions_dict: Dict
            _description_
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
            transfers = {
                'Source_Plate_Barcode': [],
                'Source_Well': [],
                'Destination_Plate_Barcode': [],
                'Destination_Well': [],
                'Transfer_Volume': []}

            for index in range(len(destination_plate)):
                transfers['Source_Plate_Barcode'].append('Plate1')
                transfers['Source_Well'].append(
                        '{} well'.format(parameter_name))
                transfers['Destination_Plate_Barcode'].append('destPlate1')
                transfers['Destination_Well'].append(
                        destination_plate.loc[index, 'well_name'])
                transfers['Transfer_Volume'].append(
                        destination_plate.loc[index, parameter_name])
            transfers = DataFrame(transfers)
            all_sources[parameter_name] = transfers
            echo_instructions = concat(all_sources.values())

        multiple_echo_instructions_list.append(echo_instructions)
        multiple_echo_instructions_dict = dict(
            zip(
                multiple_echo_instructions_dict_keys,
                multiple_echo_instructions_list))

    if desired_order:
        echo_instructions = concat([all_sources[i] for i in desired_order])

    if reset_index:
        echo_instructions = echo_instructions.reset_index(drop=True)

    return multiple_echo_instructions_dict


def single_echo_instructions_generator(
        single_destination_plates_dict,
        desired_order=None,
        reset_index=True):
    """
    Generate instructions matrix for the Echo robot.
    Merges instructions on a single triplicated plate.

    Parameters
    ----------
        single_destination_plates_dict: Dict
            _description_
        desired_order: _type_
            _description_
        reset_index: _type_
            _description_

    Returns
    -------
        multiple_echo_instructions_dict: Dict
            _description_
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
            transfers = {
                'Source_Plate_Barcode': [],
                'Source_Well': [],
                'Destination_Plate_Barcode': [],
                'Destination_Well': [],
                'Transfer_Volume': []}

            for index in range(len(destination_plate)):
                transfers['Source_Plate_Barcode'].append('Plate1')
                transfers['Source_Well'].append(
                        '{} well'.format(parameter_name))
                transfers['Destination_Plate_Barcode'].append('destPlate1')
                transfers['Destination_Well'].append(
                        destination_plate.loc[index, 'well_name'])
                transfers['Transfer_Volume'].append(
                        destination_plate.loc[index, parameter_name])
            transfers = DataFrame(transfers)
            all_sources[parameter_name] = transfers
            echo_instructions = concat(all_sources.values())

        single_echo_instructions_list.append(echo_instructions)
        single_echo_instructions_dict = dict(
            zip(
                single_echo_instructions_dict_keys,
                single_echo_instructions_list))

    if desired_order:
        echo_instructions = concat([all_sources[i] for i in desired_order])

    if reset_index:
        echo_instructions = echo_instructions.reset_index(drop=True)

    return single_echo_instructions_dict


def save_echo_instructions(
            multiple_echo_instructions_dict,
            single_echo_instructions_dict):
    """
    Save instructions matrices in tsv files
    Parameters
    ----------
        single_echo_instructions_dict: Dict
            _description_
        multiple_echo_instructions_dict: Dict
            _description_
    """
    # keys = list(echo_instructions_dict.keys())

    # for key in keys:
    #     for echo_instructions in echo_instructions_dict.values():
    #         echo_instructions.to_csv(
    #             'data/echo_instructions/' + key + '.tsv',
    #             sep='\t',
    #             index=False)

    for key, value in multiple_echo_instructions_dict.items():
        key_index = list(multiple_echo_instructions_dict.keys()).index(key)
        value.to_csv(
            'data/echo_instructions/multiple/' + str(key_index) + '.tsv',
            sep='\t',
            index=False)

    for key, value in single_echo_instructions_dict.items():
        key_index = list(single_echo_instructions_dict.keys()).index(key)
        value.to_csv(
            'data/echo_instructions/single/' + str(key_index) + '.tsv',
            sep='\t',
            index=False)
