import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from scipy.stats import qmc
from itertools import product
from tempfile import NamedTemporaryFile
from os import (
    path as os_path,
    name as os_name
)
from subprocess import run as sp_run

from icfree.sampler.sampler import (
    extract_specs,
    generate_ranges_by_ratios,
    generate_ranges_by_step,
    generate_ranges_by_nbins,
    generate_discrete_ranges,
    get_discrete_ranges,
    gen_samples,
    replace_duplicates,
    generate_all_combinations,
    random_sampling,
    sampling,
    load_parameters_file
)
from icfree.sampler.args import build_args_parser
from icfree.sampler.__main__ import main

from tests.functions import tmp_filepath, clean_file


DATA_FOLDER = os_path.join(
    os_path.dirname(os_path.realpath(__file__)),
    'data', 'sampler'
)

INPUT_FOLDER = os_path.join(
    DATA_FOLDER,
    'input'
)

REF_FOLDER = os_path.join(
    DATA_FOLDER,
    'output'
)

input_file = os_path.join(
    INPUT_FOLDER,
    'parameters.tsv'
)

ref_output_file = os_path.join(
    REF_FOLDER,
    'sampling.csv'
)


class TestExtractSpecs(unittest.TestCase):
    def test_valid_input(self):
        """Test with a valid specification string."""
        spec = "0.5,1.0|10|20"
        expected = ([0.5, 1.0], 10, 20)
        self.assertEqual(extract_specs(spec), expected)

    def test_missing_ratios(self):
        """Test with missing ratios."""
        spec = "|10|20"
        expected = (None, 10, 20)
        self.assertEqual(extract_specs(spec), expected)

    def test_missing_step(self):
        """Test with missing step."""
        spec = "0.5,1.0||20"
        expected = ([0.5, 1.0], None, 20)
        self.assertEqual(extract_specs(spec), expected)

    def test_missing_nb_bins(self):
        """Test with missing nb_bins."""
        spec = "0.5,1.0|10|"
        expected = ([0.5, 1.0], 10, None)
        self.assertEqual(extract_specs(spec), expected)

    def test_invalid_ratios(self):
        """Test with invalid ratios (non-float values)."""
        spec = "a,b|10|20"
        with self.assertRaises(ValueError):
            extract_specs(spec)

    def test_invalid_step(self):
        """Test with an invalid step (non-integer value)."""
        spec = "0.5,1.0|a|20"
        with self.assertRaises(ValueError):
            extract_specs(spec)

    def test_invalid_nb_bins(self):
        """Test with an invalid nb_bins (non-integer value)."""
        spec = "0.5,1.0|10|a"
        with self.assertRaises(ValueError):
            extract_specs(spec)

    def test_completely_empty_spec(self):
        """Test with an empty specification string."""
        spec = ""
        expected = (None, None, None)
        self.assertEqual(extract_specs(spec), expected)

    def test_only_delimiters_spec(self):
        """Test with a specification string that only contains delimiters ('|')."""
        spec = "||"
        expected = (None, None, None)
        self.assertEqual(extract_specs(spec), expected)

    def test_extra_delimiters(self):
        """Test with extra delimiters in the specification string."""
        spec = "0.5,1.0|||20"
        with self.assertRaises(ValueError):
            extract_specs(spec)


