import argparse
import numpy as np
import pandas as pd
import warnings
from sklearn.exceptions import ConvergenceWarning
from sklearn.preprocessing import MaxAbsScaler
warnings.filterwarnings("ignore", category=ConvergenceWarning)

from library.utils import *
from library.model import *
from library.active_learning import *


def parse_arguments():
    parser = argparse.ArgumentParser(description="Script for active learning and model training.")
    
    # Add all the arguments that were previously loaded from config.csv and use the CSV values as defaults
    parser.add_argument('--name_list', type=str, default='Yield1,Yield2,Yield3,Yield4,Yield5', help="Comma-separated list of names")
    parser.add_argument('--nb_rep', type=int, default=100, help="Number of repetitions")
    parser.add_argument('--flatten', type=str, choices=['true', 'false'], default='False', help="Whether to flatten data")
    parser.add_argument('--seed', type=int, default=85, help="Random seed")
    parser.add_argument('--nb_new_data_predict', type=int, default=3000, help="Number of new data points to predict")
    parser.add_argument('--nb_new_data', type=int, default=50, help="Number of new data points")
    parser.add_argument('--parameter_step', type=int, default=20, help="Parameter step")
    parser.add_argument('--test', type=int, default=1, help="Test flag")
    parser.add_argument('--n_group', type=int, default=15, help="Number of groups")
    parser.add_argument('--ks', type=int, default=20, help="ks parameter")
    parser.add_argument('--km', type=int, default=50, help="km parameter")
    parser.add_argument('--plot', type=str, choices=['true', 'false'], default='True', help="Whether to plot the results")
    parser.add_argument('--data_folder', type=str, default='data/top50', help="Folder containing data")
    parser.add_argument('--parameter_file', type=str, default='param.tsv', help="Parameter file path")
    parser.add_argument('--save_name', type=str, default='new_exp/plate3', help="Name for saving outputs")
    
    args = parser.parse_args()
    
    # Convert boolean-like strings to actual booleans
    args.flatten = args.flatten.lower() == 'true'
    args.plot = args.plot.lower() == 'true'
    
    # Convert comma-separated lists to actual Python lists
    args.name_list = args.name_list.split(',')
    
    return args

def main():
    args = parse_arguments()
    
    data_folder = args.data_folder
    name_list = args.name_list
    parameter_file = args.parameter_file
    nb_rep = args.nb_rep
    flatten = args.flatten
    seed = args.seed
    nb_new_data_predict = args.nb_new_data_predict
    nb_new_data = args.nb_new_data
    parameter_step = args.parameter_step
    test = args.test
    save_name = args.save_name
    n_group = args.n_group
    ks = args.ks
    km = args.km
    plot = args.plot

    # Proceed with the rest of the script logic
    element_list, element_max, sampling_condition = import_parameter(parameter_file, parameter_step) 

    data, size_list = import_data(data_folder, verbose = True)
    check_column_names(data,element_list)

    no_element = len(element_list)
    y = np.array(data[name_list])
    y_mean = np.nanmean(y, axis = 1)
    y_std = np.nanstd(y, axis = 1)
    X = data.iloc[:,0:no_element]

    params = {'kernel': [
                    C()*Matern(length_scale=10, nu=2.5)+ WhiteKernel(noise_level=1e-3, noise_level_bounds=(1e-3, 1e1))
                ],
    #            'alpha':[0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5]}
                'alpha':[0.05]}

    X_train, X_test, y_train, y_test = split_and_flatten(X, y, ratio = 0, flatten = flatten)
    scaler = MaxAbsScaler()
    X_train_norm = scaler.fit_transform(X_train)
    model = BayesianModels(n_folds= 10, model_type = 'gp', params=params)
    model.train(X_train_norm, y_train)

    if test:
        best_param = {'alpha': [model.best_params['alpha']],'kernel': [model.best_params['kernel']]}
        res = []
        for i in range(nb_rep):
            X_train, X_test, y_train, y_test = split_and_flatten(X, y, ratio = 0.2, flatten = flatten)

            scaler = MaxAbsScaler()
            X_train_norm = scaler.fit_transform(X_train)
            X_test_norm = scaler.transform(X_test)

            eva_model = BayesianModels(model_type ='gp', params= best_param)
            eva_model.train(X_train_norm, y_train, verbose = False)
            y_pred, std_pred = eva_model.predict(X_test_norm)
            res.append(r2_score(y_test, y_pred))

        plt.hist(res, bins = 20, color='orange')
        plt.title(f'Histogram of R2 for different testing subset, median= {np.median(res):.2f}', size = 12)

    X_new= sampling_without_repeat(sampling_condition, num_samples = nb_new_data_predict, existing_data=X_train, seed = seed)
    X_new_norm = scaler.transform(X_new)
    y_pred, std_pred = model.predict(X_new_norm)
    clusters = cluster(X_new_norm, n_group)

    ei = expected_improvement(y_pred, std_pred, max(y_train))
    print("For EI:")
    ei_top, y_ei, ratio_ei, ei_cluster = find_top_elements(X_new, y_pred, clusters, ei, km, return_ratio= True)
    ei_top_norm = scaler.transform(ei_top)

    if plot: 
        plot_selected_point(y_pred, std_pred, y_ei, 'EI selected')

        size_list.append(nb_new_data)
        y_mean = np.append(y_mean, y_ei)
        plot_each_round(y_mean,size_list, predict = True)

        plot_train_test(X_train_norm, ei_top_norm, element_list)

        fig, axes = plt.subplots(1, 1, figsize=(10, 4))
        plot_heatmap(axes, ei_top_norm, y_ei, element_list, 'EI')
        plt.tight_layout()
        plt.xlabel("Yield: left-low, right-high")
        plt.show()

    X_ei = pd.DataFrame(ei_top, columns=element_list)
    name = save_name + '_ei'+ str(km) + '.csv'
    X_ei.to_csv(name, index=False)


if __name__ == "__main__":
    main()
 





