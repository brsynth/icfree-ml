# Test for instructor

from unittest import (
    TestCase
)

from os import path as os_path
from pandas import (
    read_csv as pd_read_csv,
    testing as pd_testing
)
from json import load as json_load

from icfree.instructor.instructor import (
    check_volumes,
    instructions_generator
)
from icfree.plates_generator.plate import Plate


class TestInstructor(TestCase):

    def setUp(self):
        self.DATA_FOLDER = os_path.join(
            os_path.dirname(os_path.realpath(__file__)),
            'data', 'instructor'
        )
        for folder in ['input', 'output', 'ref']:
            setattr(
                self,
                folder + '_folder',
                os_path.join(self.DATA_FOLDER, folder)
            )
        # self.src_plt_1, self.src_plt_2
        # self.dst_plt_1, self.dst_plt_2
        for plate_type in ['src', 'dst']:
            for i in range(1, 3):
                setattr(
                    self,
                    f'{plate_type}_plt_{str(i)}',
                    os_path.join(
                        self.input_folder,
                        f'2_{plate_type}_plate_{i}.json'
                    )
                )
        self.source_plate = os_path.join(
            self.input_folder,
            'source_plate_1.json'
        )
        self.dest_plate = os_path.join(
            self.input_folder,
            'destination_plate_1.json'
        )

    def test_check_volumes(self):
        plate = Plate.from_json(self.dst_plt_1)
        warning_volumes_report = check_volumes(
            plate.to_dict(),
            lower_bound=10,
            upper_bound=1000
        )
        self.assertEqual(
            len(warning_volumes_report),
            0
        )

    def test_check_volumes_warning_upper(self):
        plate = Plate.from_json(self.src_plt_1)
        warning_volumes_report = check_volumes(
            plate.to_dict(),
            lower_bound=10,
            upper_bound=1000
        )
        # Read json ref file
        ref_report_file = os_path.join(
            self.ref_folder,
            'src_plate_1_warn_report_upper.json'
        )
        with open(ref_report_file, 'r') as f:
            d_report = json_load(f)
        # Compare
        self.assertListEqual(
            warning_volumes_report.to_dict(orient='records'),
            d_report
        )

    def test_check_volumes_warning_lower(self):
        plate = Plate.from_json(self.dest_plate)
        warning_volumes_report = check_volumes(
            plate.to_dict(),
            lower_bound=100,
            upper_bound=1000
        )
        # Read json ref file
        ref_report_file = os_path.join(
            self.ref_folder,
            'src_plate_1_warn_report_lower.json'
        )
        with open(ref_report_file, 'r') as f:
            d_report = json_load(f)
        # Compare
        self.assertListEqual(
            warning_volumes_report.to_dict(orient='records'),
            d_report
        )

    def test_instructions_generator(self):
        source_plates = {
            'plate_1': Plate.from_json(self.src_plt_1),
            'plate_2': Plate.from_json(self.src_plt_2)
        }
        destination_plates = {
            'plate_1': Plate.from_json(self.dst_plt_1),
            'plate_2': Plate.from_json(self.dst_plt_2)
        }
        instructions = instructions_generator(
            source_plates,
            destination_plates,
            robot='echo'
        )
        # Read csv ref file
        ref_instructions_file = os_path.join(
            self.output_folder,
            'echo_instructions.csv'
        )
        ref_instructions = pd_read_csv(ref_instructions_file)
        # Compare
        pd_testing.assert_frame_equal(
            instructions,
            ref_instructions
        )
