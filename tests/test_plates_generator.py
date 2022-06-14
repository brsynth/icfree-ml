from unittest import (
    TestCase
)

from os import (
    path as os_path
)

from pickle import (
    load as pickle_load
)
from numpy.testing import (
    assert_array_equal
)
from pandas.testing import (
    assert_frame_equal
)
from pandas import (
    DataFrame
)
from numpy import (
    append as np_append,
    arange as np_arange
)
from json import (
    load as json_load,
    dumps as json_dumps
)

from icfree.plates_generator.plates_generator import (
    input_importer,
    input_processor,
    doe_levels_generator,
    levels_to_concentrations,
    plates_generator,
    save_plates
)


class Test(TestCase):

    DATA_FOLDER = os_path.join(
        os_path.dirname(os_path.realpath(__file__)),
        'data', 'plates_generator'
    )

    INPUT_FOLDER = os_path.join(
        DATA_FOLDER,
        'input'
    )

    OUTPUT_FOLDER = os_path.join(
        DATA_FOLDER,
        'output'
    )

    def test_input_importer(self):
        with open(
            os_path.join(
                    self.OUTPUT_FOLDER,
                    'test_input.json'
            ), 'r'
        ) as fp:
            expected_df = DataFrame(
                json_load(fp)
            )
            cfps_parameters = os_path.join(
                self.INPUT_FOLDER,
                'proCFPS_parameters_woGOI.tsv'
                )
            tested_df = input_importer(cfps_parameters)
            assert_frame_equal(
                expected_df,
                tested_df
            )

    def test_input_processor(self):
        pass

    def test_doe_levels_generator(self):
        n_variable_parameters = 12
        doe_nb_concentrations = 5
        doe_nb_samples = 10
        seed = 123
        sampling_array = doe_levels_generator(
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

    def test_doe_levels_generator_doe_concentrations(self):
        n_variable_parameters = 12
        doe_nb_concentrations = 5
        doe_concentrations = np_append(
            np_arange(0.0, 1.0, 1/(doe_nb_concentrations-1)),
            1.0
        )
        doe_nb_samples = 10
        seed = 123
        sampling_array = doe_levels_generator(
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

    def test_levels_to_concentrations(self):
        pass

    def test_plates_generator(self):
        pass

    def test_save_plates(self):
        pass
