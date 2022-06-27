#!/usr/bin/env python
# coding: utf-8

from os import (
    path as os_path,
    mkdir as os_mkdir
)

import copy
import time

from csv import (
    DictWriter
)

from numpy import (
    concatenate as np_concatenate,
    mean as np_mean,
    std as np_std,
    # empty as np_empty,
    argmax as np_argmax
)

from pandas import (
    read_csv
)

import matplotlib.pyplot as plt

from sklearn.model_selection import (
    KFold
)

from sklearn.metrics import (
    r2_score
)

from sklearn.neural_network import (
    MLPRegressor
)

from icfree.plates_generator.plates_generator import (
    input_importer,
    input_processor,
    doe_levels_generator,
    levels_to_concentrations
)

from logging import (
    Logger,
    getLogger,
)


def dataset_generator(
        data_folder: str,
        files_number: int,
        logger: Logger = getLogger(__name__)):
    """
    Merge experimental data into a single dataset

    Parameters
    ----------
        data_folder: str
            Path to folder containing experimental data
        files_number: int
            Number of files to be merged into a single dataset

    Returns
    -------
        dataset: ndarray
            Dataset containing all experimental data
    """
    # Print out parameters
    logger.info('Generating dataset from experimental data...')
    logger.debug(
        'data folder:\n%s',
        data_folder
    )

    logger.debug(
        'files_number:\n%s',
        files_number
    )

    # Read x number of files
    experimental_data = [read_csv(
        data_folder.format(i))
        for i in range(1, files_number + 1)]

    # Concatenate all data into a single dataset
    dataset = np_concatenate(
        experimental_data,
        axis=0)

    return dataset


def dataset_processor(dataset):
    """
    Extract X and Y from dataset

    Parameters
    ----------
        dataset: ndarray
            Dataset containing all experimental data

    Returns
    -------
        initial_max: list
            List of maximum concentration values in dataset
        X_data: ndarray
            Array of concentrations
        y_data: ndarray
            Array of mean yield data or mean fluorescence data
        y_std_data: ndarray
            Array of standard deviation values of y_data mean
    """
    # Extract concentrations data
    X_data = dataset[:, 0:11]

    # Extract mean y data
    y_data = dataset[:, 11]

    # Extract std of mean y data
    y_std_data = dataset[:, 12]

    # Extract maximimum x values for nomalisation
    initial_max = []
    for i in range(X_data.shape[1]):
        initial_max.append(copy.deepcopy(max(X_data[:, i])))
        X_data[:, i] = X_data[:, i]/max(X_data[:, i])

    return (initial_max,
            X_data,
            y_data,
            y_std_data)


def create_single_regressor(
        X,
        y,
        models_number=10,
        visualize=True,
        model_name="root-model"):
    """
    _summary_

    Args:
        X (_type_): _description_
        y (_type_): _description_
        models_number (int, optional): _description_. Defaults to 10.
        visualize (bool, optional): _description_. Defaults to True.
        model_name (str, optional): _description_. Defaults to "root-model".

    Returns:
        _type_: _description_
    """
    # Train the model
    for i in range(models_number):
        X_train = X
        y_train = y

        MLP = MLPRegressor(
            hidden_layer_sizes=(10, 100, 100, 20),
            activation="relu",
            solver="adam",
            max_iter=20000,
            early_stopping=True,
            learning_rate="adaptive")

        MLP.fit(X_train, y_train.flatten())

    # Evaluate and visualize the output of the model
    y_pred = MLP.predict(X)
    score = r2_score(y, y_pred)

    if visualize:
        model = MLP
        y_pred = model.predict(X)
        score = r2_score(y, y_pred)
        fig, ax = plt.subplots()
        ax.scatter(y, y_pred, edgecolors=(0, 0, 0))
        ax.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=4)
        ax.set_xlabel("Measured")
        ax.set_title(
            "Model prediction for model {}: {}".format(model_name, score))
        ax.set_ylabel("Predicted")
        plt.show()

    return (MLP, score)


