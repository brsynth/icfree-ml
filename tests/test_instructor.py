import unittest
import pandas as pd
import numpy as np
from os import path as os_path
from icfree.instructor import parse_plate_types, generate_echo_instructions, reorder_by_dispense_order


class TestInstructorModule(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.data_path = os_path.join(
            # parent folder of the current file
            os_path.dirname(__file__),
            'data' , 'instructor'
        )
        cls.input_folder = os_path.join(
            cls.data_path, 'input'
        )
        cls.reference_output_folder = os_path.join(
            cls.data_path, 'output'
        )
        # Load source and destination plate data from files
        cls.source_plate_file = os_path.join(
            cls.input_folder, 'source_plate.csv'
        )
        cls.destination_plate_file = os_path.join(
            cls.input_folder, 'destination_plate.csv'
        )
        cls.source_plate_df = pd.read_csv(cls.source_plate_file)
        cls.destination_plate_df = pd.read_csv(cls.destination_plate_file)
        # Load expected output data
        cls.expected_output_file = os_path.join(
            cls.reference_output_folder, 'instructions.csv'
        )
        cls.expected_output_file_df = pd.read_csv(cls.expected_output_file)

    def test_parse_plate_types_normal(self):
        self.assertEqual(
            parse_plate_types("component1:type1,component2:type2"),
            {"component1": "type1", "component2": "type2", "default": "384PP_AQ_GP3"}
        )
        self.assertEqual(
            parse_plate_types("component1:type1"),
            {"component1": "type1", "default": "384PP_AQ_GP3"}
        )

    def test_parse_plate_types_edge(self):
        self.assertEqual(
            parse_plate_types(""),
            {"default": "384PP_AQ_GP3"}
        )
        self.assertEqual(
            parse_plate_types(None),
            {"default": "384PP_AQ_GP3"}
        )

    def test_parse_plate_types_invalid(self):
        with self.assertRaises(ValueError):
            parse_plate_types("component1")
        
        self.assertEqual(
            parse_plate_types("component1:"),
            {"component1": "", "default": "384PP_AQ_GP3"}
        )

    def test_generate_echo_instructions_normal(self):
        source_plate_types = {'default': '384PP_AQ_GP3'}
        result = generate_echo_instructions(self.source_plate_df, self.destination_plate_df, source_plate_types)
        # Flatten the DataFrame for easier comparison
        result = result.reset_index(drop=True)
        self.assertIsInstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result, self.expected_output_file_df)

    def test_reorder_by_dispense_order(self):
        source_plate_types = {'default': '384PP_AQ_GP3'}
        result = generate_echo_instructions(self.source_plate_df, self.destination_plate_df, source_plate_types)
        # Flatten the DataFrame for easier comparison
        result = result.reset_index(drop=True)
        dispense_order = ['Water', 'Hela lysate']
        result = reorder_by_dispense_order(result, dispense_order)
        # Reset the index for easier comparison
        result = result.reset_index(drop=True)
        self.assertIsInstance(result, pd.DataFrame)
        # Load expected output data
        expected_output_file = os_path.join(
            self.reference_output_folder, 'instructions_reordered.csv'
        )
        expected_output_file_df = pd.read_csv(expected_output_file)
        pd.testing.assert_frame_equal(result, expected_output_file_df)

    # def test_generate_echo_instructions_edge(self):
    #     empty_source_df = pd.DataFrame(columns=['Well', 'Component1', 'Component2'])
    #     empty_destination_df = pd.DataFrame(columns=['Source Plate Name', 'Source Plate Type', 'Source Well', 'Destination Plate Name', 'Destination Well', 'Transfer Volume', 'Sample ID'])
    #     source_plate_types = {'default': '384PP_AQ_GP3'}
        
    #     with self.assertRaises(KeyError):
    #         generate_echo_instructions(empty_source_df, empty_destination_df, source_plate_types)

    # def test_generate_echo_instructions_invalid(self):
    #     with self.assertRaises(AttributeError):
    #         generate_echo_instructions(None, None, None)
    #     with self.assertRaises(AttributeError):
    #         generate_echo_instructions("invalid", "invalid", "invalid")

if __name__ == '__main__':
    unittest.main()
