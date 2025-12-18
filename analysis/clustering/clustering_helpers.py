import os
import warnings
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, AgglomerativeClustering, OPTICS
from sklearn_extra.cluster import KMedoids
import gower_exp as gower
from config import RAW_PATH, SCALED_PATH

# ============================================
# Common helper functions for clustering scripts
# ============================================

def load_data(raw_path=RAW_PATH, scaled_path=SCALED_PATH):
    """Load raw and scaled datasets and return both DataFrames and feature arrays."""
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Missing file: {raw_path}")
    if not os.path.exists(scaled_path):
        raise FileNotFoundError(f"Missing file: {scaled_path}")

    raw_df = pd.read_csv(raw_path)
    scaled_df = pd.read_csv(scaled_path)
    
    id_col = "patient_id"
    
    # Extract feature matrices (NumPy arrays)
    # The feature columns are all columns except the 'patient_id'
    X_raw = raw_df.drop(columns=[id_col]).astype(float).values
    X_scaled = scaled_df.drop(columns=[id_col]).values
    
    # Return all four expected variables
    return X_raw, X_scaled

def load_feature_names(raw_path=RAW_PATH):
    """
    Load the list of feature names (column names) from the raw data file.

    """
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Missing file: {raw_path}")

    raw_df = pd.read_csv(raw_path)
    id_col = "patient_id"
    # Return column names, excluding the patient ID
    return raw_df.drop(columns=[id_col], errors='ignore').columns.tolist()


def compute_gower(X):
    """Compute Gower distance matrix ."""
    X_float = X.astype(np.float64)
    return gower.gower_matrix(X_float)


def run_pca(X_scaled, var_threshold=0.8):
    """Run PCA to reduce dimensions until target variance explained.
    
    Returns:
        X_pca: Transformed data in reduced PCA space
        var_explained: Total variance explained
    """
    pca = PCA(n_components=var_threshold, svd_solver="full", random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    var_explained = pca.explained_variance_ratio_.sum()
    return X_pca, var_explained


# ============================================
# Clustering algorithm wrapper functions
# ============================================

def run_kmedoids_gower(D, k):
    """
    Run k-medoids clustering on precomputed Gower distance matrix.
    
    Args:
        D: Precomputed distance matrix (Gower)
        k: Number of clusters
        
    Returns:
        Cluster labels
    """
    model = KMedoids(n_clusters=k, metric="precomputed", init="k-medoids++", random_state=42)
    return model.fit_predict(D)


def run_agglomerative_precomputed(D, k):
    """
    Run agglomerative clustering on precomputed distance matrix.
    
    Args:
        D: Precomputed distance matrix (Gower)
        k: Number of clusters
        
    Returns:
        Cluster labels
    """
    model = AgglomerativeClustering(n_clusters=k, metric="precomputed", linkage="average")
    return model.fit_predict(D)


def run_kmeans(X, k):
    """
    Run k-means clustering on feature matrix.
    
    Args:
        X: Feature matrix (e.g., PCA-transformed data)
        k: Number of clusters
        
    Returns:
        Cluster labels
    """
    return KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(X)


def run_agglomerative_euclidean(X, k):
    """
    Run agglomerative clustering with Euclidean distance.
    
    Args:
        X: Feature matrix (e.g., PCA-transformed data)
        k: Number of clusters
        
    Returns:
        Cluster labels
    """
    return AgglomerativeClustering(n_clusters=k, metric="euclidean", linkage="average").fit_predict(X)


def run_optics(X):
    """
    Run OPTICS clustering (does not require fixed k).
    
    Args:
        X: Feature matrix (e.g., PCA-transformed data)
        
    Returns:
        Cluster labels (-1 for noise points)
    """
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        optics = OPTICS(min_samples=10, xi=0.05, metric="euclidean").fit(X)
    return optics.labels_
