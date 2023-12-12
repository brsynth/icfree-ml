# Tests plates_generator.py
from unittest import (
    TestCase
)
from pytest import (
    raises as pytest_raises
)

from os import (
    path as os_path
)
from json import (
    load as json_load,
    dumps as json_dumps
)
from logging import getLogger
from pandas import (
    read_csv as pd_read_csv,
    testing as pd_testing
)
from tempfile import gettempdir
from uuid import uuid1

from icfree.plates_generator.plates_generator import (
    init_plate,
    dst_plate_generator,
    src_plate_generator,
    extract_dead_volumes
)
from icfree.plates_generator.__main__ import input_importer
from icfree.plates_generator.plate import Plate


class TestPlatesGenerator(TestCase):

    def setUp(self):
        self.DATA_FOLDER = os_path.join(
            os_path.dirname(os_path.realpath(__file__)),
            'data', 'plates_generator'
        )

        self.INPUT_FOLDER = os_path.join(
            self.DATA_FOLDER,
            'input'
        )

        self.REF_FOLDER = os_path.join(
            self.DATA_FOLDER,
            'output'
        )

        self.parameters = os_path.join(
            self.INPUT_FOLDER,
            'parameters.tsv'
        )

        self.sampling = os_path.join(
            self.INPUT_FOLDER,
            'sampling.tsv'
        )

    def test_init_plate(self):
        plate = init_plate()
        self.assertEqual(len(plate.get_cols()), 24)
        self.assertEqual(len(plate.get_rows()), 16)
        self.assertEqual(plate.get_dead_volume(), 15000)
        self.assertEqual(plate.get_well_capacity(), 60000)
        self.assertEqual(plate.get_current_well(), 'A1')

    def test_extract_dead_volumes(self):
        parameters_df, _ = input_importer(
            self.parameters,
            self.sampling
        )
        # Exract dead plate volumes from cfps_parameters_df
        dead_volumes = extract_dead_volumes(parameters_df)
        self.assertEqual(
            dead_volumes,
            {
                'Component_1': 0,
                'Component_2': 0,
                'Component_3': 0,
                'Component_4': 0,
                'Component_5': 0,
                'Component_6': 0,
                'Component_7': 0,
                'Component_8': 0,
                'Water': 0
            }
        )

    def test_src_plate_generator(self):
        sample_volume = 10000
        parameters_df, values_df = input_importer(
            self.parameters,
            self.sampling
        )
        # Extract dead plate volumes from parameters_df
        dead_volumes = extract_dead_volumes(parameters_df)
        values_df['Water'] = \
            sample_volume - values_df.sum(axis=1)
        # Generate source plates
        source_plates = src_plate_generator(
            volumes=values_df,
            plate_dead_volume=15000,
            plate_well_capacity=60000,
            param_dead_volumes=dead_volumes,
            starting_well='A1',
            optimize_well_volumes=[],
            vertical=True,
            plate_dimensions='16x24',
        )
        expected_plate = Plate.from_file(
            os_path.join(self.REF_FOLDER, 'source_plate_1.json')
        )
        self.assertEqual(source_plates['1'], expected_plate)

    def test_src_plate_generator_wOptVol(self):
        sample_volume = 10000
        (
            parameters_df,
            values_df
        ) = input_importer(
            self.parameters,
            self.sampling
        )
        # Exract dead plate volumes from cfps_parameters_df
        dead_volumes = extract_dead_volumes(parameters_df)
        values_df['Water'] = \
            sample_volume - values_df.sum(axis=1)

        # Generate source plates
        source_plates = src_plate_generator(
            volumes=values_df,
            plate_dead_volume=15000,
            plate_well_capacity=60000,
            param_dead_volumes=dead_volumes,
            starting_well='A1',
            optimize_well_volumes=['Component_1'],
            vertical=True,
            plate_dimensions='16x24',
        )
        self.assertEqual(
            source_plates['1'].get_well('A1')['Component_1'],
            19750.0
        )

    def test_src_plate_generator_outOfPlate(self):
        sample_volume = 10000
        (
            parameters_df,
            values_df
        ) = input_importer(
            self.parameters,
            self.sampling
        )
        # Exract dead plate volumes from parameters_df
        dead_volumes = extract_dead_volumes(parameters_df)
        values_df['Water'] = \
            sample_volume - values_df.sum(axis=1)
        # Generate source plates
        source_plates = src_plate_generator(
            volumes=values_df,
            plate_dead_volume=15000,
            plate_well_capacity=60000,
            param_dead_volumes=dead_volumes,
            starting_well='N24',
            optimize_well_volumes=[],
            vertical=True,
            plate_dimensions='16x24',
        )
        expected_plate_1 = Plate.from_file(
            os_path.join(self.REF_FOLDER, 'src_plate_1.json')
        )
        expected_plate_2 = Plate.from_file(
            os_path.join(self.REF_FOLDER, 'src_plate_2.json')
        )
        self.assertEqual(source_plates['1'], expected_plate_1)
        self.assertEqual(source_plates['2'], expected_plate_2)

    def test_src_plate_generator_WithNullVolume(self):
        sample_volume = 10000
        parameters_df, values_df = input_importer(
            self.parameters,
            self.sampling
        )
        # Exract dead plate volumes from parameters_df
        dead_volumes = extract_dead_volumes(parameters_df)
        values_df['Water'] = \
            sample_volume - values_df.sum(axis=1)
        values_df['Component_1'] = 0
        # Generate source plates
        source_plates = src_plate_generator(
            volumes=values_df,
            plate_dead_volume=15000,
            plate_well_capacity=60000,
            param_dead_volumes=dead_volumes,
            starting_well='A1',
            optimize_well_volumes=[],
            vertical=True,
            plate_dimensions='16x24',
        )
        self.assertEqual(
            source_plates['1'].get_well('A1')['Component_2'],
            60000
        )

    def test_dst_plate_generator(self):
        _, values_df = input_importer(
            self.parameters,
            self.sampling
        )
        # Generate destination plates
        dest_plates = dst_plate_generator(
            volumes=values_df,
            starting_well='A1',
            plate_well_capacity=60000,
            vertical=True,
        )
        expected_plate = Plate.from_file(
            os_path.join(self.REF_FOLDER, 'destination_plate_1.json')
        )
        self.assertEqual(dest_plates['1'], expected_plate)

    def test_dst_plate_generator_OutOfPlate(self):
        _, values_df = input_importer(
            self.parameters,
            self.sampling
        )
        # Generate destination plates
        dest_plates = dst_plate_generator(
            volumes=values_df,
            starting_well='N24',
            plate_well_capacity=60000,
            vertical=True,
        )
        expected_plate_1 = Plate.from_file(
            os_path.join(self.REF_FOLDER, 'dst_plate_1.json')
        )
        expected_plate_2 = Plate.from_file(
            os_path.join(self.REF_FOLDER, 'dst_plate_2.json')
        )
        self.assertEqual(dest_plates['1'], expected_plate_1)
        self.assertEqual(dest_plates['2'], expected_plate_2)


