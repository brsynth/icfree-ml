import unittest
import pandas as pd
from math import ceil

from icfree.plates_generator.plates_generator import (
    well_label_generator,
    gen_dst_plt,
    gen_src_plt,
    extract_literal_numeric,
    set_grid_for_display
)
from icfree.plates_generator.args import build_args_parser


class TestWellLabelGenerator(unittest.TestCase):
    def test_standard_dimensions(self):
        self.assertEqual(well_label_generator('4x6'), 
                         ['A1', 'B1', 'C1', 'D1',
                          'A2', 'B2', 'C2', 'D2',
                          'A3', 'B3', 'C3', 'D3',
                          'A4', 'B4', 'C4', 'D4',
                          'A5', 'B5', 'C5', 'D5',
                          'A6', 'B6', 'C6', 'D6'])

    def test_single_row(self):
        self.assertEqual(well_label_generator('1x10'), 
                         ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10'])

    def test_single_column(self):
        self.assertEqual(well_label_generator('10x1'), 
                         ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'I1', 'J1'])

    def test_max_single_letter_rows(self):
        self.assertEqual(well_label_generator('26x1'), 
                         [f"{chr(65+i)}1" for i in range(26)])

    def test_first_double_letter_row(self):
        self.assertEqual(well_label_generator('27x1'), 
                         [f"{chr(65+i)}1" for i in range(26)] + ['AA1'])

    def test_large_number_of_columns(self):
        self.assertEqual(well_label_generator('1x100'), 
                         [f"A{i+1}" for i in range(100)])

    def test_large_number_of_rows(self):
        expected = [f"{chr(65+j)}1" for j in range(26)]
        for i in range(2):
            expected += [f"{chr(65+i)}{chr(65+j)}1" for j in range(26)]
        expected += [f"{chr(65+2)}{chr(65+j)}1" for j in range(22)]
        self.assertEqual(well_label_generator('100x1'), 
                         expected)

    def test_invalid_dimensions_format(self):
        with self.assertRaises(ValueError):
            well_label_generator('3x')

    def test_zero_dimensions(self):
        self.assertEqual(well_label_generator('0x5'), [])
        self.assertEqual(well_label_generator('5x0'), [])

    def test_high_dimensions(self):
        # This test ensures the function can handle a large number of rows and columns
        result = well_label_generator('50x50')
        self.assertEqual(len(result), 2500)  # Ensure the total count of labels is correct
        self.assertTrue(result[-1], 'AX50')  # Check the last label for correctness


class TestGenDstPlt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Mock DataFrame setup
        cls.mock_df = pd.DataFrame({
            'Component1': [100, 200, 300],
            'Component2': [50, 100, 150]
        })

    def test_standard_case(self):
        result = gen_dst_plt(self.mock_df.copy(), 1000, 60000, '8x12', 'A1', 1)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)  # Expecting a single plate
        self.assertTrue('Well' in result[0].columns)

    def test_sample_volume_exceeds_well_capacity(self):
        with self.assertRaises(ValueError):
            gen_dst_plt(self.mock_df.copy(), 100000, 60000, '8x12', 'A1', 1)

    def test_single_plate_distribution(self):
        result = gen_dst_plt(self.mock_df.copy(), 2000, 60000, '8x12', 'A1', 1)
        self.assertEqual(len(result), 1)

    def test_multiple_plate_distribution(self):
        result = gen_dst_plt(self.mock_df.copy(), 2000, 60000, '3x3', 'A1', 10)
        self.assertTrue(len(result) > 1)

    def test_starting_well_mid_plate(self):
        result = gen_dst_plt(self.mock_df.copy(), 2000, 60000, '8x12', 'B3', 1)
        self.assertTrue(result[0]['Well'].iloc[0], 'B3')

    def test_exact_fit(self):
        result = gen_dst_plt(self.mock_df.copy(), 2000, 60000, '1x3', 'A1', 1)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 3)

    def test_overcapacity(self):
        result = gen_dst_plt(self.mock_df.copy(), 2000, 60000, '1x2', 'A1', 2)
        self.assertTrue(len(result) > 1)  # Expecting multiple plates due to overcapacity

    def test_negative_water_volume(self):
        with self.assertRaises(ValueError):
            gen_dst_plt(pd.DataFrame({'Component1': [1000], 'Component2': [1100]}), 2000, 60000, '8x12', 'A1', 1)

    def test_edge_cases(self):
        # Empty DataFrame
        self.assertEqual([], gen_dst_plt(pd.DataFrame(), 2000, 60000, '8x12', 'A1', 1))
        # Zero replicates
        self.assertEqual([], gen_dst_plt(self.mock_df.copy(), 2000, 60000, '8x12', 'A1', 0))
        # Invalid starting well
        with self.assertRaises(ValueError):
            gen_dst_plt(self.mock_df.copy(), 2000, 60000, '8x12', 'Z1', 1)


