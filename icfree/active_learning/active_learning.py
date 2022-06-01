import csv
import copy

from time import (
    time
)

from numpy import (
    concatenate,
    amax,
    reshape,
    array_equiv,
    mean,
    std,
    empty,
    argmax,
    genfromtxt
)

import matplotlib.pyplot as plt

from sklearn.metrics import (
    r2_score
)

from sklearn.neural_network import (
    MLPRegressor
)

from plates_generator import (
    
)

# Importing data
folder_for_data = "/Users/yorgo/Documents/GitHub/icfree-ml/tests/data/gold_regressor"

plate_1 = "{}/plate_AL_1_raw_yield_and_std.csv".format(folder_for_data)
plate_1_array = genfromtxt(
    plate_1,
    delimiter=',',
    skip_header=1,
    dtype="float")

plate_2 = "{}/plate_AL_2_raw_yield_and_std.csv".format(folder_for_data)
plate_2_array = genfromtxt(
    plate_2,
    delimiter=',',
    skip_header=1,
    dtype="float")

plate_3 = "{}/plate_AL_3_raw_yield_and_std.csv".format(folder_for_data)
plate_3_array = genfromtxt(
    plate_3,
    delimiter=',',
    skip_header=1,
    dtype="float")

plate_4 = "{}/plate_AL_4_raw_yield_and_std.csv".format(folder_for_data)
plate_4_array = genfromtxt(
    plate_4,
    delimiter=',',
    skip_header=1,
    dtype="float")

plate_5 = "{}/plate_AL_5_raw_yield_and_std.csv".format(folder_for_data)
plate_5_array = genfromtxt(
    plate_5,
    delimiter=',',
    skip_header=1,
    dtype="float")

plate_6 = "{}/plate_AL_6_raw_yield_and_std.csv".format(folder_for_data)
plate_6_array = genfromtxt(
    plate_6,
    delimiter=',',
    skip_header=1,
    dtype="float")

plate_7 = "{}/plate_AL_7_raw_yield_and_std.csv".format(folder_for_data)
plate_7_array = genfromtxt(
    plate_7,
    delimiter=',',
    skip_header=1,
    dtype="float")

plate_8 = "{}/plate_AL_8_raw_yield_and_std.csv".format(folder_for_data)
plate_8_array = genfromtxt(
    plate_8,
    delimiter=',',
    skip_header=1,
    dtype="float")

plate_9 = "{}/plate_AL_9_raw_yield_and_std.csv".format(folder_for_data)
plate_9_array = genfromtxt(
    plate_9,
    delimiter=',',
    skip_header=1,
    dtype="float")

plate_10 = "{}/plate_AL_10_raw_yield_and_std.csv".format(folder_for_data)
plate_10_array = genfromtxt(
    plate_10,
    delimiter=',',
    skip_header=1,
    dtype="float")


def data_from_iteration(iteration_number):
    """
    Get data from the selected number of iterations.
    """
    all_plates_list = [
        plate_1_array,
        plate_2_array,
        plate_3_array,
        plate_4_array,
        plate_5_array,
        plate_6_array,
        plate_7_array,
        plate_8_array,
        plate_9_array,
        plate_10_array
        ]

    selected_plates = all_plates_list[0:iteration_number]
    current_data = concatenate(selected_plates, axis=0)

    return current_data


data = data_from_iteration(3)
print(data.shape)

# Defining tested concentrations and volumes
# Maximum concentrations for each component
extract_max = 30
mg_gluta_max = 4
K_gluta_max = 80
aa_max = 1.5
peg_max = 2
hepes_max = 50
trna_max = 0.2
coa_max = 0.26
nad_max = 0.33
camp_max = 0.75
folinic_acid_max = 0.068
spemidine_max = 1
pga_max = 30
nucleo_mix_max = 1.5
DNA_max = 50
promoter_max = 10
RBS_max = 10

# Concentration data: tested concentrations for each reagent
mg_gluta_conc = [0.1, 0.3, 0.5, 1]
K_gluta_conc = [0.1, 0.3, 0.5, 1]
aa_conc = [0.1, 0.3, 0.5, 1]
trna_conc = [0.1, 0.3, 0.5, 1]
coa_conc = [0.1, 0.3, 0.5, 1]
nad_conc = [0.1, 0.3, 0.5, 1]
camp_conc = [0.1, 0.3, 0.5, 1]
folinic_acid_conc = [0.1, 0.3, 0.5, 1]
spermidine_conc = [0.1, 0.3, 0.5, 1]
pga_conc = [0.1, 0.3, 0.5, 1]
nucleo_conc = [0.1, 0.3, 0.5, 1]