class TestGenerateRangesByRatios(unittest.TestCase):
    def test_valid_input(self):
        """Test with a set of valid ratios leading to max_value."""
        max_value = 100
        ratios = [0.1, 0.3, 0.5, 1]
        expected = [10, 30, 50, 100]
        self.assertEqual(generate_ranges_by_ratios(max_value, ratios), expected)

    def test_empty_ratios_list(self):
        """Test with an empty ratios list."""
        max_value = 100
        ratios = []
        expected = []  # Assuming the function returns an empty list when no ratios are provided.
        self.assertEqual(generate_ranges_by_ratios(max_value, ratios), expected)

    def test_single_ratio(self):
        """Test with a single ratio of 1."""
        max_value = 100
        ratios = [1]
        expected = [100]
        self.assertEqual(generate_ranges_by_ratios(max_value, ratios), expected)

    def test_max_value_zero(self):
        """Test with `max_value` set to 0."""
        max_value = 0
        ratios = [0.1, 0.5, 1]
        expected = [0, 0, 0]  # Assuming the function scales correctly to max_value.
        self.assertEqual(generate_ranges_by_ratios(max_value, ratios), expected)

    def test_negative_ratios(self):
        """Test with negative ratios."""
        max_value = 100
        ratios = [-0.1, 0.3, 0.5, 1]
        expected = [-10, 30, 50, 100]
        self.assertEqual(generate_ranges_by_ratios(max_value, ratios), expected)

    def test_invalid_ratios_type(self):
        """Test with invalid types in the ratios list."""
        max_value = 100
        ratios = ["0.1", "0.3", "0.5", "1"]  # Strings instead of floats
        with self.assertRaises(TypeError):
            generate_ranges_by_ratios(max_value, ratios)

    def test_ratios_with_zero(self):
        """Test with valid ratios including a zero at the start."""
        max_value = 100
        ratios = [0, 0.5, 0.75, 1]
        expected = [0, 50, 75, 100]
        self.assertEqual(generate_ranges_by_ratios(max_value, ratios), expected)

    def test_large_numbers(self):
        """Test with a very large `max_value` and ratios."""
        max_value = 1000000000
        ratios = [0.1, 0.3, 0.5, 1]
        expected = [100000000, 300000000, 500000000, 1000000000]
        self.assertEqual(generate_ranges_by_ratios(max_value, ratios), expected)


class TestGenerateRangesByStep(unittest.TestCase):
    def test_valid_input(self):
        """Test with valid max_value and step."""
        max_value = 10
        step = 2
        expected = [0, 2, 4, 6, 8, 10]
        self.assertEqual(generate_ranges_by_step(max_value, step), expected)

    def test_step_zero(self):
        """Test with step set to 0."""
        max_value = 10
        step = 0
        with self.assertRaises(ValueError):  # Assuming step 0 raises a ValueError
            generate_ranges_by_step(max_value, step)

    def test_negative_step(self):
        """Test with a negative step."""
        max_value = 10
        step = -2
        with self.assertRaises(ValueError):  # Assuming negative step raises a ValueError
            generate_ranges_by_step(max_value, step)

    def test_step_larger_than_max_value(self):
        """Test with a step value larger than max_value."""
        max_value = 5
        step = 10
        expected = [0]  # Assuming the function starts with 0 and cannot step to max_value
        self.assertEqual(generate_ranges_by_step(max_value, step), expected)

    def test_max_value_zero(self):
        """Test with max_value set to 0."""
        max_value = 0
        step = 2
        expected = [0]  # Only 0 is expected in the list
        self.assertEqual(generate_ranges_by_step(max_value, step), expected)

    def test_negative_max_value(self):
        """Test with a negative max_value."""
        max_value = -10
        step = 2
        self.assertEqual(generate_ranges_by_step(max_value, step), [])

    def test_non_integer_max_value_or_step(self):
        """Test with non-integer max_value or step."""
        max_value = 10.5  # Float instead of int
        step = 2
        with self.assertRaises(TypeError):
            generate_ranges_by_step(max_value, step)

        max_value = 10
        step = 2.5  # Float instead of int
        with self.assertRaises(TypeError):
            generate_ranges_by_step(max_value, step)


