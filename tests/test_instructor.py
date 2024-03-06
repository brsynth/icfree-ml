from unittest import TestCase

from pandas import DataFrame
from tempfile import NamedTemporaryFile

from icfree.instructor.instructor import (
    parse_src_plate_type_option,
    generate_instructions_list,
    generate_instructions,
    get_plate_index,
    split_instructions_by_components
)
from icfree.instructor.args import (
    DEFAULT_ARGS,
    build_args_parser
)


class TestParseSrcPlateTypeOption(TestCase):

    def test_parse_src_plate_type_option(self):
        # Test case 1
        src_plate_type_option = "ALL:384PP_AQ_GP3;A,B,C:384PP_AQ_GP4"
        expected_result = {
            'ALL': '384PP_AQ_GP3',
            'A': '384PP_AQ_GP4', 'B': '384PP_AQ_GP4', 'C': '384PP_AQ_GP4'
        }
        result = parse_src_plate_type_option(src_plate_type_option)
        self.assertEqual(result, expected_result)

        # Test case 2
        src_plate_type_option = "ALL:384PP_AQ_GP3"
        expected_result = {'ALL': '384PP_AQ_GP3'}
        result = parse_src_plate_type_option(src_plate_type_option)
        self.assertEqual(result, expected_result)

        # Test case 3
        src_plate_type_option = ""
        expected_result = {'ALL': '384PP_AQ_GP3'}
        result = parse_src_plate_type_option(src_plate_type_option)
        self.assertEqual(result, expected_result)


class TestGenerateInstructions(TestCase):
    def test_generate_instructions(self):
        # Create sample dataframes
        source_df = DataFrame({
            'Well': ['A1', 'A2', 'B1', 'B2'],
            'Component_1': [0, 100, 100, 0],
            'Component_2': [100, 0, 0, 0],
            'Component_3': [0, 0, 0, 0]
        })
        destination_df = DataFrame({
            'Well': ['A1', 'A2', 'B1', 'B2'],
            'Component_1': [0, 10, 20, 0],
            'Component_2': [5, 0, 0, 15],
            'Component_3': [0, 0, 0, 0]
        })
        plate_types = "ALL:384PP_AQ_GP3;Component_1:384PP_AQ_GP4"

        # Write source and destination dataframes to CSV temp files
        with NamedTemporaryFile() as source_file, NamedTemporaryFile() as destination_file:
            source_df.to_csv(source_file.name, index=False)
            destination_df.to_csv(destination_file.name, index=False)

            # Generate instructions
            instructions = generate_instructions(
                [source_file.name], [destination_file.name], src_plate_type=plate_types
            )

            # Define expected instructions as DataFrame
            expected_instructions = DataFrame({
                'Source Plate Name': ['Source[1]', 'Source[1]', 'Source[1]', 'Source[1]'],
                'Source Plate Type': ['384PP_AQ_GP4', '384PP_AQ_GP4', '384PP_AQ_GP3', '384PP_AQ_GP3'],
                'Source Well': ['{A2;B1}', '{A2;B1}', 'A1', 'A1'],
                'Destination Plate Name': ['Destination[1]', 'Destination[1]', 'Destination[1]', 'Destination[1]'],
                'Destination Well': ['A2', 'B1', 'A1', 'B2'],
                'Transfer Volume': [10, 20, 5, 15],
                'Sample ID': ['Component_1', 'Component_1', 'Component_2', 'Component_2']
            })

            # Sort dataframes for comparison
            instructions = instructions.sort_values(by=['Sample ID'], ignore_index=True)
            expected_instructions = expected_instructions.sort_values(by=['Sample ID'], ignore_index=True)
            # Compare instructions with expected instructions
            self.assertTrue(instructions.equals(expected_instructions))


