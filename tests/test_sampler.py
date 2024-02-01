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
from pandas import DataFrame
from numpy import (
    append as np_append,
    arange as np_arange,
    asarray as np_asarray,
    array as np_array,
    unique as np_unique,
    array_equal as np_array_equal
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
    convert,
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

    parameters = os_path.join(
        INPUT_FOLDER,
        'parameters.tsv'
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
            tested_df = input_importer(self.parameters)
            for i, row in tested_df.iterrows():
                if not isinstance(row['Ratios'], str):
                    tested_df.at[i, 'Ratios'] = None
            self.assertTrue(
                np_array_equal(tested_df.values, expected_df.values)
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
                    'parameters.tsv'
            ), 'r'
        ) as fp:
            tested_df = input_importer(fp)

        tested_dictionary = input_processor(tested_df)
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
    #                 'parameters_woConst.tsv'
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
    #                 'parameters_woDoE.tsv'
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
            ),
            10
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
            ),
            1
        )

    def _test_sampling(
        self,
        ratios: Dict,
        n_var_param: int,
        ref_file: str,
        nb_samples: int
    ):
        seed = 123

        sampling_array = sampling(
            nb_parameters=n_var_param,
            ratios=ratios,
            nb_samples=nb_samples,
            seed=seed
        )
        # for i, sample in enumerate(sampling_array):
        #     print(f'    "{i}": [{", ".join(map(str, sample))}],')
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
                'parameters.tsv'
                ))
        parameters = input_processor(input_df)

        n_variable_parameters = 0
        seed = 123
        ratios = {
            parameter: data['Ratios']
            for parameter, data in parameters.items()
        }
        # ratios = set_sampling_ratios(
        #     ratios=dict.fromkeys(
        #         range(n_variable_parameters), None
        #     ),
        #     all_nb_steps=5
        # )
        doe_levels = sampling(
            nb_parameters=n_variable_parameters,
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
        min_max = [(0.0, 1.0), (0.0, 1.0)]
        for _sampling in [
            (
                sampling_with_duplicates,
                [
                    'WARNING:foo:Duplicates found in sampling: 1',
                    'WARNING:foo:   --> (0.0, 0.0)'
                ]
            ),
            (
                sampling_with_no_min_value,
                ['WARNING:foo:Min value not found in sampling']
            ),
            (
                sampling_with_no_max_value,
                ['WARNING:foo:Max value not found in sampling']
            )
        ]:
            with self.subTest("sampling", _sampling=_sampling):
                sampling_array = _sampling[0]
                expected_error = _sampling[1]
                with self.assertLogs('foo', level='INFO') as cm:
                    check_sampling(
                        sampling_array,
                        min_max,
                        logger=getLogger('foo')
                    )
                    self.assertEqual(
                        cm.output,
                        expected_error
                    )

    def test_convert(self):
        input_df = input_importer(os_path.join(
                self.INPUT_FOLDER,
                'parameters.tsv'
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
            nb_parameters=n_variable_parameters,
            ratios=ratios,
            nb_samples=nb_samples,
            seed=seed
        )

        max_conc = [
            v['maxValue']
            for v in parameters.values()
        ]

        tested_concentrations_array = convert(
            tested_sampling_array,
            max_conc,
        )

        # Reference array
        with open(
            os_path.join(
                self.REF_FOLDER,
                'ref_concentrations_array.json'
                ), 'r') as f:
            ref_concentrations_array = json_load(f)
        import json
        print(json.dumps(tested_concentrations_array.tolist(), indent=4))
        assert_array_equal(
            tested_concentrations_array,
            np_array(ref_concentrations_array)
        )

    def test_convert_EmptyConcentrationsArray(self):
        input_df = input_importer(os_path.join(
                self.INPUT_FOLDER,
                'parameters.tsv'
                ))
        parameters = input_processor(input_df)

        n_variable_parameters = 0
        seed = 123
        ratios = {
            parameter: data['Ratios']
            for parameter, data in parameters.items()
        }
        doe_levels = sampling(
            nb_parameters=n_variable_parameters,
            ratios=ratios,
            seed=seed
        )

        max_conc = [
            v['maxValue']
            for v in parameters.values()
        ]
        # Convert
        doe_concentrations = convert(
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
                input_file=self.parameters,
                output_folder=tmpFolder,
                output_format='csv'
            )

    def test_save_values_wExistingOutFolder(self):
        with TemporaryDirectory() as tmpFolder:
            self._test_save_values(
                input_file=self.parameters,
                output_folder=tmpFolder
            )

    def test_save_values_woExistingOutFolder(self):
        self._test_save_values(
            input_file=self.parameters,
            output_folder=NamedTemporaryFile().name
        )

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
        nb_samples = 100
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
            nb_parameters=n_variable_parameters,
            ratios=ratios,
            nb_samples=nb_samples,
            seed=seed
        )

        max_conc = [
            v['maxValue']
            for v in parameters.values()
        ]
        sampling_values = convert(
            doe_levels,
            max_conc,
        )

        # GENERATE PLATE FILES
        save_values(
            values=sampling_values,
            parameters=list(parameters.keys()),
            output_folder=output_folder,
            output_format=output_format
        )

        # Load ref file
        ref_filename = 'sampling'
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
        print(f'sampling.{output_format}')
        # compare files
        assert ref_initial_set == tested_initial_set

    def test_LHS_results(self):
        input_df = input_importer(
            os_path.join(
                self.INPUT_FOLDER,
                'parameters.tsv'
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
                nb_parameters=len(parameters),
                ratios=ratios,
                nb_samples=nb_samples
            )
            doe_concentrations = convert(
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
                nb_parameters=len(parameters),
                ratios=ratios,
                nb_samples=nb_samples
            )
            doe_concentrations = convert(
                sampling_array,
                max_conc
            )
            # Check that there is no duplicate
            self.assertEqual(
                0,
                len(doe_concentrations)
                - len(np_unique(doe_concentrations, axis=0))
            )
