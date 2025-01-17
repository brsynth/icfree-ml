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
      - [Plate Designer](#plate-designer)
        - [Usage](#usage-2)
        - [Options](#options)
      - [Instructor](#instructor)
        - [Usage](#usage-3)
        - [Options](#options-1)
      - [Learner](#learner)
        - [Usage](#usage-4)
        - [Options](#options-2)
    - [Example](#example)
  - [License](#license)
  - [Authors](#authors)

## Installation

1. **Install Conda:**
   - Download the installer for your operating system from the [Conda Installation page](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).
   - Follow the instructions on the page to install Conda. For example, on Windows, you would download the installer and run it. On macOS and Linux, you might use a command like:
     ```bash
     bash ~/Downloads/Miniconda3-latest-Linux-x86_64.sh
     ```
   - Follow the prompts on the installer to complete the installation.

2. **Install iCFree from conda-forge:**
    ```bash
    conda install -c conda-forge icfree
    ```

## Usage

The main entry point of the program is the `__main__.py` file. You can run the program from the command line by providing the necessary arguments for each step of the workflow.

### Basic Command

```bash
python -m icfree --sampler_input_filename <input_file> --sampler_nb_samples <number_of_samples> --sampler_seed <seed> --sampler_output_filename <output_file> --plate_designer_input_filename <input_file> --plate_designer_sample_volume <volume> --plate_designer_default_dead_volume <dead_volume> --plate_designer_num_replicates <replicates> --plate_designer_well_capacity <capacity> --plate_designer_start_well_src_plt <start_well_src> --plate_designer_start_well_dst_plt <start_well_dst> --plate_generat...
```

### Components

#### Sampler
The sampler.py script generates Latin Hypercube Samples (LHS) for given components.

##### Usage

```bash
python icfree/sampler.py <input_file> <output_file> <num_samples> [--step <step_size>] [--seed <seed>]
```

##### Arguments

- input_file: Input file path with components and their max values.
- output_file: Output CSV file path for the samples.
- num_samples: Number of samples to generate.
- --step: Step size for creating discrete ranges (default: 2.5).
- --seed: Seed for random number generation for reproducibility (optional).

#### Plate Designer
The plate_designer.py script generates plates based on the sampled data.

##### Usage

```bash
python icfree/plate_designer.py <input_file> <sample_volume> [options]
```

##### Options

- --default_dead_volume: Default dead volume.
- --dead_volumes: Dead volumes for specific wells.
- --num_replicates: Number of replicates.
- --well_capacity: Well capacity.
- --start_well_src_plt: Starting well for the source plate.
- --start_well_dst_plt: Starting well for the destination plate.
- --output_folder: Folder to save the output files.

#### Instructor
The instructor.py script generates instructions for handling the generated plates.

##### Usage

```bash
python icfree/instructor.py <source_plate> <destination_plate> <output_instructions> [options]
```

##### Options

- --max_transfer_volume: Maximum transfer volume.
- --split_threshold: Threshold for splitting components.
- --source_plate_type: Type of the source plate.
- --split_components: Components to split.
- --dispensing_order: Comma-separated list of component names specifying the dispensing order.

#### Learner
The Learner module carries out an active learning process to both train the model and explore the space of possible cell-free combinations.

##### Usage

```bash
python -m icfree.learner <data_folder> <parameter_file> <output_folder> [options]
```

##### Options

  - --name_list: a comma-separated string of column names or identifiers, converted to a list of strings representing columns that contain labels (y). This separates y columns from the rest (X features). (Default: Yield1,Yield2,Yield3,Yield4,Yield5)
  - --test: a flag for validating the model; not required to run inside the active learning loop. If not set, skip the validating step.
  - --nb_rep NB_REP: the number of test repetitions for validating the model behavior. 80% of data is randomly separated for training, and 20% is used for testing. (Default: 100)
  - --flatten: a flag to indicate whether to flatten Y data. If set, treats each repetition in the same experiment independently; multiple same X values with different y outputs are modeled. Else, calculates the average of y across repetitions and only model with y average.
  - --seed SEED: the random seed value used for reproducibility in random operations. (Default: 85)
  - --nb_new_data_predict: The number of new data points sampled from all possible cases. (Default: 1000)
  - --nb_new_data: The number of new data points selected from the generated ones. These are the data points labeled after active learning loops. `nb_new_data_predict` must be greater than `nb_new_data` to be meaningful. (Default: 50)
  - --parameter_step: The step size used to decrement the maximum predefined concentration sequentially. For example, if the maximum concentration is `max`, the sequence of concentrations is calculated as: `max - 1 * parameter_step`, `max - 2 * parameter_step`, `max - 3 * parameter_step`, and so on. Each concentration is a candidate for experimental testing. Smaller steps result in more possible combinations to sample. (Default: 10)
  - --n_group: parameter for the cluster margin algorithm, specifying the number of groups into which generated data will be clustered. (Default: 15)
  - --km: parameter for the cluster margin algorithm, specifying the number of data points for the first selection. Ensure `nb_new_data_predict > ks > km`. (Default: 50)
  - --ks: parameter for the cluster margin algorithm, specifying the number of data points for the second selection. This is also similar to `nb_new_data`. (Default: 20)
  - --plot: a flag to indicate whether to generate all plots for analysis visualization.
  - --save_plot: a flag to indicate whether to save all generated plots.
  - --verbose: flag to indicate whether to print all messages to the console.

### Example

Here is an example of how to run the program with sample data:

```bash
python -m icfree --sampler_input_filename data/components.csv --sampler_nb_samples 100 --sampler_seed 42 --sampler_output_filename results/samples.csv --plate_designer_input_filename results/samples.csv --plate_designer_sample_volume 10 --plate_designer_default_dead_volume 2 --plate_designer_num_replicates 3 --plate_designer_well_capacity 200 --plate_designer_start_well_src_plt A1 --plate_designer_start_well_dst_plt B1 --plate_designer_output_folder results/plates --instructor_max_transfer_volume...
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Authors

ChatGPT, OpenAI
