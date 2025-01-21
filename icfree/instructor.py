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

def reorder_by_dispense_order(df, dispense_order):
    """
    Reorders the rows of a DataFrame based on the specified dispensing order.
    
    Args:
        df (DataFrame): The DataFrame to reorder.
        dispense_order (list): List of component names specifying the desired order.
    
    Returns:
        DataFrame: Reordered DataFrame.
    """
    if dispense_order:
        # Create a mapping of components to their order
        order_mapping = {component: i for i, component in enumerate(dispense_order)}
        default_order = len(dispense_order)  # Unspecified components go to the end
        df['Dispense Order'] = df['Sample ID'].map(lambda x: order_mapping.get(x, default_order))
        df = df.sort_values(by=['Dispense Order', 'Sample ID']).drop(columns=['Dispense Order'])
    return df

def main(source_plate_file, destination_plate_file, output_file, source_plate_type="default:384PP_AQ_GP3",
         max_transfer_volume=None, split_threshold=None, split_components=None, dispense_order=None):
    """
    Main function to read input files, generate ECHO instructions, and write the output to files.
    
    Parameters:
    - source_plate_file: Path to the source plate file.
    - destination_plate_file: Path to the destination plate file.
    - output_file: Path to the output instructions file.
    - source_plate_type: Comma-separated list of component and plate type pairs.
    - max_transfer_volume: Maximum volume for a single transfer. If not specified, no splitting will be performed.
    - split_threshold: Volume threshold above which transfers need to be split. If not specified, no splitting will be performed.
    - split_components: Comma-separated list of component names to create separate files for.
    - dispense_order: Comma-separated list of component names specifying dispensing order.
    """
    source_plate_types = parse_plate_types(source_plate_type)
    source_plate_df = pd.read_csv(source_plate_file)
    destination_plate_df = pd.read_csv(destination_plate_file)
    instructions_df = generate_echo_instructions(source_plate_df, destination_plate_df, source_plate_types,
                                                 max_transfer_volume, split_threshold)
    
    if dispense_order:
        dispense_order_list = dispense_order.split(',')
        instructions_df = reorder_by_dispense_order(instructions_df, dispense_order_list)
    
    if split_components:
        split_components_list = split_components.split(',')
        for component in split_components_list:
            component_df = instructions_df[instructions_df['Sample ID'] == component]
            component_output_file = f"{os.path.splitext(output_file)[0]}_{component}.csv"
            component_df.to_csv(component_output_file, index=False)
            print(f"Instructions for {component} saved to {component_output_file}")
        
        remaining_df = instructions_df[~instructions_df['Sample ID'].isin(split_components_list)]
        if not remaining_df.empty:
            remaining_df.to_csv(output_file, index=False)
            print(f"Remaining instructions saved to {output_file}")
    else:
        instructions_df.to_csv(output_file, index=False)
        print(f"Instructions saved to {output_file}")

if __name__ == "__main__":
    import sys
    parser = argparse.ArgumentParser(description="Generate ECHO liquid handler instructions.")
    parser.add_argument("source_plate_file", type=str, help="Path to the source plate file.")
    parser.add_argument("destination_plate_file", type=str, help="Path to the destination plate file.")
    parser.add_argument("output_file", type=str, help="Path to the output instructions file.")
    parser.add_argument("--source_plate_type", type=str, default="default:384PP_AQ_GP3",
                        help="Comma-separated list of component and plate type pairs, e.g., 'Component_1:384PP_AQ_CP,Component_2:384PP_AQ_GP3'. Default for all is 384PP_AQ_GP3.")
    parser.add_argument("--max_transfer_volume", type=int, help="Maximum volume for a single transfer. No splitting if not specified.")
    parser.add_argument("--split_threshold", type=int, help="Volume threshold for splitting transfers. No splitting if not specified.")
    parser.add_argument("--split_components", type=str, help="Comma-separated list of components for separate output files.")
    parser.add_argument("--dispense_order", type=str, help="Comma-separated list of components specifying dispensing order.")
    args = parser.parse_args()
    
    main(args.source_plate_file, args.destination_plate_file, args.output_file, args.source_plate_type,
         args.max_transfer_volume, args.split_threshold, args.split_components, args.dispense_order)
