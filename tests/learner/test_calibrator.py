import unittest
import pandas as pd
import numpy as np
from icfree.learner.calibrator import calculate_yield, add_calibrated_yield, fit_regression_with_outlier_removal

class TestCalibrator(unittest.TestCase):
    def setUp(self):
        # Create sample data for testing
        self.data = pd.DataFrame({
            'Fluorescence_1': [100, 200, 300, 400],
            'Fluorescence_2': [150, 250, 350, 450]
        })
        self.jove_plus_line = 5
        self.jove_minus_line = 2
        self.a = 1.5
        self.b = 0.5
        self.y = np.array([1, 2, 3, 4, 5])
        self.y_ref = np.array([1.2, 1.9, 3.1, 4.0, 5.1])
        self.r2_limit = 0.95

    def test_calculate_yield(self):
        # Test the calculate_yield function
        result = calculate_yield(self.data, self.jove_plus_line, self.jove_minus_line)
        expected_columns = ['Fluorescence_1', 'Fluorescence_2', 'Yield_1', 'Yield_2']
        self.assertTrue(all([col in result.columns for col in expected_columns]))

        # Check if yields are calculated correctly
        # Autofluorescence is the mean of fluorescences for jove_minus_line
        autofluorescence = np.mean([self.data[fluo][self.jove_minus_line-2] for fluo in self.data if 'Fluorescence' in fluo])
        # Reference is the mean of fluorescences for jove_plus_line
        reference = np.mean([self.data[fluo][self.jove_plus_line-2] for fluo in self.data if 'Fluorescence' in fluo])
        expected_yield_1 = (self.data['Fluorescence_1'] - autofluorescence) / (reference - autofluorescence)
        pd.testing.assert_series_equal(result['Yield_1'], expected_yield_1, check_names=False)

    def test_add_calibrated_yield(self):
        # Test the add_calibrated_yield function
        yield_data = calculate_yield(self.data, self.jove_plus_line, self.jove_minus_line)
        result = add_calibrated_yield(yield_data, self.a, self.b)
        expected_columns = ['Calibrated Yield_1', 'Calibrated Yield_2']
        self.assertTrue(all([col in result.columns for col in expected_columns]))
        
        # Check if calibrated yields are calculated correctly
        expected_calibrated_yield_1 = self.a * result['Yield_1'] + self.b
        pd.testing.assert_series_equal(result['Calibrated Yield_1'], expected_calibrated_yield_1, check_names=False)

    def test_fit_regression_with_outlier_removal(self):
        # Test the fit_regression_with_outlier_removal function
        a, b, r2_value, outliers = fit_regression_with_outlier_removal(self.y, self.y_ref, self.r2_limit)
        
        # Check if the regression coefficients and R2 value are within expected limits
        self.assertIsInstance(a, float)
        self.assertIsInstance(b, float)
        self.assertGreaterEqual(r2_value, self.r2_limit)
        self.assertIsInstance(outliers, list)
        self.assertTrue(all(isinstance(i, np.int64) for i in outliers))

if __name__ == '__main__':
    unittest.main()
