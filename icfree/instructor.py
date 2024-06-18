import pandas as pd
import argparse
import os

def parse_plate_types(plate_types_str, default_type="384PP_AQ_GP3"):
    """
    Parses a string containing component-specific plate types into a dictionary.
    
    Args:
        plate_types_str (str): Input string with component and plate type pairs.
        default_type (str): Default plate type to use if no specific type is provided for a component.
    
    Returns:
        dict: Dictionary with component names as keys and plate types as values.
    """
    plate_types = {}
    if plate_types_str:
        entries = plate_types_str.split(',')
        for entry in entries:
            component, type = entry.split(':')
            plate_types[component.strip()] = type.strip()
    if "default" not in plate_types:
        plate_types["default"] = default_type
    return plate_types

def generate_echo_instructions(source_plate_df, destination_plate_df, source_plate_types,
                               max_transfer_volume=None, split_threshold=None):
    """
    Generates ECHO liquid handler instructions considering multiple source wells for each component.
    Allows each component to have a specified source plate type, or a default if not specified.
    
    Parameters:
    - source_plate_df: DataFrame containing source plate data.
    - destination_plate_df: DataFrame containing destination plate data.
    - source_plate_types: Dictionary specifying the source plate type per component or a default type.
    - max_transfer_volume: Maximum volume for a single transfer, if specified.
    - split_threshold: Volume threshold above which transfers need to be split, if specified.
    
    Returns:
    - DataFrame containing all transfer instructions, grouped by component.
    """
    instructions = []
    component_columns = [col for col in destination_plate_df.columns if col != 'Well']
    
    def split_volumes(source_well, dest_well, volume, component, plate_type):
        """
        Splits volumes greater than split_threshold into multiple instructions, each with a maximum of max_transfer_volume.
        """
        if max_transfer_volume is not None and split_threshold is not None:
            while volume > split_threshold:
                instructions.append({
                    "Source Plate Name": "Source[1]",
                    "Source Plate Type": plate_type,
                    "Source Well": source_well,
                    "Destination Plate Name": "Destination[1]",
                    "Destination Well": dest_well,
                    "Transfer Volume": min(volume, max_transfer_volume),
                    "Sample ID": component
                })
                volume -= max_transfer_volume
        if volume > 0:
            instructions.append({
                "Source Plate Name": "Source[1]",
                "Source Plate Type": plate_type,
                "Source Well": source_well,
                "Destination Plate Name": "Destination[1]",
                "Destination Well": dest_well,
                "Transfer Volume": volume,
                "Sample ID": component
            })

    for _, dest_row in destination_plate_df.iterrows():
        for component in component_columns:
            volume = dest_row[component]
            if volume > 0:
                source_rows = source_plate_df[source_plate_df[component] > 0]
                source_wells = "{%s}" % ";".join(source_rows["Well"]) if len(source_rows) > 1 else source_rows["Well"].iloc[0]
                plate_type = source_plate_types.get(component, source_plate_types.get("default"))
                if max_transfer_volume is not None and split_threshold is not None and volume > split_threshold:
                    split_volumes(source_wells, dest_row["Well"], volume, component, plate_type)
                else:
                    instructions.append({
                        "Source Plate Name": "Source[1]",
                        "Source Plate Type": plate_type,
                        "Source Well": source_wells,
                        "Destination Plate Name": "Destination[1]",
                        "Destination Well": dest_row["Well"],
                        "Transfer Volume": volume,
                        "Sample ID": component
                    })

    instructions_df = pd.DataFrame(instructions)
    return instructions_df.groupby('Sample ID', as_index=False).apply(lambda x: x)

def main():
    """
    Main function to parse arguments, read input files, generate ECHO instructions, and write the output to files.
    """
    parser = argparse.ArgumentParser(description="Generate ECHO liquid handler instructions.")
    parser.add_argument("source_plate_file", type=str, help="Path to the source plate file.")
    parser.add_argument("destination_plate_file", type=str, help="Path to the destination plate file.")
    parser.add_argument("output_file", type=str, help="Path to the output instructions file.")
    parser.add_argument("--source_plate_type", type=str, default="default:384PP_AQ_GP3",
                        help="Comma-separated list of component and plate type pairs, e.g., 'Component_1:384PP_AQ_CP,Component_2:384PP_AQ_GP3'. Default for all is 384PP_AQ_GP3.")
    parser.add_argument("--max_transfer_volume", type=int, help="Maximum volume for a single transfer. If not specified, no splitting will be performed.")
    parser.add_argument("--split_threshold", type=int, help="Volume threshold above which transfers need to be split. If not specified, no splitting will be performed.")
    parser.add_argument("--split_components", type=str, help="Comma-separated list of component names to create separate files for.")
    
    args = parser.parse_args()
    
    # Parse the source plate types from the string argument
    source_plate_types = parse_plate_types(args.source_plate_type)
    
    # Read the source and destination plate data from CSV files
    source_plate_df = pd.read_csv(args.source_plate_file)
    destination_plate_df = pd.read_csv(args.destination_plate_file)
    
    # Generate the ECHO instructions
    instructions_df = generate_echo_instructions(source_plate_df, destination_plate_df, source_plate_types,
                                                 args.max_transfer_volume, args.split_threshold)
    
    # Handle splitting of components into separate files if specified
    if args.split_components:
        split_components = args.split_components.split(',')
        for component in split_components:
            component_df = instructions_df[instructions_df['Sample ID'] == component]
            output_file = f"{os.path.splitext(args.output_file)[0]}_{component}.csv"
            component_df.to_csv(output_file, index=False)
            print(f"Instructions for {component} have been generated and saved to {output_file}")
        
        # Write remaining components to the original output file
        remaining_df = instructions_df[~instructions_df['Sample ID'].isin(split_components)]
        if not remaining_df.empty:
            remaining_df.to_csv(args.output_file, index=False)
            print(f"Instructions for remaining components have been generated and saved to {args.output_file}")
    else:
        # Write all instructions to the original output file
        instructions_df.to_csv(args.output_file, index=False)
        print(f"Instructions have been generated and saved to {args.output_file}")

if __name__ == "__main__":
    main()