class TestGenerateRangesByNBins(unittest.TestCase):
    def test_valid_input(self):
        """Test with valid max_value and nb_bins."""
        max_value = 100.0
        nb_bins = 4
        expected = [0, 25, 50, 75, 100]  # Assuming equal division and rounding
        self.assertEqual(generate_ranges_by_nbins(max_value, nb_bins), expected)

    def test_zero_nb_bins(self):
        """Test with nb_bins set to 0."""
        max_value = 100.0
        nb_bins = 0
        with self.assertRaises(ZeroDivisionError):  # Assuming division by zero error
            generate_ranges_by_nbins(max_value, nb_bins)

    def test_negative_nb_bins(self):
        """Test with a negative nb_bins."""
        max_value = 100.0
        nb_bins = -1
        with self.assertRaises(ValueError):  # Assuming negative nb_bins raises a ValueError
            generate_ranges_by_nbins(max_value, nb_bins)

    def test_one_nb_bin(self):
        """Test with nb_bins set to 1."""
        max_value = 100.0
        nb_bins = 1
        expected = [0, 100]  # Start and end of the range
        self.assertEqual(generate_ranges_by_nbins(max_value, nb_bins), expected)

    def test_floating_point_max_value(self):
        """Test with a floating-point max_value."""
        max_value = 100.5
        nb_bins = 2
        expected = [0, 50, 100]  # Assuming not generating values beyond max_value (e.g. 101 if rounding up)
        self.assertEqual(generate_ranges_by_nbins(max_value, nb_bins), expected)

    def test_negative_max_value(self):
        """Test with a negative max_value."""
        max_value = -100.0
        nb_bins = 4
        expected = [0, -25, -50, -75, -100]  # Assuming equal division into negative ranges
        self.assertEqual(generate_ranges_by_nbins(max_value, nb_bins), expected)

    def test_non_integer_nb_bins(self):
        """Test with non-integer nb_bins."""
        max_value = 100.0
        nb_bins = 2.5  # Float instead of int
        with self.assertRaises(TypeError):
            generate_ranges_by_nbins(max_value, nb_bins)

    def test_large_max_value_and_nb_bins(self):
        """Test with very large max_value and nb_bins."""
        max_value = 1000000.0
        nb_bins = 1000
        expected_last_value = 1000000  # Ensuring the last value is correct
        result = generate_ranges_by_nbins(max_value, nb_bins)
        self.assertEqual(result[-1], expected_last_value)


class TestGenerateDiscreteRanges(unittest.TestCase):

    def setUp(self):
        # Sample DataFrame setup for testing
        self.data = pd.DataFrame({
            'Component': ['Comp1', 'Comp2', 'Comp3'],
            'Ratios|Step|NbBins': ['0.1,0.9| | ', ' |10| ', ' | |3'],
            'maxValue': [100, 200, 300]
        })

    @patch('icfree.sampler.sampler.extract_specs', side_effect=[([0.1, 0.9], None, None), (None, 10, None), (None, None, 3)])
    @patch('icfree.sampler.sampler.generate_ranges_by_ratios', return_value=[10, 100])
    @patch('icfree.sampler.sampler.generate_ranges_by_step', return_value=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200])
    @patch('icfree.sampler.sampler.generate_ranges_by_nbins', return_value=[0, 150, 300])
    def test_valid_dataframe_input(self, mock_nbins, mock_step, mock_ratios, mock_extract):
        expected_ranges = [[10, 100], [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200], [0, 150, 300]]
        discrete_ranges = generate_discrete_ranges(self.data)
        self.assertEqual(discrete_ranges, expected_ranges)

    @patch('icfree.sampler.sampler.extract_specs', return_value=(None, None, None))
    def test_missing_specifications(self, mock_extract):
        discrete_ranges = generate_discrete_ranges(self.data)
        for ranges in discrete_ranges:
            self.assertEqual(ranges, [])

    def test_empty_dataframe(self):
        empty_data = pd.DataFrame(columns=['Component', 'Ratios|Step|NbBins', 'maxValue'])
        discrete_ranges = generate_discrete_ranges(empty_data)
        self.assertEqual(discrete_ranges, [])

    @patch('icfree.sampler.sampler.extract_specs', side_effect=ValueError("Invalid format"))
    def test_invalid_specifications_format(self, mock_extract):
        with self.assertRaises(ValueError):
            generate_discrete_ranges(self.data)

    # Add test with Ratios + another value in "Ratios|Step|NbBins" column
    def test_ratios_and_another_in_specifications(self):
        data = pd.DataFrame({
            'Component': ['Comp1', 'Comp2', 'Comp3'],
            'Ratios|Step|NbBins': ['0.1,0.9| | ', '0.2,0.8|10| ', '0.3,0.7| |3'],
            'maxValue': [100, 200, 300]
        })
        with patch('icfree.sampler.sampler.extract_specs', side_effect=[([0.1, 0.9], None, None), ([0.2, 0.8], 10, None), ([0.3, 0.7], None, 3)]):
            with patch('icfree.sampler.sampler.generate_ranges_by_ratios', side_effect=[[10, 100], [20, 180], [30, 270]]):
                with patch('icfree.sampler.sampler.generate_ranges_by_nbins', side_effect=[[0, 50, 100], [0, 100, 200], [0, 100, 200, 300]]):
                    expected_ranges = [[10, 100], [20, 180], [30, 270]]
                    discrete_ranges = generate_discrete_ranges(data)
                    self.assertEqual(discrete_ranges, expected_ranges)

    # Add test with Step + NbBins (without Ratios) in "Ratios|Step|NbBins" column
    def test_step_and_nbins_in_specifications(self):
        data = pd.DataFrame({
            'Component': ['Comp1', 'Comp2', 'Comp3'],
            'Ratios|Step|NbBins': [' |10| ', ' | |3', '|10|3'],
            'maxValue': [100, 300, 20]
        })
        with patch('icfree.sampler.sampler.extract_specs', side_effect=[(None, 10, None), (None, None, 3), (None, 10, 3)]):
            with patch('icfree.sampler.sampler.generate_ranges_by_step', side_effect=[[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100], [0, 10, 20]]):
                with patch('icfree.sampler.sampler.generate_ranges_by_nbins', side_effect=[[0, 100, 200, 300]]):
                    expected_ranges = [[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100], [0, 100, 200, 300], [0, 10, 20]]
                    discrete_ranges = generate_discrete_ranges(data)
                    self.assertEqual(discrete_ranges, expected_ranges)


