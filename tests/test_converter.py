# Test for sampler
from unittest import (
    TestCase
)

from os import (
    path as os_path
)
from pandas.testing import (
    assert_frame_equal
)
from pandas import read_csv as pd_read_csv

from icfree.converter.__main__ import input_importer
from icfree.converter.converter import concentrations_to_volumes


class Test(TestCase):

    def setUp(self):
        self.DATA_FOLDER = os_path.join(
            os_path.dirname(os_path.realpath(__file__)),
            'data', 'converter'
        )
        self.INPUT_FOLDER = os_path.join(
            self.DATA_FOLDER,
            'input'
        )
        self.OUTPUT_FOLDER = os_path.join(
            self.DATA_FOLDER,
            'output'
        )
        self.proCFPS_parameters = os_path.join(
            self.INPUT_FOLDER,
            'parameters.tsv'
        )
        self.sampling_concentrations = os_path.join(
            self.INPUT_FOLDER,
            'sampling_concentrations.tsv'
        )
        self.sampling_volumes = os_path.join(
            self.OUTPUT_FOLDER,
            'sampling_volumes.tsv'
        )

    def test_concentrations_to_volumes(self):
        (
            cfps_parameters_df,
            concentrations_df
        ) = input_importer(
            self.proCFPS_parameters,
            self.sampling_concentrations
        )
        volumes_df = concentrations_to_volumes(
            cfps_parameters_df,
            concentrations_df,
            1000
        )
        expected_df = pd_read_csv(self.sampling_volumes, sep='\t')
        assert_frame_equal(
            expected_df,
            volumes_df
        )
