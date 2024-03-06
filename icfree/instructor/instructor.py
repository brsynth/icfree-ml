import pandas as pd
from typing import List
from logging import (
    Logger,
    getLogger
)

from .args import DEFAULT_ARGS


def parse_src_plate_type_option(
    src_plate_type_option: str = DEFAULT_ARGS['SRC_PLATE_TYPE'],
    logger: Logger = getLogger(__name__)
) -> dict:
    """
    Parses the source plate type option and returns a dictionary of
    component-to-plate-type mappings.

    Args:
        src_plate_type_option (str): The source plate type option string in the
        format "component_list:plate_type;component_list:plate_type;...".
        logger (Logger): The logger object for logging messages.

    Returns:
        dict: A dictionary mapping each component to
        its corresponding plate type.

    Example:
        >>> parse_src_plate_type_option("ALL:384PP_AQ_GP3;A,B,C:384PP_AQ_GP4")
        {'ALL': '384PP_AQ_GP3', 'A': '384PP_AQ_GP4', 'B': '384PP_AQ_GP4',
        'C': '384PP_AQ_GP4'}
    """
    default_plate_type = "384PP_AQ_GP3"  # Default source plate type
    plate_types = {"ALL": default_plate_type}  # Initialize with default

    if src_plate_type_option:
        for spec in src_plate_type_option.split(';'):
            comp_list, plate_type = spec.split(':')
            if comp_list == "ALL":
                # Set default plate type for all components
                plate_types["ALL"] = plate_type
            else:
                for comp in comp_list.split(','):
                    # Set plate type for specific component
                    plate_types[comp] = plate_type
    return plate_types


def get_plate_index(
    component: str,
    plate_dfs: list,
    logger: Logger = getLogger(__name__)
) -> int:
    """
    Get the plate index for the given component
    from the list of plate dataframes.

    Args:
        component (str): The component name.
        plate_dfs (list): A list of plate dataframes.
        logger (Logger):
            The logger object for logging messages.
            Defaults to getLogger(__name__).

    Returns:
        int: The plate index for the given component.
    """
    for i in range(len(plate_dfs)):
        if component in plate_dfs[i].columns:
            return i
    logger.warning(
        f"Component '{component}' not found in any plate dataframe."
    )
    return -1