class TestGetDiscreteRanges(unittest.TestCase):

    def setUp(self):
        self.data = pd.DataFrame({
            'Component': ['Comp1', 'Comp2'],
            'maxValue': [100, 200]
        })
        self.ratios = [0, 0.1, 0.25, 0.5, 1]
        self.step = 10
        self.nb_bins = 2  # Assuming this means dividing maxValue into 2 bins

    def test_ratios_provided(self):
        expected = [[0, 10, 25, 50, 100], [0, 20, 50, 100, 200]]
        actual = get_discrete_ranges(self.data, self.ratios, None, None)
        self.assertEqual(actual, expected)

    def test_step_provided(self):
        expected = [list(range(0, 101, 10)), list(range(0, 201, 10))]
        actual = get_discrete_ranges(self.data, None, self.step, None)
        self.assertEqual(actual, expected)

    def test_nb_bins_provided(self):
        # Assuming corrected implementation for nb_bins
        # For nb_bins=2, the step for Comp1 should be 50 (100/2) and for Comp2 should be 100 (200/2)
        expected = [list(range(0, 101, 50)), list(range(0, 201, 100))]
        actual = get_discrete_ranges(self.data, None, None, self.nb_bins)
        self.assertEqual(actual, expected)

    def test_none_provided(self):
        with patch('icfree.sampler.sampler.generate_discrete_ranges') as mock_generate:
            mock_generate.return_value = "fallback method used"
            actual = get_discrete_ranges(self.data, None, None, None)
            self.assertEqual(actual, "fallback method used")

    def test_negative_ratios(self):
        expected = [[-10, 200], [-20, 400]]
        actual = get_discrete_ranges(self.data, [-0.1, 2], None, None)
        self.assertEqual(actual, expected)

    def test_zero_step(self):
        with self.assertRaises(ValueError):
            get_discrete_ranges(self.data, None, 0, None)

    def test_negative_nb_bins(self):
        with self.assertRaises(ValueError):
            get_discrete_ranges(self.data, None, None, -1)

    def test_empty_dataframe(self):
        empty_data = pd.DataFrame({'Component': [], 'maxValue': []})
        expected = []
        actual = get_discrete_ranges(empty_data, self.ratios, None, None, MagicMock())
        self.assertEqual(actual, expected)


