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
    # assert_almost_equal
)
from pandas.testing import (
    assert_frame_equal
)
from pandas import (
    DataFrame
)
from numpy import (
    append as np_append,
    arange as np_arange,
    genfromtxt as np_genfromtxt
)
from json import (
    load as json_load
)
from tempfile import (
    TemporaryDirectory,
    NamedTemporaryFile
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

    REF_FOLDER = os_path.join(
        DATA_FOLDER,
        'output'
    )

    proCFPS_parameters = os_path.join(
        INPUT_FOLDER,
        'proCFPS_parameters.tsv'
    )
    proCFPS_parameters_woGOI = os_path.join(
        INPUT_FOLDER,
        'proCFPS_parameters_woGOI.tsv'
    )

    def test_input_importer(self):
        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'test_input_importer.json'
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
            print(tested_df)

    def test_input_processor(self):
        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'test_input_processor.json'
            ), 'r'
        ) as fp:
            expected_dictionary = (json_load(fp))

        with open(
            os_path.join(
                    self.INPUT_FOLDER,
                    'proCFPS_parameters.tsv'
            ), 'r'
        ) as fp2:
            tested_df = input_importer(fp2)

        tested_dictionary = input_processor(tested_df)
        TestCase().assertDictEqual(
                expected_dictionary,
                tested_dictionary
            )

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
                self.REF_FOLDER,
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
                self.REF_FOLDER,
                'sampling_array.pickle'
                ), 'rb') as f:
            ref_sampling_array = pickle_load(f)

        assert_array_equal(
            sampling_array,
            ref_sampling_array
        )

    def test_levels_to_concentrations(self):
        input_df = input_importer(os_path.join(
                self.INPUT_FOLDER,
                'tested_concentrations.tsv'
                ))

        parameters = input_processor(input_df)

        n_variable_parameters = len(parameters['doe'])
        doe_nb_concentrations = 5
        doe_nb_samples = 10
        seed = 123
        tested_sampling_array = doe_levels_generator(
            n_variable_parameters=n_variable_parameters,
            doe_nb_concentrations=doe_nb_concentrations,
            doe_nb_samples=doe_nb_samples,
            seed=seed
        )

        max_conc = [
            v['Maximum concentration']
            for v in parameters['doe'].values()
        ]

        tested_concentrations_array = levels_to_concentrations(
            tested_sampling_array,
            max_conc,
        )

        # Refrence array generated from mutipltying
        # sampling_array.pickle and ref_maximum_concentrations.json
        with open(
            os_path.join(
                self.REF_FOLDER,
                'ref_concentrations_array.csv'
                ), 'r') as f1:
            ref_concentrations_array = np_genfromtxt(f1, delimiter=',')

        assert_array_equal(
            tested_concentrations_array,
            ref_concentrations_array
        )

    def test_plates_generator_all_columns(self):
        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'all_expected_columns.json'
            ), 'r'
        ) as fp1:
            all_expected_columns = json_load(fp1)

        input_df = input_importer(os_path.join(
                self.INPUT_FOLDER,
                'proCFPS_parameters.tsv'
                ))

        parameters = input_processor(input_df)

        n_variable_parameters = len(parameters['doe'])
        doe_nb_concentrations = 5
        doe_concentrations = np_append(
            np_arange(0.0, 1.0, 1/(doe_nb_concentrations-1)),
            1.0
        )
        doe_nb_samples = 10
        seed = 123
        doe_levels = doe_levels_generator(
            n_variable_parameters=n_variable_parameters,
            doe_nb_concentrations=doe_nb_concentrations,
            doe_concentrations=doe_concentrations,
            doe_nb_samples=doe_nb_samples,
            seed=seed
        )

        max_conc = [
            v['Maximum concentration']
            for v in parameters['doe'].values()
        ]
        # Convert
        doe_concentrations = levels_to_concentrations(
            doe_levels,
            max_conc,
        )

        dna_concentrations = {
            v: dna_param[v]['Maximum concentration']
            for status, dna_param in parameters.items()
            for v in dna_param
            if status.startswith('dna')
        }

        const_concentrations = {
                k: v['Maximum concentration']
                for k, v in parameters['const'].items()
            }

        plates = plates_generator(
            doe_concentrations,
            dna_concentrations,
            const_concentrations,
            parameters={k: list(v.keys()) for k, v in parameters.items()}
        )

        initial_set_df = plates['initial']
        autofluorescence_set_df = plates['background']
        normalizer_set_df = plates['normalizer']
        tested_columns_initial_set = initial_set_df.columns.tolist()
        tested_columns_normalizer_set = normalizer_set_df.columns.tolist()
        tested_columns_autofluorescence_set = \
            autofluorescence_set_df.columns.tolist()
        # tested_doe_columns =
        # tested_const_columns =
        # tested_dna_fluo_columns =
        # tested_dna_goi_columns =

        self.assertListEqual(
            all_expected_columns,
            tested_columns_initial_set)

        self.assertListEqual(
            all_expected_columns,
            tested_columns_normalizer_set)

        self.assertListEqual(
            all_expected_columns,
            tested_columns_autofluorescence_set)

        self.assertListEqual(
            tested_columns_normalizer_set,
            tested_columns_autofluorescence_set)

    def test_plates_generator_woGOI(self):
        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_columns_woGOI.json'
            ), 'r'
        ) as fp2:
            expected_columns_woGOI = json_load(fp2)

        input_df = input_importer(os_path.join(
                self.INPUT_FOLDER,
                'proCFPS_parameters_woGOI.tsv'
                ))

        parameters = input_processor(input_df)

        n_variable_parameters = len(parameters['doe'])
        doe_nb_concentrations = 5
        doe_concentrations = np_append(
            np_arange(0.0, 1.0, 1/(doe_nb_concentrations-1)),
            1.0
        )
        doe_nb_samples = 10
        seed = 123
        doe_levels = doe_levels_generator(
            n_variable_parameters=n_variable_parameters,
            doe_nb_concentrations=doe_nb_concentrations,
            doe_concentrations=doe_concentrations,
            doe_nb_samples=doe_nb_samples,
            seed=seed
        )

        max_conc = [
            v['Maximum concentration']
            for v in parameters['doe'].values()
        ]

        doe_concentrations = levels_to_concentrations(
            doe_levels,
            max_conc,
        )

        dna_concentrations = {
            v: dna_param[v]['Maximum concentration']
            for status, dna_param in parameters.items()
            for v in dna_param
            if status.startswith('dna')
        }

        const_concentrations = {
                k: v['Maximum concentration']
                for k, v in parameters['const'].items()
            }

        plates = plates_generator(
            doe_concentrations,
            dna_concentrations,
            const_concentrations,
            parameters={k: list(v.keys()) for k, v in parameters.items()}
        )

        initial_set_df = plates['initial']
        autofluorescence_set_df = plates['background']
        normalizer_set_df = plates['normalizer']
        tested_columns_initial_set = initial_set_df.columns.tolist()
        tested_columns_normalizer_set = normalizer_set_df.columns.tolist()
        tested_columns_autofluorescence_set = \
            autofluorescence_set_df.columns.tolist()

        self.assertListEqual(
            expected_columns_woGOI,
            tested_columns_initial_set)

        self.assertListEqual(
            expected_columns_woGOI,
            tested_columns_normalizer_set)

        self.assertListEqual(
            expected_columns_woGOI,
            tested_columns_autofluorescence_set)

        self.assertListEqual(
            tested_columns_normalizer_set,
            tested_columns_autofluorescence_set)

    def test_save_plates_wExistingOutFolder(self):
        with TemporaryDirectory() as tmpFolder:
            self._test_save_plates(
                input_file=self.proCFPS_parameters,
                output_folder=tmpFolder
            )

    def test_save_plates_woExistingOutFolder(self):
        self._test_save_plates(
            input_file=self.proCFPS_parameters,
            output_folder=NamedTemporaryFile().name
        )

    def test_save_plates_wExistingOutFolder_woGOI(self):
        with TemporaryDirectory() as tmpFolder:
            self._test_save_plates(
                input_file=self.proCFPS_parameters_woGOI,
                output_folder=tmpFolder,
                woGOI=True
            )

    def test_save_plates_woExistingOutFolder_woGOI(self):
        self._test_save_plates(
            input_file=self.proCFPS_parameters_woGOI,
            output_folder=NamedTemporaryFile().name,
            woGOI=True
        )

    def _test_save_plates(
        self,
        input_file: str,
        output_folder: str,
        woGOI: bool = False
    ):
        input_df = input_importer(input_file)

        parameters = input_processor(input_df)

        n_variable_parameters = len(parameters['doe'])
        doe_nb_concentrations = 5
        doe_concentrations = np_append(
            np_arange(0.0, 1.0, 1/(doe_nb_concentrations-1)),
            1.0
        )
        doe_nb_samples = 10
        seed = 123
        doe_levels = doe_levels_generator(
            n_variable_parameters=n_variable_parameters,
            doe_nb_concentrations=doe_nb_concentrations,
            doe_concentrations=doe_concentrations,
            doe_nb_samples=doe_nb_samples,
            seed=seed
        )

        max_conc = [
            v['Maximum concentration']
            for v in parameters['doe'].values()
        ]

        doe_concentrations = levels_to_concentrations(
            doe_levels,
            max_conc,
        )

        dna_concentrations = {
            v: dna_param[v]['Maximum concentration']
            for status, dna_param in parameters.items()
            for v in dna_param
            if status.startswith('dna')
        }

        const_concentrations = {
                k: v['Maximum concentration']
                for k, v in parameters['const'].items()
            }

        plates = plates_generator(
            doe_concentrations,
            dna_concentrations,
            const_concentrations,
            parameters={k: list(v.keys()) for k, v in parameters.items()}
        )

        # LOAD REF FILES
        ref_filename = 'ref_initial'
        if woGOI:
            ref_filename += '_woGOI'
        with open(
            os_path.join(
                    self.REF_FOLDER,
                    f'{ref_filename}.tsv'
            )
        ) as fp1:
            ref_initial_set = fp1.read()

        ref_filename = 'ref_autofluorescence'
        if woGOI:
            ref_filename += '_woGOI'
        with open(
            os_path.join(
                    self.REF_FOLDER,
                    f'{ref_filename}.tsv'
            )
        ) as fp2:
            ref_autofluorescence_set = fp2.read()

        ref_filename = 'ref_normalizer'
        if woGOI:
            ref_filename += '_woGOI'
        with open(
            os_path.join(
                    self.REF_FOLDER,
                    f'{ref_filename}.tsv'
            )
        ) as fp3:
            ref_normalizer_set = fp3.read()

        # GENERATE PLATE FILES
        save_plates(
            plates['initial'],
            plates['normalizer'],
            plates['background'],
            plates['parameters'],
            output_folder=output_folder
        )

        with open(
            os_path.join(
                    output_folder,
                    'initial_set.tsv'
            )
        ) as fp4:
            tested_initial_set = fp4.read()

        with open(
            os_path.join(
                    output_folder,
                    'autofluorescence_set.tsv'
            )
        ) as fp5:
            tested_autofluorescence_set = fp5.read()

        with open(
            os_path.join(
                    output_folder,
                    'normalizer_set.tsv'
            )
        ) as fp6:
            tested_normalizer_set = fp6.read()

        # COMPARE FILES
        assert ref_initial_set == tested_initial_set
        assert ref_normalizer_set == tested_normalizer_set
        assert ref_autofluorescence_set == tested_autofluorescence_set
