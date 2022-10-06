#!/usr/bin/env python
# coding: utf-8

from cmath import isnan
from os import (
    path as os_path,
    mkdir as os_mkdir
)

from numpy import (
    round as np_round,
    argmin as np_argmin,
    concatenate as np_concatenate,
    asarray as np_asarray,
    append as np_append,
    arange as np_arange,
    set_printoptions as np_set_printoptions,
    double as np_double,
    abs as np_abs,
    multiply as np_multiply,
    inf as np_inf,
    ndarray as np_ndarray,
    fromiter as np_fromiter,
    savetxt as np_savetxt,
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

from .args import DEFAULTS

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

    for dic in cfps_parameters_df.to_dict('records'):
        parameters[dic['Parameter']] = {
            k: dic[k] for k in dic.keys() - {'Parameter'}
        }
        # Convert list of ratios str into list of float
        # ratio is a list of float
        if isinstance(parameters[dic['Parameter']]['Ratios'], str):
            parameters[dic['Parameter']]['Ratios'] = list(
                map(
                    float,
                    parameters[dic['Parameter']]['Ratios'].split(',')
                )
            )
        # ratio is nan
        elif isnan(parameters[dic['Parameter']]['Ratios']):
            parameters[dic['Parameter']]['Ratios'] = []
        # ratio is a float
        else:
            parameters[dic['Parameter']]['Ratios'] = \
                [parameters[dic['Parameter']]['Ratios']]

    return parameters

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
            if isinstance(parameter['Ratios'], str):
                parameter['Ratios'] = list(
                    map(
                        float,
                        parameter['Ratios'].split(',')
                    )
                )
            else:
                parameter['Ratios'] = None

    logger.debug(f'cfps_parameters_df: {cfps_parameters_df}')
    logger.debug(f'PARAMETERS: {parameters}')

    return parameters


def set_sampling_ratios(
    ratios: Dict,
    all_nb_steps: int = DEFAULTS['NB_SAMPLING_STEPS'],
    all_ratios: np_ndarray = None,
    logger: Logger = getLogger(__name__)
) -> Dict:
    """
    Set the ratios for each parameter.

    Parameters
    ----------
    concentation_ratios : Dict
        Parameter concentration ratios.

    all_nb_steps : int
        Number of ratios for all factor

    all_ratios: np_ndarray
        Possible ratio values (between 0.0 and 1.0) for all factors.
        If no list is passed, a default list will be built,
        e.g. if nb_sampling_steps = 5 the list of considered
        discrete ratios will be: 0.0 0.25 0.5 0.75 1.0

    Returns
    -------
    sampling_ratios : Dict
        Ratio values for each parameter.
    """

    # If ratios are not defined for all parameters
    if all_ratios is None:
        all_ratios = np_append(
            np_arange(0.0, 1.0, 1/(all_nb_steps-1)),
            1.0
        ).tolist()

    _ratios = dict(ratios)

    for param in ratios:
        if len(ratios[param]) == 0:
            # Set ratios to default value
            _ratios[param] = all_ratios
        elif not isinstance(ratios[param], list):
            # Put single concentration into a list
            _ratios[param] = [ratios[param]]

    return _ratios


def sampling(
    n_variable_parameters,
    ratios: Dict,
    nb_samples: int = DEFAULTS['NB_SAMPLES'],
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

    ratios: Dict
        Ratios for each parameter.

    nb_samples: int
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
            samples=nb_samples,
            criterion=None
        )
    else:
        sampling = lhs(
            n_variable_parameters,
            samples=nb_samples,
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

    logger.debug(f'ROUNDED VALUES:\n{ratios}')
    ratios_lst = list(ratios.values())

    # Round LHS values
    rounded_sampling = list(sampling)
    # Normalize values, in case of input ratio > 1
    for i in range(len(ratios_lst)):
        sampling[:, i] = sampling[:, i] * max(ratios_lst[i])
    for i in range(len(rounded_sampling)):
        sample = sampling[i]
        # Round each value of the sample
        for j in range(len(sample)):
            # Search the index of the bin value
            idx_min = np_argmin(
                np_abs(ratios_lst[j] - sample[j])
            )
            sample[j] = ratios_lst[j][idx_min]

    # rounded_sampling = rounder(np_asarray(concentration_ratios))(sampling)
    logger.debug(f'ROUNDED LHS:\n{rounded_sampling}')

    return np_asarray(rounded_sampling)


def check_sampling(
    levels: np_ndarray,
    logger: Logger = getLogger(__name__)
):

    logger.debug('Checking sampling...')

    nb_parameters = levels.shape[1]

    # Check that the min and max concentrations
    # are in the LHS result
    # For each column, check the values
    for i_param in range(nb_parameters):
        param_levels = levels[:, i_param]
        try:
            assert 0. in param_levels
        except AssertionError:
            logger.warning(
                'Min concentration not found in LHS sampling'
            )
        try:
            assert 1. in param_levels
        except AssertionError:
            logger.warning(
                'Max concentration not found in LHS sampling'
            )

    # Check that there is no duplicate,
    # i.e. that each row is unique
    try:
        assert len(levels) == len(set(map(tuple, levels)))
    except AssertionError:
        logger.warning('Duplicate found in LHS sampling')

    logger.debug('Sampling checked')


def levels_to_absvalues(
    levels_array,
    maximum_values,
    decimals: int = 3,
    logger: Logger = getLogger(__name__)
):
    """
    Multiply levels array by maximum concentrations array.

    Parameters
    ----------
    levels_array : 2d-array
        N-by-samples array with uniformly spaced values between 0 and 1.

    maximum_values : 1d-array
        N-maximum-values array with values for each variable factor.

    Returns
    -------
    values : 2d-array
        N-by-samples array with values for each factor.
    """
    logger.debug(f'LEVELS ARRAY:\n{levels_array}')
    logger.debug(f'MAXIMUM VALUES:\n{maximum_values}')
    if levels_array is None or levels_array.size <= 0:
        return np_asarray([])

    values = np_multiply(
        levels_array,
        maximum_values
    )
    values = np_round(
        values.astype(np_double),
        decimals
    )
    logger.debug(f'VALUES:\n{values}')

    return values


# def assemble_values(
#     sampling_values: np_ndarray,
#     dna_values: np_ndarray,
#     const_values: np_ndarray,
#     parameters,
#     logger: Logger = getLogger(__name__)
# ):
#     """
#     Concatenate variable and fixed concentrations array with control array.

#     Parameters
#     ----------
#     sampling_values : 1d-array
#         Array with variable concentrations values for each factor.

#     dna_values : 1d-array
#         Array with values for each factor which are related to DNA
#         with bin values (0 or max. conc.).

#     const_values : 1d-array
#         Array with constant values for each factor.

#     parameters: dict
#         Dictionnary of cfps parameters.

#     Returns
#     -------
#     initial_set_df : dataframe
#         Matrix generated from the concatenation of all samples.

#     normalizer_set_df : dataframe
#         Duplicate of initial_set. 0 is assigned to the GOI-DNA column.

#     autofluorescence_set_df : dataframe
#         Duplicate of normalizer_set. 0 is assigned to the GFP-DNA column.

#     parameters: List
#         List of the name of cfps parameters
#     """
#     logger.debug(f'SAMPLING VALUES:\n{sampling_values}')
#     logger.debug(f'DNA VALUES:\n{dna_values}')
#     logger.debug(f'CONST VALUES:\n{const_values}')

#     # Add DoE combinatorial parameters
#     headers = parameters
#     initial_set_array = sampling_values.copy()

#     # Add constant parameters
#     # If the is no DoE concentrations
#     if len(initial_set_array) == 0:
#         # Then fill with const concentrations
#         initial_set_array = [
#             np_fromiter(const_values.values(), dtype=float)
#         ]
#     else:  # Else, add const concentrations to DoE ones
#         initial_set_array = [
#             np_concatenate(
#                 (concentrations,
#                  list(const_values.values()))
#             )
#             for concentrations in initial_set_array
#         ]
#     headers += parameters['const']

#     # Add combinatorial parameters
#     initial_set_array = [
#         np_concatenate((concentrations, list(dna_values.values())))
#         for concentrations in initial_set_array
#     ]
#     headers += sum(
#         [
#             v for k, v
#             in parameters.items()
#             if k.startswith('dna')],
#         []
#     )

#     # Create initial set with partial concentrations
#     initial_set_df = DataFrame(initial_set_array)
#     initial_set_df.columns = headers
#     logger.debug(f'INITIAL SET:\n{initial_set_df}')

#     # Create normalizer set with GOI to 0
#     normalizer_set_df = None
#     if 'dna_fluo' in parameters:
#         normalizer_set_df = initial_set_df.copy()
#         normalizer_set_df.columns = headers
#         normalizer_set_df[parameters['dna_fluo']] *= 0
#     logger.debug(f'NORMALIZER SET:\n{normalizer_set_df}')

#     # Create normalizer set with GFP to 0
#     autofluorescence_set_df = None
#     if 'dna_goi' in parameters:
#         autofluorescence_set_df = normalizer_set_df.copy()
#         autofluorescence_set_df.columns = headers
#         autofluorescence_set_df[parameters['dna_goi']] *= 0
#     logger.debug(f'BACKGROUND SET:\n{autofluorescence_set_df}')

#     logger.debug(f'HEADERS: {headers}')

#     return {
#         'parameters': headers,
#         'initial': initial_set_df,
#         'normalizer': normalizer_set_df,
#         'background': autofluorescence_set_df
#     }


def save_values(
    # initial_set_df,
    # normalizer_set_df,
    # autofluorescence_set_df,
    values,
    parameters,
    output_folder: str = DEFAULTS['OUTPUT_FOLDER'],
    output_format: str = DEFAULTS['OUTPUT_FORMAT'],
    logger: Logger = getLogger(__name__)
):
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

    if output_format == 'tsv':
        delimiter = '\t'
    elif output_format == 'csv':
        delimiter = ','

    np_savetxt(
        fname=os_path.join(
            output_folder,
            f'sampling.{output_format}'),
        fmt='%s',
        X=values,
        delimiter=delimiter,
        header=delimiter.join(parameters)
    )
    # values.to_csv(
    #     os_path.join(
    #         output_folder,
    #         'sampling.tsv'),
    #     sep='\t',
    #     header=parameters,
    #     index=False
    # )

    return

    if (normalizer_set_df is None
            and autofluorescence_set_df is None):
        initial_set_df.to_csv(
            os_path.join(
                output_folder,
                'sampling.tsv'),
            sep='\t',
            header=all_parameters,
            index=False)
    else:
        initial_set_df.to_csv(
            os_path.join(
                output_folder,
                'initial.tsv'),
            sep='\t',
            header=all_parameters,
            index=False)
        if normalizer_set_df is not None:
            normalizer_set_df.to_csv(
                os_path.join(
                    output_folder,
                    'normalizer.tsv'),
                sep='\t',
                header=all_parameters,
                index=False)

        if autofluorescence_set_df is not None:
            autofluorescence_set_df.to_csv(
                os_path.join(
                    output_folder,
                    'autofluorescence.tsv'),
                sep='\t',
                header=all_parameters,
                index=False)