class TestGenSamples(unittest.TestCase):
    def setUp(self):
        self.discrete_ranges = [[0, 1, 2], [10, 20, 30], [100, 200]]
        self.n_samples = 5
        self.sampler = qmc.LatinHypercube(d=len(self.discrete_ranges))

    def test_valid_input(self):
        samples = gen_samples(self.discrete_ranges, self.sampler, self.n_samples)
        self.assertEqual(samples.shape, (self.n_samples, len(self.discrete_ranges)))

    def test_empty_discrete_ranges(self):
        samples = gen_samples([], self.sampler, self.n_samples)
        self.assertEqual(samples.size, 0)

    def test_single_element_discrete_range(self):
        single_element_range = [[0], [1], [2]]
        samples = gen_samples(single_element_range, self.sampler, self.n_samples)
        for col in range(samples.shape[1]):
            self.assertTrue(np.all(samples[:, col] == col))

    def test_non_uniform_discrete_ranges(self):
        non_uniform_ranges = [[0, 1], [10], [100, 200, 300]]
        samples = gen_samples(non_uniform_ranges, self.sampler, self.n_samples)
        self.assertEqual(samples.shape, (self.n_samples, len(non_uniform_ranges)))

    def test_zero_samples(self):
        samples = gen_samples(self.discrete_ranges, self.sampler, 0)
        self.assertEqual(samples.shape, (0, len(self.discrete_ranges)))

    def test_invalid_n_samples(self):
        with self.assertRaises(ValueError):
            gen_samples(self.discrete_ranges, self.sampler, -1)


class TestReplaceDuplicates(unittest.TestCase):
    def setUp(self):
        self.discrete_ranges = [[0, 1, 2], [10, 20, 30]]
        self.sampler = qmc.LatinHypercube(d=len(self.discrete_ranges), seed=42)  # Assuming a sampler setup

    def test_functionality(self):
        samples_df = pd.DataFrame({
            'A': [1, 1, 2],
            'B': [10, 10, 20]
        })
        with patch('icfree.sampler.sampler.gen_samples', return_value=np.array([[2, 30]])):
            result_df = replace_duplicates(samples_df, self.discrete_ranges, self.sampler)
            self.assertEqual(len(result_df), 3)
            self.assertFalse(result_df.duplicated().any())

    # Test removing duplicates
    def test_duplicates(self):
        samples_df = pd.DataFrame({
            'A': [1, 1, 2],
            'B': [10, 10, 20]
        })
        # with patch('icfree.sampler.sampler.gen_samples', return_value=pd.DataFrame(np.array([[1, 10], [1, 20], [1, 10]]))):
        result_df = replace_duplicates(samples_df, self.discrete_ranges, self.sampler)
        self.assertFalse(result_df.duplicated().any())

    def test_no_duplicates(self):
        samples_df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [10, 20, 30]
        })
        result_df = replace_duplicates(samples_df, self.discrete_ranges, self.sampler)
        pd.testing.assert_frame_equal(samples_df, result_df)

    def test_all_rows_duplicates(self):
        samples_df = pd.DataFrame({
            'A': [1, 1],
            'B': [10, 10]
        })
        with patch('icfree.sampler.sampler.gen_samples', side_effect=[np.array([[2, 20]]), np.array([[3, 30]])]):
            result_df = replace_duplicates(samples_df, self.discrete_ranges, self.sampler)
            self.assertFalse(result_df.duplicated().any())

    def test_empty_dataframe(self):
        samples_df = pd.DataFrame(columns=['A', 'B'])
        result_df = replace_duplicates(samples_df, self.discrete_ranges, self.sampler)
        self.assertTrue(result_df.empty)

    def test_more_samples_than_possible(self):
        samples_df = pd.DataFrame({
            'A': np.random.choice([1, 2, 3], 10),
            'B': np.random.choice([10, 20, 30], 10)
        })
        with patch('icfree.sampler.sampler.gen_samples') as mock_gen_samples:
            mock_gen_samples.return_value = np.random.randint(1, 4, size=(1, 2))
            self.assertRaises(ValueError, replace_duplicates, samples_df, self.discrete_ranges, self.sampler)

    def test_equal_samples_than_possible(self):
        samples_df = pd.DataFrame({
            'A': np.random.choice([1, 2, 3], 9),
            'B': np.random.choice([10, 20, 30], 9)
        })
        with patch('icfree.sampler.sampler.gen_samples') as mock_gen_samples:
            mock_gen_samples.return_value = np.random.randint(1, 4, size=(1, 2))
            self.assertEqual(
                generate_all_combinations(self.discrete_ranges).tolist(),
                replace_duplicates(samples_df, self.discrete_ranges, self.sampler).tolist()
            )

    def test_column_types(self):
        samples_df = pd.DataFrame({
            'A': pd.Series([1, 1, 2], dtype="category"),
            'B': [10.0, 10.0, 20.0]  # Float column
        })
        with patch('icfree.sampler.sampler.gen_samples', return_value=np.array([[2, 30.0]])):
            result_df = replace_duplicates(samples_df, self.discrete_ranges, self.sampler)
            self.assertFalse(result_df.duplicated().any())
            self.assertEqual(result_df['A'].dtype, "category")
            self.assertEqual(result_df['B'].dtype, float)


