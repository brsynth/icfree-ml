from pytest import (
    raises as pytest_raises
)

from unittest import (
    TestCase,
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
    read_json,
    DataFrame
)

from string import ascii_uppercase

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
    dst_plate_generator,
    echo_instructions_generator,
    save_echo_instructions,
    src_plate_generator,
    convert_index_well
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
        'proCFPS_parameters.tsv'
    )

    tested_initial_concentrations = os_path.join(
        INPUT_FOLDER,
        'initial_concentrations.tsv'
    )

    tested_normalizer_concentrations = os_path.join(
        INPUT_FOLDER,
        'normalizer_concentrations.tsv'
    )

    tested_autofluorescence_concentrations = os_path.join(
        INPUT_FOLDER,
        'autofluorescence_concentrations.tsv'
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
                fp,
                orient='split')

        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_initial_concentrations_df.json'
            ), 'r'
        ) as fp:
            expected_initial_concentrations_df = read_json(
                fp,
                orient='split')

        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_normalizer_concentrations_df.json'
            ), 'r'
        ) as fp:
            expected_normalizer_concentrations_df = read_json(
                fp,
                orient='split')

        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_autofluorescence_concentrations_df.json'
            ), 'r'
        ) as fp:
            expected_autofluorescence_concentrations_df = read_json(
                fp,
                orient='split')

            (tested_cfps_parameters_df,
             tested_concentrations_df) = input_importer(
                self.tested_cfps_parameters,
                self.tested_initial_concentrations,
                self.tested_normalizer_concentrations,
                self.tested_autofluorescence_concentrations)

        print(expected_cfps_parameters_df)
        print(tested_cfps_parameters_df)
        # Compare dataframes while ignoring data types
        assert_frame_equal(
            expected_cfps_parameters_df,
            tested_cfps_parameters_df,
            check_dtype=False
        )

        assert_frame_equal(
            expected_initial_concentrations_df,
            tested_concentrations_df['initial'],
            check_dtype=False
        )

        assert_frame_equal(
            expected_normalizer_concentrations_df,
            tested_concentrations_df['normalizer'],
            check_dtype=False
        )

        assert_frame_equal(
            expected_autofluorescence_concentrations_df,
            tested_concentrations_df['autofluorescence'],
            check_dtype=False
        )

    def test_concentrations_to_volumes(self):
        (tested_cfps_parameters_df,
         tested_concentrations_df) = input_importer(
            self.tested_cfps_parameters,
            self.tested_initial_concentrations,
            self.tested_normalizer_concentrations,
            self.tested_autofluorescence_concentrations)

        (tested_volumes_df,
         param_dead_volumes,
         tested_warning_volumes_report) = concentrations_to_volumes(
            tested_cfps_parameters_df,
            tested_concentrations_df,
            sample_volume=10000)

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

        # Compare dataframes while ignoring data types
        assert_frame_equal(
            expected_initial_volumes_df,
            tested_volumes_df['initial'],
            check_dtype=False
            )

        assert_frame_equal(
            expected_normalizer_volumes_df,
            tested_volumes_df['normalizer'],
            check_dtype=False
            )

        assert_frame_equal(
            expected_autofluorescence_volumes_df,
            tested_volumes_df['autofluorescence'],
            check_dtype=False
            )

        with open(
            os_path.join(
                self.REF_FOLDER,
                'volumes_output',
                'expected_volumes_summary.tsv'
            )
        ) as fp:
            expected_volumes_summary = {}
            lines = fp.readlines()
            for line in lines[1:]:
                (param, vol) = line.split('\t')
                expected_volumes_summary[param] = float(vol)

        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_warning_volumes_report_df.json'
            ), 'r'
        ) as fp:
            expected_warning_volumes_report_df = read_json(
                fp,
                orient='split')

        source_plate = src_plate_generator(
            volumes=tested_volumes_df,
            plate_dead_volume=15000,
            plate_well_capacity=60000,
            param_dead_volumes=param_dead_volumes,
            starting_well='A1',
            optimize_well_volumes=['all'],
            vertical=True,
            plate_dimensions='16x24'
        )
        tested_volumes_summary = {
            param: volume['nb_wells'] * volume['volume_per_well']
            for param, volume in source_plate.items()
        }
        self.assertDictEqual(
            expected_volumes_summary,
            tested_volumes_summary
        )

        assert_frame_equal(
            expected_warning_volumes_report_df,
            tested_warning_volumes_report,
            check_dtype=False
            )

        # Generate volumes dataframes modulo
        modulo_expected_initial_volumes_df = \
            expected_initial_volumes_df % 2.5

        modulo_expected_autofluorescence_volumes_df = \
            expected_autofluorescence_volumes_df % 2.5

        modulo_expected_normalizer_volumes_df = \
            expected_normalizer_volumes_df % 2.5

        modulo_tested_initial_volumes_df = \
            tested_volumes_df['initial'] % 2.5

        modulo_tested_normalizer_volumes_df = \
            tested_volumes_df['normalizer'] % 2.5

        modulo_tested_autofluorescence_volumes_df = \
            tested_volumes_df['autofluorescence'] % 2.5

        # Compare volumes dataframes modulo
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

    def test_concentrations_to_volumes_low_stock_warning(self):
        tested_cfps_parameters = os_path.join(
                self.INPUT_FOLDER,
                'proCFPS_parameters_low_stock.tsv'
                )

        (tested_cfps_parameters_df,
         tested_concentrations_df) = input_importer(
            tested_cfps_parameters,
            self.tested_initial_concentrations,
            self.tested_normalizer_concentrations,
            self.tested_autofluorescence_concentrations)

        # Generate tested warning report
        (tested_volumes_df,
         param_dead_volumes,
         tested_warning_volumes_report) = concentrations_to_volumes(
            tested_cfps_parameters_df,
            tested_concentrations_df,
            sample_volume=10000)

        # Load reference warning report
        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_warning_volumes_report_df_low_stock.json'
            ), 'r'
        ) as fp:
            expected_warning_volumes_report_df = read_json(
                fp,
                orient='split')

        assert_array_equal(
            expected_warning_volumes_report_df,
            tested_warning_volumes_report
            )

    def test_concentrations_to_volumes_valueerror(self):
        tested_cfps_parameters = os_path.join(
                self.INPUT_FOLDER,
                'proCFPS_parameters_woGOI.tsv'
                )

        (tested_cfps_parameters_df,
         tested_concentrations_df) = input_importer(
            tested_cfps_parameters,
            self.tested_initial_concentrations,
            self.tested_normalizer_concentrations,
            self.tested_autofluorescence_concentrations)

        value_error = \
            "Unable to coerce to Series, length must be 18: given 17"
        with pytest_raises(
            ValueError,
                match=value_error):
            concentrations_to_volumes(
                tested_cfps_parameters_df,
                tested_concentrations_df,
                sample_volume=10000)

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
        (tested_cfps_parameters_df,
         tested_concentrations_df) = input_importer(
            self.tested_cfps_parameters,
            self.tested_initial_concentrations,
            self.tested_normalizer_concentrations,
            self.tested_autofluorescence_concentrations)

        (tested_volumes_df,
         param_dead_volumes,
         tested_warning_volumes_report) = concentrations_to_volumes(
            tested_cfps_parameters_df,
            tested_concentrations_df,
            sample_volume=10000)

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
        with open(
            os_path.join(
                self.REF_FOLDER_VOLUMES,
                'expected_volumes_summary.tsv'
            )
        ) as fp:
            expected_volumes_summary = {}
            lines = fp.readlines()
            for line in lines[1:]:
                (param, vol) = line.split('\t')
                expected_volumes_summary[param] = float(vol)

        # ref_filename = 'expected_autofluorescence_volumes_summary'
        # with open(
        #     os_path.join(
        #             self.REF_FOLDER_VOLUMES,
        #             f'{ref_filename}.tsv'
        #     )
        # ) as fp:
        #     expected_autofluorescence_volumes_summary = fp.read()

        # ref_filename = 'expected_normalizer_volumes_summary'
        # with open(
        #     os_path.join(
        #             self.REF_FOLDER_VOLUMES,
        #             f'{ref_filename}.tsv'
        #     )
        # ) as fp:
        #     expected_normalizer_volumes_summary = fp.read()

        ref_filename = 'expected_warning_volumes_report'
        with open(
            os_path.join(
                    self.REF_FOLDER_VOLUMES,
                    f'{ref_filename}.tsv'
            )
        ) as fp:
            expected_warning_volumes_report = fp.read()

        source_plate = src_plate_generator(
            volumes=tested_volumes_df,
            plate_dead_volume=15000,
            plate_well_capacity=60000,
            param_dead_volumes=param_dead_volumes,
            starting_well='A1',
            optimize_well_volumes=['all'],
            vertical=True,
            plate_dimensions='16x24'
        )

        tested_volumes_summary = {
            param: volume['nb_wells'] * volume['volume_per_well']
            for param, volume in source_plate.items()
        }

        # Generate test volume files
        save_volumes(
            tested_cfps_parameters_df,
            tested_volumes_df,
            tested_volumes_summary,
            tested_warning_volumes_report,
            source_plate,
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
                'volumes_summary.tsv'
            )
        ) as fp:
            tested_volumes_summary = {}
            lines = fp.readlines()
            for line in lines[1:]:
                (param, vol) = line.split('\t')
                tested_volumes_summary[param] = float(vol)

        with open(
            os_path.join(
                    output_folder,
                    'volumes_output',
                    'warning_volumes_report.tsv'
            )
        ) as fp:
            tested_warning_volumes_report = fp.read()

        # Compare volumes files
        assert expected_initial_volumes == tested_initial_volumes
        assert expected_normalizer_volumes == tested_normalizer_volumes
        assert expected_autofluorescence_volumes == \
            tested_autofluorescence_volumes

        # Compare volumes summary files
        self.assertDictEqual(
            expected_volumes_summary,
            tested_volumes_summary
        )

        # Compare warning volumes reports
        assert expected_warning_volumes_report == \
            tested_warning_volumes_report

    def test_samples_merger(self):
        (tested_cfps_parameters_df,
         tested_concentrations_df) = input_importer(
            self.tested_cfps_parameters,
            self.tested_initial_concentrations,
            self.tested_normalizer_concentrations,
            self.tested_autofluorescence_concentrations)

        (tested_volumes_df,
         param_dead_volumes,
         tested_warning_volumes_report) = concentrations_to_volumes(
            tested_cfps_parameters_df,
            tested_concentrations_df,
            sample_volume=10000)

        samples_merger_dfs = samples_merger(tested_volumes_df)

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
            samples_merger_dfs['merged_plate_1'],
            expected_merged_plate_1_final,
            check_dtype=False
            )

        assert_frame_equal(
            samples_merger_dfs['merged_plate_2'],
            expected_merged_plate_2_final,
            check_dtype=False
            )

        assert_frame_equal(
            samples_merger_dfs['merged_plate_3'],
            expected_merged_plate_3_final,
            check_dtype=False
            )

    def test_distribute_dst_plate_generator_vertical_true(self):
        (tested_cfps_parameters_df,
         tested_concentrations_df) = input_importer(
            self.tested_cfps_parameters,
            self.tested_initial_concentrations,
            self.tested_normalizer_concentrations,
            self.tested_autofluorescence_concentrations)

        (tested_volumes_df,
         param_dead_volumes,
         tested_warning_volumes_report) = concentrations_to_volumes(
            tested_cfps_parameters_df,
            tested_concentrations_df,
            sample_volume=10000)

        tested_distribute_destination_plates_dict = \
            dst_plate_generator(
                tested_volumes_df,
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

    def test_distribute_dst_plate_generator_vertical_false(self):
        (tested_cfps_parameters_df,
         tested_concentrations_df) = input_importer(
            self.tested_cfps_parameters,
            self.tested_initial_concentrations,
            self.tested_normalizer_concentrations,
            self.tested_autofluorescence_concentrations)

        (tested_volumes_df,
         param_dead_volumes,
         tested_warning_volumes_report) = concentrations_to_volumes(
            tested_cfps_parameters_df,
            tested_concentrations_df,
            sample_volume=10000)

        tested_distribute_destination_plates_dict = \
            dst_plate_generator(
                tested_volumes_df,
                starting_well='A1',
                vertical=False)

        # Load reference dictionary
        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_distribute_destination_plates_dict_false.json'
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

    def test_echo_instructions_generator(self):
        (tested_cfps_parameters_df,
         tested_concentrations_df) = input_importer(
            self.tested_cfps_parameters,
            self.tested_initial_concentrations,
            self.tested_normalizer_concentrations,
            self.tested_autofluorescence_concentrations)

        (tested_volumes_df,
         param_dead_volumes,
         tested_warning_volumes_report) = concentrations_to_volumes(
            tested_cfps_parameters_df,
            tested_concentrations_df,
            sample_volume=10000)

        tested_distribute_destination_plates_dict = \
            dst_plate_generator(
                tested_volumes_df,
                starting_well='A1',
                vertical=True)

        source_plate = src_plate_generator(
            volumes=tested_volumes_df,
            plate_dead_volume=15000,
            plate_well_capacity=60000,
            param_dead_volumes=param_dead_volumes,
            starting_well='A1',
            optimize_well_volumes=[],
            vertical=True,
            plate_dimensions='16x24'
        )

        tested_distribute_echo_instructions_dict = \
            echo_instructions_generator(
                volumes=tested_distribute_destination_plates_dict,
                source_plate=source_plate
            )

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

    def test_merge_dst_plate_generator_vertical_true(self):
        (tested_cfps_parameters_df,
         tested_concentrations_df) = input_importer(
            self.tested_cfps_parameters,
            self.tested_initial_concentrations,
            self.tested_normalizer_concentrations,
            self.tested_autofluorescence_concentrations)

        (tested_volumes_df,
         param_dead_volumes,
         tested_warning_volumes_report) = concentrations_to_volumes(
            tested_cfps_parameters_df,
            tested_concentrations_df,
            sample_volume=10000)

        samples_merger_dfs = samples_merger(tested_volumes_df)

        tested_merge_destination_plates_dict =  \
            dst_plate_generator(
                samples_merger_dfs,
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

    def test_merge_dst_plate_generator_vertical_false(self):
        (tested_cfps_parameters_df,
         tested_concentrations_df) = input_importer(
            self.tested_cfps_parameters,
            self.tested_initial_concentrations,
            self.tested_normalizer_concentrations,
            self.tested_autofluorescence_concentrations)

        (tested_volumes_df,
         param_dead_volumes,
         tested_warning_volumes_report) = concentrations_to_volumes(
            tested_cfps_parameters_df,
            tested_concentrations_df,
            sample_volume=10000)

        samples_merger_dfs = samples_merger(tested_volumes_df)

        tested_merge_destination_plates_dict =  \
            dst_plate_generator(
                samples_merger_dfs,
                starting_well='A1',
                vertical=False)

        # Load reference dictionary
        with open(
            os_path.join(
                    self.REF_FOLDER,
                    'expected_merge_destination_plates_dict_false.json'
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
        (tested_cfps_parameters_df,
         tested_concentrations_df) = input_importer(
            self.tested_cfps_parameters,
            self.tested_initial_concentrations,
            self.tested_normalizer_concentrations,
            self.tested_autofluorescence_concentrations)

        (tested_volumes_df,
         param_dead_volumes,
         tested_warning_volumes_report) = concentrations_to_volumes(
            tested_cfps_parameters_df,
            tested_concentrations_df,
            sample_volume=10000)

        samples_merger_dfs = samples_merger(tested_volumes_df)

        tested_merge_destination_plates_dict =  \
            dst_plate_generator(
                    samples_merger_dfs,
                    starting_well='A1',
                    vertical=True)

        tested_distribute_destination_plates_dict = \
            dst_plate_generator(
                    tested_volumes_df,
                    starting_well='A1',
                    vertical=True)

        source_plate = src_plate_generator(
            volumes=tested_volumes_df,
            plate_dead_volume=15000,
            plate_well_capacity=60000,
            param_dead_volumes=param_dead_volumes,
            starting_well='A1',
            optimize_well_volumes=[],
            vertical=True,
            plate_dimensions='16x24'
        )

        tested_distribute_echo_instructions_dict = \
            echo_instructions_generator(
                volumes=tested_distribute_destination_plates_dict,
                source_plate=source_plate
            )

        tested_merge_echo_instructions_dict = \
            echo_instructions_generator(
                volumes=tested_merge_destination_plates_dict,
                source_plate=source_plate
            )

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

    def test_convert_index_well_vertical_384(self):
        rows = ascii_uppercase[:16]
        cols = [i+1 for i in range(24)]
        self.assertEqual(
            convert_index_well(
                well_i=0,
                rows=rows,
                cols=cols,
                vertical=True
            ),
            'A1'
        )
        self.assertEqual(
            convert_index_well(
                well_i=1,
                rows=rows,
                cols=cols,
                vertical=True
            ),
            'B1'
        )
        self.assertEqual(
            convert_index_well(
                well_i=16,
                rows=rows,
                cols=cols,
                vertical=True
            ),
            'A2'
        )
        self.assertEqual(
            convert_index_well(
                well_i=383,
                rows=rows,
                cols=cols,
                vertical=True
            ),
            'P24'
        )

    def test_convert_index_well_horizontal_384(self):
        rows = ascii_uppercase[:16]
        cols = [i+1 for i in range(24)]
        self.assertEqual(
            convert_index_well(
                well_i=0,
                rows=rows,
                cols=cols,
                vertical=False
            ),
            'A1'
        )
        self.assertEqual(
            convert_index_well(
                well_i=1,
                rows=rows,
                cols=cols,
                vertical=False
            ),
            'A2'
        )
        self.assertEqual(
            convert_index_well(
                well_i=24,
                rows=rows,
                cols=cols,
                vertical=False
            ),
            'B1'
        )
        self.assertEqual(
            convert_index_well(
                well_i=383,
                rows=rows,
                cols=cols,
                vertical=False
            ),
            'P24'
        )

    def test_convert_index_well_vertical_1536(self):
        rows = [f"{i}{j}" for i in ["", "A"] for j in ascii_uppercase][:32]
        cols = [i+1 for i in range(48)]
        self.assertEqual(
            convert_index_well(
                well_i=0,
                rows=rows,
                cols=cols,
                vertical=True
            ),
            'A1'
        )
        self.assertEqual(
            convert_index_well(
                well_i=1,
                rows=rows,
                cols=cols,
                vertical=True
            ),
            'B1'
        )
        self.assertEqual(
            convert_index_well(
                well_i=32,
                rows=rows,
                cols=cols,
                vertical=True
            ),
            'A2'
        )
        self.assertEqual(
            convert_index_well(
                well_i=1535,
                rows=rows,
                cols=cols,
                vertical=True
            ),
            'AF48'
        )

    def test_convert_index_well_horizontal_1536(self):
        rows = [f"{i}{j}" for i in ["", "A"] for j in ascii_uppercase][:32]
        cols = [i+1 for i in range(48)]
        self.assertEqual(
            convert_index_well(
                well_i=0,
                rows=rows,
                cols=cols,
                vertical=False
            ),
            'A1'
        )
        self.assertEqual(
            convert_index_well(
                well_i=1,
                rows=rows,
                cols=cols,
                vertical=False
            ),
            'A2'
        )
        self.assertEqual(
            convert_index_well(
                well_i=48,
                rows=rows,
                cols=cols,
                vertical=False
            ),
            'B1'
        )
        self.assertEqual(
            convert_index_well(
                well_i=1535,
                rows=rows,
                cols=cols,
                vertical=False
            ),
            'AF48'
        )
