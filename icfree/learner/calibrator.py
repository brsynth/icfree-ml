import pandas as pd
import argparse
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import os
import random

def calculate_yield(data: pd.DataFrame, jove_plus_line: int, jove_minus_line: int) -> pd.DataFrame:
    # Adjust the line numbers because of the header row (subtracting an additional 1 for zero-based indexing)
    jove_plus_index = jove_plus_line - 2
    jove_minus_index = jove_minus_line - 2

    # Get the autofluorescence and reference values based on user input
    autofluorescence = data.iloc[jove_minus_index].filter(like='Fluorescence').mean()
    reference = data.iloc[jove_plus_index].filter(like='Fluorescence').mean()
    
    # Create yield columns for each fluorescence value
    for col in data.columns:
        if 'Fluorescence' in col:
            yield_col = col.replace('Fluorescence', 'Yield')
            data[yield_col] = (data[col] - autofluorescence) / (reference - autofluorescence)
    
    return data

def add_calibrated_yield(data: pd.DataFrame, a: float, b: float) -> pd.DataFrame:
    # Add "Calibrated Yield" columns for each "Yield" column
    for col in data.columns:
        if 'Yield' in col and 'Calibrated' not in col:
            calibrated_yield_col = col.replace('Yield', 'Calibrated Yield')
            data[calibrated_yield_col] = a * data[col] + b
    
    return data

def fit_regression_with_outlier_removal(y: np.ndarray, y_ref: np.ndarray, r2_limit: float) -> tuple:
    max_outliers = int(0.3 * len(y))  # 30% of data points can be considered outliers
    current_r2 = 0
    num_outliers_removed = 0

    original_indices = np.arange(len(y))
    outlier_indices = []

    while current_r2 <= r2_limit and num_outliers_removed < max_outliers:
        # Add a constant term for OLS
        X = sm.add_constant(y)
        model = sm.OLS(y_ref, X).fit()
        current_r2 = model.rsquared

        # Calculate Cook's distance
        influence = model.get_influence()
        cooks_d = influence.cooks_distance[0]

        # Identify the index of the maximum Cook's distance
        max_cooks_index = np.argmax(cooks_d)

        # Record the original index of the outlier
        outlier_indices.append(original_indices[max_cooks_index])

        # Remove the outlier from the data
        y = np.delete(y, max_cooks_index)
        y_ref = np.delete(y_ref, max_cooks_index)
        original_indices = np.delete(original_indices, max_cooks_index)
        num_outliers_removed += 1

    # Fit the final model
    final_model = sm.OLS(y_ref, sm.add_constant(y)).fit()
    a, b = final_model.params[1], final_model.params[0]
    r2_value = final_model.rsquared

    return a, b, r2_value, outlier_indices

def select_control_points(data: pd.DataFrame, jove_plus_index: int, jove_minus_index: int, n: int) -> pd.DataFrame:
    # Find the index of the point with the highest yield
    max_yield_index = data.filter(like='Yield').mean(axis=1).idxmax()

    # Select Jove+, Jove-, and the point with the highest yield
    control_indices = {jove_plus_index, jove_minus_index, max_yield_index}

    # Select additional random points to reach n control points
    remaining_indices = list(set(data.index) - control_indices)
    random_indices = random.sample(remaining_indices, n - 3)
    control_indices.update(random_indices)

    # Return the DataFrame with the selected control points
    return data.loc[list(control_indices)]

def plot_calibrated_points(y: np.ndarray, y_ref: np.ndarray, outlier_indices: list, a: float, b: float, r2_value: float, output_file: str, input_filename: str, ref_filename: str):
    # Plot the calibrated points in blue and outliers in red
    plt.figure(figsize=(10, 6))
    plt.scatter(y, y_ref, color='blue', label='Calibrated Points')
    if outlier_indices:
        plt.scatter(y[outlier_indices], y_ref[outlier_indices], color='red', label='Removed Outliers')
    # Plot the regression line ax + b
    x_vals = np.array([min(y), max(y)])
    y_vals = a * x_vals + b
    plt.plot(x_vals, y_vals, color='green', label=f'Regression Line: y = {a:.2f}x + {b:.2f}, R² = {r2_value:.2f}')
    # Add axis labels with filenames
    plt.xlabel(f'Calibrated Yield ({os.path.basename(input_filename)})')
    plt.ylabel(f'Reference Yield ({os.path.basename(ref_filename)})')
    plt.title('Calibrated Points with Outliers Removed and Regression Line')
    plt.legend()
    plt.savefig(output_file, format='png')
    plt.close()

def detect_component_columns(data: pd.DataFrame) -> list:
    # Detect columns that appear before the first "Fluorescence" column
    component_columns = []
    for col in data.columns:
        if 'Fluorescence' in col:
            break
        component_columns.append(col)
    return component_columns

def find_matching_indices(input_data: pd.DataFrame, ref_data: pd.DataFrame, component_columns: list, rounding_precision: int = 2) -> tuple:
    # Round component values before matching
    input_combinations = input_data[component_columns].round(rounding_precision).apply(tuple, axis=1)
    ref_combinations = ref_data[component_columns].round(rounding_precision).apply(tuple, axis=1)

    # Convert reference combinations to a set for efficient matching
    ref_combinations_set = set(ref_combinations)

    # Find indices where the component combinations match
    matching_input_indices = []
    matching_ref_indices = []

    for i, combination in enumerate(input_combinations):
        if combination in ref_combinations_set:
            # Find the corresponding index in the reference data
            ref_index = ref_combinations[ref_combinations == combination].index[0]
            matching_input_indices.append(i)
            matching_ref_indices.append(ref_index)

    return matching_input_indices, matching_ref_indices

