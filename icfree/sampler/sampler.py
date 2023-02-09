#!/usr/bin/env python
# coding: utf-8

from os import (
    path as os_path,
    mkdir as os_mkdir
)
from itertools import product
from numpy import (
    prod as np_prod,
    vstack as np_vstack,
    floor as np_floor,
    empty as np_empty,
    unique as np_unique,
    random as np_random,
    array as np_array,
    asarray as np_asarray,
    linspace as np_linspace,
    set_printoptions as np_set_printoptions,
    inf as np_inf,
    ndarray as np_ndarray,
    savetxt as np_savetxt
)
from pyDOE2 import (
    lhs
)
from logging import (
    Logger,
    getLogger
)
from typing import (
    Dict,
    List
)

from .args import DEFAULTS

# To print numpy arrays in full
np_set_printoptions(threshold=np_inf)


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
    logger.debug(f'ratios: {ratios}')
    logger.debug(f'all_nb_steps: {all_nb_steps}')
    logger.debug(f'all_ratios: {all_ratios}')

    # If ratios are not defined for all parameters
    if all_ratios is None:
        all_ratios = np_linspace(0.0, 1.0, all_nb_steps).tolist()

    _ratios = dict(ratios)

    for param in ratios:
        if not isinstance(ratios[param], list):
            # Put single concentration into a list
            _ratios[param] = [ratios[param]]
        elif len(ratios[param]) == 0:
            # Set ratios to default value
            _ratios[param] = all_ratios

    logger.debug(f'ratios returned: {_ratios}')

    return _ratios


def convert(
    sampling_values: np_array,
    max_values: np_array,
    logger: Logger = getLogger(__name__)
) -> np_array:
    """
    Convert sampling ratios into values.

    Parameters
    ----------
    sampling_values: np_array
        N-by-samples array where values are uniformly spaced between 0 and 1.
    max_values: np_array
        N-by-1 array of maximum values for each parameter.

    Returns
    -------
    sampling_values: np_array
        N-by-samples array where values are uniformly spaced between 0 and 1.
    """
    try:
        return sampling_values * max_values
    except ValueError:
        return np_asarray([])


def lhs_discrete_sampling(
    n_features: int,
    discrete_space: np_ndarray,
    n_samples: int = DEFAULTS['NB_SAMPLES'],
    seed: int = None,
    logger: Logger = getLogger(__name__)
) -> np_ndarray:
    """
    Generate a Latin Hypercube Sampling (LHS) in a discrete space.

    Parameters
    ----------
    n_samples : int
        Number of samples to generate.

    n_features : int
        Number of features.

    discrete_space : np_ndarray
        Discrete space.

    Returns
    -------
    samples : np_ndarray
        N-by-samples array with uniformly spaced values between 0 and 1.
    """

    logger.debug(f'n_samples: {n_samples}')
    logger.debug(f'n_features: {n_features}')
    logger.debug(f'discrete_space: {discrete_space}')
    logger.debug(f'seed: {seed}')

    # Set seed
    np_random.seed(seed)

    # Initialize the samples array
    samples = np_empty((n_samples, n_features))

    # Loop over each feature
    for i in range(n_features):
        # Get the unique values of the current feature in the discrete space
        # unique_values = np.unique(discrete_space[:, i])
        unique_values = np_unique(discrete_space[i])

        # Get the number of unique values
        n_unique = unique_values.shape[0]

        # Generate an array of random numbers between 0 and 1
        random_numbers = np_random.rand(n_samples)

        # Scale the random numbers so that they are between 0 and n_unique
        scaled_random_numbers = (random_numbers * n_unique).astype(int)

        # Sort the unique values randomly
        np_random.shuffle(unique_values)

        # Assign the random values to the samples
        for j, rn in enumerate(scaled_random_numbers):
            samples[j, i] = unique_values[rn]

    return samples

    # Remove duplicates
    samples = np_unique(samples, axis=0)

    from numpy import vstack as np_vstack
    # Resample if the number of unique samples is less than n_samples
    while samples.shape[0] < n_samples:
        new_samples = lhs_discrete_sampling(
            n_samples=n_samples - samples.shape[0],
            n_features=n_features,
            discrete_space=discrete_space,
            seed=seed,
            logger=logger
        )
        samples = np_vstack((samples, new_samples))

    return samples[:n_samples]