class TestGetPlateIndex(TestCase):
    def setUp(self):
        # Sample plate dataframes
        self.plate_df1 = DataFrame({'ComponentA': [1, 2, 3]})
        self.plate_df2 = DataFrame({'ComponentB': [4, 5, 6]})
        self.plates = [self.plate_df1, self.plate_df2]

    def test_component_found(self):
        index = get_plate_index('ComponentA', self.plates)
        self.assertEqual(index, 0)

    def test_component_not_found(self):
        index = get_plate_index('ComponentC', self.plates)
        self.assertEqual(index, -1)

    def test_multiple_occurrences(self):
        plates_with_dupes = [self.plate_df1, DataFrame({'ComponentA': [7, 8, 9]})]
        index = get_plate_index('ComponentA', plates_with_dupes)
        self.assertEqual(index, 0)

    def test_empty_list_of_plates(self):
        index = get_plate_index('ComponentA', [])
        self.assertEqual(index, -1)

    def test_no_dataframes_contain_columns(self):
        empty_df = DataFrame()
        index = get_plate_index('ComponentA', [empty_df])
        self.assertEqual(index, -1)


class TestGenerateInstructionsList(TestCase):
    def setUp(self):
        # Sample source and destination dataframes setup
        self.source_df1 = DataFrame({
            'Well': ['A1', 'A2'],
            'Component1': [200, 0],
            'Component2': [0, 100]
        })
        self.destination_df1 = DataFrame({
            'Well': ['B1', 'B2'],
            'Component1': [100, 10],
            'Component2': [10, 50]
        })
        self.plate_types = {
            'Component1': 'PlateType1',
            'Component2': 'PlateType2',
            'ALL': 'DefaultPlateType'
        }

    def test_basic_transfer(self):
        instructions = generate_instructions_list(
            [self.source_df1], 
            [self.destination_df1], 
            self.plate_types
        )
        self.assertIsInstance(instructions, list)
        self.assertGreater(len(instructions), 0)
        # Further assertions on the content of instructions can be added

    def test_basic_volume_splitting(self):
        # Adjusting source data to exceed split_upper_vol
        instructions = generate_instructions_list(
            [self.source_df1], 
            [self.destination_df1], 
            self.plate_types, 
            split_upper_vol=50,
            split_lower_vol=0
        )
        # Check that there are 3 instructions for 'Component_1'
        instructions_C1 = [i for i in instructions if i['Sample ID'] == 'Component1']
        # Extract list of volumes to transfer and check that they are correct: 2x50uL and 1x10uL
        volumes = [i['Transfer Volume'] for i in instructions_C1]
        self.assertEqual(volumes, [50, 50, 10])

    def test_volume_splitting_with_min_bound_equal_to_last_vol(self):
        # Adjusting source data to exceed split_upper_vol
        instructions = generate_instructions_list(
            [self.source_df1],
            [self.destination_df1],
            self.plate_types,
            split_upper_vol=80,
            split_lower_vol=19
        )
        # Check that there are 3 instructions for 'Component_1'
        instructions_C1 = [i for i in instructions if i['Sample ID'] == 'Component1']
        # Extract list of volumes to transfer and check that they are correct: 2x50uL and 1x10uL
        volumes = [i['Transfer Volume'] for i in instructions_C1]
        self.assertEqual(volumes, [80, 20, 10])

    def test_volume_splitting_with_min_bound_greater_than_last_vol(self):
        # Adjusting source data to exceed split_upper_vol
        instructions = generate_instructions_list(
            [self.source_df1],
            [self.destination_df1],
            self.plate_types,
            split_upper_vol=80,
            split_lower_vol=21
        )
        # Check that there are 3 instructions for 'Component_1'
        instructions_C1 = [i for i in instructions if i['Sample ID'] == 'Component1']
        # Extract list of volumes to transfer and check that they are correct: 1x50uL and 1x60uL
        volumes = [i['Transfer Volume'] for i in instructions_C1]
        self.assertEqual(volumes, [100, 10])


