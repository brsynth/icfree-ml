# Configuration Documentation

## Dataframe Structure

### Rows
- Each row in the dataframe represents an experiment, with features X (e.g., concentration/volumes of cell-free mixes) followed by labels y (e.g., yields).
- **Example**: Row 0 contains the features and labels for Experiment 1.

### Columns
- **Feature Columns (X):**
  - The first set of columns contains feature values. These are numerical or categorical variables used as input for modeling.
  - **Example**: `feature1`, `feature2`, ..., `featureN`
- **Label Columns (y):**
  - The subsequent columns represent the labels or target variables for the same experiments, i.e., model output.
  - **Example**: `label1`, `label2`, ..., `labelM`

### Key Characteristics
- **Shape**: `(n_experiments, n_features + n_labels)`
  - `n_experiments`: The number of rows (experiments).
  - `n_features`: The number of feature columns (X).
  - `n_labels`: The number of label columns (y).

**Example**:
| feature1 | feature2 | feature3 | label1 | label2 |
|----------|----------|----------|--------|--------|
|   0.1    |   1.5    |   0.7    |   0    |   1    |
|   0.3    |   1.7    |   0.5    |   1    |   0    |

---

## Configuration Variables Documentation

### `data_folder: str`
- **Required**: Yes
- **Description**: The path to the folder containing the data files.
- **Example**: `"data/top50"`

### `parameter_file: str`
- **Required**: Yes
- **Description**: The path to the file containing the parameter values for the experiments.
- **Example**: `"data/param.tsv"`

### `output_folder: str`
- **Required**: Yes
- **Description**: The path to the folder where the output files will be saved.
- **Example**: `"output"`

### `name_list: str`
- **Description**: A comma-separated string of column names or identifiers, converted to a list of strings representing columns that contain labels (y). This separates y columns from the rest (X features).
- **Example**: `Yield1,Yield2,Yield3,Yield4,Yield5`

### `test: bool`
- **Description**: A flag for validating the model; not required to run inside the active learning loop. If false, skip the validating step.
- **Example**: `True`

### `nb_rep: int`
- **Description**: The number of test repetitions for validating the model behavior. 80% of data is randomly separated for training, and 20% is used for testing.
- **Example**: `100`

### `flatten: bool`
- **Description**: A flag to indicate whether to flatten Y data. Accepts 'true' or 'false' (case-insensitive). If 'true', treats each repetition in the same experiment independently; multiple same X values with different y outputs are modeled. If 'false', calculates the average of y across repetitions and only model with y average.
- **Example**: `False`

### `seed: int`
- **Description**: The random seed value used for reproducibility in random operations.
- **Example**: `85`

### `nb_new_data_predict: int`
- **Description**: The number of new data points sampled from all possible cases.
- **Example**: `1000`

### `nb_new_data: int`
- **Description**: The number of new data points selected from the generated ones. These are the data points labeled after active learning loops. `nb_new_data_predict` must be greater than `nb_new_data` to be meaningful.
- **Example**: `50`

### `parameter_step: int`
- **Description**: The step size used to decrement the maximum predefined concentration sequentially. For example, if the maximum concentration is `max`, the sequence of concentrations is calculated as: `max - 1 * parameter_step`, `max - 2 * parameter_step`, `max - 3 * parameter_step`, and so on. Each concentration is a candidate for experimental testing. Smaller steps result in more possible combinations to sample.
- **Example**: `10`

### `n_group: int`
- **Description**: Parameter for the cluster margin algorithm, specifying the number of groups into which generated data will be clustered.
- **Example**: `15`

### `km: int`
- **Description**: Parameter for the cluster margin algorithm, specifying the number of data points for the first selection. Ensure `nb_new_data_predict > ks > km`.
- **Example**: `50`

### `ks: int`
- **Description**: Parameter for the cluster margin algorithm, specifying the number of data points for the second selection. This is also similar to `nb_new_data`.
- **Example**: `20`

### `plot: bool`
- **Description**: A flag to indicate whether to generate all plots for analysis visualization. Accepts 'true' or 'false' (case-insensitive).
- **Example**: `True`

### `save_plot: bool`
- **Description**: A flag to indicate whether to save all generated plots. Accepts 'true' or 'false' (case-insensitive).
- **Example**: `True`

---

## Example Configuration File

[config.csv](config.csv)