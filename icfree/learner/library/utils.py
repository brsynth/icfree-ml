import glob
import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from IPython.display import display
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score


def import_data(folder_for_data, verbose = True):
    """
    This function reads all CSV files in the specified folder, concatenates their contents
          into a single DataFrame, and returns this DataFrame along with a list of number of data in each csv (row counts) for ploting later
    If `verbose=True`, it prints the number of files processed, the names of the files, 
          and displays the concatenated DataFrame
    Args:
        folder_for_data (str): The path to the folder containing the CSV files.
        verbose (bool, optional): If True, prints information about the files being processed 
                                  and displays the resulting DataFrame. Defaults to True.

    Returns:
        concatenated_data (pd.DataFrame): containing the concatenated data from all CSV files 
                        in the folder. The rows from each file are appended sequentially. 
                        Noted the order of file impoerted is important because it will affect plotting later
        list: A list of integers where each value represents the number of rows in each 
                CSV file that was processed.

    """

    # List all files in folder_for_data with .csv extension
    files = glob.glob(os.path.join(folder_for_data, "*.csv"))
    # Print names without full path of found files
    filenames = ", ".join([os.path.basename(file) for file in files])
    print(f"Files found in {folder_for_data}: {filenames}")
    concatenated_data = pd.DataFrame()
    size_list = []

    for file in files:
        df = pd.read_csv(file)

        # Check if columns are consistent across files
        if concatenated_data.columns.empty:
            concatenated_data = df
            size_list.append(len(df))
        else: 
            concatenated_data = pd.concat([concatenated_data, df], ignore_index=True)
            size_list.append(len(df))

    if verbose:
        print("Read ", len(files), " files: ")
        for file in files:
            data_name = os.path.basename(file)
            print("- ", data_name)
        display(concatenated_data)

    return concatenated_data, size_list


def import_parameter(parameter_file, parameter_step, sep='\t', verbose=False):
    """
    Imports parameter data from a csv/tsv file and generates a DataFrame with sampling conditions for each element.
    Condition ranging from `parameter_step` to the element's max value in increments of `parameter_step`, obmit 0

    Args:
        parameter_file (str): The path to the CSV file containing parameter data.
        parameter_step (float): The step size used for generating ranges for each element's concentration.
        sep (str, optional): The delimiter used in parameter file (';' , ',' , '\t') Defaults to '\t'
        verbose (bool, optional): If True, prints detailed information about the loaded data and the resulting DataFrame. Defaults to False.

    Returns:
        element_list (list): A list of element names from the 'Component' column of the CSV file.
        element_max (list): A list of maximum values for each element from the 'maxValue' column of the CSV file.
        sampling_condition (pd.DataFrame): A DataFrame containing the sampling conditions for each element, 
            where each column corresponds to an element, and rows represent the possible concentrations.

    """
    parameter = pd.read_csv(parameter_file, sep=sep)
    element_list = parameter['Component'].to_list()
    element_max = parameter['maxValue'].to_list()

    sampling_condition = pd.DataFrame([])
    for i in range(len(element_list)):
        element_name = element_list[i]
        element_pool = pd.Series(
            np.arange(0, element_max[i] + parameter_step, parameter_step),
            name=element_name
        )
        sampling_condition = pd.concat([sampling_condition, element_pool], axis=1)

    sampling_condition = sampling_condition[1:]

    if verbose:
        print(f"Element List: {element_list}")
        print(f"Max Values: {element_max}")
        print("Generated Sampling Conditions:")
        display(sampling_condition)

    return element_list, element_max, sampling_condition 


