#!/usr/bin/env python
# coding: utf-8

from os import (
    path as os_path,
    mkdir as os_mkdir
)

from numpy import (
    argmin as np_argmin,
    concatenate,
    array,
    asarray as np_asarray,
    ndarray as np_ndarray,
    frompyfunc as np_frompyfunc,
    abs as np_abs,
    append as np_append,
    arange,
    shape,
    reshape,
    multiply,
    full,
    stack,
    inf as np_inf,
    set_printoptions as np_set_printoptions
)

from pandas import (
    read_csv,
    DataFrame
)

from pyDOE2 import lhs

from logging import (
    Logger,
    getLogger
)

from .args import (
    DEFAULT_SEED,
    DEFAULT_OUTPUT_FOLDER,
    DEFAULT_DOE_NB_CONCENTRATIONS,
    DEFAULT_DOE_NB_SAMPLES
)

# To print numpy arrays in full
np_set_printoptions(threshold=np_inf)


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


def input_processor(cfps_parameters_df: DataFrame, logger: Logger = getLogger(__name__)):
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

    # fixed_parameters: 1d-array
    #     N-fixed-parameters array with all of the fixed parameters names.

    # variable_parameters: 1d-array
    #     N-variable-parameters array with all of the variable parameters names.

    # n_variable_parameters: int
    #     Number of variable parameters.

    # maximum_variable_concentrations: 1d-array
    #     N-maximum-concentrations array with variable concentrations values.

    # maximum_fixed_concentrations: list
    #     N-maximum-concentrations list with fixed concentrations values.
    """
    parameters = {}

    # For each different value of 'Status' column
    for status in cfps_parameters_df['Status'].unique():
        # Create a dict indexed on 'Parameter' value
        parameters[status] = cfps_parameters_df[
            cfps_parameters_df['Status'] == status
        ].loc[
            :, cfps_parameters_df.columns!='Status'
        ].set_index('Parameter').T.to_dict('dict')

    logger.debug(f'PARAMETERS: {parameters}')

    return parameters

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
    doe_nb_concentrations: int = DEFAULT_DOE_NB_CONCENTRATIONS,
    doe_concentrations: np_ndarray = None,
    doe_nb_samples: int = DEFAULT_DOE_NB_SAMPLES,
    seed: int = DEFAULT_SEED,
    logger: Logger = getLogger(__name__)
):
    """
    Generate sampling array.
    Refactor sampling array with rounded values.

    Parameters
    ----------
    n_variable_parameters : int
        Number of variable parameters.

    doe_nb_concentrations : int
        Number of concentration ratios for all factor

    doe_concentrations: np_ndarray
        Possible concentration values (between 0.0 and 1.0) for all factors.
        If no list is passed, a default list will be built,
        e.g. if doe_nb_concentrations = 5 the list of considered
        discrete conentrations will be: 0.0 0.25 0.5 0.75 1.0

    doe_nb_samples: int
        Number of samples to generate for all factors

    seed: int
        Seed-number to controls the seed and random draws

    Returns
    -------
    levels_array : 2d-array
        N-by-samples array with uniformly spaced values between 0 and 1.
    """
    sampling = lhs(
        n_variable_parameters,
        samples=doe_nb_samples,
        criterion='center',
        random_state=seed)

    logger.debug(f'LHS: {sampling}')

    # Discretize LHS values
    def rounder(values):
        def f(x):
            idx = np_argmin(np_abs(values - x))
            return values[idx]
        return np_frompyfunc(f, 1, 1)
    if doe_concentrations is None:
        doe_concentrations = np_append(
            arange(0.0, 1.0, 1/(doe_nb_concentrations-1)),
            1.0
        )
    logger.debug(f'ROUNDED VALUES: {doe_concentrations}')
    rounded_sampling = rounder(np_asarray(doe_concentrations))(sampling)
    logger.debug(f'ROUNDED LHS: {rounded_sampling}')

    return np_asarray(rounded_sampling)


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
    return multiply(
        levels_array,
        maximum_variable_concentrations
    )


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
    input_df,
    logger: Logger = getLogger(__name__)
):
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

    all_parameters = input_df['Parameter'].tolist()
    logger.debug(f'PARAMETERS: {all_parameters}')

    initial_set_array = concatenate(
        (variable_concentrations_array,
            fixed_concentrations_array,),
        axis=1)
    initial_set_df = DataFrame(initial_set_array)
    logger.debug(f'INITIAL SET: {initial_set_df}')

    normalizer_set_df = initial_set_df.copy()
    normalizer_set_df.columns = all_parameters
    normalizer_set_df['GOI-DNA'] = normalizer_set_df['GOI-DNA']*0
    logger.debug(f'NORMALIZER SET: {normalizer_set_df}')

    autofluorescence_set_df = normalizer_set_df.copy()
    autofluorescence_set_df.columns = all_parameters
    autofluorescence_set_df['GFP-DNA'] = normalizer_set_df['GFP-DNA']*0
    logger.debug(f'BACKGROUND SET: {autofluorescence_set_df}')

    return {
        'parameters': all_parameters,
        'initial': initial_set_df,
        'normalizer': normalizer_set_df,
        'background': autofluorescence_set_df
    }

    return (initial_set_df,
            normalizer_set_df,
            autofluorescence_set_df,
            all_parameters)


def save_intial_plates(
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