def compute_average_yields(modified_data: pd.DataFrame, ref_data: pd.DataFrame, matching_input_indices: list, matching_ref_indices: list) -> tuple:
    # Calculate the average yield for the matching component combinations
    avg_yield = modified_data.filter(like='Yield').iloc[matching_input_indices].mean(axis=1).values
    avg_yield_ref = ref_data.filter(like='Yield').iloc[matching_ref_indices].mean(axis=1).values
    return avg_yield, avg_yield_ref

def load_data(file_path: str) -> pd.DataFrame:
    # Load data based on file extension
    if file_path.endswith('.xlsx'):
        return pd.read_excel(file_path, sheet_name=0)  # Read the first sheet
    elif file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file format. Please provide a .csv or .xlsx file.")

def save_data(data: pd.DataFrame, output_file: str):
    # Save data based on file extension
    if output_file.endswith('.xlsx'):
        data.to_excel(output_file, index=False)
    elif output_file.endswith('.csv'):
        data.to_csv(output_file, index=False)
    else:
        raise ValueError("Unsupported file format. Please specify a .csv or .xlsx output file.")

def calculate_yields_if_missing(data: pd.DataFrame, jove_plus_line: int, jove_minus_line: int) -> pd.DataFrame:
    # Check if "Yield" columns are present
    if not any('Yield' in col for col in data.columns):
        print("Yield columns not found. Calculating yields...")
        data = calculate_yield(data, jove_plus_line, jove_minus_line)
    else:
        print("Yield columns already exist. Skipping yield calculation.")
    return data

def validate_reference_file(ref_data: pd.DataFrame):
    """Ensure the reference file has Yield columns."""
    if not any('Yield' in col for col in ref_data.columns):
        raise ValueError("Reference file must contain 'Yield' columns. Please ensure the reference file is properly formatted.")

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Calculate yield based on fluorescence data and optionally apply calibration.')
    parser.add_argument('file', type=str, help='Path to the input file (.csv or .xlsx)')
    parser.add_argument('ref_file', type=str, help='Path to the reference input file (.csv or .xlsx)')
    parser.add_argument('--jove_plus', type=int, required=True, help='Line number for Jove+ (1-based index)')
    parser.add_argument('--jove_minus', type=int, required=True, help='Line number for Jove- (1-based index)')
    parser.add_argument('--r2_limit', type=float, default=0.8, help='R-squared limit for the regression (default: 0.8)')
    parser.add_argument('--output', type=str, required=True, help='Output file name (.csv or .xlsx)')
    parser.add_argument('--plot', type=str, help='Output PNG file name for the plot of calibrated points')
    parser.add_argument('--num_control_points', type=int, default=5, help='Number of control points to select (default: 5)')

    args = parser.parse_args()

    # Load the data from the input and reference files
    input_data = load_data(args.file)
    ref_data = load_data(args.ref_file)

    # Validate that the reference file has "Yield" columns
    try:
        validate_reference_file(ref_data)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)

    # Calculate yields if missing in the input file
    input_data = calculate_yields_if_missing(input_data, args.jove_plus, args.jove_minus)

    # Detect component columns
    component_columns = detect_component_columns(input_data)

    # Find matching indices based on component combinations
    matching_input_indices, matching_ref_indices = find_matching_indices(input_data, ref_data, component_columns)

    # Compute average yields for matching component combinations
    avg_yield, avg_yield_ref = compute_average_yields(input_data, ref_data, matching_input_indices, matching_ref_indices)

    # Fit the regression with outlier removal on average yields
    a, b, r2_value, outlier_indices = fit_regression_with_outlier_removal(avg_yield, avg_yield_ref, args.r2_limit)

    # Display the regression coefficients and R² value in the terminal
    print(f"Regression Line: y = {a:.2f}x + {b:.2f}")
    print(f"R² Value: {r2_value:.2f}")

    # Add calibrated yield columns to the input data
    calibrated_data = add_calibrated_yield(input_data, a, b)

    # Save the calibrated data to the specified output file
    save_data(calibrated_data, args.output)
    print(f"Calibrated data saved as {args.output}")

    # Select control points
    jove_plus_index = args.jove_plus - 2
    jove_minus_index = args.jove_minus - 2
    control_data = select_control_points(calibrated_data, jove_plus_index, jove_minus_index, args.num_control_points)

    # Save the control points to a separate file
    control_points_filename = args.output.rsplit('.', 1)[0] + "_control_points." + args.output.rsplit('.', 1)[1]
    save_data(control_data, control_points_filename)
    print(f"Control points saved as {control_points_filename}")

    # Plot the calibrated points with outliers and regression line if requested
    if args.plot:
        plot_calibrated_points(avg_yield, avg_yield_ref, outlier_indices, a, b, r2_value, args.plot, args.file, args.ref_file)
        print(f"Plot saved as {args.plot}")