def create_ensemble_regressor(
        X_data,
        y_data,
        y_std_data,
        ensemble_size=5):
    """
    _summary_

    Args:
        X_data (_type_): _description_
        y_data (_type_): _description_
        y_std_data (_type_): _description_
        ensemble_size (int, optional): _description_. Defaults to 5.

    Returns:
        _type_: _description_
    """
    # Train the ensemble of models
    training_start_time = time.time()
    MLP_ensemble = []

    for i in range(ensemble_size):
        model, score = create_single_regressor(
            X_data,
            y_data,
            models_number=10,
            visualize=True,
            model_name=i)

        MLP_ensemble.append(model)

    training_end_time = time.time()

    # Evaluate and visualize the ouputs of models
    for i in range(len(MLP_ensemble)):
        model = MLP_ensemble[i]
        y_pred = model.predict(X_data)
        score = r2_score(y_data, y_pred)
        fig, ax = plt.subplots()
        ax.scatter(y_data, y_pred, edgecolors=(0, 0, 0))
        ax.errorbar(y_data, y_pred, xerr=y_std_data, ls="none")
        ax.plot(
            [y_data.min(), y_data.max()],
            [y_data.min(), y_data.max()],
            "k--",
            lw=4)
        ax.set_xlabel("Measured")
        ax.set_title("Model prediction for model {}: {}".format(i, score))
        ax.set_ylabel("Predicted")
        plt.show()

    all_predictions = None
    for model in MLP_ensemble:
        y_pred = model.predict(X_data)
        # answer_array_pred = y_pred.reshape(X_data.shape[0], -1)
        if all_predictions is None:
            all_predictions = y_pred.reshape(X_data.shape[0], -1)
        else:
            all_predictions = np_concatenate((
                all_predictions,
                y_pred.reshape(X_data.shape[0], -1)),
                axis=1)

    y_pred = np_mean(all_predictions, axis=1)
    y_pred_std = np_std(all_predictions, axis=1)
    score = r2_score(y_data, y_pred)

    fig, ax = plt.subplots()
    ax.scatter(y_data, y_pred, edgecolors=(0, 0, 0))
    ax.errorbar(y_data, y_pred, xerr=y_std_data, yerr=y_pred_std, ls="none")
    ax.plot(
            [y_data.min(), y_data.max()],
            [y_data.min(), y_data.max()],
            'k--',
            lw=4)
    ax.set_xlabel("Measured")
    ax.set_title("Model prediction for ensemble of models: {}".format(score))
    ax.set_ylabel("Predicted")
    plt.show()

    return (MLP_ensemble,
            training_start_time,
            training_end_time)


def active_learning_array_generator(cfps_parameters):
    """
    _summary_

    Args:
        cfps_parameters (_type_): _description_

    Returns:
        _type_: _description_
    """
    cfps_parameters_df = input_importer(cfps_parameters)
    parameters = input_processor(cfps_parameters_df)
    doe_levels = doe_levels_generator(
            n_variable_parameters=len(parameters['doe']),
            doe_nb_concentrations=5,
            doe_concentrations=[0.1, 0.4, 0.6, 0.8, 1.0],
            doe_nb_samples=100,
            seed=2,
        )

    max_conc = [
            v['Maximum concentration']
            for v in parameters['doe'].values()
        ]

    active_learning_array = levels_to_concentrations(
            doe_levels,
            max_conc,
        )

    return (cfps_parameters_df, active_learning_array)


