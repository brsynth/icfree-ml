import argparse
import pandas as pd
import numpy as np
import random
from pyDOE2 import lhs
import ast

def generate_lhs_samples(input_file, num_samples, step=None, ratios=None, fixed_values=None, seed=None):
    """
    Generates Latin Hypercube Samples for components based on discrete ranges.
    
    Parameters:
    - input_file: Path to the input file containing components and their max values.
    - num_samples: Number of samples to generate.
    - step: Step size for creating discrete ranges.
    - ratios: List of ratios for creating discrete ranges.
    - fixed_values: Dictionary of components with fixed values (optional).
    - seed: Random seed for reproducibility.
    
    Returns:
    - DataFrame containing the generated samples.
    """
    # Set the random seed for reproducibility across numpy and random
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)
    
    # Read the input file
    components_df = pd.read_csv(input_file, sep='\t')
    
    # Initialize a list to hold the discrete ranges for each component
    discrete_ranges = []
    
    # Generate discrete ranges for each component
    for index, row in components_df.iterrows():
        component_name = row['Component']
        max_value = row['maxValue']
        if fixed_values and component_name in fixed_values:
            # If the component has a fixed value, use a single-element array
            component_range = np.array([fixed_values[component_name]])
        else:
            if ratios is not None:
                # Use ratios to create the discrete range
                component_range = np.array([r * max_value for r in ratios])
            else:
                # Use step to create the discrete range
                component_range = np.arange(0, max_value + step, step)
        discrete_ranges.append(component_range)
    
    # Determine the number of components
    num_components = len(discrete_ranges)
    
    # Generate the Latin Hypercube Sampling matrix
    lhs_matrix = lhs(n=num_components, samples=num_samples, criterion='center', random_state=seed)
    
    # Map LHS samples to the discrete ranges
    samples = np.zeros((num_samples, num_components))
    for i in range(num_components):
        samples[:, i] = [random.choice(discrete_ranges[i]) for _ in lhs_matrix[:, i]]
    
    # Create a DataFrame for the samples
    samples_df = pd.DataFrame(samples, columns=components_df['Component'])
    return samples_df

def main(input_file, output_file, num_samples, step=None, ratios=None, fixed_values=None, seed=None):
    """
    Main function to generate LHS samples and save them to a CSV file.
    
    Parameters:
    - input_file: Path to the input file containing components and their max values.
    - output_file: Path to the output CSV file where samples will be written.
    - num_samples: Number of samples to generate.
    - step: Step size for creating discrete ranges (optional).
    - ratios: List of ratios for creating discrete ranges (optional).
    - fixed_values: Dictionary of components with fixed values (optional).
    - seed: Random seed for reproducibility (optional).
    """
    # Read the input file
    components_df = pd.read_csv(input_file, sep='\t')
    
    # Get the list of components from the input file
    component_names = components_df['Component'].tolist()
    
    # Check for fixed values that are not in the list of components
    if fixed_values:
        for component in fixed_values.keys():
            if component not in component_names:
                print(f"Warning: Component '{component}' not found in the input file.")
    
    # Generate LHS samples
    samples_df = generate_lhs_samples(input_file, num_samples, step, ratios, fixed_values, seed)
    
    # Write the samples to a CSV file
    samples_df.to_csv(output_file, index=False)
    print(f"Generated {num_samples} samples and saved to {output_file}")

if __name__ == "__main__":
    # Setup command line argument parsing
    parser = argparse.ArgumentParser(description="Generate Latin Hypercube Samples for given components.")
    parser.add_argument('input_file', type=str, help='Input file path with components and their max values.')
    parser.add_argument('output_file', type=str, help='Output CSV file path for the samples.')
    parser.add_argument('num_samples', type=int, help='Number of samples to generate.')
    
    # Create a mutually exclusive group for step and ratios
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--step', type=float, help='Step size for creating discrete ranges.')
    group.add_argument('--ratios', type=str, help='Comma-separated list of ratios for creating discrete ranges (e.g., "0,0.2,0.4,0.6,0.8,1").')
    
    parser.add_argument('--fixed_values', type=str, default=None, help='Fixed values for components as a dictionary (e.g., \'{"Component1": 10, "Component2": 20}\')')
    parser.add_argument('--seed', type=int, default=None, help='Seed for random number generation for reproducibility (optional).')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Convert fixed_values argument from string to dictionary if provided
    fixed_values = ast.literal_eval(args.fixed_values) if args.fixed_values else None
    
    # Convert ratios argument from comma-separated string to list of floats if provided
    ratios = [float(r) for r in args.ratios.split(',')] if args.ratios else None
    
    # Run the main function with the parsed arguments
    main(args.input_file, args.output_file, args.num_samples, args.step, ratios, fixed_values, args.seed)
