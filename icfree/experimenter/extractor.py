import pandas as pd
import argparse

def find_n_m(sampling_file_path):
    """
    Find the number of unique combinations (n) and the number of replicates (m) from a sampling file.

    Parameters:
    sampling_file_path (str): Path to the sampling file (Excel, CSV, or TSV).

    Returns:
    tuple: A tuple containing the number of unique combinations (n) and the number of replicates (m).
    """
    # Load the sampling file
    df_sampling = pd.read_csv(sampling_file_path, sep='\t')
    
    # Drop the unnamed column if it exists
    if df_sampling.columns[0].startswith('Unnamed'):
        df_sampling = df_sampling.drop(columns=df_sampling.columns[0])
    
    # Identify unique combinations (n) and replicates (m)
    unique_combinations = df_sampling.drop_duplicates()
    n = unique_combinations.shape[0]
    m = df_sampling.shape[0] // n
    
    return n, m

def process_data(file_path, num_samples, num_replicates):
    """
    Process the initial data file to reshape the fluorescence data.

    Parameters:
    file_path (str): Path to the initial data file (Excel, CSV, or TSV).
    num_samples (int): Number of samples.
    num_replicates (int): Number of replicates.

    Returns:
    tuple: A tuple containing the reshaped DataFrame and the sheet name (if applicable).
    """
    # Determine the file extension
    file_extension = file_path.split('.')[-1].lower()
    
    # Load the data based on file extension
    if file_extension == 'xlsx':
        excel_data = pd.ExcelFile(file_path)
        sheet_name = excel_data.sheet_names[0]
        df = pd.read_excel(file_path, sheet_name=sheet_name)
    elif file_extension == 'csv':
        df = pd.read_csv(file_path)
        sheet_name = None
    elif file_extension == 'tsv':
        df = pd.read_csv(file_path, sep='\t')
        sheet_name = None
    else:
        raise ValueError("Unsupported file type. Please provide an Excel (.xlsx), CSV (.csv), or TSV (.tsv) file.")
    
    # Keep only the last row and remove the first two columns
    df_last_row = df.iloc[[-1]].drop(columns=df.columns[:2])
    
    # Keep only the required number of values
    total_values = num_samples * num_replicates
    values_to_keep = df_last_row.values.flatten()[:total_values]
    
    # Reshape the values into the specified number of columns and rows
    reshaped_values = values_to_keep.reshape((num_samples, num_replicates), order='F')
    
    # Create a new DataFrame with the reshaped values
    df_reshaped = pd.DataFrame(reshaped_values)
    
    # Add headers to the reshaped DataFrame
    headers = [f"Fluorescence Value {i+1}" for i in range(num_replicates)]
    df_reshaped.columns = headers
    
    # Add "Fluorescence Average" column
    df_reshaped["Fluorescence Average"] = df_reshaped.mean(axis=1)
    
    return df_reshaped, sheet_name

def load_sampling_file(file_path, num_samples):
    """
    Load the sampling file and take only the first num_samples lines.

    Parameters:
    file_path (str): Path to the sampling file (Excel, CSV, or TSV).
    num_samples (int): Number of samples to load.

    Returns:
    DataFrame: A DataFrame containing the first num_samples lines of the sampling file.
    """
    # Determine the file extension
    file_extension = file_path.split('.')[-1].lower()
    
    # Load the data based on file extension
    if file_extension == 'xlsx':
        df = pd.read_excel(file_path)
    elif file_extension == 'csv':
        df = pd.read_csv(file_path)
    elif file_extension == 'tsv':
        df = pd.read_csv(file_path, sep='\t')
    else:
        raise ValueError("Unsupported file type. Please provide an Excel (.xlsx), CSV (.csv), or TSV (.tsv) file.")
    
    # Take only the first num_samples lines
    df = df.head(num_samples)
    
    return df

def clean_sampling_file(df_sampling):
    """
    Clean the sampling file by removing the unnamed first column if it contains incrementing integers.

    Parameters:
    df_sampling (DataFrame): The sampling DataFrame to clean.

    Returns:
    DataFrame: The cleaned sampling DataFrame.
    """
    first_column = df_sampling.iloc[:, 0]
    if first_column.name.startswith('Unnamed') and pd.api.types.is_integer_dtype(first_column):
        if (first_column == range(len(first_column))).all():
            df_sampling = df_sampling.drop(columns=first_column.name)
    return df_sampling

def process(initial_data_file, output_file_path, sampling_file, num_samples=None, num_replicates=None, display=True):
    """
    Process the initial data file and sampling file to combine the data and save the output.

    Parameters:
    initial_data_file (str): Path to the initial data file (Excel, CSV, or TSV).
    output_file_path (str): Path for the output file.
    sampling_file (str): Path to the sampling file (Excel, CSV, or TSV).
    num_samples (int, optional): Number of samples. If not specified, it will be detected from the sampling file.
    num_replicates (int, optional): Number of replicates. If not specified, it will be detected from the sampling file.
    display (bool, optional): Whether to display the combined data. Default is True.

    Returns:
    DataFrame: The combined DataFrame.
    """
    if num_samples is None or num_replicates is None:
        n, m = find_n_m(sampling_file)
        num_samples = num_samples if num_samples is not None else n
        num_replicates = num_replicates if num_replicates is not None else m
    
    df_reshaped, sheet_name = process_data(initial_data_file, num_samples, num_replicates)
    
    df_sampling = load_sampling_file(sampling_file, num_samples)
    df_sampling_cleaned = clean_sampling_file(df_sampling)
    df_combined = pd.concat([df_sampling_cleaned, df_reshaped], axis=1)
    
    if display:
        print(df_combined)

    # Save the combined dataframe with headers and averages in the specified format
    if output_file_path.endswith('.xlsx'):
        df_combined.to_excel(output_file_path, index=False, sheet_name=sheet_name)
    elif output_file_path.endswith('.csv'):
        df_combined.to_csv(output_file_path, index=False)
    elif output_file_path.endswith('.tsv'):
        df_combined.to_csv(output_file_path, index=False, sep='\t')
    else:
        raise ValueError("Unsupported output file type. Please provide an Excel (.xlsx), CSV (.csv), or TSV (.tsv) file.")
    
    print(f"Processed data saved to {output_file_path}")
    return df_combined

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and reshape fluorescence data.")
    parser.add_argument("--initial_data_file", type=str, required=True, help="Path to the initial Excel, CSV, or TSV file.")
    parser.add_argument("--output_file", type=str, required=True, help="Path for the output file.")
    parser.add_argument("--sampling_file", type=str, required=True, help="Path to the sampling Excel, CSV, or TSV file.")
    parser.add_argument("--num_samples", type=int, help="Number of samples.")
    parser.add_argument("--num_replicates", type=int, help="Number of replicates.")
    parser.add_argument("--no_display", action="store_true", help="Do not display the result.")
    
    args = parser.parse_args()
    
    process(args.initial_data_file, args.output_file, args.sampling_file, args.num_samples, args.num_replicates, not args.no_display)
