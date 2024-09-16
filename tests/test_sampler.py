import unittest
from unittest.mock import patch, mock_open
import pandas as pd
import numpy as np
import random
from io import StringIO
from icfree.sampler import generate_lhs_samples

class TestGenerateLHSSamples(unittest.TestCase):

    def setUp(self):
        self.csv_data = "Component,maxValue\nA,10\nB,20\nC,30\n"
        self.components_df = pd.read_csv(StringIO(self.csv_data))
        self.num_samples = 5
        self.step = 2.5
        self.seed = 42

    @patch("icfree.sampler.pd.read_csv")
    def test_generate_lhs_samples_normal(self, mock_read_csv):
        mock_read_csv.return_value = self.components_df
        
        result = generate_lhs_samples("fake_path.csv", self.num_samples, self.step, None, None, self.seed)
        
        self.assertEqual(result.shape, (self.num_samples, 3))
        self.assertListEqual(list(result.columns), ['A', 'B', 'C'])

    @patch("icfree.sampler.pd.read_csv")
    def test_generate_lhs_samples_no_seed(self, mock_read_csv):
        mock_read_csv.return_value = self.components_df
        
        result = generate_lhs_samples("fake_path.csv", self.num_samples, self.step, None, None, None)
        
        self.assertEqual(result.shape, (self.num_samples, 3))
        self.assertListEqual(list(result.columns), ['A', 'B', 'C'])

    @patch("icfree.sampler.pd.read_csv")
    def test_generate_lhs_samples_edge_case_zero_maxValue(self, mock_read_csv):
        edge_case_df = self.components_df.copy()
        edge_case_df.loc[0, 'maxValue'] = 0  # Set maxValue of component 'A' to 0
        mock_read_csv.return_value = edge_case_df
        
        result = generate_lhs_samples("fake_path.csv", self.num_samples, self.step, None, None, self.seed)
        
        self.assertEqual(result.shape, (self.num_samples, 3))
        self.assertTrue((result['A'] == 0).all())  # All values in column 'A' should be zero

    @patch("icfree.sampler.pd.read_csv")
    def test_generate_lhs_samples_invalid_step(self, mock_read_csv):
        mock_read_csv.return_value = self.components_df
        
        with self.assertRaises(IndexError):
            generate_lhs_samples("fake_path.csv", self.num_samples, -2.5, None, None, self.seed)  # Negative step size should raise an error

    @patch("icfree.sampler.pd.read_csv")
    def test_generate_lhs_samples_invalid_input_file(self, mock_read_csv):
        mock_read_csv.side_effect = FileNotFoundError
        
        with self.assertRaises(FileNotFoundError):
            generate_lhs_samples("invalid_path.csv", self.num_samples, self.step, None, None, self.seed)

    @patch("icfree.sampler.pd.read_csv")
    def test_generate_lhs_samples_fix_component_value(self, mock_read_csv):
        mock_read_csv.return_value = self.components_df
        
        result = generate_lhs_samples("fake_path.csv", self.num_samples, self.step, None, {'A': 5}, self.seed)
        
        self.assertEqual(result.shape, (self.num_samples, 3))
        self.assertTrue((result['A'] == 5).all())

if __name__ == "__main__":
    unittest.main()
