#!/usr/bin/env python
#coding: utf-8

#Import Python packages
import pandas as pd #Python data analysis package
import numpy as np #Fundamental package for scientific computing in Python
from pyDOE2 import * #Experimental design package for Python

def input_importer(input_file):
    """
    Recover user csv input and import it into a dataframe

    Parameters
    ----------
    input_file : csv file
        User csv input with: list of parameters, status (variable/fixed), maximum concentration

    Returns
    -------
    input_df : 2d-array
        An n-by-samples design matrix that has been normalized so factor values are uniformly spaced between zero and one.
    """

    global input_df 
    input_df = pd.read_csv(input_file)
    return input_df

def input_processor(input_df):
    """
    Parse dataframe. Determine variable and fixed parameters and respective maximum concentrations.

    Parameters
    ----------
    input_df : 2d-array
        An n-by-samples design matrix that has been normalized so factor values are uniformly spaced between zero and one.

    Returns
    -------
    fixed_parameters : 1d-array
        An n-fixed-parameters array with the all of the fixed parameters names.

    variable_parameters : 1d-array
        An n-variable-parameters array with the all of the variable parameters names.

    n_variable_parameters : int
        The number of variable parameters.

    maximum_variable_concentrations : 1d-array
        An n-maximum-concentrations array with the maximum concentrations values for each variable factor.

    maximum_fixed_concentrations : list
        An n-maximum-concentrations list with the maximum concentrations values for each fixed factor.
    """

    global fixed_parameters
    global variable_parameters
    global n_variable_parameters
    global maximum_variable_concentrations
    global maximum_fixed_concentrations
    
    for status in input_df.columns:

        if (input_df[status] == 'fixed').any():
            fixed_parameters = input_df[input_df['Status'] == 'fixed']
            maximum_fixed_concentrations = fixed_parameters['Maximum concentration'].tolist()
            fixed_parameters = fixed_parameters['Parameter'].to_numpy()
    
        if (input_df[status] == 'variable').any():
            variable_parameters = input_df[input_df['Status'] == 'variable']
            maximum_variable_concentrations = variable_parameters['Maximum concentration'].to_numpy()
            variable_parameters = variable_parameters['Parameter'].to_numpy()
            n_variable_parameters = np.shape(variable_parameters)[0]
            maximum_variable_concentrations = np.reshape(maximum_variable_concentrations, (1, n_variable_parameters))

    return maximum_fixed_concentrations, fixed_parameters, n_variable_parameters, maximum_variable_concentrations, variable_parameters       

#
sampling = lhs(n_variable_parameters, samples=100, criterion='center')

def levels_array_generator(n_ratios):
    """
    Define concentration levels. Define thresholds. Replace levels in the sampling array. 

    Parameters
    ----------
    n_ratios : int
        The number of concentration ratios for all factor 

    Returns
    -------
    levels_array : 2d-array
        An n-by-samples design matrix that has been normalized so factor values are uniformly spaced between zero and one.
    """

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

            if parameter >= level_1 and parameter < level_2:
                new_sample.append(level_1)
                continue
            
            if parameter >= level_2 and parameter < level_3:
                new_sample.append(level_2)
                continue
            
            if parameter >= level_3 and parameter < level_4:
                new_sample.append(level_3)
                continue
            
            if parameter >= level_4 and parameter < level_5:
                new_sample.append(level_4)
                continue
                
            if parameter >= level_5:
                new_sample.append(level_5)
                continue

        levels_list.append(new_sample)

    global levels_array
    levels_array = np.asarray(levels_list)

    return levels_array

def variable_concentrations_array_generator(levels_array, maximum_variable_concentrations):
    """
    Multiply levels array by maximum concentrations vector of variable parameters

    Parameters
    ----------
    levels_array : 2d-array
        An n-by-samples matrix that has been normalized so factor values are uniformly spaced between zero and one.

    maximum_variable_concentrations : 1d-array
        An n-maximum-concentrations array with the maximum concentrations values for each variable factor.
    
    Returns
    -------
    variable_concentrations_array : 2d-array
        An n-by-samples matrix with different values of variable concentrations for each factor in each sample.
    """

    global variable_concentrations_array
    variable_concentrations_array = np.multiply(levels_array, maximum_variable_concentrations)
    return variable_concentrations_array