def generate_instructions_list(
    source_dfs: list,
    destination_dfs: list,
    plate_types: dict,
    split_upper_vol: int = DEFAULT_ARGS['SPLIT_UPPER_VOL'],
    split_lower_vol: int = DEFAULT_ARGS['SPLIT_LOWER_VOL'],
    logger: Logger = getLogger(__name__)
) -> list:
    """
    Generate instructions for transferring components from source_dfs to
    destination_dfs.

    Args:
        source_dfs (list): A list of source dataframes containing
        the components and well information.
        destination_dfs (list): A list of destination dataframes containing the
        well information.
        plate_types (dict): A dictionary mapping components to their respective
        plate types.
        split_upper_vol (int, optional): The upper volume limit for splitting
        instructions. Defaults to np.iinfo(np.int32).max.
        split_lower_vol (int, optional): The lower volume limit for splitting
        instructions. Defaults to 0.
        logger (Logger):
            The logger object for logging messages.
            Defaults to getLogger(__name__).

    Returns:
        list: A list of instructions for transferring components.
    """
    instructions = []
    unique_components = set()

    # Get unique components from all source and destination dataframes
    for source_df in source_dfs:
        unique_components.update(set(source_df.columns[1:]))
    for destination_df in destination_dfs:
        unique_components.update(set(destination_df.columns[1:]))

    for component in unique_components:
        # Get the source plate type for the current component
        source_plate_type = plate_types.get(component, plate_types["ALL"])

        # Get the source wells where the component is present
        # from all source dataframes
        source_wells = []
        for df in source_dfs:
            if component in df.columns:
                source_wells.extend(df[df[component] > 0]['Well'])

        # Skip if no source wells are found
        if not source_wells:
            continue

        source_wells_str = (
            "{" + ";".join(source_wells) + "}"
            if len(source_wells) > 1 else source_wells[0]
        )

        # Get the destination wells where the component needs to be transferred
        # from all destination dataframes
        dest_wells = []
        for df in destination_dfs:
            if component in df.columns:
                dest_wells.extend(
                    df[df[component] > 0][['Well', component]].iterrows()
                )

        src_plt_i = get_plate_index(component, source_dfs) + 1
        dst_plt_i = get_plate_index(component, destination_dfs) + 1
        # Iterate over each destination well and create transfer instructions
        for _, dest_row in dest_wells:

            transfer_volume = dest_row[component]

            if transfer_volume > split_upper_vol:
                full_splits = int(transfer_volume // split_upper_vol)
                remaining_volume = transfer_volume % split_upper_vol

                for _ in range(full_splits):
                    instructions.append({
                        'Source Plate Name': f'Source[{src_plt_i}]',
                        'Source Plate Type': source_plate_type,
                        'Source Well': source_wells_str,
                        'Destination Plate Name': f'Destination[{dst_plt_i}]',
                        'Destination Well': dest_row['Well'],
                        'Transfer Volume': split_upper_vol,
                        'Sample ID': component
                    })
                if remaining_volume > split_lower_vol:
                    instructions.append({
                        'Source Plate Name': f'Source[{src_plt_i}]',
                        'Source Plate Type': source_plate_type,
                        'Source Well': source_wells_str,
                        'Destination Plate Name': f'Destination[{dst_plt_i}]',
                        'Destination Well': dest_row['Well'],
                        'Transfer Volume': remaining_volume,
                        'Sample ID': component
                    })
                else:
                    # Integrate remaining volume into penultimate instruction
                    instructions[-1]['Transfer Volume'] += remaining_volume
            else:
                instructions.append({
                    'Source Plate Name': f'Source[{src_plt_i}]',
                    'Source Plate Type': source_plate_type,
                    'Source Well': source_wells_str,
                    'Destination Plate Name': f'Destination[{dst_plt_i}]',
                    'Destination Well': dest_row['Well'],
                    'Transfer Volume': transfer_volume,
                    'Sample ID': component
                })

    return instructions


def split_instructions_by_components(
    instructions_df: pd.DataFrame,
    base_output_file_path: str,
    split_components: str,
    logger: Logger = getLogger(__name__)
) -> dict:
    """
    Splits the instructions DataFrame into multiple CSV files based on the
    given component groups.

    Args:
        instructions_df (pandas.DataFrame): The DataFrame containing the
        instructions.
        base_output_file_path (str): The base path for the output
        CSV files.
        split_components (str): A string representing the component groups
        to split the instructions by. Each group should be separated by a
        comma, and multiple groups should be separated by a space.
        logger (Logger):
        The logger object for logging messages (default: getLogger(__name__))

    Returns:
        dict:
            A dictionary of output file paths and corresponding
            instructions DataFrames.
    """

    if instructions_df.empty:
        return {}

    # Split the component groups into a list of lists
    split_components = [comp.split(',') for comp in split_components.split()]
    processed_components = set()  # Set to keep track of processed components
    instructions = {}

    for _, component_group in enumerate(split_components):
        # Create a mask to select instructions for the current component group
        mask = instructions_df['Sample ID'].isin(component_group)
        # Select the instructions for the current component group
        selected_instructions = instructions_df[mask]
        # Concatenate component names for the file name
        components_name = "_".join(component_group)
        # Generate the output file path
        if base_output_file_path.endswith('.csv'):
            output_file_path = base_output_file_path.replace(
                '.csv', f'_split_{components_name}.csv'
            )
        else:
            output_file_path = \
                base_output_file_path + f'_split_{components_name}.csv'
        instructions[output_file_path] = selected_instructions
        # # Save the selected instructions to a CSV file
        # selected_instructions.to_csv(output_file_path, index=False)
        # # Log the generated file path
        # logger.info(f"Generated: {output_file_path}")
        # Add the processed components to the set
        processed_components.update(component_group)

    # Select the remaining instructions
    remaining_instructions = instructions_df[
        ~instructions_df['Sample ID'].isin(processed_components)
    ]
    # Generate the output file path for the remaining instructions
    if base_output_file_path.endswith('.csv'):
        remaining_file_path = base_output_file_path.replace(
            '.csv', '_split_rest.csv'
        )
    else:
        remaining_file_path = base_output_file_path + '_split_rest.csv'
    instructions[remaining_file_path] = remaining_instructions
    # # Save the remaining instructions to a CSV file
    # remaining_instructions.to_csv(remaining_file_path, index=False)
    # # Log the generated file path for the remaining instructions
    # logger.info(f"Generated: {remaining_file_path}")

    return instructions


def generate_instructions(
    source_plate_paths: List[str],
    destination_plate_paths: List[str],
    split_upper_vol: int = DEFAULT_ARGS['SPLIT_UPPER_VOL'],
    split_lower_vol: int = DEFAULT_ARGS['SPLIT_LOWER_VOL'],
    src_plate_type: str = None,
    logger: Logger = getLogger(__name__)
) -> pd.DataFrame:
    """
    Generate instructions based on the source and destination plate
    data.

    Parameters:
    source_plate_paths (List[str]):
        List of file paths of the source plate data.
    destination_plate_paths (List[str]):
        List of file paths of the destination plate data.
    split_upper_vol (int, optional):
        The upper volume limit for splitting
        instructions. Defaults to np.iinfo(np.int32).max.
    split_lower_vol (int, optional):
        The lower volume limit for splitting
        instructions. Defaults to 0.
    src_plate_type (str, optional):
        The plate type option for parsing the source plate data.
        Defaults to None.
    logger (Logger, optional):
        The logger object. Defaults to getLogger(__name__).

    Returns:
    pd.DataFrame: The final instructions DataFrame.
    """
    # Initialize an empty list to store the source dataframes
    source_dfs = []

    # Initialize an empty list to store the destination dataframes
    destination_dfs = []

    # Read the source plate data from the specified file paths
    for source_plate_path in source_plate_paths:
        source_df = pd.read_csv(source_plate_path)
        source_dfs.append(source_df)

    # Read the destination plate data from the specified file paths
    for destination_plate_path in destination_plate_paths:
        destination_df = pd.read_csv(destination_plate_path)
        destination_dfs.append(destination_df)

    # Parse the source plate type option to obtain the plate types
    plate_types = parse_src_plate_type_option(src_plate_type, logger)

    # Generate the instructions based on the source and destination plate data
    # and plate types
    instructions_final = generate_instructions_list(
        source_dfs, destination_dfs,
        plate_types, split_upper_vol, split_lower_vol, logger
    )

    # Convert the instructions to a DataFrame
    return pd.DataFrame(instructions_final)
