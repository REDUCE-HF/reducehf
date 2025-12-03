# ============================================
# 02_find_optimal_k.py (Removed 02_ from name to be able to import it in validate clusters)
# Find optimal number of clusters (k)
# using Prediction Strength (Tibshirani & Walther, 2005)
# ============================================

import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
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

# -------------------
# Clustering functions
# -------------------
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
    # Parameters set arbitrarily; tuning is required in 03_tune_optics.py
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        optics = OPTICS(min_samples=10, xi=0.05, metric="euclidean").fit(X)
    return optics.labels_

# -------------------
# Prediction Strength (PS) Calculation
# -------------------
def compute_prediction_strength(X, cluster_fn, k, precomputed=False, n_splits=5, random_state=42):
    np.random.seed(random_state)
    ps_values = []
    
    # We must index the feature matrix based on the split indices, so we grab the indices only once.
    n_samples = X.shape[0]
    for split_i in range(n_splits):
        # Generate indices for the entire dataset
        idx = np.arange(n_samples)
        np.random.shuffle(idx)
        split_point = len(idx) // 2
        
        # idx1 = Training Indices, idx2 = Test Indices
        idx1, idx2 = idx[:split_point], idx[split_point:]
        
        # --- 1. Prepare Data for Clustering and Prediction ---
        
        if precomputed:
            # Clustering input (D1, D2) is a subset of the D_gower distance matrix (X)
            D1 = X[np.ix_(idx1, idx1)]
            D2 = X[np.ix_(idx2, idx2)]
            labels1 = cluster_fn(D1, k)
            labels2 = cluster_fn(D2, k)
            
            # For Gower (precomputed), centroids are computed in raw space
            X1_centroid_space = X_raw[idx1]
            X2_centroid_space = X_raw[idx2]
            distance_metric = "gower"
        else:
            # Clustering input (X1, X2) is a subset of the feature matrix (X_pca)
            X1 = X[idx1]
            X2 = X[idx2]
            labels1 = cluster_fn(X1, k)
            labels2 = cluster_fn(X2, k)
            
            # For PCA (euclidean), centroids are computed in reduced space
            X1_centroid_space = X1
            X2_centroid_space = X2
            distance_metric = "euclidean"
            
        # 1. Compute Centroids from training data in the appropriate space
        centroids = np.vstack([X1_centroid_space[labels1 == c].mean(axis=0) for c in np.unique(labels1)])

        # 2. Assign test points to nearest centroids using appropriate distance metric
        if distance_metric == "gower":
            # Compute Gower distances between test points and centroids
            # Use gower library to compute pairwise distances efficiently
            combined_data = np.vstack([X2_centroid_space, centroids])
            dist_matrix = gower.gower_matrix(combined_data)
            # Extract distances from test points to centroids
            n_test = X2_centroid_space.shape[0]
            distances = dist_matrix[:n_test, n_test:]
            nearest = np.argmin(distances, axis=1)
        else:
            # Use euclidean distance
            nearest = np.argmin(pairwise_distances(X2_centroid_space, centroids, metric="euclidean"), axis=1)

        # 3. Calculate minimum co-membership
        ps_k = []
        for c in np.unique(labels2):
            idx_c = np.where(labels2 == c)[0]
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
# PS on Gower (distance matrix) is methodologically compromised due to the centroid step 
# requiring feature data, which defeats the purpose of Gower. However, we proceed 
# by using X_raw features for the centroid calculation as the only way to run PS.
configs = {
    # Raw data (Gower distance) - X is D_gower (distance matrix)
    "raw_kmedoids_gower": (D_gower, run_kmedoids_gower, True),
    "raw_agglomerative_gower": (D_gower, run_agglomerative_precomputed, True),
    
    # PCA data (Euclidean) - X is X_pca (feature matrix)
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
THRESHOLD = 0.8  # PS rule

for cfg in results_df["config"].unique():
    sub = results_df[results_df["config"] == cfg].dropna()
    if sub.empty or "optics" in cfg:
        summary.append({"config": cfg, "k_opt": np.nan, "ps_opt": np.nan, "se_opt": np.nan})
        continue

    # Apply PS >= 0.8 rule 
    
    eligible = sub[sub["ps"] >= THRESHOLD] 
    
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
print("Done.")
