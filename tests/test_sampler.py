# Test for sampler
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
from pandas import DataFrame
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
from typing import Dict
from logging import getLogger

from icfree.sampler.__main__ import (
    input_importer,
    input_processor,
)
from icfree.sampler.sampler import (
    sampling,
    levels_to_absvalues,
    save_values,
    set_sampling_ratios,
    check_sampling
)


class Test(TestCase):

    DATA_FOLDER = os_path.join(
        os_path.dirname(os_path.realpath(__file__)),
        'data', 'sampler'
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
                if isinstance(row['Ratios'], str):
                    tested_df.at[i, 'Ratios'] = list(
                        map(
                            float,
                            row['Ratios'].split(',')
                        )
                    )
                else:
                    tested_df.at[i, 'Ratios'] = None
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
        print(tested_dictionary)
        self.assertDictEqual(
                expected_dictionary,
                tested_dictionary
            )

    # def test_input_processor_woConstStatus(self):
    #     with open(
    #         os_path.join(
    #                 self.REF_FOLDER,
    #                 'expected_parameters_const_value_woConst.json'
    #         ), 'r'
    #     ) as fp:
    #         expected_dictionary = (json_load(fp))

    #     with open(
    #         os_path.join(
    #                 self.INPUT_FOLDER,
    #                 'proCFPS_parameters_woConst.tsv'
    #         ), 'r'
    #     ) as fp:
    #         tested_df = input_importer(fp)

    #     tested_dictionary = input_processor(tested_df)
    #     self.assertDictEqual(
    #             expected_dictionary,
    #             tested_dictionary
    #         )

    # def test_input_processor_woDoEStatus(self):
    #     with open(
    #         os_path.join(
    #                 self.REF_FOLDER,
    #                 'expected_parameters_doe_value_woDoE.json'
    #         ), 'r'
    #     ) as fp:
    #         expected_dictionary = (json_load(fp))

    #     with open(
    #         os_path.join(
    #                 self.INPUT_FOLDER,
    #                 'proCFPS_parameters_woDoE.tsv'
    #         ), 'r'
    #     ) as fp:
    #         tested_df = input_importer(fp)

    #     tested_dictionary = input_processor(tested_df)
    #     self.assertDictEqual(
    #             expected_dictionary,
    #             tested_dictionary
    #         )

    def test_sampling(self):
        doe_nb_concentrations = 5
        n_variable_parameters = 12
        ratios = set_sampling_ratios(
            ratios=dict.fromkeys(
                range(n_variable_parameters), []
            ),
            all_nb_steps=doe_nb_concentrations
        )
        self._test_sampling(
            ratios,
            n_variable_parameters,
            os_path.join(
                self.REF_FOLDER,
                'sampling_array.json'
            )
        )

    def test_sampling_withSingleRatio(self):
        n_variable_parameters = 1
        ratios = dict.fromkeys(
            range(n_variable_parameters), [1]
        )
        self._test_sampling(
            ratios,
            n_variable_parameters,
            os_path.join(
                self.REF_FOLDER,
                'sampling_array_const.json'
            )
        )

    def _test_sampling(
        self,
        ratios: Dict,
        n_var_param: int,
        ref_file: str
    ):
        nb_samples = 10
        seed = 123

        sampling_array = sampling(
            n_variable_parameters=n_var_param,
            ratios=ratios,
            nb_samples=nb_samples,
            seed=seed
        )

        with open(ref_file, 'r') as f:
            _ref_sampling_array = json_load(f)
        ref_sampling_array = []
        for sample in _ref_sampling_array.values():
            ref_sampling_array.append(sample)

        assert_array_equal(
            sampling_array,
            np_array(ref_sampling_array)
        )

    def test_sampling_Const(self):
        input_df = input_importer(os_path.join(
                self.INPUT_FOLDER,
                'proCFPS_parameters_const.tsv'
                ))
        input_processor(input_df)

        n_variable_parameters = 0
        seed = 123
        ratios = set_sampling_ratios(
            ratios=dict.fromkeys(
                range(n_variable_parameters), None
            ),
            all_nb_steps=5
        )
        doe_levels = sampling(
            n_variable_parameters=n_variable_parameters,
            ratios=ratios,
            seed=seed
        )

        expected_doe_levels = np_asarray([])

        assert_array_equal(
            doe_levels,
            expected_doe_levels
        )

    def test_set_sampling_ratios(self):
        ratios = {0: [1, 2, 3], 1: 1}
        all_nb_steps = 5
        ratios = set_sampling_ratios(
            ratios=ratios,
            all_nb_steps=all_nb_steps
        )
        self.assertDictEqual(
            ratios,
            {0: [1, 2, 3], 1: [1]}
        )

    def test_check_sampling(self):
        sampling_with_duplicates = np_array(
            [
                [0.0, 0.0],
                [1.0, 1.0],
                [0.0, 0.0],
            ]
        )
        sampling_with_no_min_value = np_array(
            [[1.0]]
        )
        sampling_with_no_max_value = np_array(
            [[0.0]]
        )
        for _sampling in [
            (sampling_with_duplicates, 'Duplicate found in sampling'),
            (sampling_with_no_min_value, 'Min value not found in sampling'),
            (sampling_with_no_max_value, 'Max value not found in sampling')
        ]:
            with self.subTest("sampling", _sampling=_sampling):
                sampling_array = _sampling[0]
                expected_error = _sampling[1]
                with self.assertLogs('foo', level='INFO') as cm:
                    check_sampling(sampling_array, logger=getLogger('foo'))
                    self.assertEqual(
                        cm.output,
                        [f'WARNING:foo:{expected_error}']
                    )

    def test_levels_to_absvalues(self):
        input_df = input_importer(os_path.join(
                self.INPUT_FOLDER,
                'tested_concentrations.tsv'
                ))

        parameters = input_processor(input_df)

        n_variable_parameters = len(parameters)
        doe_nb_concentrations = 5
        nb_samples = 10
        seed = 123
        ratios = {
            parameter: data['Ratios']
            for parameter, data in parameters.items()
        }
        ratios = set_sampling_ratios(
            ratios=ratios,
            all_nb_steps=doe_nb_concentrations
        )
        tested_sampling_array = sampling(
            n_variable_parameters=n_variable_parameters,
            ratios=ratios,
            nb_samples=nb_samples,
            seed=seed
        )

        max_conc = [
            v['maxValue']
            for v in parameters.values()
        ]

        tested_concentrations_array = levels_to_absvalues(
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

    def test_levels_to_absvalues_EmptyConcentrationsArray(self):
        input_df = input_importer(os_path.join(
                self.INPUT_FOLDER,
                'proCFPS_parameters_const.tsv'
                ))
        parameters = input_processor(input_df)

        n_variable_parameters = 0
        seed = 123
        ratios = {
            parameter: data['Ratios']
            for parameter, data in parameters.items()
        }
        doe_levels = sampling(
            n_variable_parameters=n_variable_parameters,
            ratios=ratios,
            seed=seed
        )

        max_conc = [
            v['maxValue']
            for v in parameters.values()
        ]

        # Convert
        doe_concentrations = levels_to_absvalues(
            doe_levels,
            max_conc,
        )
        expected_doe_concentrations_array = np_asarray([])

        assert_array_equal(
            doe_concentrations,
            expected_doe_concentrations_array
        )

    def test_save_values_csv(self):
        with TemporaryDirectory() as tmpFolder:
            self._test_save_values(
                input_file=self.proCFPS_parameters,
                output_folder=tmpFolder,
                output_format='csv'
            )

    def test_save_values_wExistingOutFolder(self):
        with TemporaryDirectory() as tmpFolder:
            self._test_save_values(
                input_file=self.proCFPS_parameters,
                output_folder=tmpFolder
            )

    def test_save_values_woExistingOutFolder(self):
        self._test_save_values(
            input_file=self.proCFPS_parameters,
            output_folder=NamedTemporaryFile().name
        )

    # def test_save_values_wExistingOutFolder_woGOI(self):
    #     with TemporaryDirectory() as tmpFolder:
    #         self._test_save_values(
    #             input_file=self.proCFPS_parameters_woGOI,
    #             output_folder=tmpFolder,
    #             woGOI=True
    #         )

    # def test_save_values_woExistingOutFolder_woGOI(self):
    #     self._test_save_values(
    #         input_file=self.proCFPS_parameters_woGOI,
    #         output_folder=NamedTemporaryFile().name,
    #         woGOI=True
    #     )

    def _test_save_values(
        self,
        input_file: str,
        output_folder: str,
        output_format: str = 'tsv',
    ):
        input_df = input_importer(input_file)

        parameters = input_processor(input_df)

        n_variable_parameters = len(parameters)
        doe_nb_concentrations = 5
        doe_ratios = np_append(
            np_arange(0.0, 1.0, 1/(doe_nb_concentrations-1)),
            1.0
        ).tolist()
        nb_samples = 10
        seed = 123
        ratios = {
            parameter: data['Ratios']
            for parameter, data in parameters.items()
        }
        ratios = set_sampling_ratios(
            ratios=ratios,
            all_nb_steps=doe_nb_concentrations,
            all_ratios=doe_ratios,
        )
        doe_levels = sampling(
            n_variable_parameters=n_variable_parameters,
            ratios=ratios,
            nb_samples=nb_samples,
            seed=seed
        )

        max_conc = [
            v['maxValue']
            for v in parameters.values()
        ]

        sampling_values = levels_to_absvalues(
            doe_levels,
            max_conc,
        )

        # dna_concentrations = {
        #     v: dna_param[v]['maxValue']
        #     for status, dna_param in parameters.items()
        #     for v in dna_param
        #     if status.startswith('dna')
        # }

        # const_concentrations = {
        #         k: v['maxValue']
        #         for k, v in parameters['const'].items()
        #     }

        # concentrations = assemble_values(
        #     doe_concentrations,
        #     dna_concentrations,
        #     const_concentrations,
        #     parameters={k: list(v.keys()) for k, v in parameters.items()}
        # )

        # GENERATE PLATE FILES
        # save_values(
        #     concentrations['initial'],
        #     concentrations['normalizer'],
        #     concentrations['background'],
        #     concentrations['parameters'],
        #     output_folder=output_folder
        # )
        save_values(
            values=sampling_values,
            parameters=list(parameters.keys()),
            output_folder=output_folder,
            output_format=output_format
        )

        # Load ref file
        ref_filename = 'ref_initial_LHS-None'
        with open(
            os_path.join(
                    self.REF_FOLDER,
                    f'{ref_filename}.{output_format}'
            )
        ) as fp1:
            ref_initial_set = fp1.read()
        # Load generated file
        with open(
            os_path.join(
                    output_folder,
                    f'sampling.{output_format}'
            )
        ) as fp4:
            tested_initial_set = fp4.read()
        # compare files
        assert ref_initial_set == tested_initial_set

        # if not woGOI:
        #     # Load ref file
        #     ref_filename = 'ref_autofluorescence_LHS-None'
        #     if woGOI:
        #         ref_filename += '_woGOI'
        #     with open(
        #         os_path.join(
        #                 self.REF_FOLDER,
        #                 f'{ref_filename}.tsv'
        #         )
        #     ) as fp2:
        #         ref_autofluorescence_set = fp2.read()
        #     # Load generated file
        #     with open(
        #         os_path.join(
        #                 output_folder,
        #                 'autofluorescence.tsv'
        #         )
        #     ) as fp5:
        #         tested_autofluorescence_set = fp5.read()
        #     # compare files
        #     assert ref_autofluorescence_set == tested_autofluorescence_set

        # if not woGFP:
        #     # Load ref file
        #     ref_filename = 'ref_normalizer_LHS-None'
        #     if woGOI:
        #         ref_filename += '_woGOI'
        #     with open(
        #         os_path.join(
        #                 self.REF_FOLDER,
        #                 f'{ref_filename}.tsv'
        #         )
        #     ) as fp3:
        #         ref_normalizer_set = fp3.read()
        #     # Load generated file
        #     with open(
        #         os_path.join(
        #                 output_folder,
        #                 'normalizer.tsv'
        #         )
        #     ) as fp6:
        #         tested_normalizer_set = fp6.read()
        #     # compare files
        #     assert ref_normalizer_set == tested_normalizer_set

    # def test_change_status(self):
    #     input_df = input_importer(
    #         os_path.join(
    #             self.INPUT_FOLDER,
    #             'proCFPS_parameters.tsv'
    #         )
    #     )
    #     parameters = input_processor(input_df)
    #     parameters = change_status(parameters, 'const')
    #     with open(
    #         os_path.join(
    #             self.REF_FOLDER,
    #             'proCFPS_parameters_const.json'
    #         ), 'r'
    #     ) as fp:
    #         expected_parameters = json_load(fp)

    #     self.assertDictEqual(
    #         parameters,
    #         expected_parameters
    #     )

    def test_LHS_results(self):
        input_df = input_importer(
            os_path.join(
                self.INPUT_FOLDER,
                'proCFPS_parameters.tsv'
            )
        )
        parameters = input_processor(input_df)
        doe_nb_concentrations = 5

        ratios = {
            parameter: data['Ratios']
            for parameter, data in parameters.items()
        }
        ratios = set_sampling_ratios(
            ratios=ratios,
            all_nb_steps=doe_nb_concentrations
        )

        max_conc = [
            v['maxValue']
            for v in parameters.values()
        ]
        # Generate the sampling for testing
        # presence of min and max concentrations
        # The less samples, the more likely to not have min or max
        nb_samples = 4 * doe_nb_concentrations
        for i_run in range(100):
            # LHS sampling
            sampling_array = sampling(
                n_variable_parameters=len(parameters),
                ratios=ratios,
                nb_samples=nb_samples
            )
            doe_concentrations = levels_to_absvalues(
                sampling_array,
                max_conc
            )
            # Check that the min and max concentrations
            # are in the LHS result
            # For each column, check the values
            for i_param in range(len(parameters)):
                parameter_concentrations = doe_concentrations[:, i_param]
                # Do not check for 'const' parameters
                if len(set(parameter_concentrations)) > 1:
                    assert 0.0 in parameter_concentrations
                    assert max_conc[i_param] in parameter_concentrations

        # Generate the sampling for testing
        # presence of duplicates
        # The more samples, the more likely to have duplicates
        nb_samples = 10 * len(parameters)
        nb_run = 1
        for i_run in range(nb_run):
            # LHS sampling
            sampling_array = sampling(
                n_variable_parameters=len(parameters),
                ratios=ratios,
                nb_samples=nb_samples
            )
            doe_concentrations = levels_to_absvalues(
                sampling_array,
                max_conc
            )
            # Check that there is no duplicate
            self.assertEqual(
                0,
                len(doe_concentrations)
                - len(np_unique(doe_concentrations, axis=0))
            )