class TestGenSrcPlt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setup for mock destination plates
        cls.dest_plates = [
            pd.DataFrame({
                'Well': ['A1', 'A2', 'A3'],
                'Component1': [20, 30, 40],
                'Component2': [10, 15, 25],
                'Water': [70, 55, 35]
            }),
            pd.DataFrame({
                'Well': ['A1', 'A2', 'A3'],
                'Component1': [25, 35, 45],
                'Component2': [15, 20, 30],
                'Water': [60, 45, 25]
            })
        ]

    def test_basic_functionality(self):
        source_plates = gen_src_plt(self.dest_plates, 100, '8x12', 'A1', [], 10)
        self.assertIsInstance(source_plates, list)
        self.assertTrue(len(source_plates) > 0)

    def test_single_component_distribution(self):
        # Assuming the test data setup is correct
        component_volume = sum([plate['Component1'].sum() for plate in self.dest_plates])
        effective_well_capacity = 90  # 100 - 10 dead volume
        expected_wells = ceil(component_volume / effective_well_capacity)
        source_plates = gen_src_plt(self.dest_plates, 100, '8x12', 'A1', [], 10)
        actual_wells = sum(plate['Component1'].astype(bool).sum() for plate in source_plates)
        self.assertEqual(expected_wells, actual_wells)

    def test_multiple_component_distribution(self):
        source_plates = gen_src_plt(self.dest_plates, 100, '8x12', 'A1', [], 10)
        self.assertTrue(all(['Component1' in plate for plate in source_plates]))
        self.assertTrue(all(['Component2' in plate for plate in source_plates]))

    def test_new_column_requirement(self):
        source_plates = gen_src_plt(self.dest_plates, 100, '8x12', 'A1', ['Component2'], 10)
        # Get the 'Well' value for the first non-zero value in the 'Component2' column
        # and check if it's in a new column in the plate
        well = source_plates[0].loc[source_plates[0]['Component2'] > 0, 'Well'].values
        self.assertEqual(well[0], 'A2')  # Expecting the well to be in a new column

    def test_starting_well_effect(self):
        source_plates = gen_src_plt(self.dest_plates, 100, '8x12', 'B2', [], 10)
        # Get the 'Well' value for the last non-0 value in the first plate
        well = source_plates[0]['Well'].iloc[-1]
        self.assertEqual(well, 'B3')  # Expecting the well to be the starting well

    def test_empty_destination_plates(self):
        source_plates = gen_src_plt([], 100, '8x12', 'A1', [], 10)
        self.assertTrue(source_plates[0].empty)

    def test_invalid_parameters(self):
        # Negative well capacity
        with self.assertRaises(ValueError):
            gen_src_plt(self.dest_plates, -100, '8x12', 'A1', [], 10)
        # Negative dead volume
        with self.assertRaises(ValueError):
            gen_src_plt(self.dest_plates, 100, '8x12', 'A1', [], -10)
        # Dead volume exceeding well capacity
        with self.assertRaises(ValueError):
            gen_src_plt(self.dest_plates, 100, '8x12', 'A1', [], 110)

    def test_plate_capacity_exceeded(self):
        samples_df = pd.DataFrame({
            'Component1': [100, 200, 300],
            'Component2': [50, 100, 150]
        })
        # Generate as many duplicates as needed to exceed one single source plate
        dest_plates = gen_dst_plt(samples_df, 2000, 60000, '8x12', 'A1', 2)
        result = gen_src_plt(dest_plates, 100, '8x12', 'A1', [], 10)
        self.assertTrue(len(result) > 1)  # Expecting multiple plates due to overcapacity