# Reshaping data for following tests
initial_max = []  # This stores maximum values for normalisation later on.
X_data, y_data, y_std_data = data[:, 0:11], data[:, 11], data[:, 12]

for i in range(X_data.shape[1]):
    initial_max.append(copy.deepcopy(max(X_data[:, i])))
    X_data[:, i] = X_data[:, i]/max(X_data[:, i])

print(initial_max)

# Maximum yield attained at those iterations
best_of = amax(y_data)
print(best_of)


def present_in_array_index(new_sample, array, size=11):
    """
    Verify if a sample is present in an array.
    """
    present = False
    new_sample = reshape(array(new_sample), (1, size))
    for i in range(array.shape[0]):
        if array_equiv(array[i, :], new_sample):
            present = True
            break

    return present, i


def setup_model(X,
                y,
                models_number=10,
                visualize=True,
                model_name="test"):

    # Training model
    for i in range(models_number):
        X_train = X
        y_train = y
        MLP = MLPRegressor(
            hidden_layer_sizes=(10, 100, 100, 20),
            solver="adam",
            max_iter=20000,
            early_stopping=True,
            learning_rate="adaptive")
        MLP.fit(X_train, y_train.flatten())

    # Evaluating model
    y_pred = MLP.predict(X)
    score = r2_score(y, y_pred)

    if visualize:
        model = MLP
        y_pred = model.predict(X)
        score = r2_score(y, y_pred)
        fig, ax = plt.subplots()
        ax.scatter(y, y_pred, edgecolors=(0, 0, 0))
        ax.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=4)
        ax.set_xlabel('Measured')
        ax.set_title(
            "Model prediction for model {}: {}".format(model_name, score))
        ax.set_ylabel('Predicted')
        plt.show()

    return MLP, score


# Ensemble Model Training
training_start_time = time.time()
MLP_ensemble = []
n = 6

for i in range(n):
    model, score = setup_model(
        X_data,
        y_data,
        models_number=n,
        visualize=True,
        model_name=i)
    MLP_ensemble.append(model)

training_end_time = time.time()

# See what the models do
for i in range(len(MLP_ensemble)):
    model = MLP_ensemble[i]
    y_pred = model.predict(X_data)
    score = r2_score(y_data, y_pred)
    fig, ax = plt.subplots()
    ax.scatter(y_data, y_pred, edgecolors=(0, 0, 0))
    ax.errorbar(
        y_data, y_pred, xerr=y_std_data,
        ls='none')
    ax.plot(
        [y_data.min(), y_data.max()],
        [y_data.min(), y_data.max()],
        'k--',
        lw=4)
    ax.set_xlabel('Measured')
    ax.set_title("Model prediction for model {}: {}".format(i, score))
    ax.set_ylabel('Predicted')
    plt.show()

all_predictions = None
for model in MLP_ensemble:
    y_pred = model.predict(X_data)
    answer_array_pred = y_pred.reshape(X_data.shape[0], -1)
    if all_predictions is None:
        all_predictions = y_pred.reshape(X_data.shape[0], -1)
    else:
        all_predictions = concatenate((
            all_predictions,
            y_pred.reshape(X_data.shape[0], -1)),
            axis=1)

y_pred = mean(all_predictions, axis=1)
y_pred_std = std(all_predictions, axis=1)
score = r2_score(y_data, y_pred)

fig, ax = plt.subplots()
ax.scatter(y_data, y_pred, edgecolors=(0, 0, 0))
ax.errorbar(
    y_data, y_pred, xerr=y_std_data,
    yerr=y_pred_std,
    ls='none')
ax.plot(
        [y_data.min(), y_data.max()],
        [y_data.min(), y_data.max()],
        'k--',
        lw=4)
ax.set_xlabel('Measured')
ax.set_title("Model prediction for ensemble of models: {}".format(score))
ax.set_ylabel('Predicted')
plt.show()

# Include levels_array_generator() and return active_learning_array