def select_best_predictions_from_ensemble_model(
            ensemble_of_models,
            active_learning_array,
            initial_max,
            sample_size=500,
            exploitation=1,
            exploration=1.41,
            normalisation=True,
            verbose=True,
            ):
    """
    _summary_

    Args:
        ensemble_of_models (_type_): _description_
        active_learning_array (_type_): _description_
        initial_max (_type_): _description_
        sample_size (int, optional): _description_. Defaults to 500.
        exploitation (int, optional): _description_. Defaults to 1.
        exploration (float, optional): _description_. Defaults to 1.41.
        normalisation (bool, optional): _description_. Defaults to True.
        verbose (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """
    # Predict the full grid
    # answer_array_pred = np_empty
    all_predictions = None

    if verbose:
        print("Starting ensemble predictions")

    for model in ensemble_of_models:
        y_pred = model.predict(active_learning_array)
        # answer_array_pred = y_pred.reshape(
        #     active_learning_array.shape[0], -1)

        if all_predictions is None:
            all_predictions = y_pred.reshape(
                active_learning_array.shape[0], -1)
        else:
            all_predictions = np_concatenate((
                all_predictions,
                y_pred.reshape(active_learning_array.shape[0], -1)),
                axis=1)

    if verbose:
        print("Finished ensemble predictions")

    # Get mean and std for the predicted array
    y_pred = np_mean(all_predictions, axis=1)
    y_pred_std = np_std(all_predictions, axis=1)

    # Array to maximise, while balancing between exploration and exploitation
    array_to_maximise = copy.deepcopy(
        exploitation * y_pred + exploration * y_pred_std)

    # Select arrays in regards of the exploration method
    # Only uncertainty
    # Only yield
    # Uncertainty and yield
    conditions_list_pure_exploitation = []
    for count in range(sample_size):
        i = np_argmax(y_pred)
        conditions_list_pure_exploitation.append(int(i))
        if verbose:
            print("Maximising sample {} is yield: {}, std = {}".format(
                i,
                y_pred[i],
                y_pred_std[i]))
        y_pred[i] = -1

    conditions_list_pure_exploration = []
    for count in range(sample_size):
        i = np_argmax(y_pred_std)
        conditions_list_pure_exploration.append(int(i))
        if verbose:
            print("Maximising sample {} is yield: {}, std = {}".format(
                i,
                y_pred[i],
                y_pred_std[i]))
        y_pred_std[i] = -1

    conditions_list = []
    for count in range(sample_size):
        i = np_argmax(array_to_maximise)
        conditions_list.append(int(i))
        if verbose:
            print("Maximising sample {} is yield: {}, std = {}".format(
                i,
                y_pred[i],
                y_pred_std[i]))
        array_to_maximise[i] = -1

    if normalisation:
        for i in range(active_learning_array.shape[1]):
            active_learning_array[:, i] = \
                active_learning_array[:, i] * initial_max[i]
    else:
        conditions_to_test = active_learning_array[conditions_list, :]

        conditions_to_test_exploration = \
            active_learning_array[conditions_list_pure_exploration, :]

        conditions_to_test_exploitation = \
            active_learning_array[conditions_list_pure_exploitation, :]

    return (conditions_to_test,
            conditions_to_test_exploration,
            conditions_to_test_exploitation)


def save_conditions_to_test(
        cfps_parameters_df,
        conditions_to_test,
        conditions_to_test_exploration,
        conditions_to_test_exploitation,
        global_score,
        global_score_std,
        output_folder):
    """
    Save dataframes in tsv files

    Args:
        cfps_parameters_df (_type_): _description_
        conditions_to_test (_type_): _description_
        conditions_to_test_exploration (_type_): _description_
        conditions_to_test_exploitation (_type_): _description_
        global_score (_type_): _description_
        global_score_std (_type_): _description_
        output_folder (_type_): _description_
    """
    all_parameters = cfps_parameters_df['Parameter'].tolist()

    if not os_path.exists(output_folder):
        os_mkdir(output_folder)

    conditions_to_test.to_csv(
        os_path.join(
            output_folder,
            'conditions_to_test.tsv'),
        sep='\t',
        header=all_parameters,
        index=False)

    conditions_to_test_exploration.to_csv(
        os_path.join(
            output_folder,
            'conditions_to_test_exploration.tsv'),
        sep='\t',
        header=all_parameters,
        index=False)

    conditions_to_test_exploitation.to_csv(
        os_path.join(
            output_folder,
            'conditions_to_test_exploitation.tsv'),
        sep='\t',
        header=all_parameters,
        index=False)


