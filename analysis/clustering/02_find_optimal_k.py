# ============================================
# 02_find_optimal_k.py
# Find optimal number of clusters (k)
# using Prediction Strength (Tibshirani & Walther, 2005)
# ============================================

import os
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, AgglomerativeClustering, OPTICS
from sklearn.decomposition import PCA
from sklearn.metrics import pairwise_distances
from sklearn_extra.cluster import KMedoids
import gower
import warnings

# -------------------
# Config
# -------------------
RAW_PATH = "output/clustering/clustering_raw.csv.gz"
SCALED_PATH = "output/clustering/clustering_scaled.csv.gz"
OUTPUT_DIR = "output/clustering/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------
# Load raw + scaled data
# -------------------
print("Loading clustering datasets...")
raw_df = pd.read_csv(RAW_PATH)
scaled_df = pd.read_csv(SCALED_PATH)

id_col = "patient_id"
feature_cols_raw = [c for c in raw_df.columns if c != id_col]
feature_cols_scaled = [c for c in scaled_df.columns if c != id_col]

X_raw = raw_df[feature_cols_raw].values
X_scaled = scaled_df[feature_cols_scaled].values

# -------------------
# Compute Gower distance for raw data
# -------------------
print("Computing Gower distance matrix for raw data...")
X_raw_float = X_raw.astype(np.float64)
gower_dist = gower.gower_matrix(X_raw_float)

# -------------------
# PCA on scaled data
# -------------------
print("Running PCA on scaled data...")
pca = PCA(n_components=0.8, svd_solver="auto", random_state=42)
X_pca = pca.fit_transform(X_scaled)
print(f"   Reduced to {X_pca.shape[1]} components explaining {pca.explained_variance_ratio_.sum():.1%}")

# -------------------
# Clustering functions
# -------------------
def run_kmedoids_gower(D, k):
    """K-Medoids clustering using precomputed Gower distance matrix."""
    model = KMedoids(n_clusters=k, metric="precomputed", init="k-medoids++", random_state=42)
    labels = model.fit_predict(D)
    return labels

def run_agglomerative_gower(D, k):
    """Agglomerative clustering using Gower distance matrix."""
    model = AgglomerativeClustering(n_clusters=k, affinity="precomputed", linkage="average")
    labels = model.fit_predict(D)
    return labels

def run_optics_gower(D):
    """OPTICS clustering using Gower distance matrix (not used for now)."""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        optics = OPTICS(min_samples=10, metric="precomputed", cluster_method="xi").fit(D)
    return optics.labels_

def run_kmeans(X, k):
    """K-Means clustering."""
    return KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(X)

def run_agglomerative(X, k):
    """Agglomerative clustering (Euclidean distance)."""
    return AgglomerativeClustering(n_clusters=k, affinity="euclidean", linkage="average").fit_predict(X)

def run_optics(X):
    """OPTICS clustering (Euclidean distance)."""
    optics = OPTICS(min_samples=10, metric="euclidean", cluster_method="xi").fit(X)
    return optics.labels_

