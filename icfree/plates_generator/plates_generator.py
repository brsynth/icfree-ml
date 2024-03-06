from pandas import (
    concat as pd_concat,
    DataFrame
)
from math import ceil
from re import match as re_match

from .args import DEFAULT_ARGS


def well_label_generator(dimensions):
    """
    Generate well labels for a plate based on the given dimensions.

    Args:
        dimensions (str):
            The dimensions of the plate in the format 'rowsxcols'.

    Returns:
        list: A list of well labels.

    Example:
        >>> well_label_generator('4x6')
        ['A1', 'A2', 'A3', 'A4', 'A5', 'A6',
        'B1', 'B2', 'B3', 'B4', 'B5', 'B6',
        'C1', 'C2', 'C3', 'C4', 'C5', 'C6',
        'D1', 'D2', 'D3', 'D4', 'D5', 'D6']
    """
    nb_rows, nb_cols = map(int, dimensions.split('x'))
    single_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    double_letters = [
        f"{a}{b}"
        for a in single_letters
        for b in single_letters
    ]
    # Correctly extend the list without attempting to concatenate directly
    all_labels = list(single_letters) + double_letters

    # Determine row labels based on the number of rows needed
    row_labels = all_labels[:nb_rows]

    # Generate well labels
    well_labels = [
        f"{row}{col}"
        for col in range(1, nb_cols + 1)
        for row in row_labels
    ]
    return well_labels


def gen_dst_plt(
    sampling_df: list,
    sample_volume: float,
    well_capacity: float = DEFAULT_ARGS['DST_PLT_WELL_CAPACITY'],
    dimensions: str = DEFAULT_ARGS['DST_PLT_DIM'],
    starting_well: str = DEFAULT_ARGS['DST_PLT_START_WELL'],
    nplicates: int = DEFAULT_ARGS['NPLICATES']
) -> list:
    """
    Generates a list of dataframes, each representing a destination plate
    with well assignments and water volumes to reach a specified
    sample volume, based on plate dimensions given as "nb_rows x nb_cols",
    starting from a specified well, and considering the number of replicates
    for each sample. Distributes samples across multiple plates if needed.

    Args:
    - sampling_df (pd.DataFrame): The input dataframe with sample components.
    - sample_volume (float): The target sample volume for each well.
    - well_capacity (float): The maximum capacity for each well.
    - dimensions (str): The dimensions of the plate (e.g., "8 x 12").
    - starting_well (str): The well label from which
                           to start filling (e.g., "B3").
    - nplicates (int): The number of replicates for each sample.

    Returns:
    - List[pd.DataFrame]: A list of dataframes,
                          each representing a destination plate.
    """
    # Check if sample volume is not greater than well capacity
    if sample_volume > well_capacity:
        raise ValueError(
            "The sample volume cannot be greater than the well capacity."
        )

    well_labels = well_label_generator(dimensions)
    if starting_well not in well_labels:
        raise ValueError(
            "The starting well is not valid for the given plate dimensions."
        )
    nb_rows, nb_cols = map(int, dimensions.split('x'))
    plate_size = nb_rows * nb_cols
    total_samples_needed = len(sampling_df) * nplicates

    # Calculate the total component volume and
    # the water volume needed for each sample
    sampling_df['Total_Volume'] = sampling_df.sum(axis=1)
    sampling_df['Water'] = sample_volume - sampling_df['Total_Volume']

    # Prepare the expanded sampling dataframe for replicates
    if nplicates > 0:
        sampling_df_expanded = \
            pd_concat([sampling_df]*nplicates).reset_index(drop=True)

    # List to store destination plates
    dest_plates = []

    while total_samples_needed > 0:
        current_plate_df = sampling_df_expanded.head(plate_size).copy()
        current_plate_df['Final_Volume'] = \
            current_plate_df['Total_Volume'] + current_plate_df['Water']

        # Ensure no negative water volumes
        if any(current_plate_df['Water'] < 0):
            raise ValueError(
                "Some samples require more volume"
                "than the target sample volume."
            )

        # Assign well labels for the current plate
        num_samples_current_plate = min(total_samples_needed, plate_size)
        start_index = \
            well_labels.index(starting_well) if dest_plates == [] else 0
        adjusted_well_labels = \
            well_labels[start_index:] + well_labels[:start_index]
        current_plate_df['Well'] = \
            adjusted_well_labels[:num_samples_current_plate]

        # Reorder columns for the current plate
        cols = ['Well'] + [
            col for col in
            current_plate_df.columns
            if col not in ['Well', 'Water', 'Total_Volume', 'Final_Volume']
        ] + ['Water']
        dest_plates.append(current_plate_df[cols])

        # Update counters and dataframe for remaining samples
        total_samples_needed -= num_samples_current_plate
        sampling_df_expanded = \
            sampling_df_expanded.iloc[num_samples_current_plate:].reset_index(
                drop=True
            )

    return dest_plates


