import numpy as np
from scipy.stats import norm
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from matplotlib import pyplot as plt


def sample_new_combination(sampling_condition, nb_sample = 100000, seed=None):
    """
    Generate random experiments by samples from each component of sampling_condition
    Removes NaN values from each column before sampling and samples are drawn with replacement

    Parameters:
    - sampling_condition (pandas.DataFrame): DataFrame containing all concentration/volume to pick
    - nb_sample (int, optional): Number of samples to draw from each column. Default is 100000.
    - seed (int, optional): Seed for the random number generator. Default is None.

    Returns:
    - numpy.ndarray: An array where each row is a sample with values drawn from each column of the DataFrame.

    """
    sampled_data = []
    np.random.seed(seed)
    for i in range(sampling_condition.shape[1]):
        sample_pool = sampling_condition.iloc[:,i]
        sample_pool = sample_pool[~np.isnan(sample_pool)] # remove nan if exits
        drawn_samples = np.random.choice(sample_pool , size = nb_sample, replace = True)
        sampled_data.append(drawn_samples)
    sampled_data = np.array(sampled_data).transpose()
    return sampled_data 


def sampling_without_repeat(sampling_condition, num_samples, existing_data, seed=None):
    """
    Generates a new set of samples based on the sampling condition, ensuring 
    that the generated samples do not repeat any of the existing data.

    Parameters:
    - sampling_condition (pandas.DataFrame): DataFrame containing all concentration/volume to pick
    - num_samples (int):The number of samples to generate initially
    - existing_data (array-like or np.ndarray):
        The existing data set to avoid repetitions with the new samples.
    - seed (int, optional): Seed for the random generator to ensure reproducibility
        If not provided, randomness will be uncontrolled.

    Returns:
    - new_samples (np.ndarray): A new set of samples that do not repeat the existing data.
    """
    if not isinstance(existing_data, np.ndarray):
        existing_data = np.array(existing_data)

    new_samples = sample_new_combination(sampling_condition, num_samples, seed=seed)

    while True:
        matches = np.all(new_samples[:, np.newaxis] == existing_data, axis=-1)
        rows_to_drop = np.any(matches, axis=1)

        if not np.any(rows_to_drop):
            break

        num_repeats = sum(rows_to_drop)
        resampled = sample_new_combination(sampling_condition, num_samples=num_repeats, seed=None)
        new_samples = new_samples[~rows_to_drop]
        new_samples = np.concatenate([new_samples, resampled])

    return new_samples


def find_top_elements(X, y, cluster_list, condition, n, return_ratio=False, verbose=False):
    """
    Finds the top 'n' elements from X, y, and cluster_list based on the highest values in 'condition'

    Parameters:
    - X (array-like or np.ndarray)
        Feature matrix where rows represent samples and columns represent features
    - y (array-like or np.ndarray)
        Target values or outcomes corresponding to the samples in X
    - cluster_list (list of int)
        name of cluster corresponding to the samples in X
    - condition (list)
        EI / PI/ UCB score used to rank the informativeness of samples in X
    - n (int)
        Number of top samples to return based on the highest 'condition' scores
    - return_ratio (bool, optional, default=False)
        Whether to return the ratio of the top elements based on 'condition'
        this is ratio between exploration and exploitation (only use when ucb as surrogate function)
    - verbose : bool, optional, default=True
        If True, prints the maximum value of the selected target 'y'

    Returns:
    - choosen_X (np.ndarray): The top 'n' samples from X corresponding to the highest 'condition' values.
    - choosen_y (np.ndarray): The target values 'y' corresponding to the top 'n' samples.
    - ratio (list): The 'condition' values corresponding to the top 'n' samples. Returned only if return_ratio is True.
    - choosen_cluster (array-like): The clusters corresponding to the top 'n' samples.
    """
    if not isinstance(X, np.ndarray):
        X = np.array(X)
    if not isinstance(y, np.ndarray):
        y = np.array(y)

    idx_top_n = np.argsort(-condition)[:n]

    choosen_X = X[idx_top_n, :]
    choosen_y = y[idx_top_n]
    choosen_cluster = np.array(cluster_list)[idx_top_n]

    if return_ratio:
        ratio = condition[idx_top_n]
    else:
        ratio = []

    if verbose:
        print(f"Maximum yield prediction = {np.max(choosen_y)}")

    return choosen_X, choosen_y, ratio, choosen_cluster


