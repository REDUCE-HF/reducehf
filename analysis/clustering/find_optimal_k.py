# ============================================
# 02_find_optimal_k.py (Removed 02_ from name to be able to import it in validate clusters)
# Find optimal number of clusters (k)
# using Prediction Strength (Tibshirani & Walther, 2005)
# ============================================

import os
import numpy as np
import pandas as pd
from sklearn.metrics import pairwise_distances
from sklearn.cluster import KMeans, AgglomerativeClustering, OPTICS
from sklearn_extra.cluster import KMedoids
import warnings
from clustering_helpers import load_data, compute_gower, run_pca
import gower

# -------------------
# Config
# -------------------
RAW_PATH = "output/clustering/clustering_raw.csv.gz"
SCALED_PATH = "output/clustering/clustering_scaled.csv.gz"
OUTPUT_DIR = "output/clustering/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------
# Load data and prepare feature matrices
# -------------------
print("Loading clustering datasets...")
X_raw, X_scaled = load_data(RAW_PATH, SCALED_PATH)

print("Computing Gower distance for raw data...")
D_gower = compute_gower(X_raw)

print("Running PCA on scaled data...")
X_pca, var_explained = run_pca(X_scaled)
print(f"PCA reduced to {X_pca.shape[1]} components (explaining {var_explained:.1%} variance)")
def run_kmedoids_gower(D, k):
    # D is Gower distance matrix
    model = KMedoids(n_clusters=k, metric="precomputed", init="k-medoids++", random_state=42)
    return model.fit_predict(D)

def run_agglomerative_precomputed(D, k):
    # D is Gower distance matrix
    model = AgglomerativeClustering(n_clusters=k, metric="precomputed", linkage="average")
    return model.fit_predict(D)

def run_kmeans(X, k):
    return KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(X)

def run_agglomerative_euclidean(X, k):
    return AgglomerativeClustering(n_clusters=k, metric="euclidean", linkage="average").fit_predict(X)

def run_optics(X):
    # OPTICS does not require a fixed k
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        optics = OPTICS(min_samples=10, xi=0.05, metric="euclidean").fit(X)
    return optics.labels_

# -------------------
# Prediction Strength (PS) Calculation
# -------------------
def compute_prediction_strength(X, cluster_fn, k, X_raw=None, precomputed=False, n_splits=5, random_state=42):
    np.random.seed(random_state)
    ps_values = []
    
    # number of patients
    n_samples = X.shape[0]
    for split_i in range(n_splits):
        # Generate indices for the entire dataset
        idx = np.arange(n_samples)
        np.random.shuffle(idx)
        split_point = len(idx) // 2
        
        # Split the data into two halves
        idx_half1, idx_half2 = idx[:split_point], idx[split_point:]
        
        # --- 1. Prepare Data for Clustering and Prediction ---
        # Precomputed indicates if X is a distance matrix (Gower) or feature matrix (PCA)
        if precomputed:
            # subset distance matrix for half1 and half2
            D_half1 = X[np.ix_(idx_half1, idx_half1)]
            D_half2 = X[np.ix_(idx_half2, idx_half2)]
            # Cluster each half separately
            labels_half1 = cluster_fn(D_half1, k)
            labels_half2 = cluster_fn(D_half2, k)
            
            # For Gower (precomputed), centroids are computed in raw space
            X_half1_centroid_space = X_raw[idx_half1]
            X_half2_centroid_space = X_raw[idx_half2]
            distance_metric = "gower"
        else:
            # Clustering input (X_half1, X_half2) is a subset of the feature matrix (X_pca)
            X_half1 = X[idx_half1]
            X_half2 = X[idx_half2]
            labels_half1 = cluster_fn(X_half1, k)
            labels_half2 = cluster_fn(X_half2, k)
            
            # For PCA (euclidean), centroids are computed in PCA space
            X_half1_centroid_space = X_half1
            X_half2_centroid_space = X_half2
            distance_metric = "euclidean"
            
        # 1. Compute Centroids/Medoids from training data 
        if distance_metric == "gower":
            # For Gower, use medoids (actual data points) instead of centroids (means)
            medoids = []
            # For each cluster, find the medoid: the point with minimum average distance to all other cluster members
            for c in np.unique(labels_half1):
                # Get indices of points in the cluster
                cluster_members = np.where(labels_half1 == c)[0] 
                cluster_data = X_half1_centroid_space[cluster_members]
                cluster_dist = gower.gower_matrix(cluster_data)
                medoid_idx = np.argmin(cluster_dist.sum(axis=1))
                medoids.append(cluster_members[medoid_idx])
            representatives = X_half1_centroid_space[medoids]
        else:
            # For Euclidean (PCA), use centroids (mean points)
            representatives = np.vstack([X_half1_centroid_space[labels_half1 == c].mean(axis=0) for c in np.unique(labels_half1)])

        # 2. Assign test points to nearest representatives using appropriate distance metric
        if distance_metric == "gower":
            # Compute Gower distances between second half points and medoids
            combined_data = np.vstack([X_half2_centroid_space, representatives])
            dist_matrix = gower.gower_matrix(combined_data)
            # Extract distances from second half points to medoids
            n_half2 = X_half2_centroid_space.shape[0]
            distances = dist_matrix[:n_half2, n_half2:]
            nearest = np.argmin(distances, axis=1)
        else:
            # Use euclidean distance to centroids
            nearest = np.argmin(pairwise_distances(X_half2_centroid_space, representatives, metric="euclidean"), axis=1)

        # Calculate minimum co-membership
        ps_k = []
        for c in np.unique(labels_half2):
            idx_c = np.where(labels_half2 == c)[0]
            if len(idx_c) < 2: continue
            
            pairs = [(i, j) for i in idx_c for j in idx_c if i < j]
            
            # Check prediction co-membership
            same = sum(nearest[i] == nearest[j] for i, j in pairs)
            
            if pairs: ps_k.append(same / len(pairs))
        
        if ps_k: ps_values.append(min(ps_k))

    # Calculate mean PS and SE
    if not ps_values:
        return np.nan, np.nan
    return np.mean(ps_values), np.std(ps_values) / np.sqrt(n_splits)

