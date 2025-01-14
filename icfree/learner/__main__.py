import argparse
import re
from os import path as os_path
import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.preprocessing import MaxAbsScaler
import warnings
warnings.filterwarnings("ignore", category=ConvergenceWarning)

from icfree.learner.library import *

def csv_to_dict(file_path):
    import pandas as pd
    # Read the CSV file
    data = pd.read_csv(file_path, header=None)
    # Create a dictionary from the two columns
    param_dict = dict(zip(data.iloc[:, 0], data.iloc[:, 1]))
    return param_dict

def parse_readme(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Regular expression to extract parameter sections
    param_regex = r"### `(?P<name>\w+): (?P<type>\w+)`(\n- \*\*Required\*\*: (?P<required>.+?))*\n- \*\*Description\*\*: (?P<description>.+?)(?:\n- \*\*Example\*\*: (?P<example>.+?))?\n"
    matches = re.finditer(param_regex, content, re.DOTALL)
    
    params_dict = {}
    for match in matches:
        name = match.group('name')
        params_dict[name] = {
            'required': match.group('required') if match.groupdict().get('required') else None,
            'type': match.group('type'),
            'description': match.group('description').strip(),
            'example': match.group('example').strip() if match.groupdict().get('example') else None
        }
    
    return params_dict

def merge_dicts_for_argparse(config_dict, doc_dict):
    merged_dict = {}
    for param, value in config_dict.items():
        param_info = doc_dict.get(param, {})
        merged_dict[param] = {
            'default': value,
            'type': param_info.get('type', 'str'),
            'help': param_info.get('description', '') + f" (Default: {value})",
            'example': param_info.get('example', None)
        }
    return merged_dict

def string_to_type(type_string):
    # Supported types in Python
    type_mapping = {
        'str': str,
        'int': int,
        'float': float
    }
    return type_mapping.get(type_string, str)  # Default to str if type is unknown

def setup_argparse(parameters, parser=None):
    if parser is None:
        parser = argparse.ArgumentParser(description="Application Configuration")
    for param, param_info in parameters.items():
        required_value = param_info['required'].lower() == 'yes' if param_info['required'] else False
        default_value = param_info['example'].replace('`', '') if param_info['example'] else ''
        type_value = eval(param_info['type'])
        default_value = type_value(default_value) if default_value else ''
        example_value = param_info['example'].replace('`', '') if param_info['example'] else ''
        help_value = f"{param_info['description']} (Example: {example_value})"
        # Replace all '%' with '%%' to avoid formatting issues
        help_value = help_value.replace('%', '%%')
        # print(f"--{param}",
        #     required_value,
        #     default_value,
        #     type(default_value),
        #     type_value,
        #     help_value
        # )
        if required_value:
            parser.add_argument(
                f"--{param}",
                required=True,
                type=type_value,
                help=help_value
            )
        else:
            parser.add_argument(
                f"--{param}",
                default=default_value,
                type=type_value,
                help=help_value
            )
    return parser

def parse_arguments():
    parser = argparse.ArgumentParser(description="Script for active learning and model training.")

    cur_folder = os_path.join(
        os_path.dirname(
            os_path.dirname(__file__)
        ),
        'learner'
    )
    readme_path = os_path.join(cur_folder, 'README.md')
    # config_path = os_path.join(cur_folder, 'config.csv')

    # params = csv_to_dict(config_path)
    doc = parse_readme(readme_path)

    # # Create argparse parser
    # parser = setup_argparse(doc, parser)
   
    # Add all the arguments that were previously loaded from config.csv and use the CSV values as defaults
    parser.add_argument('--data_folder', required=doc['data_folder']['required'].lower()=='yes', type=eval(doc['data_folder']['type']), help=doc['data_folder']['description'].replace('%', '%%'))
    parser.add_argument('--parameter_file', required=doc['parameter_file']['required'].lower()=='yes', type=eval(doc['parameter_file']['type']), help=doc['parameter_file']['description'].replace('%', '%%'))
    parser.add_argument('--output_folder', required=doc['output_folder']['required'].lower()=='yes', type=eval(doc['output_folder']['type']), help=doc['output_folder']['description'].replace('%', '%%'))
    parser.add_argument('--name_list', required=doc['name_list']['required'].lower()=='yes', type=eval(doc['name_list']['type']), default=doc['name_list']['example'].replace('`', ''), help=doc['name_list']['description'].replace('%', '%%'))
    parser.add_argument('--nb_rep', required=doc['nb_rep']['required'].lower()=='yes', type=eval(doc['nb_rep']['type']), default=doc['nb_rep']['example'].replace('`', ''), help=doc['nb_rep']['description'].replace('%', '%%'))
    parser.add_argument('--flatten', required=doc['flatten']['required'].lower()=='yes', help=doc['flatten']['description'].replace('%', '%%'), action='store_true')
    parser.add_argument('--seed', required=doc['seed']['required'].lower()=='yes', type=eval(doc['seed']['type']), default=doc['seed']['example'].replace('`', ''), help=doc['seed']['description'].replace('%', '%%'))
    parser.add_argument('--nb_new_data_predict', required=doc['nb_new_data_predict']['required'].lower()=='yes', type=eval(doc['nb_new_data_predict']['type']), default=doc['nb_new_data_predict']['example'].replace('`', ''), help=doc['nb_new_data_predict']['description'].replace('%', '%%'))
    parser.add_argument('--nb_new_data', required=doc['nb_new_data']['required'].lower()=='yes', type=eval(doc['nb_new_data']['type']), default=doc['nb_new_data']['example'].replace('`', ''), help=doc['nb_new_data']['description'].replace('%', '%%'))
    parser.add_argument('--parameter_step', required=doc['parameter_step']['required'].lower()=='yes', type=eval(doc['parameter_step']['type']), default=doc['parameter_step']['example'].replace('`', ''), help=doc['parameter_step']['description'].replace('%', '%%'))
    parser.add_argument('--test', required=doc['test']['required'].lower()=='yes', help=doc['test']['description'].replace('%', '%%'), action='store_true')
    parser.add_argument('--n_group', required=doc['n_group']['required'].lower()=='yes', type=eval(doc['n_group']['type']), default=doc['n_group']['example'].replace('`', ''), help=doc['n_group']['description'].replace('%', '%%'))
    parser.add_argument('--ks', required=doc['ks']['required'].lower()=='yes', type=eval(doc['ks']['type']), default=doc['ks']['example'].replace('`', ''), help=doc['ks']['description'].replace('%', '%%'))
    parser.add_argument('--km', required=doc['km']['required'].lower()=='yes', type=eval(doc['km']['type']), default=doc['km']['example'].replace('`', ''), help=doc['km']['description'].replace('%', '%%'))
    parser.add_argument('--plot', required=doc['plot']['required'].lower()=='yes', help=doc['plot']['description'].replace('%', '%%'), action='store_true')
    parser.add_argument('--save_plot', required=doc['save_plot']['required'].lower()=='yes', help=doc['save_plot']['description'].replace('%', '%%'), action='store_true')

    args = parser.parse_args()
    
    # # Convert boolean-like strings to actual booleans
    # args.flatten = args.flatten.lower() == 'true'
    # args.plot = args.plot.lower() == 'true'
    
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
    output_folder = args.output_folder
    n_group = args.n_group
    ks = args.ks
    km = args.km
    plot = args.plot
    save_plot = args.save_plot

    # Proceed with the rest of the script logic
    element_list, element_max, sampling_condition = import_parameter(parameter_file, parameter_step)

    data, size_list = import_data(data_folder, verbose = True)
    if len(size_list) == 0:
        print("No data found")
        print("Exiting...")
        exit()
    check_column_names(data, element_list)

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
        print("Testing the model...")
        best_param = {'alpha': [model.best_params['alpha']],'kernel': [model.best_params['kernel']]}
        res = []
        for i in range(nb_rep):
            X_train, X_test, y_train, y_test = split_and_flatten(X, y, ratio = 0.2, flatten = flatten)

            scaler = MaxAbsScaler()
            X_train_norm = scaler.fit_transform(X_train)
            X_test_norm = scaler.transform(X_test)

            eva_model = BayesianModels(model_type ='gp', params=best_param)
            eva_model.train(X_train_norm, y_train, verbose = False)
            y_pred, std_pred = eva_model.predict(X_test_norm)
            res.append(r2_score(y_test, y_pred))

        plt.hist(res, bins = 20, color='orange')
        plt.title(f'Histogram of R2 for different testing subset, median= {np.median(res):.2f}', size = 12)
    else:
        print("Skipping testing the model...")

    X_new = sampling_without_repeat(sampling_condition, num_samples=nb_new_data_predict, existing_data=X_train, seed=seed)
    X_new_norm = scaler.transform(X_new)
    y_pred, std_pred = model.predict(X_new_norm)
    clusters = cluster(X_new_norm, n_group)

    ei = expected_improvement(y_pred, std_pred, max(y_train))
    print("For EI:")
    ei_top, y_ei, ratio_ei, ei_cluster = find_top_elements(X_new, y_pred, clusters, ei, km, return_ratio=True)
    ei_top_norm = scaler.transform(ei_top)

    # Create outfolder if it does not exist
    if not os_path.exists(output_folder):
        os.makedirs(output_folder)
    
    _output_folder = None
    if save_plot:
        _output_folder = output_folder

    if plot: 
        plot_selected_point(y_pred, std_pred, y_ei, 'EI selected', outfolder=output_folder)

        size_list.append(nb_new_data)
        y_mean = np.append(y_mean, y_ei)
        plot_each_round(y_mean,size_list, predict = True, outfolder=output_folder)

        plot_train_test(X_train_norm, ei_top_norm, element_list, outfolder=output_folder)

        fig, axes = plt.subplots(1, 1, figsize=(10, 4))
        plot_heatmap(axes, ei_top_norm, y_ei, element_list, 'EI', outfolder=output_folder)
        plt.tight_layout()
        plt.xlabel("Yield: left-low, right-high")
        plt.show()

    X_ei = pd.DataFrame(ei_top, columns=element_list)
    outfile = os_path.join(output_folder, 'next_sampling_ei'+ str(km) + '.csv')
    print(f"Saving next sampling points to {outfile}...")
    X_ei.to_csv(outfile, index=False)


if __name__ == "__main__":
    main()
 





