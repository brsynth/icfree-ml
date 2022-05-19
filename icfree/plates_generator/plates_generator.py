#!/usr/bin/env python
# coding: utf-8

from os import (
    path as os_path,
    mkdir as os_mkdir
)

from numpy import (
    concatenate,
    array,
    asarray,
    shape,
    reshape,
    multiply,
    full,
    stack
)

from pandas import (
    read_csv,
    DataFrame
)

from pyDOE2 import (
    lhs
)

from .args import (
    DEFAULT_SEED
)

# from typing import (
#     Dict,
#     List,
#     Tuple
# )


def input_importer(cfps_parameters) -> DataFrame:
    """
    Import tsv input into a dataframe

    Parameters
    ----------
    input_file : tsv file
        tsv with list of cfps parameters and relative features

    Returns
    -------
    cfps_parameters_df : DataFrame
        Pandas dataframe populated with cfps_parameters data
    """
    cfps_parameters_df = read_csv(
                        cfps_parameters,
                        sep='\t')
    return cfps_parameters_df


def input_processor(cfps_parameters_df: DataFrame):
    """
    Determine variable and fixed parameters, and maximum concentrations.

    Parameters
    ----------
    input_df : 2d-array
        N-by-samples array where values are uniformly spaced between 0 and 1.

    Returns
    -------
    fixed_parameters : 1d-array
        N-fixed-parameters array with all of the fixed parameters names.

    variable_parameters : 1d-array
        N-variable-parameters array with all of the variable parameters names.

    n_variable_parameters : int
        Number of variable parameters.

    maximum_variable_concentrations : 1d-array
        N-maximum-concentrations array with variable concentrations values.

    maximum_fixed_concentrations : list
        N-maximum-concentrations list with fixed concentrations values.
    """
    for status in cfps_parameters_df.columns:

        if (cfps_parameters_df[status] == 'fixed').any():
            fixed_parameters = cfps_parameters_df[
                cfps_parameters_df['Status'] == 'fixed']
            maximum_fixed_concentrations = list(
                fixed_parameters['Maximum concentration'])
            fixed_parameters = array(fixed_parameters['Parameter'])

        if (cfps_parameters_df[status] == 'variable').any():
            variable_parameters = cfps_parameters_df[
                cfps_parameters_df['Status'] == 'variable']
            maximum_variable_concentrations = array(
                variable_parameters['Maximum concentration'])
            variable_parameters = array(variable_parameters['Parameter'])
            n_variable_parameters = shape(variable_parameters)[0]
            maximum_variable_concentrations = reshape(
                maximum_variable_concentrations,
                (1, n_variable_parameters))

    return (n_variable_parameters,
            maximum_fixed_concentrations,
            fixed_parameters,
            maximum_variable_concentrations,
            variable_parameters)


def levels_array_generator(
        n_variable_parameters,
        n_ratios,
        seed: int = DEFAULT_SEED):
    """
    Generate sampling array.
    Refactor sampling array with levels values.

    Parameters
    ----------
    n_variable_parameters : int
        Number of variable parameters.

    n_ratios : int
        Number of concentration ratios for all factor

    seed: int
        Seed-number to controls the seed and random draws

    Returns
    -------
    levels_array : 2d-array
        N-by-samples array with uniformly spaced values between 0 and 1.
    """
    sampling = lhs(
        n_variable_parameters,
        samples=99,
        criterion='center',
        random_state=seed)

    levels = (1 / n_ratios)
    level_1 = levels*0
    level_2 = levels*1
    level_3 = levels*3
    level_4 = levels*4
    level_5 = levels*5

    levels_list = []

    for sample in sampling:
        new_sample = []

        for parameter in sample:

            if parameter >= 0 and parameter < 0.2:
                new_sample.append(level_1)
                continue

            if parameter >= 0.2 and parameter < 0.4:
                new_sample.append(level_2)
                continue

            if parameter >= 0.4 and parameter < 0.6:
                new_sample.append(level_3)
                continue

            if parameter >= 0.6 and parameter < 0.8:
                new_sample.append(level_4)
                continue

            if parameter >= 0.8 and parameter <= 1:
                new_sample.append(level_5)
                continue

        levels_list.append(new_sample)

    levels_array = asarray(
        levels_list)

    return levels_array


def variable_concentrations_array_generator(
        levels_array,
        maximum_variable_concentrations):
    """
    Multiply levels array by maximum variable concentrations array.

    Parameters
    ----------
    levels_array : 2d-array
        N-by-samples array with uniformly spaced values between 0 and 1.

    maximum_variable_concentrations : 1d-array
        N-maximum-concentrations array with values for each variable factor.

    Returns
    -------
    variable_concentrations_array : 2d-array
        N-by-samples array with variable concentrations values for each factor.
    """
    variable_concentrations_array = multiply(
        levels_array,
        maximum_variable_concentrations)
    return variable_concentrations_array