class TestRandomSampling(unittest.TestCase):
    def setUp(self):
        self.discrete_ranges = [[0, 1, 2], [10, 20, 30]]
        self.n_samples = 5
        self.seed = 42

    def test_valid_input(self):
        np.random.seed(self.seed)  # Ensuring reproducibility for comparison
        expected_samples = np.array([
            [np.random.choice(range_) for range_ in self.discrete_ranges]
            for _ in range(self.n_samples)
        ])
        actual_samples = random_sampling(self.discrete_ranges, self.n_samples, self.seed)
        np.testing.assert_array_equal(actual_samples, expected_samples)

    def test_empty_discrete_ranges(self):
        samples = random_sampling([], self.n_samples, self.seed)
        self.assertEqual(samples.size, 0)
        self.assertEqual(samples.shape, (self.n_samples, 0))

    def test_single_element_discrete_range(self):
        single_element_range = [[0], [1]]
        samples = random_sampling(single_element_range, self.n_samples, self.seed)
        expected_samples = np.array([[0, 1]] * self.n_samples)
        np.testing.assert_array_equal(samples, expected_samples)

    def test_seed_reproducibility(self):
        samples_first = random_sampling(self.discrete_ranges, self.n_samples, self.seed)
        samples_second = random_sampling(self.discrete_ranges, self.n_samples, self.seed)
        np.testing.assert_array_equal(samples_first, samples_second)

    def test_zero_samples(self):
        samples = random_sampling(self.discrete_ranges, 0, self.seed)
        print(samples)
        self.assertEqual(samples.shape, (0,))

    def test_negative_samples(self):
        with self.assertRaises(ValueError):
            random_sampling(self.discrete_ranges, -1, self.seed)

    def test_data_type_and_shape(self):
        samples = random_sampling(self.discrete_ranges, self.n_samples, self.seed)
        self.assertTrue(isinstance(samples, np.ndarray))
        self.assertEqual(samples.shape, (self.n_samples, len(self.discrete_ranges)))


class TestGenerateAllCombinations(unittest.TestCase):
    def setUp(self):
        self.discrete_ranges = [[1, 2], [3, 4]]

    def test_valid_input(self):
        expected_combinations = np.array(list(product(*self.discrete_ranges)))
        actual_combinations = generate_all_combinations(self.discrete_ranges)
        np.testing.assert_array_equal(actual_combinations, expected_combinations)

    def test_empty_discrete_ranges(self):
        actual_combinations = generate_all_combinations([])
        self.assertEqual(actual_combinations.size, 0)
        self.assertEqual(actual_combinations.shape, (1, 0))

    def test_single_element_discrete_range(self):
        single_element_range = [[1], [3, 4]]
        expected_combinations = np.array(list(product(*single_element_range)))
        actual_combinations = generate_all_combinations(single_element_range)
        np.testing.assert_array_equal(actual_combinations, expected_combinations)

    def test_mixed_length_discrete_ranges(self):
        mixed_ranges = [[1, 2], [3], [4, 5, 6]]
        expected_combinations = np.array(list(product(*mixed_ranges)))
        actual_combinations = generate_all_combinations(mixed_ranges)
        np.testing.assert_array_equal(actual_combinations, expected_combinations)

    def test_empty_element_in_discrete_ranges(self):
        ranges_with_empty = [[1, 2], [], [3, 4]]
        actual_combinations = generate_all_combinations(ranges_with_empty)
        self.assertEqual(actual_combinations.size, 0)
        self.assertEqual(actual_combinations.shape, (0,))

    def test_output_shape(self):
        ranges = [[1, 2, 3], [4, 5], [6, 7]]
        expected_num_combinations = np.prod([len(r) for r in ranges])
        actual_combinations = generate_all_combinations(ranges)
        self.assertEqual(actual_combinations.shape[0], expected_num_combinations)
        self.assertEqual(actual_combinations.shape[1], len(ranges))