def bin_LHS(
    nb_parameters: int,
    nb_samples: int,
    nb_levels: List[int],
    seed: int = None,
    logger: Logger = getLogger(__name__)
):
    """
    Generate a Latin Hypercube Sampling (LHS) in a discrete space.

    Parameters
    ----------
    nb_parameters : int
        Number of parameters.

    nb_samples : int
        Number of samples to generate.

    nb_levels : List[int]
        Number of levels for each parameter.

    seed : int
        Seed for the random number generator.

    Returns
    -------
    samples : np_ndarray
        N-by-samples array with uniformly spaced values between 0 and 1.
    """
    if seed is None:
        sampling = lhs(
            nb_parameters,
            samples=nb_samples,
            criterion='center'
        )
    else:
        sampling = lhs(
            nb_parameters,
            samples=nb_samples,
            criterion='center',
            random_state=seed
        )

    # Put each value in the right bin
    for i in range(sampling.shape[1]):
        sampling[:, i] = sampling[:, i] * nb_levels[i]
        # Round each value to the nearest integer
        sampling[:, i] = np_floor(sampling[:, i])

    return sampling


def remove_duplicates(samples: np_ndarray) -> np_ndarray:
    """
    Remove duplicate rows from a 2D array.

    Parameters
    ----------
    samples : np_ndarray
        2D array of samples.

    Returns
    -------
    samples : np_ndarray
        2D array of samples with duplicate rows removed.
    """
    return np_asarray(
        [
            samples[i]
            for i in sorted(
                np_unique(samples, axis=0, return_index=True)[1]
            )
        ]
    )


def random_sampling(
    nb_samples: int,
    nb_levels: List[int],
    seed: int = None,
    logger: Logger = getLogger(__name__)
):
    """
    Generate a random sampling in a discrete space.

    Parameters
    ----------
    nb_samples : int
        Number of samples to generate.

    nb_levels : List[int]
        Number of levels for each parameter.

    seed : int
        Seed for the random number generator.

    Returns
    -------
    samples : np_ndarray
        N-by-samples array with uniformly spaced values between 0 and 1.
    """
    nb_parameters = len(nb_levels)
    if seed is None:
        sampling = np_random.randint(
            0,
            nb_levels,
            (nb_samples, nb_parameters)
        )
    else:
        sampling = np_random.RandomState(seed).randint(
            0,
            nb_levels,
            (nb_samples, nb_parameters)
        )

    return sampling


def full_factorial_sampling(
    nb_levels: List[int],
    logger: Logger = getLogger(__name__)
):
    """
    Generate a full factorial sampling in a discrete space.

    Parameters
    ----------
    nb_levels : List[int]
        Number of levels for each parameter.

    seed : int
        Seed for the random number generator.

    Returns
    -------
    samples : np_ndarray
        N-by-samples array with uniformly spaced values between 0 and 1.
    """
    return np_asarray(
        list(
            product(
                *[
                    range(nb_levels[i])
                    for i in range(len(nb_levels))
                ]
            )
        )
    )


