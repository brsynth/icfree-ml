import argparse
import pandas as pd
import numpy as np
import random
from pyDOE2 import lhs

def generate_lhs_samples(input_file, num_samples, step, seed=None):
    """
    Generates Latin Hypercube Samples for components based on discrete ranges.
    
    Parameters:
    - input_file: Path to the input file containing components and their max values.
    - num_samples: Number of samples to generate.
    - step: Step size for creating discrete ranges.
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
        component_range = np.arange(0, row['maxValue'] + step, step)
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

def main(input_file, output_file, num_samples, step=2.5, seed=None):
    """
    Main function to generate LHS samples and save them to a CSV file.
    
    Parameters:
    - input_file: Path to the input file containing components and their max values.
    - output_file: Path to the output CSV file where samples will be written.
    - num_samples: Number of samples to generate.
    - step: Step size for creating discrete ranges (default: 2.5).
    - seed: Random seed for reproducibility (optional).
    """
    # Generate LHS samples
    samples_df = generate_lhs_samples(input_file, num_samples, step, seed)
    
    # Write the samples to a CSV file
    samples_df.to_csv(output_file, index=False)
    print(f"Generated {num_samples} samples and saved to {output_file}")

if __name__ == "__main__":
    # Setup command line argument parsing
    parser = argparse.ArgumentParser(description="Generate Latin Hypercube Samples for given components.")
    parser.add_argument('input_file', type=str, help='Input file path with components and their max values.')
    parser.add_argument('output_file', type=str, help='Output CSV file path for the samples.')
    parser.add_argument('num_samples', type=int, help='Number of samples to generate.')
    parser.add_argument('--step', type=float, default=2.5, help='Step size for creating discrete ranges (default: 2.5).')
    parser.add_argument('--seed', type=int, default=None, help='Seed for random number generation for reproducibility (optional).')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the main function with the parsed arguments
    main(args.input_file, args.output_file, args.num_samples, args.step, args.seed)