def select_best_predictions_from_ensemble_model(
            ensemble_of_models,
            array_to_avoid,
            total_sampling_size=1000,
            sample_size=500,
            exploitation=1,
            exploration=1.41,
            normalisation=True,
            initial_max=initial_max,
            verbose=True):
    """
    """
    # Random concentrations to test
    active_learning_array = generate_random_grid(
        array_to_avoid,
        sample_size=total_sampling_size,
        normalisation=normalisation)

    # Predicting the full random grid
    answer_array_pred = empty
    all_predictions = None

    if verbose:
        print("Starting ensemble predictions")

    for model in ensemble_of_models:
        y_pred = model.predict(active_learning_array)
        answer_array_pred = y_pred.reshape(
            active_learning_array.shape[0], -1)

        if all_predictions is None:
            all_predictions = y_pred.reshape(
                active_learning_array.shape[0], -1)
        else:
            all_predictions = concatenate((
                all_predictions,
                y_pred.reshape(active_learning_array.shape[0], -1)),
                axis=1)

    if verbose:
        print("Finished ensemble predictions")

    # Get mean and std for the predicted array
    y_pred = mean(all_predictions, axis=1)
    y_pred_std = std(all_predictions, axis=1)

    # Array to maximise, while balancing between exploration and exploitation
    array_to_maximise = copy.deepcopy(
        exploitation * y_pred + exploration * y_pred_std)

    # Select arrays in regards of the exploration method
    # Only uncertainty
    # Only yield
    # Uncertainty and yield
    conditions_list_pure_exploitation = []
    for count in range(sample_size):
        i = argmax(y_pred)
        conditions_list_pure_exploitation.append(int(i))
        if verbose:
            print("Maximising sample {} is yield: {}, std = {}".format(
                i,
                y_pred[i],
                y_pred_std[i]))
        y_pred[i] = -1

    conditions_list_pure_exploration = []
    for count in range(sample_size):
        i = argmax(y_pred_std)
        conditions_list_pure_exploration.append(int(i))
        if verbose:
            print("Maximising sample {} is yield: {}, std = {}".format(
                i,
                y_pred[i],
                y_pred_std[i]))
        y_pred_std[i] = -1

    conditions_list = []
    for count in range(sample_size):
        i = argmax(array_to_maximise)
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
        active_learning_array = active_learning_array

    conditions_to_test = active_learning_array[conditions_list, :]
    conditions_to_test_exploration = \
        active_learning_array[conditions_list_pure_exploration, :]
    conditions_to_test_exploitation = \
        active_learning_array[conditions_list_pure_exploitation, :]

    return (conditions_to_test,
            conditions_to_test_exploration,
            conditions_to_test_exploitation)


def export_array_of_elements_of_interest(array, file_place):
    """
    Export an array as a csv in the destined place
    """
    fieldnames = [
        "nad",
        "folinic_acid",
        "DNA",
        "coa",
        "RBS",
        "peg",
        "nucleo_mix",
        "spermidin",
        "pga",
        "aa",
        "trna",
        "mg_gluta",
        "hepes",
        "camp",
        "K_gluta",
        "promoter"]

    export_as_list = []

    for row in array:
        new_dict = {}
        new_dict["nad"] = round(float(row[0]), 5)
        new_dict["folinic_acid"] = round(float(row[1]), 5)
        new_dict["DNA"] = 50
        new_dict["coa"] = round(float(row[2]), 5)
        new_dict["RBS"] = 10
        new_dict["peg"] = 2
        new_dict["nucleo_mix"] = round(float(row[3]), 5)
        new_dict["spermidin"] = round(float(row[4]), 5)
        new_dict["pga"] = round(float(row[5]), 5)
        new_dict["aa"] = round(float(row[6]), 5)
        new_dict["trna"] = round(float(row[7]), 5)
        new_dict["mg_gluta"] = round(float(row[8]), 4)
        new_dict["hepes"] = 50
        new_dict["camp"] = round(float(row[9]), 4)
        new_dict["K_gluta"] = round(float(row[10]), 4)
        new_dict["promoter"] = 10
        export_as_list.append(new_dict)

    with open(file_place, "w") as csv_handle:
        csv_writer = csv.DictWriter(
            csv_handle,
            fieldnames,
            restval='',
            extrasaction='ignore')
        csv_writer.writeheader()
        for result in export_as_list:
            csv_writer.writerow(result)


conditions_to_test, \
    conditions_to_test_exploration, \
    conditions_to_test_exploitation = \
    select_best_predictions_from_ensemble_model(
        ensemble_of_models=MLP_ensemble,
        array_to_avoid=X_data,
        total_sampling_size=1000,
        verbose=False,
        sample_size=50)

base_name = "showcase_AL"

export_array_of_elements_of_interest(
    conditions_to_test, file_place="{}.csv".format(base_name))

export_array_of_elements_of_interest(
    conditions_to_test_exploration,
    file_place="{}_exploration.csv".format(base_name))

export_array_of_elements_of_interest(
    conditions_to_test_exploitation,
    file_place="{}_exploitation.csv".format(base_name))
