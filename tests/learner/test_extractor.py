import unittest
import pandas as pd
from io import StringIO
from os import path as os_path
from icfree.learner.extractor import (
    find_n_m_from_sampling,
    infer_replicates,
    process_data,
    process,
)

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
            "plate1_sampling.csv"
        )
        cls.reference_output_file = os_path.join(
            cls.data_path, 'output',
            "plate1.csv"
        )
        cls.output_file = "output.csv"

        cls.num_samples = 57
        cls.num_replicates = 6

        cls.df_sampling = pd.read_csv(cls.sampling_file)
        cls.df_initial = pd.read_excel(cls.initial_data_file)
        cls.reference_output = pd.read_csv(cls.reference_output_file)

    def test_find_n_m_from_sampling(self):
        """Test detection of unique combinations and repetitions in sampling."""
        n, has_repetitions = find_n_m_from_sampling(self.df_sampling)
        self.assertEqual(n, self.num_samples)  # Unique combinations
        self.assertTrue(has_repetitions)  # Repetitions exist

    def test_infer_replicates(self):
        """Test inference of replicates from initial and sampling data."""
        num_replicates = infer_replicates(self.df_initial, self.df_sampling, self.num_samples)
        self.assertEqual(num_replicates, self.num_replicates)  # Expected replicates based on data structure

    def test_process_data(self):
        """Test reshaping of fluorescence data."""
        df_reshaped = process_data(self.df_initial, self.num_samples, self.num_replicates)
        self.assertEqual(df_reshaped.shape, (self.num_samples, self.num_replicates+1))  # Rows = num_samples, Columns = num_replicates + 1 (average column)
        self.assertAlmostEqual(df_reshaped["Fluorescence Average"].iloc[0], 1551)  # Verify first row's average

    def test_process(self):
        """Test end-to-end processing of data and file saving."""
        # Save the processed output to a temporary file
        output_file = "/tmp/test_output.csv"
        combined_df = process(
            initial_data_file=self.initial_data_file,
            output_file_path=output_file,
            sampling_file=self.sampling_file,
            num_samples=self.num_samples,
            num_replicates=self.num_replicates,
            display=False
        )
        self.assertIsInstance(combined_df, pd.DataFrame)
        self.assertEqual(combined_df.shape[0], self.num_samples)  # Number of samples
        self.assertTrue(combined_df.columns[-1] == "Fluorescence Average")  # Check last column name
        
    def test_process_with_inference(self):
        """Test end-to-end processing with automatic inference."""
        output_file = "/tmp/test_output_inferred.csv"
        combined_df = process(
            initial_data_file=self.initial_data_file,
            output_file_path=output_file,
            sampling_file=self.sampling_file,
            num_samples=None,  # Let the function infer num_samples
            num_replicates=None,  # Let the function infer num_replicates
            display=False
        )
        self.assertIsInstance(combined_df, pd.DataFrame)
        self.assertEqual(combined_df.shape[0], self.num_samples)  # Number of samples inferred
        self.assertEqual(combined_df.shape[1], 18)  # Sampling columns + reshaped fluorescence columns
        
if __name__ == "__main__":
    unittest.main(argv=[''], verbosity=2, exit=False)
