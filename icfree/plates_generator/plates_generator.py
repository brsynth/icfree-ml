#!/usr/bin/env python
# coding: utf-8

from os import (
    path as os_path,
    mkdir as os_mkdir
)

from numpy import (
    round as np_round,
    argmin as np_argmin,
    concatenate as np_concatenate,
    asarray as np_asarray,
    frompyfunc as np_frompyfunc,
    append as np_append,
    arange as np_arange,
    set_printoptions as np_set_printoptions,
    double as np_double,
    abs as np_abs,
    multiply as np_multiply,
    inf as np_inf,
    ndarray as np_ndarray,
    array as np_array,
    fromiter as np_fromiter
)

from pandas import (
    read_csv as pd_read_csv,
    DataFrame
)

from pyDOE2 import (
    lhs
)

from logging import (
    Logger,
    getLogger
)

from typing import (
    Dict
)

from .args import (
    DEFAULT_OUTPUT_FOLDER,
    DEFAULT_DOE_NB_CONCENTRATIONS,
    DEFAULT_DOE_NB_SAMPLES
)

# To print numpy arrays in full
np_set_printoptions(threshold=np_inf)


def input_importer(
    cfps_parameters,
    logger: Logger = getLogger(__name__)
) -> DataFrame:
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
    cfps_parameters_df = pd_read_csv(
                        cfps_parameters,
                        sep='\t')

    logger.debug(f'CFPs parameters dataframe: {cfps_parameters_df}')

    return cfps_parameters_df


def input_processor(
    cfps_parameters_df: DataFrame,
    logger: Logger = getLogger(__name__)
) -> Dict:
    """
    Determine variable and fixed parameters, and maximum concentrations.

    Parameters
    ----------
    input_df: 2d-array
        N-by-samples array where values are uniformly spaced between 0 and 1.

    Returns
    -------
    parameters: dict
        Dictionnary of parameters.
        First level is indexed on 'Status' column.
        Second level is indexed on 'Parameter' column.
    """
    parameters = {}

    # For each different value of 'Status' column
    for status in cfps_parameters_df['Status'].unique():
        # Create a dict indexed on 'Parameter' value
        parameters[status] = cfps_parameters_df[
            cfps_parameters_df['Status'] == status
        ].loc[
            :, cfps_parameters_df.columns != 'Status'
        ].set_index('Parameter').T.to_dict('dict')

    for key in ['doe', 'const']:
        if key not in parameters:
            parameters[key] = {}

    # Split concentration strings into lists
    for comb in parameters:
        for parameter in parameters[comb].values():
            if isinstance(parameter['Concentration ratios'], str):
                parameter['Concentration ratios'] = list(
                    map(
                        float,
                        parameter['Concentration ratios'].split(',')
                    )
                )
            else:
                parameter['Concentration ratios'] = None

    logger.debug(f'cfps_parameters_df: {cfps_parameters_df}')
    logger.debug(f'PARAMETERS: {parameters}')

    return parameters


def set_concentration_ratios(
    concentration_ratios: Dict,
    all_doe_nb_concentrations: int = DEFAULT_DOE_NB_CONCENTRATIONS,
    all_doe_concentration_ratios: np_ndarray = None,
    logger: Logger = getLogger(__name__)
) -> Dict:
    """
    Set the concentration ratios for each parameter.

    Parameters
    ----------
    concentation_ratios : Dict
        Parameter concentration ratios.

    all_doe_nb_concentrations : int
        Number of concentration ratios for all factor

    all_doe_concentration_ratios: np_ndarray
        Possible concentration values (between 0.0 and 1.0) for all factors.
        If no list is passed, a default list will be built,
        e.g. if doe_nb_concentrations = 5 the list of considered
        discrete conentrations will be: 0.0 0.25 0.5 0.75 1.0

    Returns
    -------
    doe_concentration_ratios : Dict
        Concentration ratios for each parameter.
    """

    # If concentration ratios are not defined for all parameters
    if all_doe_concentration_ratios is None:
        all_doe_concentration_ratios = np_append(
            np_arange(0.0, 1.0, 1/(all_doe_nb_concentrations-1)),
            1.0
        )

    doe_concentration_ratios = dict(concentration_ratios)

    for param in concentration_ratios:
        if concentration_ratios[param] is None:
            # Set concentration ratios to default value
            doe_concentration_ratios[param] = all_doe_concentration_ratios

    return doe_concentration_ratios


def doe_levels_generator(
    n_variable_parameters,
    concentration_ratios: Dict,
    doe_nb_samples: int = DEFAULT_DOE_NB_SAMPLES,
    seed: int = None,
    logger: Logger = getLogger(__name__)
):
    """
    Generate sampling array.
    Refactor sampling array with rounded values.

    Parameters
    ----------
    n_variable_parameters : int
        Number of variable parameters.

    concentration_ratios: Dict
        Concentration ratios for each parameter.

    doe_nb_samples: int
        Number of samples to generate for all factors

    seed: int
        Seed-number to controls the seed and random draws

    Returns
    -------
    levels_array : 2d-array
        N-by-samples array with uniformly spaced values between 0 and 1.
    """

    if n_variable_parameters <= 0:
        return np_asarray([])

    if seed is None:
        sampling = lhs(
            n_variable_parameters,
            samples=doe_nb_samples,
            criterion=None
        )
    else:
        sampling = lhs(
            n_variable_parameters,
            samples=doe_nb_samples,
            criterion=None,
            random_state=seed
        )

    logger.debug(f'LHS: {sampling}')

    # # Discretize LHS values
    # def rounder(values):
    #     def f(x):
    #         idx = np_argmin(np_abs(values - x))
    #         return values[idx]
    #     return np_frompyfunc(f, 1, 1)

    logger.debug(f'ROUNDED VALUES:\n{concentration_ratios}')
    concentration_ratios_lst = list(concentration_ratios.values())

    # Round LHS values
    rounded_sampling = list(sampling)
    for i in range(len(rounded_sampling)):
        sample = sampling[i]
        # Round each value of the sample
        for j in range(len(sample)):
            # Search the index of the bin value
            idx_min = np_argmin(
                np_abs(concentration_ratios_lst[j] - sample[j])
            )
            # print(sample[j], concentration_ratios_lst[j], concentration_ratios_lst[j][idx_min])
            sample[j] = concentration_ratios_lst[j][idx_min]

    # rounded_sampling = rounder(np_asarray(concentration_ratios))(sampling)
    logger.debug(f'ROUNDED LHS:\n{rounded_sampling}')

    return np_asarray(rounded_sampling)