def probability_of_improvement(mu, sigma, current_best):
    """
    Calculate Probability of Improvement (PI) for Gaussian process predictions.

    Parameters:
    - mu: Mean of the Gaussian process prediction.
    - sigma: Standard deviation of the Gaussian process prediction.
    - current_best: Current best observed value.
    Returns:
    - pi: Probability of Improvement.
    """

    # Avoid division by zero
    sigma = sigma + 1e-4

    # Calculate standard normal cumulative distribution function
    z = (mu - current_best) / sigma
    pi = norm.cdf(z)

    return pi


def expected_improvement(mu, sigma, current_best):
    """
    Calculate Expected Improvement (EI) for Gaussian process predictions.

    Parameters:
    - mu: Mean of the Gaussian process prediction.
    - sigma: Standard deviation of the Gaussian process prediction.
    - current_best: Current best observed value.
    - epsilon: Small positive constant to avoid division by zero.

    Returns:
    - ei: Expected Improvement.
    """

    # Avoid division by zero
    sigma = sigma + 1e-4

    # Calculate standard normal cumulative distribution function
    z = (mu - current_best) / sigma
    ei = (mu - current_best) * norm.cdf(z) + sigma * norm.pdf(z)

    return ei

def upper_confident_bound(mu, sigma, theta, r2):
    """
    Calculate UCB for Gaussian process predictions.

    Parameters:
    - mu: Mean of the Gaussian process prediction.
    - sigma: Standard deviation of the Gaussian process prediction.
    - epsilon: Small positive constant to avoid division by zero.

    Returns:
    - ucb: 
    """
    if r2 <= 0.8:
        ucb = mu + theta*sigma
    else:
        ucb = mu
    return ucb


def cluster(X, n_clusters, method='complete', plot=False):
    """
    Performs hierarchical clustering on the given data and optionally plots the dendrogram.

    Parameters:
    - X (np.ndarray): data to be clustered, where rows are samples and columns are features.
    - n_clusters (int): The number of clusters to form.
    - method (str, optional, default='complete'): 
        The linkage algorithm to use for hierarchical clustering. Options include:
        'single', 'complete', 'average', 'ward', etc.
    - plot (bool, optional, default=False)
        If True, plots the dendrogram of the hierarchical clustering.

    Returns:
    - clusters (np.ndarray)
        Cluster labels for each sample in X. An array of size (n_samples,).
    """
    Z = linkage(X, method=method)
    clusters = fcluster(Z, n_clusters, criterion='maxclust')

    if plot:
        plt.figure(figsize=(10, 5))
        plt.title('Hierarchical Clustering Dendrogram')
        plt.xlabel('Sample Index')
        plt.ylabel('Distance')
        dendrogram(Z)
        plt.show()
    
    return clusters


def pick_by_cluster(chosen_clust, n_sample, seed=42, verbose=False):
    """
    Selects data points based on round robin sampling: arrange cluster by size (small to big), 
    in each cluster sort sample based on their EI value, then chose one point out of each cluster by order, 
    in this way we prioritize chosing the points with the highest EI value from each cluster 
    until the specified number of samples is reached

    Parameters:
    - chosen_clust (np.ndarray)
        A 2D array where the first column contains cluster labels and the second column contains EI values
    - n_sample (int): The number of samples to select.
    - seed (int, optional, default=42) rndom seed for reproducibility 
    - verbose (bool, optional, default=False)
        If True, prints information about each cluster and its size
    Returns:
    - selected_indices (list)
        List of indices representing the selected data points, based on the highest EI from each cluster
    """
    np.random.seed(seed)
    cluster_info = {}
    
    for cluster_label in np.unique(chosen_clust[:, 0]):
        indices = np.where(chosen_clust[:, 0] == cluster_label)[0]
        ei_values = chosen_clust[indices, 1]
        num_points = len(indices)
        cluster_info[cluster_label] = {'indices': indices, 'ei_values': ei_values, 'num_points': num_points}

    sorted_clusters = sorted(cluster_info.items(), key=lambda x: x[1]['num_points'], reverse=False)

    if verbose:
        for cluster_label, info in sorted_clusters:
            print(f"Cluster {cluster_label}: {info['num_points']} points")

    selected_indices = []
    selected_count = 0

    while selected_count < n_sample:
        for cluster_label, info in sorted_clusters:
            if info['indices'].size > 0:
                highest_ei_index = np.argmax(info['ei_values'])
                selected_index = info['indices'][highest_ei_index]
                selected_indices.append(selected_index)

                info['indices'] = np.delete(info['indices'], highest_ei_index)
                info['ei_values'] = np.delete(info['ei_values'], highest_ei_index)

                selected_count += 1
                if selected_count == n_sample:
                    break

    return selected_indices