def fixed_concentrations_array_generator(variable_concentrations_array, maximum_fixed_concentrations):
    """
    Generate fixed concentrations array by iterating through the fixed concentrations list

    Parameters
    ----------
    variable_concentrations_array : 2d-array
        An n-by-samples matrix with different values of concentrations for each factor in each sample.

    maximum_fixed_concentrations : list
        An n-maximum-concentrations list with the maximum concentrations values for each fixed factor.
    
    Returns
    -------
    fixed_concentrations_array : 2d-array
        An n-by-samples matrix with values of fixed concentrations for each factor in each sample.
    """
    
    nrows_variable_concentrations_array = np.shape(variable_concentrations_array)[0]
    fixed_concentrations_array_list = []

    global fixed_concentrations_array

    for maximum_fixed_concentration in maximum_fixed_concentrations:
        fixed_concentrations_array = np.full(nrows_variable_concentrations_array, maximum_fixed_concentration)
        fixed_concentrations_array_list.append(fixed_concentrations_array)

    fixed_concentrations_array = np.stack(fixed_concentrations_array_list, axis=-1)

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
        An n-maximum-concentrations matrix with the maximum concentrations values for all factor
    """
        
    global maximum_concentrations_dict
    maximum_concentrations_dict = dict(input_df[['Parameter', 'Maximum concentration']].to_numpy())
        
    global maximum_concentrations_sample
    maximum_concentrations_sample = np.fromiter(maximum_concentrations_dict.values(), dtype=float)
    nrows_maximum_concentrations_sample = np.shape(maximum_concentrations_sample)[0]
    maximum_concentrations_sample = np.reshape(maximum_concentrations_sample, (1, nrows_maximum_concentrations_sample))

    return maximum_concentrations_dict, maximum_concentrations_sample
    
def autofluorescence_sample_generator(maximum_concentrations_dict): 
    """
    Generate control sample with all factors (but DNA) at maximum concentration to account for autoluorescence

    Parameters
    ----------
    input : dataframe
        User csv input imported into a pandas dataframe.
  
    Returns
    -------
    autofluorescence_concentrations_sample : 1d-array
        An n-maximum-concentrations matrix with the maximum concentrations values for all factor without DNA
    """
    autofluorescence_dict = maximum_concentrations_dict

    if 'GOI-DNA' in autofluorescence_dict:
        autofluorescence_dict['GOI-DNA']=0

    if 'GFP-DNA' in autofluorescence_dict:
        autofluorescence_dict['GFP-DNA']=0

    global autofluorescence_sample
    autofluorescence_sample = np.fromiter(autofluorescence_dict.values(), dtype=float)
    nrows_autofluorescence_sample = np.shape(autofluorescence_sample)[0]
    autofluorescence_sample = np.reshape(autofluorescence_sample, (1, nrows_autofluorescence_sample))

    return autofluorescence_sample

def control_concentrations_array_generator(maximum_concentrations_sample, autofluorescence_sample):
    """
    Concatenate all control samples into a single array
    
    Parameters
    ----------
    maximum_concentrations_sample : 1d-array
        An n-maximum-concentrations matrix with the maximum concentrations values for all factor
    
    autofluorescence_concentrations_sample : 1d-array
        An n-maximum-concentrations matrix with the maximum concentrations values for all factor without DNA

    Returns
    -------
    control_concentrations_array : 2d-array
        An n-by-samples matrix generated from the concatenation of all control samples.
    """
    global control_concentrations_array
    control_concentrations_array = np.concatenate((maximum_concentrations_sample, autofluorescence_sample), axis=0)
    return control_concentrations_array

def initial_training_set_generator(variable_concentrations_array, fixed_concentrations_array, control_concentrations_array):
    """
    Concatenate variable contrations array,  fixed contenrations array, control concentrations samples into a single array
    
    Parameters
    ----------
    variable_concentrations_array : 2d-array
        An n-by-samples matrix with different values of concentrations for each factor in each sample.
    
    fixed_concentrations_array : 2d-array
        An n-by-samples matrix with values of fixed concentrations for each factor in each sample.
    
    control_concentrations_array : 2d-array 
        An n-by-samples matrix generated from the concatenation of all control samples.
    
    Returns
    -------
    full_concentrations_df : dataframe
        An n-by-samples matrix generated from the concatenation of all samples.
    """    
    
    default_concentrations_array = np.concatenate((variable_concentrations_array, fixed_concentrations_array), axis=1)
    full_concentrations_array = np.concatenate((default_concentrations_array, control_concentrations_array), axis=0)
    
    global full_concentrations_df
    full_concentrations_df = pd.DataFrame(full_concentrations_array)

    return full_concentrations_df

def save_intial_training_set(input_df, full_concentrations_df):
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
    global output_file
    output_file = full_concentrations_df.to_csv('output/initial_training_set.csv', header=all_parameters)
    return output_file

if __name__ == "__main__":
    input_importer('input/proCFPS_parameters.csv')
    input_processor(input_df)
    levels_array_generator(5)
    variable_concentrations_array_generator(levels_array, maximum_variable_concentrations)
    fixed_concentrations_array_generator(variable_concentrations_array, maximum_fixed_concentrations)
    maximum_concentrations_sample_generator(input_df)
    autofluorescence_sample_generator(maximum_concentrations_dict)
    control_concentrations_array_generator(maximum_concentrations_sample, autofluorescence_sample)
    initial_training_set_generator(variable_concentrations_array, fixed_concentrations_array, control_concentrations_array)
    save_intial_training_set(input_df, full_concentrations_df)