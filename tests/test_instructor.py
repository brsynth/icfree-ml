import unittest
import pandas as pd
import numpy as np
from icfree.instructor import parse_plate_types, generate_echo_instructions, reorder_instructions


class TestInstructorModule(unittest.TestCase):

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
        source_plate_df = pd.DataFrame({
            'Well': ['A1', 'B1', 'C1'],
            'Component1': [1000, 0, 0],
            'Component2': [0, 1500, 0]
        })
        destination_plate_df = pd.DataFrame({
            'Well': ['A1', 'B1', 'C1'],
            'Component1': [10, 20, 30],
            'Component2': [5, 15, 25]
        })
        source_plate_types = {'default': '384PP_AQ_GP3'}
        
        result = generate_echo_instructions(source_plate_df, destination_plate_df, source_plate_types)
        self.assertIsInstance(result, pd.DataFrame)

        expected_result = pd.DataFrame({
            'Source Plate Name': ['Source[1]', 'Source[1]', 'Source[1]', 'Source[1]', 'Source[1]', 'Source[1]'],
            'Source Plate Type': ['384PP_AQ_GP3'] * 6,
            'Source Well': ['A1', 'A1', 'B1', 'B1', 'C1', 'C1'],
            'Destination Plate Name': ['Destination[1]'] * 6,
            'Destination Well': ['A1', 'A1', 'B1', 'B1', 'C1', 'C1'],
            'Transfer Volume': [10, 5, 20, 15, 30, 25],
            'Sample ID': ['Component1', 'Component1', 'Component1', 'Component2', 'Component2', 'Component2']
        })
        np.array_equal(result.values, expected_result.values)

    def test_reorder_instructions(self):
        source_plate_df = pd.DataFrame({
            'Well': ['A1', 'B1', 'C1'],
            'Component1': [1000, 0, 0],
            'Component2': [0, 1500, 0]
        })
        destination_plate_df = pd.DataFrame({
            'Well': ['A1', 'B1', 'C1'],
            'Component1': [10, 20, 30],
            'Component2': [5, 15, 25]
        })
        source_plate_types = {'default': '384PP_AQ_GP3'}
        dispensing_order = 'Component2'
        
        result = generate_echo_instructions(source_plate_df, destination_plate_df, source_plate_types)
        dispensing_order_list = dispensing_order.split(',')
        result = reorder_instructions(result, dispensing_order_list)
        self.assertIsInstance(result, pd.DataFrame)

        expected_result = pd.DataFrame({
            'Source Plate Name': ['Source[1]', 'Source[1]', 'Source[1]', 'Source[1]', 'Source[1]', 'Source[1]'],
            'Source Plate Type': ['384PP_AQ_GP3'] * 6,
            'Source Well': ['A1', 'A1', 'B1', 'B1', 'C1', 'C1'],
            'Destination Plate Name': ['Destination[1]'] * 6,
            'Destination Well': ['A1', 'A1', 'B1', 'B1', 'C1', 'C1'],
            'Transfer Volume': [10, 5, 20, 15, 30, 25],
            'Sample ID': ['Component2', 'Component2', 'Component2', 'Component1', 'Component1', 'Component1']
        })
        # Compare 'Sample ID' list order
        self.assertEqual(result['Sample ID'].tolist(), expected_result['Sample ID'].tolist())

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