def gen_src_plt(
    dest_plates: list,
    well_capacity: float = DEFAULT_ARGS['SRC_PLT_WELL_CAPACITY'],
    dimensions: str = DEFAULT_ARGS['SRC_PLT_DIM'],
    starting_well: str = DEFAULT_ARGS['SRC_PLT_START_WELL'],
    new_col: str = DEFAULT_ARGS['NEW_COL_COMP'],
    dead_volume: str = DEFAULT_ARGS['SRC_PLT_DEAD_VOLUME']
) -> list:
    """
    Generate source plates based on the destination plates and
    other parameters.

    Args:
        dest_plates (list): List of destination plates.
        well_capacity (float): Capacity of each well in the source plates.
        dimensions (str): Dimensions of the source plates in
                          the format 'rows x columns'.
        starting_well (str): Label of the starting well in the source plates.
        new_col (list): List of components that should be placed
                        in a new column.
        dead_volume (float): Dead volume to be added to each well.

    Returns:
        list: List of source plates, where each plate
              is represented as a DataFrame.

    """
    if well_capacity < 0:
        raise ValueError("The well capacity cannot be negative.")
    if dead_volume < 0:
        raise ValueError("The dead volume cannot be negative.")
    # Adjust effective well capacity to account for dead volume
    effective_well_capacity = well_capacity - dead_volume
    if effective_well_capacity < 0:
        raise ValueError(
            "The well capacity must be greater than the dead volume."
        )

    # Aggregate component volumes across all destination plates
    component_volumes = {}
    for plate in dest_plates:
        # Include all components, assuming last column is 'Water'
        for component in plate.columns[1:]:
            component_volumes[component] = \
                component_volumes.get(component, 0) + plate[component].sum()

    # Generate well labels and find the starting index
    well_labels = well_label_generator(dimensions)
    start_index = well_labels.index(starting_well)

    # Initialize source plates data structure
    nb_rows, nb_cols = map(int, dimensions.split('x'))
    plate_capacity = nb_rows * nb_cols
    source_plates = [
        DataFrame(0, index=well_labels, columns=component_volumes.keys())
    ]
    # Offset to move to new column for components in new_col
    well_column_offset = 0

    # Allocate wells to components starting from the starting_well
    current_well_index = start_index
    for component, volume in component_volumes.items():
        wells_needed = ceil(volume / effective_well_capacity)

        if component in new_col:
            # Move to new column if the component is in new_col
            current_well_index += nb_rows - (current_well_index % nb_rows)

        for _ in range(wells_needed):
            # If last plate is full, add a new plate
            if current_well_index == len(well_labels):
                # Add a new plate
                source_plates.append(
                    DataFrame(
                        0,
                        index=well_labels,
                        columns=component_volumes.keys()
                    )
                )
                # Reset to the beginning
                current_well_index = 0

            well_position = \
                (current_well_index + well_column_offset) % plate_capacity
            well_label = well_labels[well_position]
            actual_volume = min(volume, effective_well_capacity)
            source_plates[-1].at[well_label, component] = \
                actual_volume + dead_volume  # Add dead volume
            volume -= actual_volume
            current_well_index += 1

    # Remove rows contain only 0s
    for i in range(len(source_plates)):
        plate = source_plates[i]
        source_plates[i] = plate[(plate.T != 0).any()]
        # Convert index in 'Well' column
        source_plates[i].reset_index(inplace=True)
        source_plates[i] = source_plates[i].rename(columns={'index': 'Well'})

    return source_plates


def extract_literal_numeric(s):
    """
    Extracts the first literal part and the first numeric part
    from a given string, e.g. 'A123' -> ('A', '123').
    All remaining parts, are ignored, e.g. 'xYA123B456' -> ('xYA', '123').

    Args:
        s (str): The input string to extract from.

    Returns:
        tuple: A tuple containing the literal part and numeric part extracted
               from the input string.
               If the pattern is not found, returns (None, None).
    """
    # Pattern to match the literal part (letters) and the numeric part (digits)
    pattern = r'([A-Za-z]+)(\d+)'

    # Search for the pattern in the input string
    match = re_match(pattern, s)

    if match:
        # Extract the literal and numeric parts
        literal_part = match.group(1)
        numeric_part = match.group(2)
        return literal_part, numeric_part
    else:
        return None, None


def set_grid_for_display(plate, dimensions):
    """
    Returns a DataFrame with 'X' in the wells where the plate has non-0 values.

    Args:
        plate (DataFrame):
            The plate data containing well information.
        dimensions (tuple):
            The dimensions of the plate (number of rows, number of columns).

    Returns:
        None

    """
    well_labels = well_label_generator(dimensions)
    # Extract with regex numeric and literal parts from well labels
    rows = set()
    cols = set()
    for well in well_labels:
        row, col = extract_literal_numeric(well)
        rows.add(row)
        cols.add(col)
    rows = sorted(rows)
    cols = list(map(str, sorted([int(x) for x in cols])))

    # Extract number of rows and columns from dimensions
    grid = DataFrame('', columns=cols, index=rows)
    # For each non-0 value in the plate, write an 'X' in the corresponding well
    for _, row in plate.iterrows():
        well = row['Well']
        row, col = extract_literal_numeric(well)
        grid.at[row, col] = 'X'

    return grid
