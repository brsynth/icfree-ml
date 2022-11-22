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
            'proCFPS_parameters.tsv'
        )
        self.sampling_concentrations = os_path.join(
            self.INPUT_FOLDER,
            'sampling_concentrations.tsv'
        )
        self.sampling_volumes = os_path.join(
            self.OUTPUT_FOLDER,
            'sampling_volumes.tsv'
        )

    # def test_input_importer(self):
    #     with open(
    #         os_path.join(
    #                 self.REF_FOLDER,
    #                 'test_input_importer.json'
    #         ), 'r'
    #     ) as fp:
    #         expected_df = DataFrame(
    #             json_load(fp)
    #         )
    #         cfps_parameters = os_path.join(
    #             self.INPUT_FOLDER,
    #             'proCFPS_parameters_woGOI.tsv'
    #             )
    #         tested_df = input_importer(cfps_parameters)
    #         for i, row in tested_df.iterrows():
    #             if isinstance(row['Ratios'], str):
    #                 tested_df.at[i, 'Ratios'] = list(
    #                     map(
    #                         float,
    #                         row['Ratios'].split(',')
    #                     )
    #                 )
    #             else:
    #                 tested_df.at[i, 'Ratios'] = None
    #         assert_frame_equal(
    #             expected_df,
    #             tested_df
    #         )

    # def test_input_processor(self):
    #     with open(
    #         os_path.join(
    #                 self.REF_FOLDER,
    #                 'test_input_processor.json'
    #         ), 'r'
    #     ) as fp:
    #         expected_dictionary = (json_load(fp))

    #     with open(
    #         os_path.join(
    #                 self.INPUT_FOLDER,
    #                 'proCFPS_parameters.tsv'
    #         ), 'r'
    #     ) as fp:
    #         tested_df = input_importer(fp)

    #     tested_dictionary = input_processor(tested_df)
    #     print(tested_dictionary)
    #     self.assertDictEqual(
    #             expected_dictionary,
    #             tested_dictionary
    #         )

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