def check_column_names(data, element_list):
    """
    Checks if the first n columns of the `data` DataFrame match the expected element list from parameter file.

    Args:
        data (pd.DataFrame): The DataFrame containing the actual data with columns to be checked.
        element_list (list): The list of expected element names (columns).

    Raises:
        ValueError: If there are mismatched column names between the data and the element list.
    """
    element_len = len(element_list)
    element_data = data.columns[:element_len]

    columns_only_in_data = set(element_data).difference(element_list)
    columns_only_in_parameter = set(element_list).difference(element_data)

    try:
        if columns_only_in_data or columns_only_in_parameter:
            print("- Columns only in data files:", columns_only_in_data)
            print("- Columns only in parameter files:", columns_only_in_parameter)
            raise ValueError("Column names are not matched, please modify parameter column names.")
        else:
            print("All column names matched successfully!")
    
    except ValueError as e:
        error_message = f"{type(e).__name__}: {e}"
        print("\033[1;91m{}\033[0m".format(error_message)) 



def flatten_X_y(feature_matrix, label_matrix):
    """
    Flattens the input feature and label matrices, removing any entries where labels contain NaN values.

    Args:
        feature_matrix (np.ndarray): A 2D array where each row represents a sample and columns are features.
        label_matrix (np.ndarray): A 2D array where each row contains labels corresponding to the samples in `feature_matrix`.

    Returns:
        flattened feature (np.ndarray): matrix with rows where labels contained NaN values removed.
        flattened label (np.ndarray): labels array (y) with NaN values removed.
    """
    flattened_features = []

    for i in range(feature_matrix.shape[0]):
        current_features = feature_matrix[i]
        current_labels = label_matrix[i]
        
        for _ in current_labels:
            flattened_features.append(current_features)

    flattened_features = np.array(flattened_features)
    flattened_labels = np.array([label for sublist in label_matrix for label in sublist])

    non_nan_indices = ~np.isnan(flattened_labels)
    flattened_labels = flattened_labels[non_nan_indices]
    flattened_features = flattened_features[non_nan_indices]

    return flattened_features, flattened_labels


def average_and_drop_na(feature_matrix, label_matrix):
    """
    Averages the labels for each sample in the label matrix and removes any samples where the averaged label is NaN.

    Args:
        feature_matrix (np.ndarray): A 2D array where each row represents a sample, and each column represents a feature.
        label_matrix (list): each row contains multiple labels corresponding to the samples in `feature_matrix`.

    Returns:
        filtered feature (np.ndarray): matrix with rows where the corresponding averaged label was NaN removed.
        filtered_labels (np.ndarray): Averaged label array with NaN values removed.
    """

    if len(label_matrix) == 0:
        return feature_matrix, label_matrix

    averaged_labels = np.nanmean(label_matrix, axis=1)
    valid_indices = ~np.isnan(averaged_labels)

    filtered_features = feature_matrix[valid_indices]
    filtered_labels = averaged_labels[valid_indices]

    return filtered_features, filtered_labels


def split_and_flatten(feature_matrix, label_array, ratio=0.2, seed=None, flatten=True):
    """
    Splits the feature matrix and label array into training and testing sets, and flattens or averages the labels of only train set
    
    Args:
        feature_matrix (np.ndarray): A 2D array where each row is a sample, and columns are features.
        label_array (list of np.ndarray): A list of 1D arrays representing labels corresponding to each sample in `feature_matrix`.
        ratio (float, optional): The proportion of data to include in the test split. Default is 0.2.
        seed (int, optional): Seed for random splitting of data. Default is None.
        flatten (bool, optional): If True, the labels are flattened. If False, the labels are averaged and NaNs are removed. Default is True.

    Returns:
        X_train (np.ndarray): Training feature matrix.
        X_test (np.ndarray): Test feature matrix.
        y_train (np.ndarray): Training label array, flattened or averaged based on the `flatten` argument.
        y_test (np.ndarray): Test label array, flattened.
    """

    feature_matrix = np.array(feature_matrix)

    max_len = len(max(label_array, key=len))
    label_array = np.array([np.pad(arr, (0, max_len - len(arr)), 'constant', constant_values=np.nan) for arr in label_array])

    _, unique_indices = np.unique(feature_matrix, axis=0, return_index=True)
    
    if len(unique_indices) != len(feature_matrix):
        print("WARNING: Repeated rows found in 'feature_matrix'. Unique rows will be used for splitting.")
    
    if ratio == 0:
        X_train, X_test = feature_matrix, np.array([])
        y_train, y_test = label_array, np.array([])
    else:
        train_indices, test_indices = train_test_split(unique_indices, test_size=ratio, random_state=seed)
        X_train, X_test = feature_matrix[train_indices], feature_matrix[test_indices]
        y_train = [label_array[i] for i in train_indices]
        y_test = [label_array[i] for i in test_indices]

    if flatten:
        X_train, y_train = flatten_X_y(X_train, y_train)
    else:
        X_train, y_train = average_and_drop_na(X_train, y_train)

    X_test, y_test = flatten_X_y(X_test, y_test)

    return X_train, X_test, y_train, y_test

