import os
import warnings
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, AgglomerativeClustering, OPTICS
from sklearn_extra.cluster import KMedoids
import gower_exp as gower
from config import (
    RAW_PATH, SCALED_PATH,
    MEMBERSHIP_DATE_COLS, AGE_BINS, AGE_LABELS, HOUSEHOLD_BINS, HOUSEHOLD_LABELS,
    CATEGORICAL_COLS, DATE_BASED_CONDITIONS, OBESITY_DATE_COLS, OBESITY_BMI_THRESHOLD,
    LTC_COLS, UNDERSERVED_COLS, CONDITION_TIME_WINDOW_DAYS, DIABETES_UNLIKELY_VALUE,
    DIAGNOSIS_PRIMARY_COL, DIAGNOSIS_HOSPITAL_COLS
)

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

def get_best_config(validation_results_path):
    """
    Load validation results and return the best configuration name.
    """
    if not os.path.exists(validation_results_path):
        raise FileNotFoundError(f"Validation results not found: {validation_results_path}")
    
    val_df = pd.read_csv(validation_results_path)
    # add ranks rather than adding scores because scales are very differnt
    val_df["rank"] = (val_df["silhouette"].rank(ascending=False) + 
                      val_df["calinski_harabasz"].rank(ascending=False))
    
    best_config = val_df.sort_values("rank").iloc[0]["config"]
    
    return best_config


def variance_of_means(labels, X):
    """Calculate variance of cluster means for each feature."""
    df = X.assign(cluster=labels)
    df = df[df["cluster"] != -1]
    return df.groupby("cluster").mean(numeric_only=True).var()

def get_diagnosis_location(df):
    """
    Determine diagnosis location (community vs emergency) based on earliest diagnosis date.
    
    """
    all_diag_cols = [DIAGNOSIS_PRIMARY_COL, *DIAGNOSIS_HOSPITAL_COLS]
    diag_dates = df[all_diag_cols].apply(pd.to_datetime, errors="coerce")

    primary_date = diag_dates[DIAGNOSIS_PRIMARY_COL]
    earliest_overall = diag_dates.min(axis=1)

    diagnosis_community = primary_date.eq(earliest_overall).astype(int)
    diagnosis_emergency = (1- diagnosis_community).astype(int)

    return diagnosis_community, diagnosis_emergency

def build_membership_features(df):
    """Build membership features for cluster characterization."""
    out = pd.DataFrame({"patient_id": df["patient_id"]},index=df.index)

    # Convert all date columns to datetime
    dates_df = {col: pd.to_datetime(df[col], errors="coerce") 
             for col in MEMBERSHIP_DATE_COLS }
    
    # Diagnosis location
    out["diagnosis_community"], out["diagnosis_emergency"] = get_diagnosis_location(df)
    
    # Age bands
    age = np.floor((dates_df["patient_index_date"] - dates_df["birth_date"]).dt.days / 365.25)
    out["age_band"] = pd.cut(age, bins=AGE_BINS, labels=AGE_LABELS, right=False).astype("object")
    
    # Categorical variables - Household size
    hs_numeric = pd.to_numeric(df["household_size"], errors="coerce")
    out["cat_household_size"] = pd.cut(
        hs_numeric,
        bins=HOUSEHOLD_BINS,
        labels=HOUSEHOLD_LABELS,
        right=True,
        include_lowest=True
    ).astype("object")

    out.loc[hs_numeric.isna() | (hs_numeric <= 0), "cat_household_size"] = "unknown"

    for col in CATEGORICAL_COLS:
        out[col] = df[col].astype("object")
    
    # Create pre_existing and new conditions based on time window before hf diagnosis
    hf_diagnosis_date = dates_df["hf_diagnosis_date"]
    time_window = pd.Timedelta(days=CONDITION_TIME_WINDOW_DAYS)
    
    for condition, cols in DATE_BASED_CONDITIONS.items():
        condition_dates = pd.DataFrame({c: dates_df.get(c) for c in cols if c in dates_df})
        first_date = condition_dates.min(axis=1)
        out[f"{condition}_preexisting"] = (first_date < (hf_diagnosis_date - time_window)).fillna(False).astype(int)
        out[f"{condition}_new"] = ((first_date >= (hf_diagnosis_date - time_window)) & (first_date <= hf_diagnosis_date)).fillna(False).astype(int)
    
    # Obesity: combine date-based and BMI-based
    obesity_dates = pd.DataFrame({c: dates_df.get(c) for c in OBESITY_DATE_COLS if c in dates_df})
    obesity_from_dates = obesity_dates.notna().any(axis=1).astype(int) if not obesity_dates.empty else 0
    obesity_bmi = (pd.to_numeric(df["bmi_value"], errors="coerce") >= OBESITY_BMI_THRESHOLD).fillna(False).astype(int)
    out["obesity"] = ((obesity_from_dates == 1) | (obesity_bmi == 1)).astype(int)
    
    # Diabetes
    out["has_diabetes"] = (df["cat_diabetes"] != DIABETES_UNLIKELY_VALUE).astype(int)
    
    # Multi-morbidity
    out["mltc_count"] = out[LTC_COLS].sum(axis=1)
    out["has_mltc"] = (out["mltc_count"] >= 2).astype(int)
    
    # Under-served groups
    for col in UNDERSERVED_COLS:
        out[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    
    return out