def sampling(
    nb_parameters,
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
    nb_parameters : int
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

    logger.debug(f'nb parameters: {nb_parameters}')
    logger.debug(f'ratios: {ratios}')
    logger.debug(f'nb samples: {nb_samples}')

    if nb_parameters <= 0:
        return np_asarray([])

    nb_levels = [len(ratios_lst) for ratios_lst in ratios.values()]

    # Check if the number of samples is greater
    # than the number of possible combinations
    # And select the sampling method
    nb_combinations = np_prod(nb_levels)
    if nb_samples == nb_combinations:
        logger.warning(
            f'Number of samples ({nb_samples}) is equal to the number of '
            f'possible combinations ({np_prod(nb_levels)})'
        )
        logger.warning('Proceeding to full factorial design')
        # Proceed to full factorial design
        sampling = full_factorial_sampling(
            nb_levels=nb_levels,
            logger=logger
        )
    elif nb_samples > nb_combinations / 3:
        logger.warning(
            f'Number of samples ({nb_samples}) is greater than 1/3 of the '
            f'number of possible combinations ({np_prod(nb_levels)})'
        )
        logger.warning('Proceeding to random sampling')
        # 1. Proceed to initial random sampling
        sampling = random_sampling(
            nb_samples=nb_samples,
            nb_levels=nb_levels,
            seed=seed,
            logger=logger
        )
    else:
        # 1. Generate initial LHS
        sampling = bin_LHS(
            nb_parameters,
            nb_samples,
            nb_levels,
            seed=seed,
            logger=logger
        )

    # 2. If needed, replace duplicate samples by random ones
    # 2.1 remove duplicates
    sampling = remove_duplicates(sampling)
    nb_duplicates = nb_samples - sampling.shape[0]
    logger.warning(f'{nb_duplicates} duplicates removed')
    while nb_duplicates > 0:
        # 2.2 generate random new samples
        logger.warning(f'Generating {nb_duplicates} random sample(s)')
        new_samples = random_sampling(
            nb_samples=nb_samples - sampling.shape[0],
            nb_levels=nb_levels,
            seed=seed,
            logger=logger
        )
        # 2.3 add new samples to sampling
        sampling = np_vstack((sampling, new_samples))
        # 2.4 remove duplicates
        sampling = remove_duplicates(sampling)
        nb_duplicates = nb_samples - sampling.shape[0]
        logger.warning(f'{nb_duplicates} duplicates removed')

    # 3. Replace values by ratios
    f_sampling = sampling.astype(float)
    for i in range(nb_parameters):
        f_sampling[:, i] = np_asarray(
            list(ratios.values())[i]
        )[sampling[:, i].astype(int)]

    logger.debug(f'LHS:\n{f_sampling}')

    return f_sampling


# def sampling(
#     bin_values: Dict,
#     nb_samples: int,
#     seed: int,
#     logger: Logger = getLogger(__name__)
# ) -> list:
#     """
#     Sample values.

#     Parameters
#     ----------
#     bin_values: dict
#         Dictionnary of sampling values.
#     nb_samples: int
#         Number of samples.
#     seed: int
#         Seed for random sampling.

#     Returns
#     -------
#     values: list
#         List of sampled values.
#     """

#     logger.debug(f'bin values: {bin_values}')
#     logger.debug(f'nb samples: {nb_samples}')
#     logger.debug(f'seed: {seed}')

#     # set the seed
#     if seed is not None:
#         random.seed(seed)

#     # create an array of the values lists
#     lists = np_array(list(bin_values.values()))

#     # create an empty list to store the samples
#     samples = []

#     # do LHS sampling

#     # loop over the number of samples
#     for i in range(nb_samples):
#         # create an empty list to store the current sample
#         sample = []
#         for lst in lists:
#             # shuffle the list
#             random.shuffle(lst)
#             # select the first value from the shuffled list
#             value = lst[0]
#             # add the value to the current sample
#             sample.append(value)
#         # append the current sample to the list of samples
#         samples.append(sample)

#     logger.debug(f'samples: {samples}')

#     # convert the list of samples to a numpy array
#     return np_array(samples)


def check_sampling(
    values: np_ndarray,
    min_max: list,
    logger: Logger = getLogger(__name__)
):
    logger.debug('Checking sampling...')
    logger.debug(f'values: {values}')
    logger.debug(f'min_max: {min_max}')

    nb_parameters = values.shape[1]

    # Check that the min and max values
    # are in the LHS result
    # For each column, check the values
    for i_param in range(nb_parameters):
        param_levels = values[:, i_param]
        try:
            assert min_max[i_param][0] in param_levels
        except AssertionError:
            logger.warning(
                'Min value not found in sampling'
            )
        try:
            assert min_max[i_param][1] in param_levels
        except AssertionError:
            logger.warning(
                'Max value not found in sampling'
            )

    # Check that there is no duplicate,
    # i.e. that each row is unique
    nb_dup = len(values) - len(set(map(tuple, values)))
    if nb_dup > 0:
        # Find duplicates
        unique = set()
        duplicates = set()
        for row in values:
            if tuple(row) in unique:
                duplicates.add(tuple(row))
            else:
                unique.add(tuple(row))
        logger.warning(f'Duplicates found in sampling: {nb_dup}')
        # Print one duplicate per line
        for dup in duplicates:
            logger.warning(f'   --> {dup}')
        # logger.warning(f'{nb_dup} duplicates found in sampling')

    logger.debug('Sampling checked')


# def levels_to_absvalues(
#     levels_array,
#     maximum_values,
#     decimals: int = 3,
#     logger: Logger = getLogger(__name__)
# ):
#     """
#     Multiply levels array by maximum concentrations array.

#     Parameters
#     ----------
#     levels_array : 2d-array
#         N-by-samples array with uniformly spaced values between 0 and 1.

#     maximum_values : 1d-array
#         N-maximum-values array with values for each variable factor.

#     Returns
#     -------
#     values : 2d-array
#         N-by-samples array with values for each factor.
#     """
#     logger.debug(f'LEVELS ARRAY:\n{levels_array}')
#     logger.debug(f'maxValueS:\n{maximum_values}')
#     if levels_array is None or levels_array.size <= 0:
#         return np_asarray([])

#     values = np_multiply(
#         levels_array,
#         maximum_values
#     )
#     values = np_round(
#         values.astype(np_double),
#         decimals
#     )
#     logger.debug(f'VALUES:\n{values}')

#     return values


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
        header=delimiter.join(parameters),
        comments=''
    )
