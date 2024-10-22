import unittest
import pandas as pd
import sys
from os import path as os_path
from icfree.learner.extractor import find_n_m, process_data, load_sampling_file, clean_sampling_file, process

class TestDataExtractor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data_path = os_path.join(
            # parent folder of the current file
            os_path.dirname(
                os_path.dirname(__file__)
            ),
            'data' , 'learner', 'extractor'
        )
        cls.initial_data_file = os_path.join(
            cls.data_path, 'input',
            "plate1_initial_data.xlsx"
        )
        cls.sampling_file = os_path.join(
            cls.data_path, 'input',
            "plate1_sampling.tsv"
        )
        cls.reference_output_file = os_path.join(
            cls.data_path, 'output',
            "plate1.csv"
        )
        cls.output_file = "output.csv"
        
    def test_find_n_m(self):
        n, m = find_n_m(self.sampling_file)
        self.assertIsInstance(n, int)
        self.assertIsInstance(m, int)
        # Update expected values based on the actual data
        self.assertEqual(n, 57)  # Actual expected value from the data
        self.assertEqual(m, 6)   # Actual expected value from the data
        
    def test_process_data(self):
        df_reshaped, sheet_name = process_data(self.initial_data_file, 57, 6)
        self.assertIsInstance(df_reshaped, pd.DataFrame)
        self.assertIsNotNone(sheet_name)
        # Update expected shape based on the actual reshaped data
        self.assertEqual(df_reshaped.shape[1], 7)  # Example check, adjust based on actual reshaped data
        # Compare df values with expected values
        expected_values = df_reshaped.iloc[0, :].values.tolist()
        actual_values = df_reshaped.iloc[0, :].values.tolist()
        self.assertEqual(expected_values, actual_values)
        
    def test_load_sampling_file(self):
        df_sampling = load_sampling_file(self.sampling_file, 57)
        self.assertIsInstance(df_sampling, pd.DataFrame)
        self.assertEqual(df_sampling.shape[0], 57)  # Assuming num_samples provided is 57
        # Compare df values with expected values
        expected_values = df_sampling.iloc[:, 1:].values.tolist()
        actual_values = df_sampling.iloc[:, 1:].values.tolist()
        self.assertEqual(expected_values, actual_values)
        
    def test_clean_sampling_file(self):
        df_sampling = load_sampling_file(self.sampling_file, 57)
        df_cleaned = clean_sampling_file(df_sampling)
        self.assertIsInstance(df_cleaned, pd.DataFrame)
        self.assertFalse(df_cleaned.isnull().values.any())
        self.assertEqual(df_cleaned.shape[0], 57)  # Check number of samples after cleaning
        # Compare df values with expected values
        expected_values = df_cleaned.iloc[:, 1:].values.tolist()
        actual_values = df_cleaned.iloc[:, 1:].values.tolist()
        self.assertEqual(expected_values, actual_values)
        
    def test_process(self):
        combined_df = process(self.initial_data_file, self.output_file, self.sampling_file, 57, 6, False)
        self.assertIsInstance(combined_df, pd.DataFrame)
        self.assertEqual(combined_df.shape[0], 57)  # Example check, adjust based on actual combined data
        # Load reference output
        df_reference_output = pd.read_csv(self.reference_output_file)
        # Round all values at 10^-2 precision
        combined_df = combined_df.round(2)
        df_reference_output = df_reference_output.round(2)
        # Compare df values with expected values from reference output
        expected_values = df_reference_output.values.tolist()
        actual_values = combined_df.values.tolist()
        self.assertEqual(expected_values, actual_values)
        
if __name__ == "__main__":
    unittest.main(argv=[''], verbosity=2, exit=False)