# -------------------
# Prediction Strength
# -------------------
def compute_prediction_strength(X, cluster_fn, k, precomputed=False, n_splits=5, random_state=42):
    np.random.seed(random_state)
    ps_values = []

    for _ in range(n_splits):
        # Randomly split data into two halves for prediction strength calculation
        # This tests whether clusters found in one half are reproducible in the other half
        idx = np.arange(X.shape[0])  # Create array of indices [0, 1, 2, ..., n-1]
        np.random.shuffle(idx)  # Randomly permute the indices
        split = int(len(idx) / 2)  # Find midpoint for 50/50 split
        idx1, idx2 = idx[:split], idx[split:]  # Split indices into training and test sets
        X1, X2 = X[idx1], X[idx2]  # Extract corresponding data rows using indices

        # Cluster both halves independently
        # For precomputed distances: extract sub-matrices using np.ix_ (rows AND columns)
        # For feature matrices: use the data directly (X1, X2)
        if precomputed:
            D1 = X[np.ix_(idx1, idx1)]  # Training distance sub-matrix
            D2 = X[np.ix_(idx2, idx2)]  # Test distance sub-matrix
            labels1 = cluster_fn(D1, k)
            labels2 = cluster_fn(D2, k)
        else:
            labels1 = cluster_fn(X1, k)
            labels2 = cluster_fn(X2, k)

        # Compute centroids from first half
        centroids = []
        for c in np.unique(labels1):
            centroids.append(X1[labels1 == c].mean(axis=0))
        centroids = np.vstack(centroids)

        # Assign second-half points to nearest centroids
        dists = pairwise_distances(X2, centroids, metric="euclidean")
        nearest = np.argmin(dists, axis=1)

        ps_k = []
        for c in np.unique(labels2):
            idx_c = np.where(labels2 == c)[0]
            if len(idx_c) < 2:
                continue
            n_pairs, same = 0, 0
            for i in range(len(idx_c)):
                for j in range(i + 1, len(idx_c)):
                    n_pairs += 1
                    if nearest[idx_c[i]] == nearest[idx_c[j]]:
                        same += 1
            if n_pairs > 0:
                ps_k.append(same / n_pairs)

        if ps_k:
            ps_values.append(min(ps_k))

    return np.mean(ps_values), np.std(ps_values) / np.sqrt(n_splits)

# -------------------
# Configurations
# -------------------
configs = {
    # Raw data (Gower distance)
    "raw_kmedoids_gower": (gower_dist, run_kmedoids_gower, True),
    "raw_agglomerative_gower": (gower_dist, run_agglomerative_gower, True),
    "raw_optics_gower": (gower_dist, run_optics_gower, True),  # defined, not used for PS

    # PCA data (Euclidean)
    "pca_kmeans_euclidean": (X_pca, run_kmeans, False),
    "pca_agglomerative_euclidean": (X_pca, run_agglomerative, False),
    "pca_optics_euclidean": (X_pca, run_optics, False),  # defined, not used for PS
}

# -------------------
# Run PS for each config
# -------------------
results = []
print("\nStarting prediction strength estimation...")

for cfg_name, (X, cluster_fn, precomputed) in configs.items():
    print(f"\nConfiguration: {cfg_name}")
    if "optics" in cfg_name:
        for k in range(2, 11):
            results.append({"config": cfg_name, "k": k, "ps": np.nan, "se": np.nan})
        print("   OPTICS (density-based); PS skipped.")
        continue

    for k in range(2, 11):
        ps, se = compute_prediction_strength(X, cluster_fn, k, precomputed)
        results.append({"config": cfg_name, "k": k, "ps": ps, "se": se})
        print(f"   k={k}: PS={ps:.3f}, SE={se:.3f}, PS+SE={ps+se:.3f}")

# -------------------
# Save results
# -------------------
results_df = pd.DataFrame(results)
results_path = os.path.join(OUTPUT_DIR, "optimal_k_results.csv")
results_df.to_csv(results_path, index=False)
print(f"\nSaved detailed PS results to: {results_path}")

# Determine best k per configuration
summary = []
for cfg in results_df["config"].unique():
    sub = results_df[results_df["config"] == cfg].copy()
    if "optics" in cfg:
        summary.append({"config": cfg, "k_opt": np.nan, "ps_opt": np.nan, "se_opt": np.nan})
        continue
    valid_ks = sub[sub["ps"] + sub["se"] >= 0.8]
    if not valid_ks.empty:
        best_row = valid_ks.iloc[-1]  # largest k satisfying PS+SE ≥ 0.8
    else:
        best_row = sub.loc[sub["ps"].idxmax()]  #  max PS
    summary.append({
        "config": cfg,
        "k_opt": int(best_row["k"]),
        "ps_opt": float(best_row["ps"]),
        "se_opt": float(best_row["se"]),
    })

summary_df = pd.DataFrame(summary)
summary_path = os.path.join(OUTPUT_DIR, "optimal_k_summary.csv")
summary_df.to_csv(summary_path, index=False)
print("\nSaved optimal k summary to:", summary_path)
print("\nAll done.")
