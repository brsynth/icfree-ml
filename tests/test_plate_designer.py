import unittest
import pandas as pd
import numpy as np
from pathlib import Path
from io import StringIO
import tempfile
from icfree.plate_designer import (
    parse_args,
    prepare_destination_plate,
    prepare_source_plate,
    write_output_files
)

class TestPlateDesigner(unittest.TestCase):

    def setUp(self):
        # Sample data for testing
        self.sampling_data = pd.DataFrame({
            'Component1': [100, 150, 200],
            'Component2': [200, 250, 300]
        })

        self.plate_dims = '8x12'
        self.sample_volume = 1000
        self.num_replicates = 2
        self.start_well_dst_plt = 'A1'
        self.dead_volumes_str = 'Component1=10,Component2=10'
        self.default_dead_volume = 10
        self.well_capacity = 'Component1=55000'
        self.default_well_capacity = 60000
        self.start_well_src_plt = 'A1'
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parse_args(self):
        # Implement test cases for parse_args() function
        import sys
        from unittest.mock import patch

        test_args = [
            'plate_designer.py',
            'sampling_data.csv',
            '1000',
            '--start_well_dst_plt', 'A1',
            '--plate_dims', '8x12',
            '--num_replicates', '2',
            '--dead_volumes', 'Component1=10,Component2=10',
            '--default_dead_volume', '10',
            '--well_capacity', 'Component1=55000',
            '--default_well_capacity', '60000',
            '--start_well_src_plt', 'A1',
            '--output_folder', self.temp_dir.name
        ]

        with patch.object(sys, 'argv', test_args):
            args = parse_args()
            self.assertEqual(args.sampling_file, 'sampling_data.csv')
            self.assertEqual(args.start_well_dst_plt, 'A1')
            self.assertEqual(args.plate_dims, '8x12')
            self.assertEqual(args.sample_volume, 1000)
            self.assertEqual(args.num_replicates, 2)
            self.assertEqual(args.dead_volumes, 'Component1=10,Component2=10')
            self.assertEqual(args.default_dead_volume, 10)
            self.assertEqual(args.well_capacity, 'Component1=55000')
            self.assertEqual(args.default_well_capacity, 60000)
            self.assertEqual(args.start_well_src_plt, 'A1')
            self.assertEqual(args.output_folder, self.temp_dir.name)

    def test_prepare_destination_plate(self):
        result = prepare_destination_plate(
            self.sampling_data,
            self.start_well_dst_plt,
            self.plate_dims,
            self.sample_volume,
            self.num_replicates
        )
        self.assertEqual(result.shape[0], self.sampling_data.shape[0] * self.num_replicates)

    def test_prepare_source_plate(self):
        destination_data = prepare_destination_plate(
            self.sampling_data,
            self.start_well_dst_plt,
            self.plate_dims,
            self.sample_volume,
            self.num_replicates
        )
        result = prepare_source_plate(
            destination_data,
            self.dead_volumes_str,
            self.default_dead_volume,
            self.well_capacity,
            self.default_well_capacity,
            self.start_well_src_plt
        )
        self.assertEqual(result.shape[0], self.sampling_data.shape[0])

    def test_write_output_files(self):
        destination_data = prepare_destination_plate(
            self.sampling_data,
            self.start_well_dst_plt,
            self.plate_dims,
            self.sample_volume,
            self.num_replicates
        )
        source_data = prepare_source_plate(
            destination_data,
            self.dead_volumes_str,
            self.default_dead_volume,
            self.well_capacity,
            self.default_well_capacity,
            self.start_well_src_plt
        )
        write_output_files(source_data, destination_data, Path(self.temp_dir.name))
        self.assertTrue((Path(self.temp_dir.name) / 'destination_plate.csv').exists())
        self.assertTrue((Path(self.temp_dir.name) / 'source_plate.csv').exists())

    def test_main(self):
        # Create a temporary CSV file for sampling data
        sampling_file_path = Path(self.temp_dir.name) / 'sampling_data.csv'
        self.sampling_data.to_csv(sampling_file_path, index=False)

        # Mocking the args for the main function
        import sys
        from unittest.mock import patch

        test_args = [
            'plate_designer.py',
            str(sampling_file_path),
            '1000',
            '--start_well_dst_plt', 'A1',
            '--plate_dims', '8x12',
            '--num_replicates', '2',
            '--dead_volumes', 'Component1=10,Component2=10',
            '--default_dead_volume', '10',
            '--well_capacity', 'Component1=55000',
            '--default_well_capacity', '60000',
            '--start_well_src_plt', 'A1',
            '--output_folder', self.temp_dir.name
        ]

        with patch.object(sys, 'argv', test_args):
            from icfree.plate_designer import main
            main()
            self.assertTrue((Path(self.temp_dir.name) / 'destination_plate.csv').exists())
            self.assertTrue((Path(self.temp_dir.name) / 'source_plate.csv').exists())

if __name__ == '__main__':
    unittest.main()
