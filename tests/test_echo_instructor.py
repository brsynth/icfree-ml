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
    echo_wells
)
from icfree.echo_instructor.plate import Plate


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
                'volumes_summary.tsv'
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

        source_plates = src_plate_generator(
            volumes=tested_volumes_df,
            plate_dead_volume=15000,
            plate_well_capacity=60000,
            param_dead_volumes=param_dead_volumes,
            starting_well='A1',
            optimize_well_volumes=['all'],
            vertical=True,
            plate_dimensions='16x24'
        )
        wells = {}
        for plate_id, plate in source_plates.items():
            wells[plate_id] = echo_wells(plate)
        tested_volumes_summary = {
            param: well['nb_wells'] * well['volume_per_well']
            for param, well in wells['1'].items()
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

        # value_error = \
        #     "Unable to coerce to Series, length must be 18: given 17"
        with pytest_raises(
            ValueError,
            # match=value_error
        ):
            concentrations_to_volumes(
                tested_cfps_parameters_df,
                tested_concentrations_df,
                sample_volume=10000)

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
                plate_dead_volume=15000,
                plate_well_capacity=60000,
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

        source_plates = src_plate_generator(
            volumes=tested_volumes_df,
            plate_dead_volume=15000,
            plate_well_capacity=60000,
            param_dead_volumes=param_dead_volumes,
            starting_well='A1',
            optimize_well_volumes=[],
            vertical=True,
            plate_dimensions='16x24'
        )

        wells = {}
        for plate_id, plate in source_plates.items():
            wells[plate_id] = echo_wells(plate)

        tested_distribute_echo_instructions_dict = \
            echo_instructions_generator(
                volumes=tested_distribute_destination_plates_dict,
                echo_wells=wells
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
                input_folder=self.INPUT_FOLDER,
                ref_folder=self.REF_FOLDER,
                output_folder=tmpFolder
            )

    def test_save_echo_instructions_woExistingOutFolder(self):
        self._test_save_echo_instructions(
            input_folder=self.INPUT_FOLDER,
            ref_folder=self.REF_FOLDER,
            output_folder=NamedTemporaryFile().name
        )

    def _test_save_echo_instructions(
        self,
        input_folder,
        ref_folder,
        output_folder
    ):
        concentrations = {}
        distributed = {}
        for set in ['initial', 'normalizer', 'autofluorescence']:
            concentrations[set] = os_path.join(
                input_folder,
                f'{set}_concentrations.tsv'
            )
            distributed[set] = os_path.join(
                ref_folder,
                'echo_instructions',
                'distributed',
                f'distributed_{set}_instructions.csv'
            )
        merged = []
        for i in range(3):
            merged.append(
                os_path.join(
                    ref_folder,
                    'echo_instructions',
                    'merged',
                    f'merged_plate_{i+1}_final_instructions.csv'
                )
            )
        input_file = os_path.join(
            input_folder,
            'proCFPS_parameters.tsv'
        )
        self.__test_save_echo_instructions(
            tested_cfps_parameters=input_file,
            concentrations=concentrations,
            expected_merged=merged,
            expected_distributed=distributed,
            output_folder=output_folder
        )

    def __test_save_echo_instructions(
            self,
            tested_cfps_parameters,
            concentrations,
            expected_merged,
            expected_distributed,
            output_folder: str
            ):
        tested_initial_concentrations = concentrations['initial']
        tested_normalizer_concentrations = concentrations['normalizer']
        tested_autofluorescence_concentrations = \
            concentrations['autofluorescence']
        (tested_cfps_parameters_df,
         tested_concentrations_df) = input_importer(
            tested_cfps_parameters,
            tested_initial_concentrations,
            tested_normalizer_concentrations,
            tested_autofluorescence_concentrations)

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
                plate_dead_volume=15000,
                plate_well_capacity=60000,
                vertical=True)

        tested_distribute_destination_plates_dict = \
            dst_plate_generator(
                tested_volumes_df,
                starting_well='A1',
                plate_dead_volume=15000,
                plate_well_capacity=60000,
                vertical=True)

        source_plates = src_plate_generator(
            volumes=tested_volumes_df,
            plate_dead_volume=15000,
            plate_well_capacity=60000,
            param_dead_volumes=param_dead_volumes,
            starting_well='A1',
            optimize_well_volumes=[],
            vertical=True,
            plate_dimensions='16x24'
        )

        wells = {}
        for plate_id, plate in source_plates.items():
            wells[plate_id] = echo_wells(plate)

        tested_distribute_echo_instructions_dict = \
            echo_instructions_generator(
                volumes=tested_distribute_destination_plates_dict,
                echo_wells=wells
            )

        tested_merge_echo_instructions_dict = \
            echo_instructions_generator(
                volumes=tested_merge_destination_plates_dict,
                echo_wells=wells
            )

        # Generate tested echo instructions files (distributed and merged)
        save_echo_instructions(
            tested_distribute_echo_instructions_dict,
            tested_merge_echo_instructions_dict,
            output_folder=output_folder)

        # TEST MERGED ECHO INSTRUCTIONS FILES
        # Load refrence files
        expected_merged_files = []
        for _expected_merged in expected_merged:
            with open(_expected_merged) as fp:
                expected_merged_files.append(fp.read())

        # Load tested merged echo instructions files
        tested_merged_files = []
        for i in range(len(expected_merged_files)):
            with open(
                os_path.join(
                        output_folder,
                        'echo_instructions',
                        'merged',
                        f'merged_plate_{i+1}_final_instructions.csv'
                )
            ) as fp:
                tested_merged_files.append(fp.read())

        # Compare merged echo instructions files
        for i in range(len(tested_merged_files)):
            assert expected_merged_files[i] == \
                tested_merged_files[i]

        # TEST DISTRBUTED ECHO INSTRUCTIONS FILES
        # Load refrence files
        for set in expected_distributed.keys():
            ref_filename = expected_distributed[set]
            with open(ref_filename) as fp:
                expected_distributed_file = fp.read()
            # Load tested distributed echo instructions files
            with open(
                os_path.join(
                        output_folder,
                        'echo_instructions',
                        'distributed',
                        f'distributed_{set}_instructions.csv'
                )
            ) as fp:
                tested_distributed_file = fp.read()
            # Compare distributed echo instructions files
            assert expected_distributed_file == \
                tested_distributed_file

    def test_save_volumes_wExistingOutFolder(self):
        with TemporaryDirectory() as tmpFolder:
            self._test_save_volumes(
                cfps_file=self.tested_cfps_parameters,
                input_folder=self.INPUT_FOLDER,
                ref_folder=self.REF_FOLDER_VOLUMES,
                output_folder=tmpFolder
            )

    def test_save_volumes_woExistingOutFolder(self):
        self._test_save_volumes(
            cfps_file=self.tested_cfps_parameters,
            input_folder=self.INPUT_FOLDER,
            ref_folder=self.REF_FOLDER_VOLUMES,
            output_folder=NamedTemporaryFile().name
        )

    def test_save_volumes_PaulData(self):
        input_folder = os_path.join(
            self.INPUT_FOLDER,
            'Paul'
        )
        ref_folder = os_path.join(
            self.REF_FOLDER,
            'Paul',
            'volumes_output'
        )
        cfps_file = os_path.join(
            self.INPUT_FOLDER,
            'Paul',
            'proCFPS_parameters.tsv'
        )
        with TemporaryDirectory() as tmpFolder:
            self._test_save_volumes(
                cfps_file=cfps_file,
                input_folder=input_folder,
                ref_folder=ref_folder,
                output_folder=tmpFolder
            )

    def _test_save_volumes(
        self,
        cfps_file,
        input_folder,
        ref_folder,
        output_folder
    ):
        concentrations = {}
        volumes = {}
        for set in ['initial', 'normalizer', 'autofluorescence']:
            concentrations[set] = os_path.join(
                input_folder,
                f'{set}_concentrations.tsv'
            )
            volumes[set] = os_path.join(
                ref_folder,
                f'{set}_volumes.tsv'
            )
        volumes_report = {}
        volumes_report['warning'] = os_path.join(
            ref_folder,
            'warning_volumes_report.tsv'
        )
        volumes_report['summary'] = os_path.join(
            ref_folder,
            'volumes_summary.tsv'
        )
        self.__test_save_volumes(
            tested_cfps_parameters=cfps_file,
            concentrations=concentrations,
            expected_volumes=volumes,
            expected_volumes_report=volumes_report,
            output_folder=output_folder
        )

    def __test_save_volumes(
            self,
            tested_cfps_parameters,
            concentrations,
            expected_volumes,
            expected_volumes_report,
            output_folder: str
            ):
        tested_initial_concentrations = concentrations['initial']
        tested_normalizer_concentrations = concentrations['normalizer']
        tested_autofluorescence_concentrations = \
            concentrations['autofluorescence']
        (tested_cfps_parameters_df,
         tested_concentrations_df) = input_importer(
            tested_cfps_parameters,
            tested_initial_concentrations,
            tested_normalizer_concentrations,
            tested_autofluorescence_concentrations)

        (tested_volumes_df,
         param_dead_volumes,
         tested_warning_volumes_report) = concentrations_to_volumes(
            tested_cfps_parameters_df,
            tested_concentrations_df,
            sample_volume=10000)

        source_plates = src_plate_generator(
            volumes=tested_volumes_df,
            plate_dead_volume=15000,
            plate_well_capacity=60000,
            param_dead_volumes=param_dead_volumes,
            starting_well='A1',
            optimize_well_volumes=['all'],
            vertical=True,
            plate_dimensions='16x24'
        )

        _echo_wells = {}
        for plate_id, plate in source_plates.items():
            _echo_wells[plate_id] = echo_wells(plate)

        tested_volumes_summary = {
            param: well['nb_wells'] * well['volume_per_well']
            for wells in _echo_wells.values()
            for param, well in wells.items()
        }

        # Generate test volume files
        save_volumes(
            tested_volumes_df,
            tested_volumes_summary,
            tested_warning_volumes_report,
            _echo_wells,
            output_folder=output_folder)

        for set, filename in expected_volumes.items():
            # Load volumes refrence files
            with open(filename) as fp:
                ref_volumes = fp.read()
            # Load test volume files
            with open(
                os_path.join(
                        output_folder,
                        'volumes_output',
                        f'{set}_volumes.tsv'
                )
            ) as fp:
                tested_volumes = fp.read()
            # Compare volumes files
            assert ref_volumes == tested_volumes

        # Load summary volumes refrence files
        with open(expected_volumes_report['summary']) as fp:
            expected_volumes_summary = {}
            lines = fp.readlines()
            for line in lines[1:]:
                (param, vol) = line.split('\t')
                expected_volumes_summary[param] = float(vol)

        with open(expected_volumes_report['warning']) as fp:
            expected_warning_volumes_report = fp.read()

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
                try:
                    (param, vol) = line.split('\t')
                except ValueError:
                    continue
                tested_volumes_summary[param] = float(vol)

        with open(
            os_path.join(
                    output_folder,
                    'volumes_output',
                    'warning_volumes_report.tsv'
            )
        ) as fp:
            tested_warning_volumes_report = fp.read()

        # Compare volumes summary files
        self.assertDictEqual(
            expected_volumes_summary,
            tested_volumes_summary
        )

        # Compare warning volumes reports
        assert expected_warning_volumes_report == \
            tested_warning_volumes_report

    def test_src_plate_generator(self):
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

        for starting_well in ['A1', 'A2']:
            source_plates = src_plate_generator(
                volumes=tested_volumes_df,
                plate_dead_volume=15000,
                plate_well_capacity=60000,
                param_dead_volumes=param_dead_volumes,
                starting_well=starting_well,
                optimize_well_volumes=['all'],
                vertical=True,
                plate_dimensions='16x24'
            )
            keys = source_plates['1'].get_well(starting_well).keys()
            self.assertEqual(
                'Mg-glutamate',
                list(keys)[0]
            )

        with pytest_raises(ValueError):
            src_plate_generator(
                volumes=tested_volumes_df,
                plate_dead_volume=15000,
                plate_well_capacity=60000,
                param_dead_volumes=param_dead_volumes,
                starting_well='Z1',
                optimize_well_volumes=['all'],
                vertical=True,
                plate_dimensions='16x24'
            )

    def test_src_plate_generator_multiple(self):
        cfps_file = os_path.join(
            self.INPUT_FOLDER,
            'Paul',
            'proCFPS_parameters.tsv'
        )
        concentrations = os_path.join(
            self.INPUT_FOLDER,
            'Paul',
            'autofluorescence_concentrations.tsv'
        )
        (tested_cfps_parameters_df,
         tested_concentrations_df) = input_importer(
            cfps_file,
            concentrations,
            concentrations,
            concentrations)

        (tested_volumes_df,
         param_dead_volumes,
         tested_warning_volumes_report) = concentrations_to_volumes(
            tested_cfps_parameters_df,
            tested_concentrations_df,
            sample_volume=565995)

        source_plates = src_plate_generator(
            volumes=tested_volumes_df,
            plate_dead_volume=15000,
            plate_well_capacity=60000,
            param_dead_volumes=param_dead_volumes,
            starting_well='A1',
            optimize_well_volumes=['all'],
            vertical=True,
            plate_dimensions='16x24'
        )

        self.assertEqual(2, len(source_plates))

        (tested_volumes_df,
         param_dead_volumes,
         tested_warning_volumes_report) = concentrations_to_volumes(
            tested_cfps_parameters_df,
            tested_concentrations_df,
            sample_volume=1500000)

        source_plates = src_plate_generator(
            volumes=tested_volumes_df,
            plate_dead_volume=15000,
            plate_well_capacity=60000,
            param_dead_volumes=param_dead_volumes,
            starting_well='A1',
            optimize_well_volumes=['all'],
            vertical=True,
            plate_dimensions='16x24'
        )

        self.assertEqual(3, len(source_plates))


