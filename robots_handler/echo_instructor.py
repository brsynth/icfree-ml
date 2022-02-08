#!/usr/bin/env python
# coding: utf-8


from pandas import (
    concat,
    DataFrame
)

from string import (
    ascii_uppercase
)


def volumes_dispatcher(
        volumes_array,
        starting_well,
        vertical):

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

        echo_instructions = volumes_array.copy()
        names = ['{}{}'.format(
            plate_rows[index // 24],
            index % 24 + 1) for index in echo_instructions.index]
        echo_instructions['well_name'] = names

    return all_dataframe, echo_instructions


def source_to_destination(
        echo_instructions,
        desired_order=None,
        reset_index=True,
        check_zero=False):

    all_sources = {}
    for parameter_name in echo_instructions.drop(columns=['well_name']):
        transfers = {
            'Source_Plate_Barcode': [],
            'Source_Well': [],
            'Destination_Plate_Barcode': [],
            'Destination_Well': [],
            'Transfer_Volume': []}

        for index in range(len(echo_instructions)):
            if echo_instructions.loc[index, parameter_name] > 0 or check_zero == False:
                transfers['Source_Plate_Barcode'].append('Plate1')
                transfers['Source_Well'].append(
                    '{} well'.format(parameter_name))
                transfers['Destination_Plate_Barcode'].append('destPlate1')
                transfers['Destination_Well'].append(
                    echo_instructions.loc[index, 'well_name'])
                transfers['Transfer_Volume'].append(
                    echo_instructions.loc[index, parameter_name])
        transfers = DataFrame(transfers)
        all_sources[parameter_name] = transfers

    aggregated = concat(all_sources.values())

    if desired_order:
        aggregated = concat([all_sources[i] for i in desired_order])

    if reset_index:
        aggregated = aggregated.reset_index(drop=True)

    return all_sources, aggregated
