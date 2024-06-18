# Test for sampler
from unittest import TestCase
from unittest.mock import patch

from os import (
    path as os_path
)
from pandas.testing import (
    assert_frame_equal
)
from pandas import (
    read_csv as pd_read_csv,
    testing as pd_testing
)
from tempfile import NamedTemporaryFile
from subprocess import run as sp_run

from icfree.converter.__main__ import (
    input_importer,
    main
)
from icfree.converter.converter import concentrations_to_volumes
from icfree.converter.args import build_args_parser

from tests.functions import tmp_filepath, clean_file


__DATA_FOLDER = os_path.join(
    os_path.dirname(os_path.realpath(__file__)),
    'data', 'converter'
)
__INPUT_FOLDER = os_path.join(
    __DATA_FOLDER,
    'input'
)
__OUTPUT_FOLDER = os_path.join(
    __DATA_FOLDER,
    'output'
)
parameters = os_path.join(
    __INPUT_FOLDER,
    'parameters.tsv'
)
sampling_concentrations = os_path.join(
    __INPUT_FOLDER,
    'sampling_concentrations.tsv'
)
sampling_volumes = os_path.join(
    __OUTPUT_FOLDER,
    'sampling_volumes.tsv'
)
sampling_volumes_other = os_path.join(
    __OUTPUT_FOLDER,
    'sampling_volumes_other.tsv'
)


class Test(TestCase):

    def test_concentrations_to_volumes(self):
        (
            cfps_parameters_df,
            concentrations_df
        ) = input_importer(
            parameters,
            sampling_concentrations
        )
        volumes_df = concentrations_to_volumes(
            cfps_parameters_df,
            concentrations_df,
            1000,
            2.5
        )
        expected_df = pd_read_csv(sampling_volumes, sep='\t')
        assert_frame_equal(
            expected_df,
            volumes_df
        )


class TestArgsParser(TestCase):

    def setUp(self):
        self.parser = build_args_parser(
            signature="",
            description=""
        )

    def test_valid_input(self):
        args = self.parser.parse_args(
            [
                'parameters.tsv',
                'concentrations.tsv',
                '-v', '1000',
                '-o', 'outfile.tsv',
                '-r', 'echo'
            ]
        )
        self.assertEqual(args.parameters, 'parameters.tsv')
        self.assertEqual(args.concentrations, 'concentrations.tsv')
        self.assertEqual(args.sample_volume, 1000)
        self.assertEqual(args.outfile, 'outfile.tsv')
        self.assertEqual(args.robot, 'echo')

    def test_missing_input(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(
                [
                    'parameters.tsv',
                    'concentrations.tsv',
                    '-v', '1000',
                    '-r', 'echo'
                ]
            )


# Test with CLI simulation and check output file
class TestCLI(TestCase):
    def setUp(self):
        self.parser = build_args_parser(
            signature="",
            description=""
        )

    def test_valid_input(self):
        tmp_fn = tmp_filepath('.tsv')
        args = [
            parameters,
            sampling_concentrations,
            '-v', '1000',
            '-o', tmp_fn,
            '-r', 'echo'
        ]
        main(args)
        actual = pd_read_csv(tmp_fn, sep='\t')
        expected = pd_read_csv(sampling_volumes, sep='\t')
        pd_testing.assert_frame_equal(actual, expected)
        clean_file(tmp_fn)

    def test_other_robot(self):
        tmp_fn = tmp_filepath('.tsv')
        args = [
            parameters,
            sampling_concentrations,
            '-v', '1000',
            '-o', tmp_fn,
            '-r', 'other'
        ]
        main(args)
        actual = pd_read_csv(tmp_fn, sep='\t')
        expected = pd_read_csv(sampling_volumes_other, sep='\t')
        pd_testing.assert_frame_equal(actual, expected)
        clean_file(tmp_fn)

    def test_system_exit(self):
        args = [
                parameters,
                sampling_concentrations,
                '-v', '1000',
                '-o', 'outfile.tsv',
                '-r', 'other'
            ]
        with patch('icfree.converter.__main__.concentrations_to_volumes', side_effect=ValueError("Invalid robot")):
            with self.assertRaises(SystemExit):
                main(args)

    def test_subprocess_call(self):
        tmp_fn = tmp_filepath('.tsv')
        cmd = 'python -m icfree.converter {} {} -o {} -v 1000 -r echo'.format(parameters, sampling_concentrations, tmp_fn)
        sp_run(cmd.split())
        actual = pd_read_csv(tmp_fn)
        expected = pd_read_csv(sampling_volumes)
        pd_testing.assert_frame_equal(actual, expected)
        clean_file(tmp_fn)