def levels_to_concentrations(
    levels_array,
    maximum_concentrations,
    decimals: int = 3,
    logger: Logger = getLogger(__name__)
):
    """
    Multiply levels array by maximum concentrations array.

    Parameters
    ----------
    levels_array : 2d-array
        N-by-samples array with uniformly spaced values between 0 and 1.

    maximum_concentrations : 1d-array
        N-maximum-concentrations array with values for each variable factor.

    Returns
    -------
    concentrations : 2d-array
        N-by-samples array with concentrations values for each factor.
    """
    logger.debug(f'LEVELS ARRAY:\n{levels_array}')
    logger.debug(f'MAXIMUM CONCENTRATIONS:\n{maximum_concentrations}')
    if levels_array is None or levels_array.size <= 0:
        return np_asarray([])

    concentrations = np_multiply(
        levels_array,
        maximum_concentrations
    )
    concentrations = np_round(
        concentrations.astype(np_double),
        decimals
    )
    logger.debug(f'CONCENTRATIONS:\n{concentrations}')

    return concentrations


def plates_generator(
    doe_concentrations,
    dna_concentrations,
    const_concentrations,
    parameters,
    logger: Logger = getLogger(__name__)
):
    """
    Concatenate variable and fixed concentrations array with control array.

    Parameters
    ----------
    doe_concentrations : 1d-array
        Array with variable concentrations values for each factor.

    dna_concentrations : 1d-array
        Array with values for each factor which are related to DNA
        with bin values (0 or max. conc.).

    const_concentrations : 1d-array
        Array with constant values for each factor.

    maximum_concentrations_sample : 1d-array
        N-maximum-concentrations array with values for all factor.

    parameters: dict
        Dictionnary of cfps parameters.

    Returns
    -------
    initial_set_df : dataframe
        Matrix generated from the concatenation of all samples.

    normalizer_set_df : dataframe
        Duplicate of initial_set. 0 is assigned to the GOI-DNA column.

    autofluorescence_set_df : dataframe
        Duplicate of normalizer_set. 0 is assigned to the GFP-DNA column.

    parameters: List
        List of the name of cfps parameters
    """
    # initial_set_array = concatenate(
    #     (all_concentrations_array,
    #         maximum_concentrations_sample),
    #     axis=0)

    logger.debug(f'DOE_CONCENTRATIONS:\n{doe_concentrations}')
    logger.debug(f'CONST_CONCENTRATIONS: {const_concentrations}')
    logger.debug(f'DNA_CONCENTRATIONS: {dna_concentrations}')
    logger.debug(f'PARAMETERS:\n{parameters}')

    # Add DoE combinatorial parameters
    headers = parameters['doe']
    initial_set_array = doe_concentrations.copy()

    # Add constant parameters
    # If the is no DoE concentrations
    if len(initial_set_array) == 0:
        # Then fill with const concentrations
        initial_set_array = [
            np_fromiter(const_concentrations.values(), dtype=float)
        ]
    else:  # Else, add const concentrations to DoE ones
        initial_set_array = [
            np_concatenate(
                (concentrations,
                 list(const_concentrations.values()))
            )
            for concentrations in initial_set_array
        ]
    headers += parameters['const']

    # Add combinatorial parameters
    initial_set_array = [
        np_concatenate((concentrations, list(dna_concentrations.values())))
        for concentrations in initial_set_array
    ]
    headers += sum(
        [
            v for k, v
            in parameters.items()
            if k.startswith('dna')],
        []
    )

    # Create initial set with partial concentrations
    initial_set_df = DataFrame(initial_set_array)
    initial_set_df.columns = headers
    logger.debug(f'INITIAL SET:\n{initial_set_df}')

    # Create normalizer set with GOI to 0
    normalizer_set_df = initial_set_df.copy()
    normalizer_set_df.columns = headers
    if 'dna_fluo' in parameters:
        normalizer_set_df[parameters['dna_fluo']] *= 0
    logger.debug(f'NORMALIZER SET:\n{normalizer_set_df}')

    # Create normalizer set with GFP to 0
    autofluorescence_set_df = normalizer_set_df.copy()
    autofluorescence_set_df.columns = headers
    if 'dna_goi' in parameters:
        autofluorescence_set_df[parameters['dna_goi']] *= 0
    logger.debug(f'BACKGROUND SET:\n{autofluorescence_set_df}')

    logger.debug(f'HEADERS: {headers}')

    return {
        'parameters': headers,
        'initial': initial_set_df,
        'normalizer': normalizer_set_df,
        'background': autofluorescence_set_df
    }


def save_plates(
        initial_set_df,
        normalizer_set_df,
        autofluorescence_set_df,
        all_parameters,
        output_folder: str = DEFAULT_OUTPUT_FOLDER):
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

    autofluorescence_set_df.to_csv(
        os_path.join(
            output_folder,
            'autofluorescence_set.tsv'),
        sep='\t',
        header=all_parameters,
        index=False)