class TestExtractLiteralNumeric(unittest.TestCase):
    def test_basic_match(self):
        self.assertEqual(extract_literal_numeric('A123'), ('A', '123'))

    def test_no_match(self):
        self.assertEqual(extract_literal_numeric('123A'), (None, None))
        self.assertEqual(extract_literal_numeric('ABC'), (None, None))

    def test_multiple_matches(self):
        self.assertEqual(extract_literal_numeric('ABC123XYZ456'), ('ABC', '123'))

    def test_special_characters(self):
        self.assertEqual(extract_literal_numeric('AB-CD123'), (None, None))
        self.assertEqual(extract_literal_numeric('AB CD123'), (None, None))

    def test_case_sensitivity(self):
        self.assertEqual(extract_literal_numeric('aBc123'), ('aBc', '123'))

    def test_long_strings(self):
        long_input = 'A' * 1000 + '123'
        self.assertEqual(extract_literal_numeric(long_input), ('A' * 1000, '123'))

    def test_empty_string(self):
        self.assertEqual(extract_literal_numeric(''), (None, None))

    def test_numeric_only_and_literal_only(self):
        self.assertEqual(extract_literal_numeric('12345'), (None, None))
        self.assertEqual(extract_literal_numeric('ABCDE'), (None, None))


class TestSetGridForDisplay(unittest.TestCase):
    def setUp(self):
        # Sample plate data setup
        self.sample_plate_data = pd.DataFrame({
            'Well': ['A1', 'B2', 'C3'],
            'Value': [1, 2, 3]
        })

    def test_standard_usage(self):
        grid = set_grid_for_display(self.sample_plate_data, '3x3')
        expected_grid = pd.DataFrame('', columns=['1', '2', '3'], index=['A', 'B', 'C'])
        expected_grid.at['A', '1'] = 'X'
        expected_grid.at['B', '2'] = 'X'
        expected_grid.at['C', '3'] = 'X'
        pd.testing.assert_frame_equal(grid, expected_grid)

    def test_empty_plate(self):
        empty_plate_data = pd.DataFrame(columns=['Well', 'Value'])
        grid = set_grid_for_display(empty_plate_data, '3x3')
        expected_grid = pd.DataFrame('', columns=['1', '2', '3'], index=['A', 'B', 'C'])
        pd.testing.assert_frame_equal(grid, expected_grid)

    def test_full_plate(self):
        full_plate_data = pd.DataFrame({
            'Well': ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3'],
            'Value': [1] * 9
        })
        grid = set_grid_for_display(full_plate_data, '3x3')
        expected_grid = pd.DataFrame('X', columns=['1', '2', '3'], index=['A', 'B', 'C'])
        pd.testing.assert_frame_equal(grid, expected_grid)


class TestArgsParser(unittest.TestCase):
    def setUp(self):
        self.parser = build_args_parser(
            signature="",
            description=""
        )

    def test_valid_input(self):
        args = self.parser.parse_args(
            [
                'sampling.csv',
                '-of', 'outN',
                '-ofmt', 'csv',
                '-sdv', '1000',
                '-ssw', 'A2',
                '-spd', '3x3',
                '-spwc', '10000',
                '-ncc', 'Component_2',
                '-dsw', 'B12',
                '-dpd', '4x4',
                '-dpwc', '11000',
                '-v', '5555',
                '--nplicates', '3'
            ]
        )
        self.assertEqual(args.volumes_file, 'sampling.csv')
        self.assertEqual(args.output_folder, 'outN')
        self.assertEqual(args.output_format, 'csv')
        self.assertEqual(args.src_plt_dead_volume, 1000)
        self.assertEqual(args.src_start_well, 'A2')
        self.assertEqual(args.src_plt_dim, '3x3')
        self.assertEqual(args.src_plt_well_capacity, 10000)
        self.assertEqual(args.new_col_comp, ['Component_2'])
        self.assertEqual(args.dst_start_well, 'B12')
        self.assertEqual(args.dst_plt_dim, '4x4')
        self.assertEqual(args.dst_plt_well_capacity, 11000)
        self.assertEqual(args.sample_volume, 5555)
        self.assertEqual(args.nplicates, 3)

    def test_missing_input(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['-of', 'outN', '-ofmt', 'csv', '-sdv', '1000', '-ssw', "'A2'", '-spd', "'3x3'", '-spwc', '10000', '--nplicates', '3', '-ncc', 'Component_2', '-dsw', "'B12'", '-dpd', "'4x4'", '-dpwc', '11000', '-v', '5555', '--nplicates', '3'])
