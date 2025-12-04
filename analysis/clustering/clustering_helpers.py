import os
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
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