class TestSplitInstructionsByComponents(TestCase):
    def setUp(self):
        # Sample DataFrame setup
        self.instructions_df = DataFrame({
            'Sample ID': ['C1', 'C2', 'C2', 'C2', 'C3'],
            'Instruction': ['Do X', 'Do Y', 'Do Z', 'Do W', 'Do V']
        })

    def test_basic_split(self, outfile_path='test.csv', split_components='C1 C2 C3'):
        print(outfile_path)
        instructions_split = split_instructions_by_components(self.instructions_df, outfile_path, split_components)
        # Replace commas with underscores in split_components
        split_components = '_'.join(split_components.split(',')).split()
        # Add the remaining component to the list
        split_components.append('rest')
        print(split_components)
        # Check all outfile paths have been created,
        # and no extra files were created.
        # Doing this by using sets
        if outfile_path.endswith('.csv'):
            outfile_paths = [f'{outfile_path[:-4]}_split_{comp}.csv' for comp in split_components]
        else:
            outfile_paths = [f'{outfile_path}_split_{comp}.csv' for comp in split_components]
        print(instructions_split.keys())
        print(outfile_paths)
        # Check no extra files were created
        self.assertSetEqual(set(instructions_split.keys()), set(outfile_paths))
        # For each instruction set, check there are only instructions for the corresponding components
        single_split_components = [comp.split('_') for comp in split_components[:-1]]
        # Flatten the list
        flat_single_split_components = [item for sublist in single_split_components for item in sublist]
        print(single_split_components)
        rest_components = list(set([comp for comp in self.instructions_df['Sample ID'] if comp not in flat_single_split_components]))
        single_split_components.append(rest_components)
        print(single_split_components)
        for comp in single_split_components:
            print(comp)
            print(instructions_split[outfile_paths[single_split_components.index(comp)]])
            print(self.instructions_df[self.instructions_df['Sample ID'].isin(comp)])
            # Check that the instructions for the component are equal to the instructions in the original dataframe
            self.assertTrue(
                instructions_split[outfile_paths[single_split_components.index(comp)]].equals(
                    self.instructions_df[self.instructions_df['Sample ID'].isin(comp)]
                )
            )

    def test_split_without_csv_in_basefilepath(self):
        with NamedTemporaryFile() as temp_file:
            outfile_path = temp_file.name
            self.test_basic_split(outfile_path)

    def test_split_by_grouping_components_without_rest(self):
        outfile_path = 'test.csv'
        split_components = 'C1,C2 C3'
        self.test_basic_split(outfile_path, split_components)

    def test_split_by_grouping_components_with_single_rest(self):
        outfile_path = 'test.csv'
        split_components = 'C1 C3'
        self.test_basic_split(outfile_path, split_components)

    def test_split_by_grouping_components_with_multiple_rest(self):
        outfile_path = 'test.csv'
        split_components = 'C1'
        self.test_basic_split(outfile_path, split_components)

    def test_no_matching_component(self):
        outfile_path = 'test.csv'
        split_components = 'C1 FOO'
        self.test_basic_split(outfile_path, split_components)

    def test_empty_dataframe(self):
        outfile_path = 'test.csv'
        split_components = 'C1 C2 C3'
        instructions_df = DataFrame()
        instructions_split = split_instructions_by_components(instructions_df, outfile_path, split_components)
        # Check that no files were created
        self.assertEqual(len(instructions_split), 0)

    def test_empty_split_components(self):
        outfile_path = 'test.csv'
        split_components = ''
        self.test_basic_split(outfile_path, split_components)

    def test_malformed_split_components(self):
        outfile_path = 'test.csv'
        split_components = 'C1;C2 C3'
        self.test_basic_split(outfile_path, split_components)


class TestArgsParser(TestCase):

    def setUp(self):
        self.parser = build_args_parser(
            signature="",
            description=""
        )

    def test_valid_input(self):
        args = self.parser.parse_args(
            [
                '--source-plates', 'src_plate.csv',
                '--destination-plates', 'dest_plate.csv',
                '-of', 'output.csv',
                '-suv', '10',
                '-slv', '5',
                '-soc', 'C1,C2 C3',
                '-spt', 'ALL:384PP_AQ_GP3;C1:384PP_AQ_GP4'
            ]
        )
        self.assertEqual(args.source_plates, ['src_plate.csv'])
        self.assertEqual(args.destination_plates, ['dest_plate.csv'])
        self.assertEqual(args.output_file, 'output.csv')
        self.assertEqual(args.split_upper_vol, 10)
        self.assertEqual(args.split_lower_vol, 5)
        self.assertEqual(args.split_outfile_components, 'C1,C2 C3')
        self.assertEqual(args.src_plate_type, 'ALL:384PP_AQ_GP3;C1:384PP_AQ_GP4')

    def test_missing_input(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(
                [
                    '--source-plates', 'src_plate.csv',
                    '-of', 'output.csv',
                    '-suv', '10',
                    '-slv', '5',
                    '-soc', 'C1,C2 C3',
                    '-spt', 'ALL:384PP_AQ_GP3;C1:384PP_AQ_GP4'
                ]
            )
