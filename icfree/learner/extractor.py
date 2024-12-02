import pandas as pd
import argparse

def find_n_m_from_sampling(df_sampling):
    """
    Find the number of unique combinations (n) and determine if there are repetitions in the sampling file.

    Parameters:
    df_sampling (DataFrame): The sampling DataFrame.

    Returns:
    tuple: Number of unique combinations (n) and a boolean indicating if repetitions exist.
    """
    # Drop the unnamed column if it exists
    if df_sampling.columns[0].startswith('Unnamed'):
        df_sampling = df_sampling.drop(columns=df_sampling.columns[0])
    
    unique_combinations = df_sampling.drop_duplicates()
    n = unique_combinations.shape[0]
    has_repetitions = df_sampling.shape[0] > n
    
    return n, has_repetitions

def infer_replicates(df_initial, df_sampling, num_samples):
    """
    Infer the number of replicates from the initial data file and sampling file.

    Parameters:
    df_initial (DataFrame): The initial data DataFrame.
    df_sampling (DataFrame): The sampling DataFrame.
    num_samples (int): Number of unique combinations (n).

    Returns:
    int: Inferred number of replicates.
    """
    # Remove the first two columns from the initial data
    df_initial = df_initial.iloc[:, 2:]
    
    # Infer replicates based on the number of columns
    total_columns = df_initial.shape[1]
    
    # Check for repetitions in the sampling file
    _, has_repetitions = find_n_m_from_sampling(df_sampling)
    
    if has_repetitions:
        num_replicates = total_columns // num_samples
    else:
        # Assume control wells if extra columns exist
        num_replicates = total_columns // num_samples
    
    return num_replicates

def process_data(df_initial, num_samples, num_replicates):
    """
    Process the initial data file to reshape the fluorescence data.

    Parameters:
    df_initial (DataFrame): The initial data DataFrame.
    num_samples (int): Number of samples.
    num_replicates (int): Number of replicates.

    Returns:
    DataFrame: The reshaped DataFrame.
    """
    # Remove the first two columns
    df_initial = df_initial.iloc[:, 2:]
    
    # Reshape data based on num_samples and num_replicates
    total_values = num_samples * num_replicates
    values_to_keep = df_initial.values.flatten()[:total_values]
    reshaped_values = values_to_keep.reshape((num_samples, num_replicates), order='F')
    
    # Create reshaped DataFrame
    df_reshaped = pd.DataFrame(reshaped_values)
    df_reshaped.columns = [f"Fluorescence Value {i+1}" for i in range(num_replicates)]
    df_reshaped["Fluorescence Average"] = df_reshaped.mean(axis=1)
    
    return df_reshaped

def process(initial_data_file, output_file_path, sampling_file, num_samples=None, num_replicates=None, display=True):
    """
    Process the initial data file and sampling file to combine the data and save the output.

    Parameters:
    initial_data_file (str): Path to the initial data file (Excel, CSV, or TSV).
    output_file_path (str): Path for the output file.
    sampling_file (str): Path to the sampling file (Excel, CSV, or TSV).
    num_samples (int, optional): Number of samples. If not specified, inferred from sampling file.
    num_replicates (int, optional): Number of replicates. If not specified, inferred from initial data file.
    display (bool, optional): Whether to display the combined data. Default is True.

    Returns:
    DataFrame: The combined DataFrame.
    """
    # Load files once
    file_extension = initial_data_file.split('.')[-1].lower()
    if file_extension == 'xlsx':
        df_initial = pd.read_excel(initial_data_file)
    elif file_extension == 'csv':
        df_initial = pd.read_csv(initial_data_file)
    elif file_extension == 'tsv':
        df_initial = pd.read_csv(initial_data_file, sep='\t')
    else:
        raise ValueError("Unsupported file type. Please provide an Excel (.xlsx), CSV (.csv), or TSV (.tsv) file.")
    
    sampling_extension = sampling_file.split('.')[-1].lower()
    if sampling_extension == 'xlsx':
        df_sampling = pd.read_excel(sampling_file)
    elif sampling_extension == 'csv':
        df_sampling = pd.read_csv(sampling_file)
    elif sampling_extension == 'tsv':
        df_sampling = pd.read_csv(sampling_file, sep='\t')
    else:
        raise ValueError("Unsupported file type. Please provide an Excel (.xlsx), CSV (.csv), or TSV (.tsv) file.")
    
    # Infer num_samples and num_replicates if not provided
    if num_samples is None or num_replicates is None:
        n, _ = find_n_m_from_sampling(df_sampling)
        num_samples = num_samples if num_samples is not None else n
        num_replicates = num_replicates if num_replicates is not None else infer_replicates(df_initial, df_sampling, num_samples)
    
    # Process data
    df_reshaped = process_data(df_initial, num_samples, num_replicates)
    
    # Combine sampling file and reshaped data
    df_sampling = df_sampling.head(num_samples)
    df_combined = pd.concat([df_sampling, df_reshaped], axis=1)
    
    if display:
        print(df_combined)

    # Save output
    if output_file_path.endswith('.xlsx'):
        df_combined.to_excel(output_file_path, index=False, sheet_name="Sheet1")
    elif output_file_path.endswith('.csv'):
        df_combined.to_csv(output_file_path, index=False)
    elif output_file_path.endswith('.tsv'):
        df_combined.to_csv(output_file_path, index=False, sep='\t')
    else:
        raise ValueError("Unsupported output file type. Please provide an Excel (.xlsx), CSV (.csv), or TSV (.tsv) file.")
    
    print(f"Processed data saved to {output_file_path}")
    return df_combined

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process fluorescence data.")
    parser.add_argument("--initial_data_file", type=str, required=True, help="Path to the initial data file.")
    parser.add_argument("--output_file", type=str, required=True, help="Path for the output file.")
    parser.add_argument("--sampling_file", type=str, required=True, help="Path to the sampling file.")
    parser.add_argument("--num_samples", type=int, help="Number of samples (overrides detection).")
    parser.add_argument("--num_replicates", type=int, help="Number of replicates (overrides detection).")
    parser.add_argument("--no_display", action="store_true", help="Suppress displaying the combined data.")
    args = parser.parse_args()

    process(args.initial_data_file, args.output_file, args.sampling_file, args.num_samples, args.num_replicates, not args.no_display)