class Test_Plate(TestCase):
    def test_plate_creation(self):
        plate = Plate(
            nb_rows=16,
            nb_cols=24,
            dead_volume=15000,
            well_capacity=60000,
        )
        self.assertEqual(plate.get_nb_rows(), 16)
        self.assertEqual(plate.get_nb_cols(), 24)
        self.assertEqual(plate.get_dead_volume(), 15000)
        self.assertEqual(plate.get_well_capacity(), 60000)
        self.assertEqual(plate.get_nb_wells(), 384)
        self.assertEqual(plate.get_nb_empty_wells(), 384)
        self.assertDictEqual(plate.get_wells(), {})
        self.assertEqual(plate.get_current_well(), 'A1')

    def test_set_nb_empty_wells(self):
        plate = Plate(
            nb_rows=16,
            nb_cols=24,
            dead_volume=15000,
            well_capacity=60000,
        )
        self.assertEqual(plate.get_nb_empty_wells(), 384)
        plate.set_nb_empty_wells(0)
        self.assertEqual(plate.get_nb_empty_wells(), 0)
        plate.set_nb_empty_wells(384)
        self.assertEqual(plate.get_nb_empty_wells(), 384)
        plate.set_nb_empty_wells(385)
        self.assertEqual(plate.get_nb_empty_wells(), 384)

    def test_get_current_well_384(self):
        plate = Plate(
            nb_rows=16,
            nb_cols=24,
            dead_volume=15000,
            well_capacity=60000,
        )
        self.assertEqual(plate.get_current_well(), 'A1')
        plate.set_current_well('P1')
        self.assertEqual(plate.get_current_well(), 'P1')
        plate.set_current_well('P24')
        self.assertEqual(plate.get_current_well(), 'P24')
        with pytest_raises(ValueError):
            plate.set_current_well('P25')

    def test_get_current_well_1536(self):
        plate = Plate(
            nb_rows=32,
            nb_cols=48,
            dead_volume=15000,
            well_capacity=60000,
        )
        self.assertEqual(plate.get_current_well(), 'A1')
        plate.set_current_well('AF1')
        self.assertEqual(plate.get_current_well(), 'AF1')
        plate.set_current_well('AF48')
        self.assertEqual(plate.get_current_well(), 'AF48')
        with pytest_raises(ValueError):
            plate.set_current_well('AF49')

    def test_get_well_volume(self):
        plate = Plate(
            nb_rows=16,
            nb_cols=24,
            dead_volume=15000,
            well_capacity=60000,
        )
        self.assertEqual(plate.get_well_volume('A1'), 0)
        plate.fill_well(well='A1', parameter='param1', volume=15000)
        print(plate.get_well_volume('A1'))
        self.assertEqual(plate.get_well_volume('A1'), 15000)
        self.assertEqual(plate.get_well_volume('A17'), 0)

    def test_fill_well(self):
        plate = Plate(
            nb_rows=16,
            nb_cols=24,
            dead_volume=15000,
            well_capacity=60000,
        )
        plate.fill_well('param1', 10000)
        self.assertEqual(
            10000,
            plate.get_well_volume(plate.get_current_well())
        )
        plate.fill_well('param1', 10000, well='A12')
        self.assertEqual(plate.get_well_volume('A12'), 10000)
        with pytest_raises(IndexError):
            plate.fill_well('param1', 10000, well='Z12')
        plate.fill_well('param1', 100000, well='F1')

    def test_set_current_well(self):
        plate = Plate(
            nb_rows=16,
            nb_cols=24,
            dead_volume=15000,
            well_capacity=60000,
        )
        plate.set_current_well('A1')
        self.assertEqual(plate.get_current_well(), 'A1')
        with pytest_raises(ValueError):
            plate.set_current_well('Z12')

    def test_horizontal_384(self):
        plate = Plate(
            nb_rows=16,
            nb_cols=24,
            dead_volume=15000,
            well_capacity=60000,
            vertical=False
        )
        self.assertEqual(plate.get_current_well(), 'A1')
        plate.next_well()
        self.assertEqual(plate.get_current_well(), 'A2')
        for i in range(1, 24):
            plate.next_well()
        self.assertEqual(plate.get_current_well(), 'B1')

    def test_horizontal_1536(self):
        plate = Plate(
            nb_rows=32,
            nb_cols=48,
            dead_volume=15000,
            well_capacity=60000,
            vertical=False
        )
        self.assertEqual(plate.get_current_well(), 'A1')
        plate.next_well()
        self.assertEqual(plate.get_current_well(), 'A2')
        for i in range(1, 24):
            plate.next_well()
        self.assertEqual(plate.get_current_well(), 'A25')
        for i in range(1, 25):
            plate.next_well()
        self.assertEqual(plate.get_current_well(), 'B1')

    def test_get_dimensions(self):
        plate = Plate(
            nb_rows=16,
            nb_cols=24,
            dead_volume=15000,
            well_capacity=60000,
        )
        self.assertTupleEqual(plate.get_dimensions(), (16, 24))
        plate = Plate(
            nb_rows=32,
            nb_cols=48,
            dead_volume=15000,
            well_capacity=60000,
        )
        self.assertTupleEqual(plate.get_dimensions(), (32, 48))

    def test_get_dimensions_str(self):
        plate = Plate(
            nb_rows=16,
            nb_cols=24,
            dead_volume=15000,
            well_capacity=60000,
        )
        self.assertEqual(plate.get_dimensions_str(), '16x24')
        plate = Plate(
            nb_rows=32,
            nb_cols=48,
            dead_volume=15000,
            well_capacity=60000,
        )
        self.assertEqual(plate.get_dimensions_str(), '32x48')

    def test_get_list_of_wells(self):
        plate = Plate(
            nb_rows=16,
            nb_cols=24,
            dead_volume=15000,
            well_capacity=60000,
        )
        for i in range(8):
            plate.fill_well(f'param{i}', 10000)
            plate.next_well()
        list_of_wells = plate.get_list_of_wells()
        self.assertEqual(list_of_wells[0], 'A1')
        self.assertEqual(list_of_wells[-1], 'H1')

    def test___str__(self):
        plate = Plate(
            nb_rows=16,
            nb_cols=24,
            dead_volume=15000,
            well_capacity=60000,
        )
        _print = (
            'Dimensions: 16x24\n'
            'Dead volume: 15000\n'
            'Well capacity: 60000\n'
            'Empty wells: 384\n'
            'Current well: A1\n'
            'Parameters: []\n'
            'Wells: {}'
        )
        print(plate)
        self.assertEqual(plate.__str__(), _print)

    def test_next_well(self):
        plate = Plate(
            nb_rows=16,
            nb_cols=24,
            dead_volume=15000,
            well_capacity=60000,
        )
        plate.set_current_well('P24')
        with pytest_raises(ValueError):
            plate.next_well()
