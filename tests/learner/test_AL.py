import unittest
from unittest.mock import patch
from hashlib import sha256
import sys
from os import (
    path as os_path,
    listdir as os_listdir
)
from tempfile import TemporaryDirectory

# Import your main function from main.py
from icfree.learner.__main__ import main



def file_fingerprint(file_path):
    """
    Calculate the fingerprint (SHA-256 hash) of a file.
    """
    hasher = sha256()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
    except FileNotFoundError:
        return None
    return hasher.hexdigest()

def compare_folders(folder1, folder2):
    """
    Compare two folders to check if their files are identical based on filename and fingerprint.

    Args:
        folder1 (str): Path to the first folder.
        folder2 (str): Path to the second folder.

    Returns:
        dict: A dictionary with file comparison results.
              Keys are filenames, and values are tuples (status, fingerprint1, fingerprint2):
                  - "Identical": Files are identical.
                  - "Mismatch": Files have the same name but different fingerprints.
                  - "Missing": File is missing in one of the folders.
    """
    folder1_files = {file: os_path.join(folder1, file) for file in os_listdir(folder1)}
    folder2_files = {file: os_path.join(folder2, file) for file in os_listdir(folder2)}

    all_files = set(folder1_files.keys()).union(set(folder2_files.keys()))
    comparison_results = {}

    for file in all_files:
        file1_path = folder1_files.get(file)
        file2_path = folder2_files.get(file)

        if file1_path and file2_path:
            # Both folders have the file, compare fingerprints
            fingerprint1 = file_fingerprint(file1_path)
            fingerprint2 = file_fingerprint(file2_path)
            if fingerprint1 == fingerprint2:
                comparison_results[file] = ("Identical", fingerprint1, fingerprint2)
            else:
                comparison_results[file] = ("Mismatch", fingerprint1, fingerprint2)
        elif file1_path:
            # File exists only in folder1
            comparison_results[file] = ("Missing in folder2", file_fingerprint(file1_path), None)
        else:
            # File exists only in folder2
            comparison_results[file] = ("Missing in folder1", None, file_fingerprint(file2_path))

    return comparison_results

# Example usage
# results = compare_folders("/path/to/folder1", "/path/to/folder2")
# for file, details in results.items():
#     print(f"{file}: {details}")

class TestCLI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data_path = os_path.join(
            # parent folder of the current file
            os_path.dirname(
                os_path.dirname(__file__)
            ),
            'data' , 'learner'
        )
        cls.input_folder = os_path.join(
            cls.data_path, 'input'
        )
        cls.reference_output_folder = os_path.join(
            cls.data_path, 'output'
        )

        cls.seed = 85
        cls.parameter_file = os_path.join(
            cls.input_folder, 'param.tsv'
        )

    def test_basic(self):
        # Define what sys.argv should look like
        with TemporaryDirectory() as temp_dir:
            test_args = [
                "python -m icfree.learner",
                "--data_folder", os_path.join(TestCLI.input_folder, "top50"),
                "--parameter_file", TestCLI.parameter_file,
                "--output_folder", temp_dir,
                "--save_plot",
                "--seed", f"{TestCLI.seed}"
            ]
            with patch.object(sys, 'argv', test_args):
                main()

            results = compare_folders(temp_dir, TestCLI.reference_output_folder)
            for file, details in results.items():
                # Check if all files are identical
                self.assertTrue(details[0] == "Identical", f"{file}: {details}")
                
                
 
        

    # @patch('sys.stdout', new_callable=io.StringIO)
    # def test_main_no_arguments(self, mock_stdout):
    #     """
    #     Test the main() function with no additional arguments,
    #     e.g., `python main.py`
    #     """
    #     test_args = ["python -m icfree.learner"]
    #     with patch.object(sys, 'argv', test_args):
    #         main()

    #     output = mock_stdout.getvalue()

    #     # Check if your program's behavior with no arguments matches expectations
    #     # This will depend on how your main() handles empty arguments
    #     self.assertIn("CLI arguments received: []", output)


if __name__ == "__main__":
    unittest.main()
