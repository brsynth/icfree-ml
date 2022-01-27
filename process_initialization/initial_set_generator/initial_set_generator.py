#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
from pyDOE2 import (
    lhs
)


def input_importer(input_file):
    """
    Import csv input into a dataframe

    Parameters
    ----------
    input_file : csv file
        csv with list of parameters and relative features

    Returns
    -------
    input_df : dataframe
        dataframe populated with input_file data
    """

    input_df = pd.read_csv(input_file)
    return input_df


def input_processor(input_df):
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

    for status in input_df.columns:

        if (input_df[status] == 'fixed').any():
            fixed_parameters = input_df[input_df['Status'] == 'fixed']
            maximum_fixed_concentrations = list(
                fixed_parameters['Maximum concentration'])
            fixed_parameters = np.array(fixed_parameters['Parameter'])

        if (input_df[status] == 'variable').any():
            variable_parameters = input_df[input_df['Status'] == 'variable']
            maximum_variable_concentrations = np.array(
                variable_parameters['Maximum concentration'])
            variable_parameters = np.array(variable_parameters['Parameter'])
            n_variable_parameters = np.shape(variable_parameters)[0]
            maximum_variable_concentrations = np.reshape(
                maximum_variable_concentrations,
                (1, n_variable_parameters))

    return (n_variable_parameters,
            maximum_fixed_concentrations,
            fixed_parameters,
            maximum_variable_concentrations,
            variable_parameters)


def levels_array_generator(
        n_variable_parameters,
        n_ratios):
    """
    LHS sampling and replace values in the sampling array with levels.

    Parameters
    ----------
    n_variable_parameters : int
        Number of variable parameters.

    n_ratios : int
        Number of concentration ratios for all factor

    Returns
    -------
    levels_array : 2d-array
        N-by-samples array with uniformly spaced values between 0 and 1.
    """

    sampling = lhs(
        n_variable_parameters,
        samples=100,
        criterion='center')

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

    levels_array = np.asarray(
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

    variable_concentrations_array = np.multiply(
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

    nrows_variable_concentrations_array = np.shape(
        variable_concentrations_array)[0]

    fixed_concentrations_array_list = []

    for maximum_fixed_concentration in maximum_fixed_concentrations:
        fixed_concentrations_array = np.full(
            nrows_variable_concentrations_array,
            maximum_fixed_concentration)

        fixed_concentrations_array_list.append(
            fixed_concentrations_array)

    fixed_concentrations_array = np.stack(
        fixed_concentrations_array_list, axis=-1)

    return fixed_concentrations_array


def maximum_concentrations_sample_generator(input_df):
    """
    Generate control sample with all factors at maximum concentration

    Parameters
    ----------
    input_df : dataframe
        User csv input imported into a dataframe.

    Returns
    -------
    maximum_concentrations_sample : 1d-array
        N-maximum-concentrations array with values for all factor.
    """

    maximum_concentrations_dict = dict(
        input_df[['Parameter', 'Maximum concentration']].to_numpy())
    maximum_concentrations_sample = np.fromiter(
        maximum_concentrations_dict.values(),
        dtype=float)

    nrows_maximum_concentrations_sample = np.shape(
        maximum_concentrations_sample)[0]

    maximum_concentrations_sample = np.reshape(
        maximum_concentrations_sample,
        (1, nrows_maximum_concentrations_sample))

    return maximum_concentrations_dict, maximum_concentrations_sample


def autofluorescence_sample_generator(maximum_concentrations_dict):
    """
    Generate autofluorescence sample.
    All factors (w/ DNA) are at maximum concentration.

    Parameters
    ----------
    input : dataframe
        User csv input imported into a dataframe.

    Returns
    -------
    autofluorescence_concentrations_sample : 1d-array
        N-maximum-concentrations array with values for all factor (w/ DNA).
    """

    autofluorescence_dict = maximum_concentrations_dict

    if 'GOI-DNA' in autofluorescence_dict:
        autofluorescence_dict['GOI-DNA'] = 0

    if 'GFP-DNA' in autofluorescence_dict:
        autofluorescence_dict['GFP-DNA'] = 0

    autofluorescence_sample = np.fromiter(
        autofluorescence_dict.values(), dtype=float)

    nrows_autofluorescence_sample = np.shape(
        autofluorescence_sample)[0]

    autofluorescence_sample = np.reshape(
        autofluorescence_sample, (1, nrows_autofluorescence_sample))

    return autofluorescence_sample


def control_concentrations_array_generator(
        maximum_concentrations_sample,
        autofluorescence_sample):
    """
    Concatenate all control samples into a single array

    Parameters
    ----------
    maximum_concentrations_sample : 1d-array
        N-maximum-concentrations array with maximum concentrations values.

    autofluorescence_concentrations_sample : 1d-array
        N-maximum-concentrations array with values for factors w/o DNA.

    Returns
    -------
    control_concentrations_array : 2d-array
        N-by-samples array. Concatenation of all control samples.
    """

    control_concentrations_array = np.concatenate(
        (maximum_concentrations_sample, autofluorescence_sample), axis=0)
    return control_concentrations_array


def initial_training_set_generator(
        variable_concentrations_array,
        fixed_concentrations_array,
        control_concentrations_array,
        input_df):
    """
    Concatenate variable and fixed concentrations array with control array.

    Parameters
    ----------
    variable_concentrations_array : 2d-array
        N-by-samples array with variable concentrations values for each factor.

    fixed_concentrations_array : 2d-array
        N-fixed-concentrations array with values for each factor.

    control_concentrations_array : 2d-array
        N-by-samples array. Concatenation of all control samples.

    Returns
    -------
    initial_set : dataframe
        Matrix generated from the concatenation of all samples.

    initial_set_without_goi : dataframe
        Duplicate of initial_training_set. 0 is assigned to the GOI-DNA column.
    """

    all_concentrations_array = np.concatenate(
        (variable_concentrations_array, fixed_concentrations_array),
        axis=1)

    initial_set_array = np.concatenate(
        (all_concentrations_array, control_concentrations_array),
        axis=0)

    initial_set = pd.DataFrame(initial_set_array)
    initial_set_without_goi = initial_set.copy()
    all_parameters = input_df['Parameter'].tolist()
    initial_set_without_goi.columns = all_parameters
    initial_set_without_goi['GOI-DNA'] = initial_set_without_goi['GOI-DNA']*0

    return initial_set, initial_set_without_goi


def save_intial_training_set(
        input_df,
        initial_set,
        initial_set_without_goi):
    """
    Save initial training set in csv file

    Parameters
    ----------
    input_df : dataframe
        User csv input imported into dataframe.

    full_concentrations_df : dataframe
        An n-by-samples matrix generated from the concatenation of all samples.

    Returns
    -------
    initial_training_set.csv : csv file
        full_concentrations_df data in a csv file
    """

    all_parameters = input_df['Parameter'].tolist()

    initial_set = initial_set.to_csv(
        'initial_training_set.csv',
        header=all_parameters)

    initial_set_without_goi = initial_set_without_goi.to_csv(
        'initial_training_set_without_goi.csv',
        header=all_parameters)

    return initial_set, initial_set_without_goi