class TestSampling(unittest.TestCase):
    def setUp(self):
        self.discrete_ranges = [[0, 1, 2], [10, 20, 30]]
        self.seed = 42

    @patch('icfree.sampler.sampler.gen_samples')
    def test_valid_lhs_sampling(self, mock_gen_samples):
        n_samples = 2  # Less than one third of total combinations (3*3=9)
        mock_gen_samples.return_value = np.random.rand(n_samples, len(self.discrete_ranges))
        result = sampling(self.discrete_ranges, n_samples, 'lhs', self.seed)
        self.assertIsInstance(result, pd.DataFrame)

    @patch('icfree.sampler.sampler.random_sampling')
    def test_valid_random_sampling(self, mock_random_sampling):
        n_samples = 5  # More than one third but less than total combinations
        mock_random_sampling.return_value = np.random.rand(n_samples, len(self.discrete_ranges))
        result = sampling(self.discrete_ranges, n_samples, 'random', self.seed)
        self.assertIsInstance(result, pd.DataFrame)

    @patch('icfree.sampler.sampler.generate_all_combinations')
    def test_valid_all_combinations(self, mock_all_combinations):
        n_samples = 9  # Equals total combinations
        mock_all_combinations.return_value = np.random.rand(n_samples, len(self.discrete_ranges))
        result = sampling(self.discrete_ranges, n_samples, 'all', self.seed)
        self.assertIsInstance(result, pd.DataFrame)

    def test_auto_method_selection(self):
        # Example test for auto method; adjust based on the specific logic and expected outcomes
        n_samples = 2
        result = sampling(self.discrete_ranges, n_samples, 'auto', self.seed)
        self.assertIsInstance(result, pd.DataFrame)

    def test_seed_reproducibility(self):
        # Example for LHS or random sampling; adjust mock as needed
        n_samples = 2
        with patch('icfree.sampler.sampler.gen_samples') as mock_gen_samples:
            mock_gen_samples.return_value = np.random.rand(n_samples, len(self.discrete_ranges))
            result1 = sampling(self.discrete_ranges, n_samples, 'lhs', self.seed)
            result2 = sampling(self.discrete_ranges, n_samples, 'lhs', self.seed)
            pd.testing.assert_frame_equal(result1, result2)

    def test_with_duplicates(self):
        discrete_ranges = [[0, 1, 2], [10, 20, 30], [100, 200], [1000, 2000]]
        result_df = sampling(discrete_ranges, 30, 'lhs', self.seed)
        self.assertFalse(result_df.duplicated().any())

    def test_invalid_number_of_samples(self):
        n_samples = 100  # Exceeds total combinations
        with self.assertRaises(ValueError):
            sampling(self.discrete_ranges, n_samples, 'auto', self.seed)

    def test_empty_discrete_ranges(self):
        pd.testing.assert_frame_equal(
            sampling([], 1, 'auto', self.seed),
            pd.DataFrame([])
        )

    def test_zero_samples_request(self):
        pd.testing.assert_frame_equal(
            sampling(self.discrete_ranges, 0, 'auto', self.seed),
            pd.DataFrame(columns=[0, 1], dtype='float64')
        )

    def test_negative_samples_request(self):
        with self.assertRaises(ValueError):
            sampling(self.discrete_ranges, -1, 'auto', self.seed)


class TestLoadParametersFile(unittest.TestCase):
    def setUp(self) -> None:
        self.parameters_df = pd.DataFrame({
            'Component': ['Component_1', 'Component_2', 'Component_3', 'Component_4', 'Component_5', 'Component_6'],
            'maxValue': [200, 125, 40, 100, 400, 100],
            'Ratios|Step|NbBins': ['0.0,0.1,0.3,0.5,1.0||', '1||', '1||', '|10|', '||10', '1'
            ]
        })

    def test_with_existing_file(self):
        data = load_parameters_file(input_file)
        pd.testing.assert_frame_equal(data, self.parameters_df)

    def test_invalid_file_path(self):
        with self.assertRaises(FileNotFoundError):
            load_parameters_file('nonexistent_file.csv')

    def test_empty_file(self):
        with NamedTemporaryFile(mode='r', suffix='.csv') as temp_file:
            with self.assertRaises(pd.errors.EmptyDataError):
                load_parameters_file(temp_file.name)

    def test_with_dead_volume(self):
        parameters_df = self.parameters_df.copy()
        # Add deadVolume column with no value
        parameters_df['deadVolume'] = ""
        tmp_fn = tmp_filepath(suffix='.tsv')
        parameters_df.to_csv(tmp_fn, index=False, sep='\t')
        data = load_parameters_file(tmp_fn)
        clean_file(tmp_fn)
        parameters_df['deadVolume'] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        pd.testing.assert_frame_equal(data, parameters_df)


