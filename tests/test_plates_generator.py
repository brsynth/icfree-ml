from unittest import (
    TestCase
)

from os import (
    path as os_path
)

from numpy.testing import (
    assert_array_equal
)

from pandas.testing import (
    assert_frame_equal
)

from pandas import (
    DataFrame,
    read_json as pd_read_json
)

from numpy import (
    append as np_append,
    arange as np_arange,
    asarray as np_asarray,
    array as np_array,
    unique as np_unique
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
    save_plates,
    set_concentration_ratios
)

from icfree.plates_generator.__main__ import (
    change_status
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
            for i, row in tested_df.iterrows():
                if isinstance(row['Concentration ratios'], str):
                    tested_df.at[i, 'Concentration ratios'] = list(
                        map(
                            float,
                            row['Concentration ratios'].split(',')
                        )
                    )
                else:
                    tested_df.at[i, 'Concentration ratios'] = None
            assert_frame_equal(
                expected_df,
                tested_df
            )

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
        ) as fp:
            tested_df = input_importer(fp)

        tested_dictionary = input_processor(tested_df)
        self.assertDictEqual(
                expected_dictionary,
                tested_dictionary
            )

    def test_input_processor_woConstStatus(self):
        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_parameters_const_value_woConst.json'
            ), 'r'
        ) as fp:
            expected_dictionary = (json_load(fp))

        with open(
            os_path.join(
                    self.INPUT_FOLDER,
                    'proCFPS_parameters_woConst.tsv'
            ), 'r'
        ) as fp:
            tested_df = input_importer(fp)

        tested_dictionary = input_processor(tested_df)
        self.assertDictEqual(
                expected_dictionary,
                tested_dictionary
            )

    def test_input_processor_woDoEStatus(self):
        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_parameters_doe_value_woDoE.json'
            ), 'r'
        ) as fp:
            expected_dictionary = (json_load(fp))

        with open(
            os_path.join(
                    self.INPUT_FOLDER,
                    'proCFPS_parameters_woDoE.tsv'
            ), 'r'
        ) as fp:
            tested_df = input_importer(fp)

        tested_dictionary = input_processor(tested_df)
        self.assertDictEqual(
                expected_dictionary,
                tested_dictionary
            )

    def test_doe_levels_generator(self):
        n_variable_parameters = 12
        doe_nb_concentrations = 5
        doe_nb_samples = 10
        seed = 123

        concentration_ratios = set_concentration_ratios(
            concentration_ratios=dict.fromkeys(
                range(n_variable_parameters), None
            ),
            all_doe_nb_concentrations=doe_nb_concentrations
        )
        sampling_array = doe_levels_generator(
            n_variable_parameters=n_variable_parameters,
            concentration_ratios=concentration_ratios,
            doe_nb_samples=doe_nb_samples,
            seed=seed
        )

        with open(
            os_path.join(
                self.REF_FOLDER,
                'sampling_array.json'
                ), 'r') as f:
            _ref_sampling_array = json_load(f)
        ref_sampling_array = []
        for sample in _ref_sampling_array.values():
            ref_sampling_array.append(sample)

        assert_array_equal(
            sampling_array,
            np_array(ref_sampling_array)
        )

    def test_doe_levels_generator_doe_concentrations(self):
        n_variable_parameters = 12
        doe_nb_concentrations = 5
        doe_nb_samples = 10
        seed = 123
        concentration_ratios = set_concentration_ratios(
            concentration_ratios=dict.fromkeys(
                range(n_variable_parameters), None
            ),
            all_doe_nb_concentrations=doe_nb_concentrations
        )
        concentration_ratios = set_concentration_ratios(
            concentration_ratios=concentration_ratios,
            all_doe_nb_concentrations=doe_nb_concentrations
        )
        sampling_array = doe_levels_generator(
            n_variable_parameters=n_variable_parameters,
            concentration_ratios=concentration_ratios,
            doe_nb_samples=doe_nb_samples,
            seed=seed
        )

        with open(
            os_path.join(
                self.REF_FOLDER,
                'sampling_array.json'
                ), 'r') as f:
            _ref_sampling_array = json_load(f)
        ref_sampling_array = []
        for sample in _ref_sampling_array.values():
            ref_sampling_array.append(sample)

        assert_array_equal(
            sampling_array,
            np_array(ref_sampling_array)
        )

    def test_doe_levels_generator_EmptyDoELevelsArray(self):
        input_df = input_importer(os_path.join(
                self.INPUT_FOLDER,
                'proCFPS_parameters_woDoE.tsv'
                ))
        input_processor(input_df)

        n_variable_parameters = 0
        seed = 123
        concentration_ratios = set_concentration_ratios(
            concentration_ratios=dict.fromkeys(
                range(n_variable_parameters), None
            ),
            all_doe_nb_concentrations=5
        )
        doe_levels = doe_levels_generator(
            n_variable_parameters=n_variable_parameters,
            concentration_ratios=concentration_ratios,
            seed=seed
        )

        expected_doe_levels = np_asarray([])

        assert_array_equal(
            doe_levels,
            expected_doe_levels
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
        concentration_ratios = {
            parameter: data['Concentration ratios']
            for parameter, data in parameters['doe'].items()
        }
        concentration_ratios = set_concentration_ratios(
            concentration_ratios=concentration_ratios,
            all_doe_nb_concentrations=doe_nb_concentrations
        )
        tested_sampling_array = doe_levels_generator(
            n_variable_parameters=n_variable_parameters,
            concentration_ratios=concentration_ratios,
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
                'ref_concentrations_array.json'
                ), 'r') as f:
            _ref_concentrations_array = json_load(f)
        ref_concentrations_array = []
        for sample in _ref_concentrations_array.values():
            ref_concentrations_array.append(sample)

        assert_array_equal(
            tested_concentrations_array,
            np_array(ref_concentrations_array)
        )

    def test_levels_to_concentrations_EmptyConcentrationsArray(self):
        input_df = input_importer(os_path.join(
                self.INPUT_FOLDER,
                'proCFPS_parameters_woDoE.tsv'
                ))
        parameters = input_processor(input_df)

        n_variable_parameters = 0
        seed = 123
        concentration_ratios = {
            parameter: data['Concentration ratios']
            for parameter, data in parameters['doe'].items()
        }
        doe_levels = doe_levels_generator(
            n_variable_parameters=n_variable_parameters,
            concentration_ratios=concentration_ratios,
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
        expected_doe_concentrations_array = np_asarray([])

        assert_array_equal(
            doe_concentrations,
            expected_doe_concentrations_array
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
        doe_concentration_ratios = np_append(
            np_arange(0.0, 1.0, 1/(doe_nb_concentrations-1)),
            1.0
        )
        doe_nb_samples = 10
        seed = 123
        concentration_ratios = {
            parameter: data['Concentration ratios']
            for parameter, data in parameters['doe'].items()
        }
        concentration_ratios = set_concentration_ratios(
            concentration_ratios=concentration_ratios,
            all_doe_nb_concentrations=doe_nb_concentrations,
            all_doe_concentration_ratios=doe_concentration_ratios,
        )
        doe_levels = doe_levels_generator(
            n_variable_parameters=n_variable_parameters,
            concentration_ratios=concentration_ratios,
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
        doe_concentration_ratios = np_append(
            np_arange(0.0, 1.0, 1/(doe_nb_concentrations-1)),
            1.0
        )
        doe_nb_samples = 10
        seed = 123
        concentration_ratios = {
            parameter: data['Concentration ratios']
            for parameter, data in parameters['doe'].items()
        }
        concentration_ratios = set_concentration_ratios(
            concentration_ratios=concentration_ratios,
            all_doe_nb_concentrations=doe_nb_concentrations,
            all_doe_concentration_ratios=doe_concentration_ratios,
        )
        doe_levels = doe_levels_generator(
            n_variable_parameters=n_variable_parameters,
            concentration_ratios=concentration_ratios,
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

    def test_plates_generator_AllStatusConst(self):
        input_df = input_importer(os_path.join(
                self.INPUT_FOLDER,
                'proCFPS_parameters_woDoE.tsv'
                ))
        parameters = input_processor(input_df)

        n_variable_parameters = 0
        seed = 123
        concentration_ratios = {
            parameter: data['Concentration ratios']
            for parameter, data in parameters['doe'].items()
        }
        doe_levels = doe_levels_generator(
            n_variable_parameters=n_variable_parameters,
            concentration_ratios=concentration_ratios,
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

        # Load Reference Files
        expected_initial_sampling_array_woDoE_df = pd_read_json(
            os_path.join(
                self.REF_FOLDER,
                'expected_initial_sampling_array_woDoE_arr.json'
            ),
            orient='split'
        )
        expected_initial_sampling_array_woDoE_arr = \
            expected_initial_sampling_array_woDoE_df.to_numpy()
        expected_initial_sampling_array_woDoE_arr = \
            expected_initial_sampling_array_woDoE_arr.reshape(1, 18)

        expected_normalizer_sampling_array_woDoE_df = pd_read_json(
            os_path.join(
                self.REF_FOLDER,
                'expected_normalizer_sampling_array_woDoE_arr.json'
            ),
            orient='split'
        )
        expected_normalizer_sampling_array_woDoE_arr = \
            expected_normalizer_sampling_array_woDoE_df.to_numpy()
        expected_normalizer_sampling_array_woDoE_arr = \
            expected_normalizer_sampling_array_woDoE_arr.reshape(1, 18)

        expected_autofluorescence_sampling_array_woDoE_df = pd_read_json(
            os_path.join(
                self.REF_FOLDER,
                'expected_autofluorescence_sampling_array_woDoE_arr.json'
            ),
            orient='split'
        )
        expected_autofluorescence_sampling_array_woDoE_arr = \
            expected_autofluorescence_sampling_array_woDoE_df.to_numpy()
        expected_autofluorescence_sampling_array_woDoE_arr = \
            expected_autofluorescence_sampling_array_woDoE_arr.reshape(1, 18)

        assert_array_equal(
            initial_set_df,
            expected_initial_sampling_array_woDoE_arr
        )
        assert_array_equal(
            normalizer_set_df,
            expected_normalizer_sampling_array_woDoE_arr
        )
        assert_array_equal(
            autofluorescence_set_df,
            expected_autofluorescence_sampling_array_woDoE_arr
        )

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
        doe_concentration_ratios = np_append(
            np_arange(0.0, 1.0, 1/(doe_nb_concentrations-1)),
            1.0
        )
        doe_nb_samples = 10
        seed = 123
        concentration_ratios = {
            parameter: data['Concentration ratios']
            for parameter, data in parameters['doe'].items()
        }
        concentration_ratios = set_concentration_ratios(
            concentration_ratios=concentration_ratios,
            all_doe_nb_concentrations=doe_nb_concentrations,
            all_doe_concentration_ratios=doe_concentration_ratios,
        )
        doe_levels = doe_levels_generator(
            n_variable_parameters=n_variable_parameters,
            concentration_ratios=concentration_ratios,
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
        ref_filename = 'ref_initial_LHS-None'
        if woGOI:
            ref_filename += '_woGOI'
        with open(
            os_path.join(
                    self.REF_FOLDER,
                    f'{ref_filename}.tsv'
            )
        ) as fp1:
            ref_initial_set = fp1.read()

        ref_filename = 'ref_autofluorescence_LHS-None'
        if woGOI:
            ref_filename += '_woGOI'
        with open(
            os_path.join(
                    self.REF_FOLDER,
                    f'{ref_filename}.tsv'
            )
        ) as fp2:
            ref_autofluorescence_set = fp2.read()

        ref_filename = 'ref_normalizer_LHS-None'
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

    def test_change_status(self):
        input_df = input_importer(
            os_path.join(
                self.INPUT_FOLDER,
                'proCFPS_parameters.tsv'
            )
        )
        parameters = input_processor(input_df)
        parameters = change_status(parameters, 'const')
        with open(
            os_path.join(
                self.REF_FOLDER,
                'proCFPS_parameters_const.json'
            ), 'r'
        ) as fp:
            expected_parameters = json_load(fp)

        self.assertDictEqual(
            parameters,
            expected_parameters
        )

    def test_LHS_results(self):
        input_df = input_importer(
            os_path.join(
                self.INPUT_FOLDER,
                'proCFPS_parameters.tsv'
            )
        )
        parameters = input_processor(input_df)
        doe_nb_concentrations = 5
        doe_nb_samples = 45

        concentration_ratios = {
            parameter: data['Concentration ratios']
            for parameter, data in parameters['doe'].items()
        }
        concentration_ratios = set_concentration_ratios(
            concentration_ratios=concentration_ratios,
            all_doe_nb_concentrations=doe_nb_concentrations
        )

        # Generate the sampling many times
        for i_run in range(100):
            max_conc = [
                v['Maximum concentration']
                for v in parameters['doe'].values()
            ]
            sampling_array = doe_levels_generator(
                n_variable_parameters=len(parameters['doe']),
                concentration_ratios=concentration_ratios,
                doe_nb_samples=doe_nb_samples
            )
            doe_concentrations = levels_to_concentrations(
                sampling_array,
                max_conc
            )
            # 1. Check that the min and max concentrations
            # are in the LHS result
            # For each column, check the values
            for i_param in range(len(parameters['doe'])):
                parameter_concentrations = doe_concentrations[:, i_param]
                assert 0.0 in parameter_concentrations
                assert max_conc[i_param] in parameter_concentrations
            # 2. Check that there is no duplicate
            self.assertEqual(
                0,
                len(doe_concentrations)
                - len(np_unique(doe_concentrations, axis=0))
            )
