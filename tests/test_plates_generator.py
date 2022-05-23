from unittest import TestCase
from os import path as os_path
from pickle import load as pickle_load
from numpy.testing import assert_array_equal
from numpy import (
    append as np_append,
    arange as np_arange,
)
from icfree.plates_generator.plates_generator import levels_array_generator


class Test(TestCase):

    DATA_FOLDER = os_path.join(
        os_path.dirname(os_path.realpath(__file__)),
        'data', 'plates_generator'
    )
    OUTPUT_FOLDER = os_path.join(
        DATA_FOLDER,
        'output'
    )

    def test_levels_array_generator(self):
        n_variable_parameters = 12
        doe_nb_concentrations = 5
        doe_nb_samples = 10
        seed = 123
        sampling_array = levels_array_generator(
            n_variable_parameters=n_variable_parameters,
            doe_nb_concentrations=doe_nb_concentrations,
            doe_nb_samples=doe_nb_samples,
            seed=seed
        )
        with open(
            os_path.join(
                self.OUTPUT_FOLDER,
                'sampling_array.pickle'
                ), 'rb') as f:
            ref_sampling_array = pickle_load(f)
        assert_array_equal(
            sampling_array,
            ref_sampling_array
        )

    def test_levels_array_generator_doe_concentrations(self):
        n_variable_parameters = 12
        doe_nb_concentrations = 5
        doe_concentrations = np_append(
            np_arange(0.0, 1.0, 1/(doe_nb_concentrations-1)),
            1.0
        )
        doe_nb_samples = 10
        seed = 123
        sampling_array = levels_array_generator(
            n_variable_parameters=n_variable_parameters,
            doe_nb_concentrations=doe_nb_concentrations,
            doe_concentrations=doe_concentrations,
            doe_nb_samples=doe_nb_samples,
            seed=seed
        )
        with open(
            os_path.join(
                self.OUTPUT_FOLDER,
                'sampling_array.pickle'
                ), 'rb') as f:
            ref_sampling_array = pickle_load(f)
        assert_array_equal(
            sampling_array,
            ref_sampling_array
        )