class TestArgsParser(unittest.TestCase):

    def setUp(self):
        self.parser = build_args_parser(
            signature="",
            description=""
        )

    def test_valid_input(self):
        args = self.parser.parse_args(
            [
                'input.csv',
                '-o', 'output.csv',
                '--nb-samples', '10',
                '--method', 'lhs',
                '--step', '10',
                '--ratios', '0.1', '0.9',
                '--nb-bins', '5',
                '--seed', '42'
            ]
        )
        self.assertEqual(args.input_file, 'input.csv')
        self.assertEqual(args.output_file, 'output.csv')
        self.assertEqual(args.nb_samples, 10)
        self.assertEqual(args.method, 'lhs')
        self.assertEqual(args.seed, 42)
        self.assertEqual(args.step, 10)
        self.assertEqual(args.ratios, [0.1, 0.9])
        self.assertEqual(args.nb_bins, 5)

    def test_missing_input(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['-o', 'output.csv', '-n', '10', '-m', 'lhs', '-S', '42'])


# Test with CLI simulation and check output file
class TestCLI(unittest.TestCase):
    def setUp(self):
        self.parser = build_args_parser(
            signature="",
            description=""
        )

    def test_valid_input(self):
        # Do not use NamedTemporaryFile as opening a file
        # already opened is not supported on Windows
        tmp_fn = tmp_filepath()
        args = [
                input_file,
                '-o', tmp_fn,
                '--nb-samples', '40',
                '--method', 'lhs',
                '--seed', '42'
            ]
        main(args)
        actual = pd.read_csv(tmp_fn)
        clean_file(tmp_fn)
        expected = pd.read_csv(ref_output_file)
        pd.testing.assert_frame_equal(actual, expected)

    def test_missing_input(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['-o', 'output.csv', '-n', '10', '-m', 'lhs', '-S', '42'])

    def test_nonexistent_file(self):
        args = [
                'nonexistent_file.csv',
                '-o', 'output.csv',
                '--nb-samples', '40',
                '--method', 'lhs',
                '--seed', '42'
            ]
        with self.assertRaises(SystemExit):
            main(args)

    def test_system_exit(self):
        args = [
                input_file,
                '-o', 'output.csv',
                '--nb-samples', '40',
                '--method', 'lhs',
                '--seed', '42'
            ]
        with patch('icfree.sampler.__main__.load_parameters_file', side_effect=ValueError("Invalid method")):
            with self.assertRaises(SystemExit):
                main(args)
        with patch('icfree.sampler.__main__.sampling', side_effect=ValueError("Invalid method")):
            with self.assertRaises(SystemExit):
                main(args)

    def test_without_ouput_file(self):
        # Do not run on Windows
        if os_name == 'nt':
            return
        import sys
        with NamedTemporaryFile(mode='w', suffix='.csv') as temp_file:
            # simulate a redirection of the output to a file
            sys.stdout = open(temp_file.name, 'w')
            args = [
                    input_file,
                    '--nb-samples', '40',
                    '--method', 'lhs',
                    '--seed', '42',
                    '--silent'
                ]
            main(args)
            sys.stdout = sys.__stdout__
            actual = pd.read_csv(temp_file.name)
            expected = pd.read_csv(ref_output_file)
            pd.testing.assert_frame_equal(actual, expected)

    def test_subprocess_call(self):
        tmp_fn = tmp_filepath()
        cmd = 'python -m icfree.sampler {} -o {} --nb-samples 40 --method lhs --seed 42 --silent'.format(input_file, tmp_fn)
        sp_run(cmd.split())
        actual = pd.read_csv(tmp_fn)
        clean_file(tmp_fn)
        expected = pd.read_csv(ref_output_file)
        pd.testing.assert_frame_equal(actual, expected)
