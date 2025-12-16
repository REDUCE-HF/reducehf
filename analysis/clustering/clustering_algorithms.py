#!/usr/bin/env python3
# ============================================
# clustering_algorithms.py
# Clustering algorithm wrapper functions
# Used by find_optimal_k.py, 04_validate_clusters.py, and 07_test_clustering_on_synthetic_data.py
# ============================================

import warnings
import numpy as np
from sklearn.cluster import KMeans, AgglomerativeClustering, OPTICS
from sklearn_extra.cluster import KMedoids


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
