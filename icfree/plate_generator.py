import argparse
import pandas as pd
import numpy as np
from pathlib import Path

def parse_args():
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Prepare source and destination well-plate mappings with advanced options.")
    # Required arguments
    parser.add_argument('sampling_file', type=str, help='Path to the sampling file')
    parser.add_argument('sample_volume', type=int, help='Wanted sample volume in the destination plate')
    # Optional arguments
    parser.add_argument('--start_well_src_plt', type=str, default='A1', help='Starting well for the source plate')
    parser.add_argument('--start_well_dst_plt', type=str, default='A1', help='Starting well for the destination plate')
    parser.add_argument('--plate_dims', type=str, default='16x24', help='Plate dimensions (Format: NxM)')
    parser.add_argument('--well_capacity', type=int, default=60000, help='Well capacity in nL')
    parser.add_argument('--dead_volumes', type=str, default='', help='Dead volumes for specific components in format component1=volume1,component2=volume2,...')
    parser.add_argument('--default_dead_volume', type=int, default=15000, help='Default dead volume in nL for the source plate')
    parser.add_argument('--num_replicates', type=int, default=1, help='Number of wanted replicates')
    parser.add_argument('--output_folder', type=str, default='.', help='Output folder for the result files')
    return parser.parse_args()

def generate_well_positions(start_well, plate_dims, num_positions):
    """
    Generate well positions in a plate given a starting well, plate dimensions, and the number of positions needed.
    
    Args:
        start_well (str): Starting well position (e.g., 'A1').
        plate_dims (str): Dimensions of the plate (e.g., '16x24').
        num_positions (int): Number of well positions to generate.
    
    Returns:
        list: List of well positions.
    """
    rows, cols = map(int, plate_dims.split('x'))
    start_row = ord(start_well[0].upper()) - ord('A')
    start_col = int(start_well[1:]) - 1
    
    positions = []
    for col in range(start_col, cols):
        for row in range(start_row, rows):
            if len(positions) < num_positions:
                positions.append(f"{chr(ord('A') + row)}{col + 1}")
            else:
                break
        if len(positions) >= num_positions:
            break
    return positions

def parse_dead_volumes(dead_volumes_str, default_dead_volume):
    """
    Parse the dead volumes string into a dictionary, with a fallback to the default dead volume.
    
    Args:
        dead_volumes_str (str): Dead volumes for specific components (format: component1=volume1,component2=volume2,...).
        default_dead_volume (int): Default dead volume to use if not specified in dead_volumes_str.
    
    Returns:
        tuple: Dictionary of dead volumes and the default dead volume.
    """
    dead_volumes = {}
    if dead_volumes_str:
        components_volumes = dead_volumes_str.split(',')
        for cv in components_volumes:
            component, volume = cv.split('=')
            dead_volumes[component] = int(volume)
    return dead_volumes, default_dead_volume

def prepare_destination_plate(sampling_data, start_well, plate_dims, sample_volume, num_replicates):
    """
    Prepare the destination plate data by replicating the sampling data and assigning well positions.
    
    Args:
        sampling_data (pd.DataFrame): DataFrame containing the sampling data.
        start_well (str): Starting well position for the destination plate.
        plate_dims (str): Dimensions of the plate (e.g., '16x24').
        sample_volume (int): Desired sample volume in each well of the destination plate.
        num_replicates (int): Number of replicates for each sample.
    
    Returns:
        pd.DataFrame: DataFrame with destination plate data, including well positions and water volumes.
    """
    # Replicate the sampling data according to the specified number of replicates
    replicated_data = pd.concat([sampling_data] * num_replicates, ignore_index=True)
    num_wells_needed = len(replicated_data)
    well_positions = generate_well_positions(start_well, plate_dims, num_wells_needed)
    
    # Insert the well positions and calculate the water volume needed to reach the desired sample volume
    replicated_data.insert(0, 'Well', well_positions)
    replicated_data['Water'] = sample_volume - replicated_data.drop('Well', axis=1).sum(axis=1)
    
    return replicated_data

def prepare_source_plate(destination_data, dead_volumes_str, default_dead_volume, well_capacity, start_well):
    """
    Prepare the source plate data by calculating the total volume needed for each component and assigning well positions.
    
    Args:
        destination_data (pd.DataFrame): DataFrame with destination plate data.
        dead_volumes_str (str): Dead volumes for specific components (format: component1=volume1,component2=volume2,...).
        default_dead_volume (int): Default dead volume to use if not specified in dead_volumes_str.
        well_capacity (int): Capacity of each well in nL.
        start_well (str): Starting well position for the source plate.
    
    Returns:
        pd.DataFrame: DataFrame with source plate data, including well positions and volumes for each component.
    """
    # Parse dead volumes
    dead_volumes, default_dead_volume = parse_dead_volumes(dead_volumes_str, default_dead_volume)
    
    # Calculate total volume needed for each component from the destination data
    component_totals = destination_data.drop(columns='Well').sum()

    # List to store source well allocations
    source_rows = []
    well_positions = generate_well_positions(start_well, '16x24', 1000)  # Generate ample well positions
    current_position = 0

    for component, total_volume in component_totals.items():
        dead_volume = dead_volumes.get(component, default_dead_volume)
        remaining_volume = total_volume

        while remaining_volume > 0:
            # Calculate effective capacity for the current well
            effective_capacity = well_capacity - dead_volume
            volume_this_well = min(remaining_volume, effective_capacity)
            actual_volume_in_well = volume_this_well + dead_volume
            source_rows.append({
                'Well': well_positions[current_position],
                'Component': component,
                'Volume': actual_volume_in_well
            })
            remaining_volume -= volume_this_well
            if remaining_volume > 0:
                current_position += 1

        current_position += 1

    # Convert source well allocations to a DataFrame and pivot for the desired format
    source_df = pd.DataFrame(source_rows)
    source_df_pivoted = source_df.pivot(index='Well', columns='Component', values='Volume').fillna(0)
    source_df_pivoted.reset_index(inplace=True)

    # Ensure 'Well' is the first column
    cols = ['Well'] + [col for col in source_df_pivoted.columns if col != 'Well']
    source_df_final = source_df_pivoted[cols]

    return source_df_final

def write_output_files(source_data, destination_data, output_folder):
    """
    Write the source and destination plate data to CSV files in the specified output folder.
    
    Args:
        source_data (pd.DataFrame): DataFrame with source plate data.
        destination_data (pd.DataFrame): DataFrame with destination plate data.
        output_folder (Path): Path to the output folder.
    """
    destination_path = output_folder / 'destination_plate.csv'
    source_path = output_folder / 'source_plate.csv'
    
    destination_data.to_csv(destination_path, index=False)
    source_data.to_csv(source_path, index=False)
    
    print(f"Destination plate data written to {destination_path}")
    print(f"Source plate data written to {source_path}")

def main():
    """
    Main function to prepare source and destination well-plate mappings and write the results to files.
    """
    args = parse_args()

    # Read the sampling data from the specified file
    sampling_data = pd.read_csv(args.sampling_file)
    
    # Prepare the destination plate data
    destination_data = prepare_destination_plate(sampling_data, args.start_well_dst_plt, args.plate_dims, args.sample_volume, args.num_replicates)
    
    # Prepare the source plate data
    source_data = prepare_source_plate(destination_data, args.dead_volumes, args.default_dead_volume, args.well_capacity, args.start_well_src_plt)
    
    # Write the output files to the specified output folder
    write_output_files(source_data, destination_data, Path(args.output_folder))

if __name__ == "__main__":
    main()
