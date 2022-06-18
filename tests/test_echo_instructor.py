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
    read_json
)

from icfree.echo_instructor.echo_instructor import (
    input_importer,
    volumes_array_generator
    # save_volumes_array,
    # samples_merger,
    # multiple_destination_plate_generator,
    # multiple_echo_instructions_generator,
    # single_destination_plate_generator,
    # single_echo_instructions_generator,
    # save_echo_instructions
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
        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_proCFPS_parameters_df.json'
            ), 'r'
        ) as fp1:
            expected_cfps_parameters_df = read_json(
                fp1, orient='split')

        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_initial_concentrations_df.json'
            ), 'r'
        ) as fp2:
            expected_initial_concentrations_df = read_json(
                fp2, orient='split')

        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_normalizer_concentrations_df.json'
            ), 'r'
        ) as fp3:
            expected_normalizer_concentrations_df = read_json(
                fp3, orient='split')

        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_autofluorescence_concentrations_df.json'
            ), 'r'
        ) as fp4:
            expected_autofluorescence_concentrations_df = read_json(
                fp4, orient='split')

            input_importer_dfs = input_importer(
                self.tested_cfps_parameters,
                self.tested_initial_concentrations,
                self.tested_normalizer_concentrations,
                self.tested_autofluorescence_concentrations)

            tested_cfps_parameters_df = input_importer_dfs[0]
            tested_initial_concentrations_df = input_importer_dfs[1]
            tested_normalizer_concentrations_df = input_importer_dfs[2]
            tested_autofluorescence_concentrations_df = input_importer_dfs[3]

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

    def test_volumes_array_generator(self):
        input_importer_dfs = input_importer(
            self.tested_cfps_parameters,
            self.tested_initial_concentrations,
            self.tested_normalizer_concentrations,
            self.tested_autofluorescence_concentrations)

        tested_cfps_parameters_df = input_importer_dfs[0]
        tested_initial_concentrations_df = input_importer_dfs[1]
        tested_normalizer_concentrations_df = input_importer_dfs[2]
        tested_autofluorescence_concentrations_df = input_importer_dfs[3]

        volumes_array_generator_dfs = volumes_array_generator(
            tested_cfps_parameters_df,
            tested_initial_concentrations_df,
            tested_normalizer_concentrations_df,
            tested_autofluorescence_concentrations_df,
            sample_volume=10000)

        tested_initial_volumes_df = volumes_array_generator_dfs[0]
        tested_normalizer_volumes_df = volumes_array_generator_dfs[1]
        tested_autofluorescence_volumes_df = volumes_array_generator_dfs[2]

        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_initial_volumes_df.json'
            ), 'r'
        ) as fp1:
            expected_initial_volumes_df = read_json(
                fp1, orient='split')

        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_normalizer_volumes_df.json'
            ), 'r'
        ) as fp2:
            expected_normalizer_volumes_df = read_json(
                fp2, orient='split')

        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_autofluorescence_volumes_df.json'
            ), 'r'
        ) as fp3:
            expected_autofluorescence_volumes_df = read_json(
                fp3, orient='split')

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

    def test_save_volumes_array(self):
        pass

    def test_samples_merger(self):
        pass

    def test_multiple_destination_plate_generator(self):
        pass

    def test_multiple_echo_instructions_generator(self):
        pass

    def test_single_destination_plate_generator(self):
        pass

    def test_single_echo_instructions_generator(self):
        pass

    def test_save_echo_instructions(self):
        pass