#########################################################################################
def plot_r2_curve(y_true, y_pred, outfile=None):
    """
    Plots a scatter plot of true (on x axis) vs. predicted values (y axis) and displays the R-squared value on the plot
    also add a diagonal reference dot line for reference

    Args:
        y_true (np.ndarray): Ground truth (actual) values.
        y_pred (np.ndarray): Predicted values from the model.

    """
     
    r2 = r2_score(y_true, y_pred)
    TRUE, PRED = y_true, y_pred
    sns.set(
        font="arial",
        palette="colorblind",
        style="whitegrid",
        font_scale=1.5,
        rc={"figure.figsize": (5, 5), "axes.grid": False},
    )
    sns.regplot(
        x=TRUE,
        y=PRED,
        fit_reg=0,
        marker="+",
        color="black",
        scatter_kws={"s": 40, "linewidths": 0.7},
    )
    plt.plot([min(TRUE), max(TRUE)], [min(TRUE), max(TRUE)], 
             linestyle='--', 
             color='blue',
             linewidth=1)
    plt.xlabel("Experiment ground truth ")
    plt.ylabel("Model prediction")
    plt.title(f'R2: {r2:.2f}', fontsize=14)
    plt.xlim(min(TRUE) - 0.2, max(TRUE) + 0.5)
    plt.ylim(min(PRED) - 0.2, max(PRED) + 0.5)
    if outfile is not None:
        plt.savefig(outfile)
    plt.show()


def plot_selected_point(y_pred, std_pred, condition, title):
    """
    Plots a scatter plot of all generated point's predicted values (y_pred) vs. predicted standard deviations (std_pred),
    highlighting choosen points in red by active learning based on EI condition (or UCB or PI)

    Args:
        ax (matplotlib.axes.Axes): The matplotlib axis to plot on.
        y_pred (np.ndarray): The predicted yield values.
        std_pred (np.ndarray): The predicted standard deviation values.
        condition (list or np.ndarray): The condition used to select points for highlighting (EI)
        title (str): The title of the plot.

    """
    fig, ax = plt.subplots(1, 1, figsize=(5, 5))
    position = np.where(np.isin(y_pred, condition))[0]
    selected_std = std_pred[position]
    selected_y = y_pred[position]

    y_not = np.delete(y_pred,position)
    std_not = np.delete(std_pred,position)

    ax.scatter(y_not, std_not, c='grey', label='Unselected points', alpha = 0.5)
    ax.scatter(selected_y, selected_std, c='red', alpha = 0.5, label='Selected_point')

    ax.set_title(title)
    ax.set_xlabel('Predicted yield')
    ax.set_ylabel('Predicted std')
    ax.legend(loc='upper left',  prop={'size': 10})

    plt.tight_layout()
    
    return title


