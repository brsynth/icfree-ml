from unittest import (
    TestCase
)

from os import (
    path as os_path
)

from pandas.testing import (
    assert_frame_equal
)
from pandas import (
    read_json,
    DataFrame
)
from json import (
    load as json_load
)
from tempfile import (
    TemporaryDirectory,
    NamedTemporaryFile
)

from icfree.echo_instructor.echo_instructor import (
    input_importer,
    concentrations_to_volumes,
    save_volumes,
    samples_merger,
    distribute_destination_plate_generator,
    distribute_echo_instructions_generator,
    merge_destination_plate_generator,
    merge_echo_instructions_generator,
    save_echo_instructions
)


class Test(TestCase):

    DATA_FOLDER = os_path.join(
        os_path.dirname(os_path.realpath(__file__)),
        'data', 'echo_instructor'
    )

    INPUT_FOLDER = os_path.join(
        DATA_FOLDER,
        'input'
    )

    REF_FOLDER = os_path.join(
        DATA_FOLDER,
        'output'
    )

    REF_FOLDER_VOLUMES = os_path.join(
        DATA_FOLDER,
        'output', 'volumes_output'
    )

    REF_FOLDER_INSTRUCTIONS = os_path.join(
        DATA_FOLDER,
        'output', 'echo_instructions'
    )

    tested_cfps_parameters = os_path.join(
        INPUT_FOLDER,
        'tested_proCFPS_parameters.tsv'
    )

    tested_initial_concentrations = os_path.join(
        INPUT_FOLDER,
        'tested_initial_concentrations.tsv'
    )

    tested_normalizer_concentrations = os_path.join(
        INPUT_FOLDER,
        'tested_normalizer_concentrations.tsv'
    )

    tested_autofluorescence_concentrations = os_path.join(
        INPUT_FOLDER,
        'tested_autofluorescence_concentrations.tsv'
    )

    def test_input_importer(self):
        # Load references files
        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_proCFPS_parameters_df.json'
            ), 'r'
        ) as fp:
            expected_cfps_parameters_df = read_json(
                fp, orient='split')

        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_initial_concentrations_df.json'
            ), 'r'
        ) as fp:
            expected_initial_concentrations_df = read_json(
                fp, orient='split')

        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_normalizer_concentrations_df.json'
            ), 'r'
        ) as fp:
            expected_normalizer_concentrations_df = read_json(
                fp, orient='split')

        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_autofluorescence_concentrations_df.json'
            ), 'r'
        ) as fp:
            expected_autofluorescence_concentrations_df = read_json(
                fp, orient='split')

            input_importer_dfs = input_importer(
                self.tested_cfps_parameters,
                self.tested_initial_concentrations,
                self.tested_normalizer_concentrations,
                self.tested_autofluorescence_concentrations)

            tested_cfps_parameters_df = input_importer_dfs[0]
            tested_initial_concentrations_df = input_importer_dfs[1]
            tested_normalizer_concentrations_df = input_importer_dfs[2]
            tested_autofluorescence_concentrations_df = input_importer_dfs[3]

        # Compare dataframes
        assert_frame_equal(
            expected_cfps_parameters_df,
            tested_cfps_parameters_df,
            check_dtype=False
        )

        assert_frame_equal(
            expected_initial_concentrations_df,
            tested_initial_concentrations_df,
            check_dtype=False
        )

        assert_frame_equal(
            expected_normalizer_concentrations_df,
            tested_normalizer_concentrations_df,
            check_dtype=False
        )

        assert_frame_equal(
            expected_autofluorescence_concentrations_df,
            tested_autofluorescence_concentrations_df,
            check_dtype=False
        )

    def test_concentrations_to_volumes(self):
        input_importer_dfs = input_importer(
            self.tested_cfps_parameters,
            self.tested_initial_concentrations,
            self.tested_normalizer_concentrations,
            self.tested_autofluorescence_concentrations)

        tested_cfps_parameters_df = input_importer_dfs[0]
        tested_initial_concentrations_df = input_importer_dfs[1]
        tested_normalizer_concentrations_df = input_importer_dfs[2]
        tested_autofluorescence_concentrations_df = input_importer_dfs[3]

        concentrations_to_volumes_dfs = concentrations_to_volumes(
            tested_cfps_parameters_df,
            tested_initial_concentrations_df,
            tested_normalizer_concentrations_df,
            tested_autofluorescence_concentrations_df,
            sample_volume=10000)

        tested_initial_volumes_df = concentrations_to_volumes_dfs[0]
        tested_normalizer_volumes_df = concentrations_to_volumes_dfs[1]
        tested_autofluorescence_volumes_df = concentrations_to_volumes_dfs[2]

        # Load references files
        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_initial_volumes_df.json'
            ), 'r'
        ) as fp:
            expected_initial_volumes_df = read_json(
                fp,
                orient='split')

        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_normalizer_volumes_df.json'
            ), 'r'
        ) as fp:
            expected_normalizer_volumes_df = read_json(
                fp,
                orient='split')

        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_autofluorescence_volumes_df.json'
            ), 'r'
        ) as fp:
            expected_autofluorescence_volumes_df = read_json(
                fp,
                orient='split')

        # Compare dataframes
        assert_frame_equal(
            expected_initial_volumes_df,
            tested_initial_volumes_df,
            check_dtype=False
            )

        assert_frame_equal(
            expected_normalizer_volumes_df,
            tested_normalizer_volumes_df,
            check_dtype=False
            )

        assert_frame_equal(
            expected_autofluorescence_volumes_df,
            tested_autofluorescence_volumes_df,
            check_dtype=False
            )

        # Compare dataframes modulo
        modulo_expected_initial_volumes_df = \
            expected_initial_volumes_df % 2.5

        modulo_expected_autofluorescence_volumes_df = \
            expected_autofluorescence_volumes_df % 2.5

        modulo_expected_normalizer_volumes_df = \
            expected_normalizer_volumes_df % 2.5

        modulo_tested_initial_volumes_df = \
            tested_initial_volumes_df % 2.5

        modulo_tested_normalizer_volumes_df = \
            tested_normalizer_volumes_df % 2.5

        modulo_tested_autofluorescence_volumes_df = \
            tested_autofluorescence_volumes_df % 2.5

        # Compare dataframes
        assert_frame_equal(
            modulo_expected_initial_volumes_df,
            modulo_tested_initial_volumes_df
            )

        assert_frame_equal(
            modulo_expected_autofluorescence_volumes_df,
            modulo_tested_autofluorescence_volumes_df
            )

        assert_frame_equal(
            modulo_expected_normalizer_volumes_df,
            modulo_tested_normalizer_volumes_df
            )

    def test_concentrations_to_volumes_min_warning_factor(self):
        pass

    def test_concentrations_to_volumes_min_warning_water(self):
        pass

    def test_concentrations_to_volumes_max_warning_factor(self):
        pass

    def test_concentrations_to_volumes_max_warning_water(self):
        pass

    def test_save_volumes_wExistingOutFolder(self):
        with TemporaryDirectory() as tmpFolder:
            self._test_save_volumes(
                output_folder=tmpFolder
            )

    def test_save_volumes_woExistingOutFolder(self):
        self._test_save_volumes(
            output_folder=NamedTemporaryFile().name
        )

    def _test_save_volumes(
            self,
            output_folder: str
    ):
        input_importer_dfs = input_importer(
            self.tested_cfps_parameters,
            self.tested_initial_concentrations,
            self.tested_normalizer_concentrations,
            self.tested_autofluorescence_concentrations)

        tested_cfps_parameters_df = input_importer_dfs[0]
        tested_initial_concentrations_df = input_importer_dfs[1]
        tested_normalizer_concentrations_df = input_importer_dfs[2]
        tested_autofluorescence_concentrations_df = input_importer_dfs[3]

        concentrations_to_volumes_dfs = concentrations_to_volumes(
            tested_cfps_parameters_df,
            tested_initial_concentrations_df,
            tested_normalizer_concentrations_df,
            tested_autofluorescence_concentrations_df,
            sample_volume=10000)

        tested_initial_volumes_df = concentrations_to_volumes_dfs[0]
        tested_normalizer_volumes_df = concentrations_to_volumes_dfs[1]
        tested_autofluorescence_volumes_df = concentrations_to_volumes_dfs[2]
        tested_initial_volumes_summary = concentrations_to_volumes_dfs[3]
        tested_normalizer_volumes_summary = concentrations_to_volumes_dfs[4]
        tested_autofluorescence_volumes_summary = \
            concentrations_to_volumes_dfs[5]

        # Load volumes refrence files
        ref_filename = 'expected_initial_volumes'
        with open(
            os_path.join(
                    self.REF_FOLDER_VOLUMES,
                    f'{ref_filename}.tsv'
            )
        ) as fp:
            expected_initial_volumes = fp.read()

        ref_filename = 'expected_autofluorescence_volumes'
        with open(
            os_path.join(
                    self.REF_FOLDER_VOLUMES,
                    f'{ref_filename}.tsv'
            )
        ) as fp:
            expected_autofluorescence_volumes = fp.read()

        ref_filename = 'expected_normalizer_volumes'
        with open(
            os_path.join(
                    self.REF_FOLDER_VOLUMES,
                    f'{ref_filename}.tsv'
            )
        ) as fp:
            expected_normalizer_volumes = fp.read()

        # Load summary volumes refrence files
        ref_filename = 'expected_initial_volumes_summary'
        with open(
            os_path.join(
                    self.REF_FOLDER_VOLUMES,
                    f'{ref_filename}.tsv'
            )
        ) as fp:
            expected_initial_volumes_summary = fp.read()

        ref_filename = 'expected_autofluorescence_volumes_summary'
        with open(
            os_path.join(
                    self.REF_FOLDER_VOLUMES,
                    f'{ref_filename}.tsv'
            )
        ) as fp:
            expected_autofluorescence_volumes_summary = fp.read()

        ref_filename = 'expected_normalizer_volumes_summary'
        with open(
            os_path.join(
                    self.REF_FOLDER_VOLUMES,
                    f'{ref_filename}.tsv'
            )
        ) as fp:
            expected_normalizer_volumes_summary = fp.read()

        # Generate test volume files
        save_volumes(
            tested_cfps_parameters_df,
            tested_initial_volumes_df,
            tested_normalizer_volumes_df,
            tested_autofluorescence_volumes_df,
            tested_initial_volumes_summary,
            tested_normalizer_volumes_summary,
            tested_autofluorescence_volumes_summary,
            output_folder=output_folder)

        # Load test volume files
        with open(
            os_path.join(
                    output_folder,
                    'volumes_output',
                    'initial_volumes.tsv'
            )
        ) as fp:
            tested_initial_volumes = fp.read()

        with open(
            os_path.join(
                    output_folder,
                    'volumes_output',
                    'normalizer_volumes.tsv'
            )
        ) as fp:
            tested_normalizer_volumes = fp.read()

        with open(
            os_path.join(
                    output_folder,
                    'volumes_output',
                    'autofluorescence_volumes.tsv'
            )
        ) as fp:
            tested_autofluorescence_volumes = fp.read()

        with open(
            os_path.join(
                    output_folder,
                    'volumes_output',
                    'initial_volumes_summary.tsv'
            )
        ) as fp:
            tested_initial_volumes_summary = fp.read()

        with open(
            os_path.join(
                    output_folder,
                    'volumes_output',
                    'normalizer_volumes_summary.tsv'
            )
        ) as fp:
            tested_normalizer_volumes_summary = fp.read()

        with open(
            os_path.join(
                    output_folder,
                    'volumes_output',
                    'autofluorescence_volumes_summary.tsv'
            )
        ) as fp:
            tested_autofluorescence_volumes_summary = fp.read()

        # Compare volumes files
        assert expected_initial_volumes == tested_initial_volumes
        assert expected_normalizer_volumes == tested_normalizer_volumes
        assert expected_autofluorescence_volumes == \
            tested_autofluorescence_volumes

        # Compare volumes summary files
        assert expected_initial_volumes_summary == \
            tested_initial_volumes_summary
        assert expected_normalizer_volumes_summary == \
            tested_normalizer_volumes_summary
        assert expected_autofluorescence_volumes_summary == \
            tested_autofluorescence_volumes_summary

    def test_samples_merger(self):
        input_importer_dfs = input_importer(
            self.tested_cfps_parameters,
            self.tested_initial_concentrations,
            self.tested_normalizer_concentrations,
            self.tested_autofluorescence_concentrations)

        tested_cfps_parameters_df = input_importer_dfs[0]
        tested_initial_concentrations_df = input_importer_dfs[1]
        tested_normalizer_concentrations_df = input_importer_dfs[2]
        tested_autofluorescence_concentrations_df = input_importer_dfs[3]

        volumes_array_generator_dfs = concentrations_to_volumes(
            tested_cfps_parameters_df,
            tested_initial_concentrations_df,
            tested_normalizer_concentrations_df,
            tested_autofluorescence_concentrations_df,
            sample_volume=10000)

        tested_initial_volumes_df = volumes_array_generator_dfs[0]
        tested_normalizer_volumes_df = volumes_array_generator_dfs[1]
        tested_autofluorescence_volumes_df = volumes_array_generator_dfs[2]

        samples_merger_dfs = samples_merger(
            tested_initial_volumes_df,
            tested_normalizer_volumes_df,
            tested_autofluorescence_volumes_df)

        tested_merged_plate_1_final = samples_merger_dfs[0]
        tested_merged_plate_2_final = samples_merger_dfs[1]
        tested_merged_plate_3_final = samples_merger_dfs[2]

        # Load reference files
        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_merged_plate_1_final.json'
            ), 'r'
        ) as fp:
            expected_merged_plate_1_final = read_json(
                fp,
                orient='split')

        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_merged_plate_2_final.json'
            ), 'r'
        ) as fp:
            expected_merged_plate_2_final = read_json(
                fp,
                orient='split')

        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_merged_plate_3_final.json'
            ), 'r'
        ) as fp:
            expected_merged_plate_3_final = read_json(
                fp,
                orient='split')

        # Compare dataframes
        assert_frame_equal(
            tested_merged_plate_1_final,
            expected_merged_plate_1_final,
            check_dtype=False
            )

        assert_frame_equal(
            tested_merged_plate_2_final,
            expected_merged_plate_2_final,
            check_dtype=False
            )

        assert_frame_equal(
            tested_merged_plate_3_final,
            expected_merged_plate_3_final,
            check_dtype=False
            )

    def test_distribute_destination_plate_generator(self):
        input_importer_dfs = input_importer(
            self.tested_cfps_parameters,
            self.tested_initial_concentrations,
            self.tested_normalizer_concentrations,
            self.tested_autofluorescence_concentrations)

        tested_cfps_parameters_df = input_importer_dfs[0]
        tested_initial_concentrations_df = input_importer_dfs[1]
        tested_normalizer_concentrations_df = input_importer_dfs[2]
        tested_autofluorescence_concentrations_df = input_importer_dfs[3]

        volumes_array_generator_dfs = concentrations_to_volumes(
            tested_cfps_parameters_df,
            tested_initial_concentrations_df,
            tested_normalizer_concentrations_df,
            tested_autofluorescence_concentrations_df,
            sample_volume=10000)

        tested_initial_volumes_df = volumes_array_generator_dfs[0]
        tested_normalizer_volumes_df = volumes_array_generator_dfs[1]
        tested_autofluorescence_volumes_df = volumes_array_generator_dfs[2]

        tested_distribute_destination_plates_dict = \
            distribute_destination_plate_generator(
                tested_initial_volumes_df,
                tested_normalizer_volumes_df,
                tested_autofluorescence_volumes_df,
                starting_well='A1',
                vertical=True)

        # Load reference dictionary
        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_distribute_destination_plates_dict.json'
            ), 'r'
        ) as fp:
            expected_distribute_destination_plates_dict = (json_load(fp))

        # Convert dictionaries into dataframes
        expected_distribute_destination_plates_dict = {
            key: DataFrame(expected_distribute_destination_plates_dict[key])
            for key in expected_distribute_destination_plates_dict
        }

        # Compare dict keys
        assert tested_distribute_destination_plates_dict.keys() ==  \
            expected_distribute_destination_plates_dict.keys()

        # Compare dict values types
        expected_type_class = \
            type(expected_distribute_destination_plates_dict.values())
        isinstance(
            tested_distribute_destination_plates_dict,
            expected_type_class)

        # Compare dict values
        for keys, values in tested_distribute_destination_plates_dict.items():
            assert_frame_equal(
                values,
                expected_distribute_destination_plates_dict[keys],
                check_dtype=False
                )

    def test_distribute_echo_instructions_generator(self):
        input_importer_dfs = input_importer(
            self.tested_cfps_parameters,
            self.tested_initial_concentrations,
            self.tested_normalizer_concentrations,
            self.tested_autofluorescence_concentrations)

        tested_cfps_parameters_df = input_importer_dfs[0]
        tested_initial_concentrations_df = input_importer_dfs[1]
        tested_normalizer_concentrations_df = input_importer_dfs[2]
        tested_autofluorescence_concentrations_df = input_importer_dfs[3]

        volumes_array_generator_dfs = concentrations_to_volumes(
            tested_cfps_parameters_df,
            tested_initial_concentrations_df,
            tested_normalizer_concentrations_df,
            tested_autofluorescence_concentrations_df,
            sample_volume=10000)

        tested_initial_volumes_df = volumes_array_generator_dfs[0]
        tested_normalizer_volumes_df = volumes_array_generator_dfs[1]
        tested_autofluorescence_volumes_df = volumes_array_generator_dfs[2]

        tested_distribute_destination_plates_dict = \
            distribute_destination_plate_generator(
                tested_initial_volumes_df,
                tested_normalizer_volumes_df,
                tested_autofluorescence_volumes_df,
                starting_well='A1',
                vertical=True)

        tested_distribute_echo_instructions_dict = \
            distribute_echo_instructions_generator(
                tested_distribute_destination_plates_dict)

        # Load reference dictionary
        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_distribute_echo_instructions_dict.json'
            ), 'r'
        ) as fp:
            expected_distribute_echo_instructions_dict = (json_load(fp))

        # Convert dictionaries into dataframes
        expected_distribute_echo_instructions_dict = {
            key: DataFrame(expected_distribute_echo_instructions_dict[key])
            for key in expected_distribute_echo_instructions_dict
        }

        # Compare dict keys
        assert tested_distribute_echo_instructions_dict.keys() ==  \
            expected_distribute_echo_instructions_dict.keys()

        # Compare dict values types
        expected_type_class = \
            type(expected_distribute_echo_instructions_dict.values())
        isinstance(
            tested_distribute_echo_instructions_dict,
            expected_type_class)

        # Compare dict values
        for keys, values in tested_distribute_echo_instructions_dict.items():
            assert_frame_equal(
                values,
                expected_distribute_echo_instructions_dict[keys],
                check_dtype=False
                )

    def test_merge_destination_plate_generator(self):
        input_importer_dfs = input_importer(
            self.tested_cfps_parameters,
            self.tested_initial_concentrations,
            self.tested_normalizer_concentrations,
            self.tested_autofluorescence_concentrations)

        tested_cfps_parameters_df = input_importer_dfs[0]
        tested_initial_concentrations_df = input_importer_dfs[1]
        tested_normalizer_concentrations_df = input_importer_dfs[2]
        tested_autofluorescence_concentrations_df = input_importer_dfs[3]

        volumes_array_generator_dfs = concentrations_to_volumes(
            tested_cfps_parameters_df,
            tested_initial_concentrations_df,
            tested_normalizer_concentrations_df,
            tested_autofluorescence_concentrations_df,
            sample_volume=10000)

        tested_initial_volumes_df = volumes_array_generator_dfs[0]
        tested_normalizer_volumes_df = volumes_array_generator_dfs[1]
        tested_autofluorescence_volumes_df = volumes_array_generator_dfs[2]

        samples_merger_dfs = samples_merger(
            tested_initial_volumes_df,
            tested_normalizer_volumes_df,
            tested_autofluorescence_volumes_df)

        tested_merged_plate_1_final = samples_merger_dfs[0]
        tested_merged_plate_2_final = samples_merger_dfs[1]
        tested_merged_plate_3_final = samples_merger_dfs[2]

        tested_merge_destination_plates_dict =  \
            merge_destination_plate_generator(
                tested_merged_plate_1_final,
                tested_merged_plate_2_final,
                tested_merged_plate_3_final,
                starting_well='A1',
                vertical=True)

        # Load reference dictionary
        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_merge_destination_plates_dict.json'
            ), 'r'
        ) as fp:
            expected_merge_destination_plates_dict = (json_load(fp))

        # Convert dictionaries into dataframes
        expected_merge_destination_plates_dict = {
            key: DataFrame(expected_merge_destination_plates_dict[key])
            for key in expected_merge_destination_plates_dict
        }

        # Compare dict keys
        assert tested_merge_destination_plates_dict.keys() ==  \
            expected_merge_destination_plates_dict.keys()

        # Compare dict values types
        expected_type_class = \
            type(expected_merge_destination_plates_dict.values())
        isinstance(tested_merge_destination_plates_dict, expected_type_class)

        # Compare dict values
        for keys, values in tested_merge_destination_plates_dict.items():
            assert_frame_equal(
                values,
                expected_merge_destination_plates_dict[keys],
                check_dtype=False
                )

    def test_merge_echo_instructions_generator(self):
        input_importer_dfs = input_importer(
            self.tested_cfps_parameters,
            self.tested_initial_concentrations,
            self.tested_normalizer_concentrations,
            self.tested_autofluorescence_concentrations)

        tested_cfps_parameters_df = input_importer_dfs[0]
        tested_initial_concentrations_df = input_importer_dfs[1]
        tested_normalizer_concentrations_df = input_importer_dfs[2]
        tested_autofluorescence_concentrations_df = input_importer_dfs[3]

        volumes_array_generator_dfs = concentrations_to_volumes(
            tested_cfps_parameters_df,
            tested_initial_concentrations_df,
            tested_normalizer_concentrations_df,
            tested_autofluorescence_concentrations_df,
            sample_volume=10000)

        tested_initial_volumes_df = volumes_array_generator_dfs[0]
        tested_normalizer_volumes_df = volumes_array_generator_dfs[1]
        tested_autofluorescence_volumes_df = volumes_array_generator_dfs[2]

        samples_merger_dfs = samples_merger(
            tested_initial_volumes_df,
            tested_normalizer_volumes_df,
            tested_autofluorescence_volumes_df)

        tested_merged_plate_1_final = samples_merger_dfs[0]
        tested_merged_plate_2_final = samples_merger_dfs[1]
        tested_merged_plate_3_final = samples_merger_dfs[2]

        tested_merge_destination_plates_dict =  \
            merge_destination_plate_generator(
                tested_merged_plate_1_final,
                tested_merged_plate_2_final,
                tested_merged_plate_3_final,
                starting_well='A1',
                vertical=True)

        tested_merge_echo_instructions_dict = \
            merge_echo_instructions_generator(
                tested_merge_destination_plates_dict)

        # Load reference dictionary
        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_merge_echo_instructions_dict.json'
            ), 'r'
        ) as fp:
            expected_merge_echo_instructions_dict = (json_load(fp))

        # Convert dictionaries into dataframes
        expected_merge_echo_instructions_dict = {
            key: DataFrame(expected_merge_echo_instructions_dict[key])
            for key in expected_merge_echo_instructions_dict
        }

        # Compare dict keys
        assert tested_merge_echo_instructions_dict.keys() ==  \
            expected_merge_echo_instructions_dict.keys()

        # Compare dict values types
        expected_type_class = \
            type(expected_merge_echo_instructions_dict.values())
        isinstance(tested_merge_echo_instructions_dict, expected_type_class)

        # Compare dict values
        for keys, values in tested_merge_echo_instructions_dict.items():
            assert_frame_equal(
                values,
                expected_merge_echo_instructions_dict[keys],
                check_dtype=False
                )

    def test_save_echo_instructions_wExistingOutFolder(self):
        with TemporaryDirectory() as tmpFolder:
            self._test_save_echo_instructions(
                output_folder=tmpFolder
            )

    def test_save_echo_instructions_woExistingOutFolder(self):
        self._test_save_echo_instructions(
            output_folder=NamedTemporaryFile().name
        )

    def _test_save_echo_instructions(
            self,
            output_folder: str
            ):
        input_importer_dfs = input_importer(
            self.tested_cfps_parameters,
            self.tested_initial_concentrations,
            self.tested_normalizer_concentrations,
            self.tested_autofluorescence_concentrations)

        tested_cfps_parameters_df = input_importer_dfs[0]
        tested_initial_concentrations_df = input_importer_dfs[1]
        tested_normalizer_concentrations_df = input_importer_dfs[2]
        tested_autofluorescence_concentrations_df = input_importer_dfs[3]

        volumes_array_generator_dfs = concentrations_to_volumes(
            tested_cfps_parameters_df,
            tested_initial_concentrations_df,
            tested_normalizer_concentrations_df,
            tested_autofluorescence_concentrations_df,
            sample_volume=10000)

        tested_initial_volumes_df = volumes_array_generator_dfs[0]
        tested_normalizer_volumes_df = volumes_array_generator_dfs[1]
        tested_autofluorescence_volumes_df = volumes_array_generator_dfs[2]

        samples_merger_dfs = samples_merger(
            tested_initial_volumes_df,
            tested_normalizer_volumes_df,
            tested_autofluorescence_volumes_df)

        tested_merged_plate_1_final = samples_merger_dfs[0]
        tested_merged_plate_2_final = samples_merger_dfs[1]
        tested_merged_plate_3_final = samples_merger_dfs[2]

        tested_merge_destination_plates_dict =  \
            merge_destination_plate_generator(
                    tested_merged_plate_1_final,
                    tested_merged_plate_2_final,
                    tested_merged_plate_3_final,
                    starting_well='A1',
                    vertical=True)

        tested_distribute_destination_plates_dict = \
            distribute_destination_plate_generator(
                    tested_initial_volumes_df,
                    tested_normalizer_volumes_df,
                    tested_autofluorescence_volumes_df,
                    starting_well='A1',
                    vertical=True)

        tested_distribute_echo_instructions_dict = \
            distribute_echo_instructions_generator(
                tested_distribute_destination_plates_dict)

        tested_merge_echo_instructions_dict = \
            merge_echo_instructions_generator(
                tested_merge_destination_plates_dict)

        # Generate tested echo instructions files (distributed and merged)
        save_echo_instructions(
            tested_distribute_echo_instructions_dict,
            tested_merge_echo_instructions_dict,
            output_folder=output_folder)

        # TEST MERGED ECHO INSTRUCTIONS FILES
        # Load refrence files
        ref_filename = 'expected_merged_plate_1_final_instructions'
        with open(
            os_path.join(
                    self.REF_FOLDER_INSTRUCTIONS,
                    'merged',
                    f'{ref_filename}.csv'
            )
        ) as fp:
            expected_merged_plate_1_final_instructions = fp.read()

        ref_filename = 'expected_merged_plate_2_final_instructions'
        with open(
            os_path.join(
                    self.REF_FOLDER_INSTRUCTIONS,
                    'merged',
                    f'{ref_filename}.csv'
            )
        ) as fp:
            expected_merged_plate_2_final_instructions = fp.read()

        ref_filename = 'expected_merged_plate_3_final_instructions'
        with open(
            os_path.join(
                    self.REF_FOLDER_INSTRUCTIONS,
                    'merged',
                    f'{ref_filename}.csv'
            )
        ) as fp:
            expected_merged_plate_3_final_instructions = fp.read()

        # Load tested merged echo instructions files
        with open(
            os_path.join(
                    output_folder,
                    'echo_instructions',
                    'merged',
                    'merged_plate_1_final_instructions.csv'
            )
        ) as fp:
            tested_merged_plate_1_final_instructions = fp.read()

        with open(
            os_path.join(
                    output_folder,
                    'echo_instructions',
                    'merged',
                    'merged_plate_2_final_instructions.csv'
            )
        ) as fp:
            tested_merged_plate_2_final_instructions = fp.read()

        with open(
            os_path.join(
                    output_folder,
                    'echo_instructions',
                    'merged',
                    'merged_plate_3_final_instructions.csv'
            )
        ) as fp:
            tested_merged_plate_3_final_instructions = fp.read()

        # Compare merged echo instructions files
        assert expected_merged_plate_1_final_instructions == \
            tested_merged_plate_1_final_instructions
        assert expected_merged_plate_2_final_instructions == \
            tested_merged_plate_2_final_instructions
        assert expected_merged_plate_3_final_instructions == \
            tested_merged_plate_3_final_instructions

        # TEST DISTRBUTED ECHO INSTRUCTIONS FILES
        # Load refrence files
        ref_filename = 'expected_distributed_initial_instructions'
        with open(
            os_path.join(
                    self.REF_FOLDER_INSTRUCTIONS,
                    'distributed',
                    f'{ref_filename}.csv'
            )
        ) as fp:
            expected_distributed_initial_instructions = fp.read()

        ref_filename = 'expected_distributed_normalizer_instructions'
        with open(
            os_path.join(
                    self.REF_FOLDER_INSTRUCTIONS,
                    'distributed',
                    f'{ref_filename}.csv'
            )
        ) as fp:
            expected_distributed_normalizer_instructions = fp.read()

        ref_filename = 'expected_distributed_autofluorescence_instructions'
        with open(
            os_path.join(
                    self.REF_FOLDER_INSTRUCTIONS,
                    'distributed',
                    f'{ref_filename}.csv'
            )
        ) as fp:
            expected_distributed_autofluorescence_instructions = fp.read()

        # Load tested distributed echo instructions files
        with open(
            os_path.join(
                    output_folder,
                    'echo_instructions',
                    'distributed',
                    'distributed_initial_instructions.csv'
            )
        ) as fp:
            tested_distributed_initial_instructions = fp.read()

        with open(
            os_path.join(
                    output_folder,
                    'echo_instructions',
                    'distributed',
                    'distributed_normalizer_instructions.csv'
            )
        ) as fp:
            tested_distributed_normalizer_instructions = fp.read()

        with open(
            os_path.join(
                    output_folder,
                    'echo_instructions',
                    'distributed',
                    'distributed_autofluorescence_instructions.csv'
            )
        ) as fp:
            tested_distributed_autofluorescence_instructions = fp.read()

        # Compare distributed echo instructions files
        assert expected_distributed_initial_instructions == \
            tested_distributed_initial_instructions
        assert expected_distributed_normalizer_instructions == \
            tested_distributed_normalizer_instructions
        assert expected_distributed_autofluorescence_instructions == \
            tested_distributed_autofluorescence_instructions