def model_statistics_generator(
        X_data,
        y_data,
        y_std_data,
        iteration_number,
        folder_to_save,
        dataset,
        ensemble_size=25,
        nbr_fold=5):
    """
    _summary_

    Args:
        X_data (_type_): _description_
        y_data (_type_): _description_
        y_std_data (_type_): _description_
        iteration_number (_type_): _description_
        folder_to_save (_type_): _description_
        dataset (_type_): _description_
        ensemble_size (int, optional): _description_. Defaults to 25.
        nbr_fold (int, optional): _description_. Defaults to 5.

    Returns:
        _type_: _description_
    """
    # Extract model number of layers.
    dictionnary_of_models = {2: 0, 3: 0, 4: 0, 5: 0, 6: 0}

    kf = KFold(n_splits=nbr_fold, shuffle=True)
    scores_on_folds = []
    fold_number = 0

    for train_index, test_index in kf.split(X_data):
        fold_number = fold_number + 1
        X_train, X_test = X_data[train_index], X_data[test_index]
        y_train, y_test = y_data[train_index], y_data[test_index]
        # y_std_train = y_std_data[train_index]
        y_std_test = y_std_data[test_index]

        # Training ensemble of models
        ensemble_models = []
        for n in range(ensemble_size):
            MLP, score = create_single_regressor(
                X_train,
                y_train,
                models_number=10,
                visualize=True,
                model_name=n)

            ensemble_models.append(MLP)

        # Analysing the models
        for model in ensemble_models:
            dictionnary_of_models[model.n_layers_] = \
                dictionnary_of_models[model.n_layers_] + 1
        print(dictionnary_of_models)

        # Evaluating the models
        all_predictions = None
        for model in ensemble_models:
            y_pred = model.predict(X_test)
            # answer_array_pred = y_pred.reshape(X_test.shape[0], -1)
            if all_predictions is None:
                all_predictions = y_pred.reshape(X_test.shape[0], -1)
            else:
                all_predictions = np_concatenate(
                        (all_predictions,
                            y_pred.reshape(X_test.shape[0], -1)), axis=1)

        y_pred = np_mean(all_predictions, axis=1)
        y_pred_std = np_std(all_predictions, axis=1)

        score = r2_score(y_test, y_pred)
        fig, ax = plt.subplots()
        ax.scatter(y_test, y_pred, edgecolors=(0, 0, 0))
        ax.errorbar(
            y_test,
            y_pred,
            xerr=y_std_test,
            yerr=y_pred_std,
            ls="none")
        ax.plot([
                y_test.min(),
                y_test.max()],
                [y_test.min(),
                y_test.max()],
                'k--',
                lw=4)
        ax.set_xlabel("Measured")
        ax.set_title("R squared is: {}".format(score))
        ax.set_ylabel("Predicted")
        name_for_plotting = folder_to_save
        + '/' + "iteration_{}".format(iteration_number)
        + "fold_{}".format(fold_number) + ".png"

        plt.savefig(name_for_plotting)
        plt.show()
        scores_on_folds.append(score)

    global_score = np_mean(scores_on_folds)
    global_score_std = np_std(scores_on_folds)

    iteration_results = {}
    for iteration in range(1, 11):
        dataset = dataset_generator(iteration)
        X_data = dataset[:, 0:11]
        y_data = dataset[:, 11]
        y_std_data = dataset[:, 12]

        for i in range(X_data.shape[1]):
            X_data[:, i] = X_data[:, i]/max(X_data[:, i])

        iteration_results["{}".format(iteration)] = \
            global_score, \
            global_score_std

    print("For iteration {}, global score is ({}, {})".format(
            iteration,
            global_score,
            global_score_std))

    return (global_score, global_score_std, iteration_results)


def save_model_statistics(
        iteration_results,
        output_folder):
    """
    Save models statistics in a csv file

    Args:
        iteration_results (_type_): _description_
        output_folder (_type_): _description_
    """
    with open(
            "{}/iteration_results.csv".format(output_folder),
            "w") as csv_writer:
        headers = ["iteration", "score", "scores_std"]
        writer = DictWriter(csv_writer, headers)
        writer.writeheader()
        for key, value in iteration_results.items():
            row = {}
            global_score, global_score_std = value
            row["score"] = global_score
            row["scores_std"] = global_score_std
            row["iteration"] = key
            writer.writerow(row)
