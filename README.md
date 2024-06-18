# iCFree

iCFree is a Python-based program designed to automate the process of generating and running a Snakemake workflow for sampling and preparing instructions for laboratory experiments. The program includes components for generating samples, creating plates, and instructing the handling of these plates.

## Table of Contents

- [iCFree](#icfree)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Basic Command](#basic-command)
  - [Components](#components)
    - [Sampler](#sampler)
      - [Usage](#usage-1)
      - [Arguments](#arguments)
    - [Plate Generator](#plate-generator)
      - [Usage](#usage-2)
      - [Options](#options)
    - [Instructor](#instructor)
      - [Usage](#usage-3)
      - [Options](#options-1)
  - [Example](#example)
  - [License](#license)
  - [Authors](#authors)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/icfree.git
    cd icfree
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

The main entry point of the program is the `__main__.py` file. You can run the program from the command line by providing the necessary arguments for each step of the workflow.

### Basic Command

```bash
python -m icfree --sampler_input_filename <input_file> --sampler_nb_samples <number_of_samples> --sampler_seed <seed> --sampler_output_filename <output_file> --plate_generator_input_filename <input_file> --plate_generator_sample_volume <volume> --plate_generator_default_dead_volume <dead_volume> --plate_generator_num_replicates <replicates> --plate_generator_well_capacity <capacity> --plate_generator_start_well_src_plt <start_well_src> --plate_generator_start_well_dst_plt <start_well_dst> --plate_generator_output_folder <output_folder> --instructor_max_transfer_volume <max_volume> --instructor_split_threshold <split_threshold> --instructor_source_plate_type <plate_type> --instructor_split_components <components> --instructor_output_filename <instructions_file>
```

## Components

### Sampler

The `sampler.py` script generates Latin Hypercube Samples (LHS) for given components.

#### Usage

```bash
python icfree/sampler.py <input_file> <output_file> <num_samples> [--step <step_size>] [--seed <seed>]
```

#### Arguments

- `input_file`: Input file path with components and their max values.
- `output_file`: Output CSV file path for the samples.
- `num_samples`: Number of samples to generate.
- `--step`: Step size for creating discrete ranges (default: 2.5).
- `--seed`: Seed for random number generation for reproducibility (optional).

### Plate Generator

The `plate_generator.py` script generates plates based on the sampled data.

#### Usage

```bash
python icfree/plate_generator.py <input_file> <sample_volume> [options]
```

#### Options

- `--default_dead_volume`: Default dead volume.
- `--dead_volumes`: Dead volumes for specific wells.
- `--num_replicates`: Number of replicates.
- `--well_capacity`: Well capacity.
- `--start_well_src_plt`: Starting well for the source plate.
- `--start_well_dst_plt`: Starting well for the destination plate.
- `--output_folder`: Folder to save the output files.

### Instructor

The `instructor.py` script generates instructions for handling the generated plates.

#### Usage

```bash
python icfree/instructor.py <source_plate> <destination_plate> <output_instructions> [options]
```

#### Options

- `--max_transfer_volume`: Maximum transfer volume.
- `--split_threshold`: Threshold for splitting components.
- `--source_plate_type`: Type of the source plate.
- `--split_components`: Components to split.

## Example

Here is an example of how to run the program with sample data:

```bash
python -m icfree --sampler_input_filename data/components.csv --sampler_nb_samples 100 --sampler_seed 42 --sampler_output_filename results/samples.csv --plate_generator_input_filename results/samples.csv --plate_generator_sample_volume 10 --plate_generator_default_dead_volume 2 --plate_generator_num_replicates 3 --plate_generator_well_capacity 200 --plate_generator_start_well_src_plt A1 --plate_generator_start_well_dst_plt B1 --plate_generator_output_folder results/plates --instructor_max_transfer_volume 50 --instructor_split_threshold 5 --instructor_source_plate_type '96-well' --instructor_split_components 'component1,component2' --instructor_output_filename results/instructions.txt
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


## Authors
ChatGPT-4
