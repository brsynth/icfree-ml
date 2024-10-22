import numpy as np
import pandas as pd
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Matern, DotProduct, WhiteKernel
from sklearn.gaussian_process.kernels import ConstantKernel as C

def predict_rf(model, X):
    """
    Predict using a RandomForestRegressor model and return mean and standard deviation of predictions from all trees
    
    Parameters:
    - model: RandomForestRegressor
        The trained RandomForestRegressor model.
    - X: array-like
        The input features for prediction.
    
    Returns:
    - mean: ndarray
        Mean prediction across all trees.
    - std: ndarray
        Standard deviation of predictions across all trees.
    """
    tree_predictions = np.array([tree.predict(X) for tree in model.estimators_])
    mean = np.mean(tree_predictions, axis=0)
    std = np.std(tree_predictions, axis=0)
    return mean, std

def predict_gp(model, X):
    """
    Predict using a GaussianProcessRegressor model and return mean and standard deviation of predictions.
    
    Parameters:
    - model: GaussianProcessRegressor
        The trained GaussianProcessRegressor model.
    - X: array-like
        The input features for prediction.
    
    Returns:
    - mean: ndarray
        Mean prediction.
    - std: ndarray
        Standard deviation of prediction.
    """
    mean, std = model.predict(X, return_std=True)
    return mean, std

def predict_ensemble(models, X):
    """
    Predict using an ensemble of models and return mean and standard deviation of ensemble predictions.
    
    Parameters:
    - models: list of models
        The list of trained models.
    - X: array-like
        The input features for prediction.
    
    Returns:
    - pred_mean: ndarray
        Mean prediction across all models.
    - pred_std: ndarray
        Standard deviation of predictions across all models.
    """
    predictions = [model.predict(X).reshape(-1, 1) for model in models]
    pred_std = np.std(predictions, axis=0).ravel()
    pred_mean = np.mean(predictions, axis=0).ravel()
    return pred_mean, pred_std

class BayesianModels:
    def __init__(self, n_folds=5, model_type='', params=None):
        """
        Initialize the BayesianModels class with specified parameters.
        
        Parameters:
        - n_folds: int, optional (default=5)
            Number of folds for cross-validation.
        - model_type: str, optional (default='')
            The type of model to be used ('rf', 'xgboost', 'mlp', or 'gp').
        - params: dict, optional (default=None)
            Parameters for model creation. If None, default parameters for Gaussian Process are used.
        """
        self.n_folds = n_folds
        self.model_type = model_type
        self.models = []
        self.score = []
        if params is None:
            self.params = {
                'kernel': [
                    RBF() + WhiteKernel(),
                    DotProduct() + WhiteKernel(),
                    Matern(length_scale=1, nu=1.5) + WhiteKernel(),
                    RBF() + C() + WhiteKernel(),
                    Matern(length_scale=1, nu=1.5) + C() + WhiteKernel(),
                    Matern(length_scale=1, nu=1.5) + RBF() + WhiteKernel(),
                    Matern(length_scale=1, nu=1.5) + DotProduct() + WhiteKernel(),
                    RBF() + DotProduct() + WhiteKernel(),
                    RBF() * DotProduct() + WhiteKernel(),
                    RBF() + DotProduct() + C() + WhiteKernel(),
                    RBF() * DotProduct() + C() + WhiteKernel()
                ]
            }            
            self.model_type = 'gp'
        else:    
            self.params = params

    def create(self, params=None):
        """
        Create and return a model based on the specified model type and parameters.
        
        Parameters:
        - params: dict, optional
            Parameters to pass to the model constructor.
        
        Returns:
        - model: sklearn or xgboost model
            The instantiated model.
        
        Raises:
        - ValueError: If an invalid model type is specified.
        """
        model_types = {
            'rf': lambda: RandomForestRegressor(**params),
            'xgboost': lambda: XGBRegressor(**params),
            'mlp': lambda: MLPRegressor(**params),
            'gp': lambda: GaussianProcessRegressor(**params, optimizer="fmin_l_bfgs_b", n_restarts_optimizer=10)
        }

        if self.model_type not in model_types:
            raise ValueError("Invalid model type")

        return model_types[self.model_type]()

    def train(self, X, y, verbose=True):
        """
        Train the model using GridSearchCV to find the best hyperparameters.
        
        Parameters:
        - X: array-like
            The input features for training.
        - y: array-like
            The target values for training.
        - verbose: bool, optional (default=True)
            Whether to print the best hyperparameters.
        """
        if not isinstance(X, np.ndarray):
            X = np.array(X)
        if not isinstance(y, np.ndarray):
            y = np.array(y)

        model = self.create(self.params)
        grid_search = GridSearchCV(model, self.params, cv=self.n_folds, n_jobs=None, scoring='neg_root_mean_squared_error')

        grid_search.fit(X, y)
        self.best_params = grid_search.best_params_
        self.cv_score = pd.DataFrame(grid_search.cv_results_)

        if verbose:
            print(f"Best hyperparameter found: {self.best_params}")

        if self.model_type in ['gp', 'rf']:
            model = self.create(params=self.best_params)
            self.model = model.fit(X, y)

        if self.model_type in ['xgboost', 'mlp']:
            self.model = [self.create(params=self.best_params).fit(X, y) for _ in range(20)]

    def predict(self, X):
        """
        Predict using the trained model(s).
        
        Parameters:
        - X: array-like
            The input features for prediction.
        
        Returns:
        - tuple of ndarray
            Mean and standard deviation of predictions.
        """
        model_dict = {
            'rf': lambda: predict_rf(self.model, X),
            'gp': lambda: predict_gp(self.model, X),
            'xgboost': lambda: predict_ensemble(self.model, X),
            'mlp': lambda: predict_ensemble(self.model, X)
        }

        return model_dict[self.model_type]()
