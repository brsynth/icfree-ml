#!/usr/bin/env python
# coding: utf-8


from numpy import (
    fromiter,
    multiply
)

from pandas import (
    read_csv,
    DataFrame
)


def input_importer(
        input_file,
        input_file_1,
        input_file_2,
        input_file_3) -> DataFrame:

    input_df = read_csv(input_file, sep='\t')
    input_df_1 = read_csv(input_file_1, sep='\t')
    input_df_2 = read_csv(input_file_2, sep='\t')
    input_df_3 = read_csv(input_file_3, sep='\t')

    return (input_df,
            input_df_1,
            input_df_2,
            input_df_3)


def volumes_array_generator(
        input_df,
        input_df_1,
        input_df_2,
        input_df_3,
        sample_volume):

    stock_concentrations_dict = dict(
        input_df[['Parameter', 'Stock concentration']].to_numpy())

    stock_concentrations_array = fromiter(
        stock_concentrations_dict.values(),
        dtype=float)

    stock_concentrations_array = \
        sample_volume / \
        stock_concentrations_array / \
        0.0025

    intial_set_volumes = (multiply(
        input_df_1, stock_concentrations_array)) * 0.0025

    normalizer_set_volumes = (multiply(
        input_df_2, stock_concentrations_array)) * 0.0025

    autofluorescence_set_volumes = (multiply(
        input_df_3, stock_concentrations_array)) * 0.0025

    return (intial_set_volumes,
            normalizer_set_volumes,
            autofluorescence_set_volumes)


def save_volumes_array(
    input_df,
    intial_set_volumes,
    normalizer_set_volumes,
    autofluorescence_set_volumes
):

    all_parameters = input_df['Parameter'].tolist()

    initial_set_volumes = intial_set_volumes.to_csv(
        'data/volumes_output/intial_set_volumes.tsv',
        sep='\t',
        header=all_parameters,
        index=False)

    normalizer_set_volumes = normalizer_set_volumes.to_csv(
        'data/volumes_output/normalizer_set_volumes.tsv',
        sep='\t',
        header=all_parameters)

    autofluorescence_set_volumes = autofluorescence_set_volumes.to_csv(
        'data/volumes_output/autofluorescence_set_volumes.tsv',
        sep='\t',
        header=all_parameters,
        index=False)

    return (initial_set_volumes,
            normalizer_set_volumes,
            autofluorescence_set_volumes)