def plot_heatmap(X_new_norm, y_pred, element_list, title):
    """
    Plots a heatmap of normalized data (X_new_norm), sorted by predicted values (y_pred),
    with elements along the y-axis. This shows how the model understand the evolution/relationship of each component to yield

    Args:
        ax (matplotlib.axes.Axes): The matplotlib axis to plot on.
        X_new_norm (np.ndarray): A 2D array of normalized feature data (rows = samples, columns = features).
        y_pred (np.ndarray): Predicted values used for sorting the heatmap rows.
        element_list (list of str): List of element names to display on the y-axis.
        title (str): The title of the plot.

    Returns:
        None: The plot is drawn on the provided axis `ax`.
    """
    fig, axes = plt.subplots(1, 1, figsize=(10, 4))
    n = len(y_pred)
    sorted_indices = np.argsort(y_pred)
    sorted_X = X_new_norm[sorted_indices].T  

    heatmap = axes.imshow(sorted_X, aspect='auto', cmap='viridis')

    axes.set_xticks([])  
    axes.set_title(f"{title}, samples = {n}", size=12)
    
    axes.set_yticks(np.arange(len(element_list)))
    axes.set_yticklabels(element_list, fontsize=12)

    cbar = plt.colorbar(heatmap, ax=axes)
    cbar.set_label('Ratio to Max Concentration', size=12)

    plt.tight_layout()
    plt.xlabel("Yield: left-low, right-high")

    return title


def plot_each_round(y, size_list, predict):
    """
    Plots a boxplot showing the distribution of 'y' values across different rounds,
    with an option to highlight the last boxplot if it's a prediction from our model.

    Args:
        y (np.ndarray or list): The yield values to plot.
        size_list (list of int): A list containing the number of data in each round.
        predict (bool): If True, the last boxplot will be highlighted with a different color.

    """
    cumulative_sizes = np.cumsum(size_list)
    subarrays = np.split(y, cumulative_sizes)
    flattened_arrays = [subarray.flatten() for subarray in subarrays]

    y_by_file = {}
    for i in range(len(size_list)):
        name = 'round ' + str(i)
        y_by_file[name] = flattened_arrays[i]

    y_by_file = pd.DataFrame.from_dict(y_by_file, orient='index').transpose()

    boxprops = dict(linewidth=0)
    medianprops = dict(linewidth=1, color='red', linestyle='dashed')
    ax = sns.boxplot(y_by_file, color = 'yellow', width=0.3, boxprops=boxprops, medianprops= medianprops)

    median_values = y_by_file.median()
    for i, value in enumerate(median_values):
        ax.annotate(f'{value:.2f}', (i, value), textcoords="offset points", xytext=(0,3),
                    ha='center', fontsize=8, color='black')

    if predict:
        last_box = ax.patches[-1]

        last_box.set_facecolor('silver')

    plt.ylabel('Yield')
    title = 'Yield evolution through each active learning query'
    plt.title(title)

    return title


def plot_train_test(train, test, element_list):
    """
    Plots histograms comparing train and test data distributions for each element
    in the provided element list. Histograms for each element are displayed in a grid.

    Args:
        train (np.ndarray or pd.DataFrame): The training data with elements as columns.
        test (np.ndarray or pd.DataFrame): The test data with elements as columns.
        element_list (list of str): List of element names (column names) to plot.
    """
    test = pd.DataFrame(test, columns=element_list)
    train = pd.DataFrame(train, columns=element_list)

    no_element = len(element_list)
    nrows = int(np.ceil(np.sqrt(no_element)))
    ncols = int(np.ceil(no_element / nrows))
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(15, 8))

    axes = axes.flatten()  

    for i, column in enumerate(element_list):
        hist_range = [min(train[column]), max(train[column])]
        axes[i].hist(train[column], alpha=0.3, label='Previous data', bins=10)
        axes[i].hist(test[column], range=hist_range, alpha=1, label='New data', bins=10)
        axes[i].set_title(column)
        axes[i].legend()

    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    return "Train_Test.png"