class TestPlate(TestCase):

    def setUp(self):
        self.DATA_FOLDER = os_path.join(
            os_path.dirname(os_path.realpath(__file__)),
            'data', 'plates_generator'
        )

        self.INPUT_FOLDER = os_path.join(
            self.DATA_FOLDER,
            'input'
        )

        self.REF_FOLDER = os_path.join(
            self.DATA_FOLDER,
            'output'
        )

    def test_plate_vertical(self):
        plate = Plate(
            dimensions='16x24',
            dead_volume=15000,
            well_capacity=60000,
            vertical=True
        )
        plate.next_well()
        self.assertEqual(plate.get_current_well(), 'B1')

    def test_plate_horizontal(self):
        plate = Plate(
            dimensions='16x24',
            dead_volume=15000,
            well_capacity=60000,
            vertical=False
        )
        plate.next_well()
        self.assertEqual(plate.get_current_well(), 'A2')

    def test_plate_get_dimensions(self):
        plate = Plate(
            dimensions='16x24',
            dead_volume=15000,
            well_capacity=60000,
            vertical=True
        )
        self.assertEqual(plate.get_dimensions(), '16x24')

    def test_plate_get_list_of_parameters_null(self):
        plate = Plate(
            dimensions='16x24',
            dead_volume=15000,
            well_capacity=60000,
            vertical=True
        )
        self.assertEqual(plate.get_list_of_parameters(), [])

    def test_plate_well_out_of_range(self):
        plate = Plate(
            dimensions='16x24',
            dead_volume=15000,
            well_capacity=60000,
            vertical=True
        )
        self.assertTrue(plate.well_out_of_range('A25'))

    def test_plate_from_file(self):
        plate = Plate.from_file(
            os_path.join(self.REF_FOLDER, 'dst_plate_1.json')
        )
        self.assertEqual(plate.get_well('N24')['Component_1'], 0)

    def test_plate_to_file(self):
        plate = Plate.from_file(
            os_path.join(self.REF_FOLDER, 'source_plate_1.json')
        )
        tmp_outfile = os_path.join(
            gettempdir(),
            str(uuid1())
        ) + '.csv'
        plate.to_file(tmp_outfile, 'csv')
        _tmp_outfile = os_path.splitext(tmp_outfile)
        plate_test = Plate.from_file(f'{_tmp_outfile[0]}.json')
        self.assertEqual(plate, plate_test)

    def test_plate_to_csv(self):
        plate = Plate.from_file(
            os_path.join(self.REF_FOLDER, 'source_plate_2.json')
        )
        tmp_outfile = os_path.join(
            gettempdir(),
            str(uuid1())
        ) + '.csv'
        plate.to_file(tmp_outfile, 'csv')
        df = pd_read_csv(f'{tmp_outfile}', index_col=0)
        ref_df = pd_read_csv(
            os_path.join(self.REF_FOLDER, 'source_plate_1.csv'),
            index_col=0
        )
        pd_testing.assert_frame_equal(df, ref_df)
        plate.to_file(tmp_outfile, 'tsv')
        df = pd_read_csv(f'{tmp_outfile}', index_col=0, sep='\t')
        ref_df = pd_read_csv(
            os_path.join(self.REF_FOLDER, 'source_plate_1.tsv'),
            index_col=0,
            sep='\t'
        )
        pd_testing.assert_frame_equal(df, ref_df)

    def test_plate_get_well(self):
        plate = Plate.from_file(
            os_path.join(self.REF_FOLDER, 'dst_plate_1.json')
        )
        self.assertEqual(plate.get_well('N24')['Component_1'], 0)

    def test_plate_set_current_well(self):
        plate = Plate.from_file(
            os_path.join(self.REF_FOLDER, 'source_plate_1.json')
        )
        plate.set_current_well('D4')
        plate.next_well()
        self.assertEqual(plate.get_current_well(), 'E4')

    def test_plate_fill_well(self):
        plate = Plate.from_file(
            os_path.join(self.REF_FOLDER, 'dst_plate_1.json')
        )
        plate.fill_well('Component_1', 12.5, 'A1')
        plate.fill_well('Component_2', 125.0, 'A1')
        self.assertEqual(plate.get_well_volume('A1'), 137.5)
        plate.fill_well('Component_1', 12.5, 'N24')
        plate.fill_well('Component_2', 125.0, 'N24')
        self.assertEqual(plate.get_well_volume('N24'), 668.75)

    def test_plate_fill_well_OutOfRange(self):
        plate = Plate(
            dimensions='16x24',
            dead_volume=15000,
            well_capacity=60000,
            vertical=True,
            logger=getLogger('foo')
        )
        # Add new parameter with too high volume
        with pytest_raises(ValueError):
            plate.fill_well('Component_1', 60001, 'A1')
        # Add new parameter with out of range well
        with pytest_raises(IndexError):
            plate.fill_well('Component_1', 12.5, 'A25')
        plate = Plate.from_file(
            os_path.join(self.REF_FOLDER, 'dst_plate_1.json')
        )
        # # Add already existing parameter
        # with pytest_raises(ValueError):
        #     plate.fill_well('Component_1', 59483, 'N24')

    def test_plate_get_well_volume(self):
        plate = Plate.from_file(
            os_path.join(self.REF_FOLDER, 'dst_plate_1.json')
        )
        self.assertEqual(plate.get_well_volume('N24'), 531.25)
        self.assertDictEqual(
            plate.get_well('N24'),
            {
                "Component_1": 0.0,
                "Component_2": 125.0,
                "Component_3": 62.5,
                "Component_4": 93.75,
                "Component_5": 62.5,
                "Component_6": 125.0,
                "Component_7": 0.0,
                "Component_8": 62.5
            }
        )

    def test_plate_to_dict(self):
        file = os_path.join(self.REF_FOLDER, 'source_plate_1.json')
        plate = Plate.from_file(file)
        with open(file, 'r') as f:
            d_plate = json_load(f)
        d_plate['Wells'] = Plate.wells_from_csv(d_plate['Wells'])
        _d_plate = plate.to_dict()
        self.assertEqual(_d_plate['Dimensions'], d_plate['Dimensions'])
        self.assertEqual(
            sorted(_d_plate['Parameters']),
            sorted(d_plate['Parameters'])
        )
        self.assertEqual(_d_plate['Wells'], d_plate['Wells'])
        self.assertEqual(_d_plate['deadVolume'], d_plate['deadVolume'])
        self.assertEqual(_d_plate['Well capacity'], d_plate['Well capacity'])
        # self.assertEqual(_d_plate['Empty wells'], d_plate['Empty wells'])
        self.assertEqual(_d_plate['Current well'], d_plate['Current well'])

    def test_plate___str__(self):
        file = os_path.join(self.REF_FOLDER, 'source_plate_1.json')
        plate = Plate.from_file(file)
        s_plate = json_dumps(plate.to_dict(), indent=4)
        self.assertEqual(str(plate), s_plate)

    def test_plate___eq__(self):
        file = os_path.join(self.REF_FOLDER, 'source_plate_1.json')
        plate = Plate.from_file(file)
        plate_test = Plate.from_file(file)
        self.assertEqual(plate, plate_test)
        self.assertNotEqual(plate, Plate())

    def test_plate_reindex_wells_by_factor(self):
        plate = Plate.from_file(
            os_path.join(self.REF_FOLDER, 'source_plate_1.json')
        )
        d = plate.reindex_wells_by_factor()
        self.assertDictEqual(
            d,
            json_load(
                open(
                    os_path.join(
                        self.REF_FOLDER,
                        'plate_reindexed_by_factors.json'
                    )
                )
            )
        )

    def test_plate_get_volumes_summary_dict(self):
        plate_1 = Plate.from_file(
            os_path.join(self.REF_FOLDER, 'src_plate_1.json')
        )
        plate_2 = Plate.from_file(
            os_path.join(self.REF_FOLDER, 'src_plate_2.json')
        )
        d = Plate.get_volumes_summary(
            [plate_1, plate_2],
            type_='dict'
        )
        self.assertDictEqual(
            d,
            json_load(
                open(
                    os_path.join(
                        self.REF_FOLDER,
                        'plate_volumes_summary.json'
                    )
                )
            )
        )

    def test_plate_get_volumes_summary_pandas(self):
        plate_1 = Plate.from_file(
            os_path.join(self.REF_FOLDER, 'src_plate_1.json')
        )
        plate_2 = Plate.from_file(
            os_path.join(self.REF_FOLDER, 'src_plate_2.json')
        )
        df = Plate.get_volumes_summary(
            [plate_1, plate_2],
            type_='pandas'
        )
        pd_testing.assert_frame_equal(
            df,
            pd_read_csv(
                open(
                    os_path.join(
                        self.REF_FOLDER,
                        'plate_volumes_summary.csv'
                    )
                ),
                index_col=0
            )
        )

    def test_plate_get_volumes_summary_str(self):
        plate_1 = Plate.from_file(
            os_path.join(self.REF_FOLDER, 'src_plate_1.json')
        )
        plate_2 = Plate.from_file(
            os_path.join(self.REF_FOLDER, 'src_plate_2.json')
        )
        s = Plate.get_volumes_summary(
            [plate_1, plate_2],
            type_='str'
        )
        with open(
            os_path.join(
                self.REF_FOLDER,
                'plate_volumes_summary.txt'
            ), 'r'
        ) as f:
            lines = f.readlines()
        self.assertEqual(s, ''.join(lines))

    def test_from_file(self):
        file = os_path.join(self.REF_FOLDER, 'src_plate_1.json')
        wells_files = os_path.join(self.REF_FOLDER, 'src_plate_2.csv')
        plate = Plate.from_file(file, wells_files)
        self.assertDictEqual(
            plate.to_dict()['Wells'],
            Plate.wells_from_csv(wells_files)
        )