# -------------------
# Configurations
# -------------------

configs = {
    "raw_kmedoids_gower": (D_gower, run_kmedoids_gower, True),
    "raw_agglomerative_gower": (D_gower, run_agglomerative_precomputed, True),
    
    "pca_kmeans_euclidean": (X_pca, run_kmeans, False),
    "pca_agglomerative_euclidean": (X_pca, run_agglomerative_euclidean, False),
    "pca_optics": (X_pca, run_optics, False), # PS skipped in loop below
}

# -------------------
# Run PS for each config
# -------------------
print("\nStarting prediction strength estimation...")
results = []

for cfg, (X, cluster_fn, precomputed) in configs.items():
    print(f"\nConfiguration: {cfg}")
    if "optics" in cfg:
        labels = cluster_fn(X)
        for k in range(2, 11):
            results.append({"config": cfg, "k": k, "ps": np.nan, "se": np.nan})
        print("   OPTICS skipped (no fixed k).")
        continue

    for k in range(2, 11):
        ps, se = compute_prediction_strength(
            X,
            cluster_fn,
            k,
            X_raw=X_raw,
            precomputed=precomputed,
        )
        
        results.append({"config": cfg, "k": k, "ps": ps, "se": se})
        print(f"   k={k}: PS={ps:.3f}, SE={se:.3f}, PS+SE={ps+se:.3f}")

# -------------------
# Save results
# -------------------
results_df = pd.DataFrame(results)
results_path = os.path.join(OUTPUT_DIR, "optimal_k_results.csv")
results_df.to_csv(results_path, index=False)
print(f"\nSaved detailed PS results to: {results_path}")

# Determine optimal k
summary = []
THRESHOLD = 0.8  # PS + SE rule

for cfg in results_df["config"].unique():
    sub = results_df[results_df["config"] == cfg].dropna()
    if sub.empty or "optics" in cfg:
        summary.append({"config": cfg, "k_opt": np.nan, "ps_opt": np.nan, "se_opt": np.nan})
        continue

    # Apply PS + SE >= 0.8 rule
    sub["ps_plus_se"] = sub["ps"] + sub["se"]
    eligible = sub[sub["ps_plus_se"] >= THRESHOLD] 
    
    if not eligible.empty:
        # Find the largest k satisfying the rule
        best = eligible.loc[eligible["k"].idxmax()]  
    else:
        # Fallback: Find the most stable k if none meet the threshold
        best = sub.loc[sub["ps"].idxmax()]           

    summary.append({
        "config": cfg,
        "k_opt": int(best["k"]),
        "ps_opt": float(best["ps"]),
        "se_opt": float(best["se"]),
    })

summary_df = pd.DataFrame(summary)
summary_df.to_csv(os.path.join(OUTPUT_DIR, "optimal_k_summary.csv"), index=False)
print("\nSaved optimal k summary.")

# -------------------
# Save D_gower and X_pca for downstream use
# -------------------
pd.DataFrame(D_gower).to_csv(os.path.join(OUTPUT_DIR, "D_gower.csv.gz"), index=False, compression="gzip")
print(f"Saved Gower distance matrix to: {os.path.join(OUTPUT_DIR, 'D_gower.csv.gz')}")

pd.DataFrame(X_pca).to_csv(os.path.join(OUTPUT_DIR, "X_pca.csv.gz"), index=False, compression="gzip")
print(f"Saved PCA-transformed data to: {os.path.join(OUTPUT_DIR, 'X_pca.csv.gz')}")

print("Done.")