def fixed_concentrations_array_generator(
        variable_concentrations_array,
        maximum_fixed_concentrations):
    """
    Generate fixed concentrations array

    Parameters
    ----------
    variable_concentrations_array : 2d-array
        N-by-samples array with variable concentrations values for each factor.

    maximum_fixed_concentrations : list
        N-maximum-concentrations list with values for each variable factor.

    Returns
    -------
    fixed_concentrations_array : 2d-array
        N-by-samples array with fixed concentrations values for each factor.
    """
    nrows_variable_concentrations_array = shape(
        variable_concentrations_array)[0]

    fixed_concentrations_array_list = []

    for maximum_fixed_concentration in maximum_fixed_concentrations:
        fixed_concentrations_array = full(
            nrows_variable_concentrations_array,
            maximum_fixed_concentration)

        fixed_concentrations_array_list.append(
            fixed_concentrations_array)

    fixed_concentrations_array = stack(
        fixed_concentrations_array_list, axis=-1)

    return fixed_concentrations_array


# def maximum_concentrations_sample_generator(input_df):
#     """
#     Generate control sample with all factors at maximum concentration

#     Parameters
#     ----------
#     input_df : dataframe
#         User csv input imported into a dataframe.

#     Returns
#     -------
#     maximum_concentrations_sample : 1d-array
#         N-maximum-concentrations array with values for all factor.
#     """

#     maximum_concentrations_dict = dict(
#         input_df[['Parameter', 'Maximum concentration']].to_numpy())
#     maximum_concentrations_sample = fromiter(
#         maximum_concentrations_dict.values(),
#         dtype=float)

#     nrows_maximum_concentrations_sample = shape(
#         maximum_concentrations_sample)[0]

#     maximum_concentrations_sample = reshape(
#         maximum_concentrations_sample,
#         (1, nrows_maximum_concentrations_sample))

#     return maximum_concentrations_sample


# def control_concentrations_array_generator():
#     """
#     Concatenate all control samples into a single array
#     Template in case more controls are needed
#
#     Parameters
#     ----------
#     maximum_concentrations_sample : 1d-array
#         N-maximum-concentrations array with maximum concentrations values.
#
#     Returns
#     -------
#     control_concentrations_array : nd-array
#         N-by-samples array. Concatenation of all control samples.
#     """

#     control_concentrations_array = concatenate(
#         (), axis=0)
#     return control_concentrations_array


def initial_plates_generator(
        variable_concentrations_array,
        fixed_concentrations_array,
        input_df):
    """
    Concatenate variable and fixed concentrations array with control array.

    Parameters
    ----------
    variable_concentrations_array : 2d-array
        N-by-samples array with variable concentrations values for each factor.

    fixed_concentrations_array : 2d-array
        N-fixed-concentrations array with values for each factor.

    maximum_concentrations_sample : 1d-array
        N-maximum-concentrations array with values for all factor.

    Returns
    -------
    initial_set_df : dataframe
        Matrix generated from the concatenation of all samples.

    normalizer_set_df : dataframe
        Duplicate of initial_set. 0 is assigned to the GOI-DNA column.

    autofluorescence_set_df : dataframe
        Duplicate of normalizer_set. 0 is assigned to the GFP-DNA column.

    all_parameters: List
        List of the name of all cfps parameters
    """

    # all_concentrations_array = concatenate(
    #     (variable_concentrations_array,
    #         fixed_concentrations_array,),
    #     axis=1)

    # initial_set_array = concatenate(
    #     (all_concentrations_array,
    #         maximum_concentrations_sample),
    #     axis=0)

    initial_set_array = concatenate(
        (variable_concentrations_array,
            fixed_concentrations_array,),
        axis=1)

    initial_set_df = DataFrame(initial_set_array)

    normalizer_set_df = initial_set_df.copy()
    all_parameters = input_df['Parameter'].tolist()
    normalizer_set_df.columns = all_parameters
    normalizer_set_df['GOI-DNA'] = normalizer_set_df['GOI-DNA']*0

    autolfuorescence_set_df = normalizer_set_df.copy()
    autolfuorescence_set_df.columns = all_parameters
    autolfuorescence_set_df['GFP-DNA'] = normalizer_set_df['GFP-DNA']*0

    return (initial_set_df,
            normalizer_set_df,
            autolfuorescence_set_df,
            all_parameters)


def save_intial_plates(
        initial_set_df,
        normalizer_set_df,
        autolfuorescence_set_df,
        all_parameters,
        output_folder: str):
    """
    Save Pandas dataframes in tsv files

    Parameters
    ----------
    initial_set_df : dataframe
        Matrix generated from the concatenation of all samples.

    normalizer_set_df : dataframe
        Duplicate of initial_set. 0 is assigned to the GOI-DNA column.

    autofluorescence_set_df : dataframe
        Duplicate of normalizer_set. 0 is assigned to the GFP-DNA column.

    all_parameters: List
        List of the name of all cfps parameters
    
    output_folder: str
        Path where store output files
    """

    if not os_path.exists(output_folder):
        os_mkdir(output_folder)

    initial_set_df.to_csv(
        os_path.join(
            output_folder,
            'initial_set.tsv'),
        sep='\t',
        header=all_parameters,
        index=False)

    normalizer_set_df.to_csv(
        os_path.join(
            output_folder,
            'normalizer_set.tsv'),
        sep='\t',
        header=all_parameters,
        index=False)

    autolfuorescence_set_df.to_csv(
        os_path.join(
            output_folder,
            'autolfuorescence_set.tsv'),
        sep='\t',
        header=all_parameters,
        index=False)
