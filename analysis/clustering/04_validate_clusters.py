#!/usr/bin/env python3
# ============================================
# 04_validate_clusters.py
# Validate clustering results using silhouette and CH scores
# Uses optimal k from find_optimal_k.py
# Saves cluster labels for later visualization
# ============================================

import os
import numpy as np
import pandas as pd
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from config import (
    D_GOWER_PATH,
    OUTPUT_DIR,
    OPTIMAL_K_SUMMARY_PATH,
    RAW_PATH,
    SCALED_PATH,
    VALIDATION_RESULTS_PATH,
    X_PCA_PATH,
    labels_path,
)
from clustering_helpers import load_data
from find_optimal_k import (
    run_kmedoids_gower,
    run_agglomerative_precomputed,
    run_kmeans,
    run_agglomerative_euclidean,
    run_optics,
)

# -----------------------------
# Setup
# -----------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Loading datasets...")
X_raw, X_scaled = load_data(RAW_PATH, SCALED_PATH)

# -----------------------------
# Load optimal K values
# -----------------------------
opt_k_df = pd.read_csv(OPTIMAL_K_SUMMARY_PATH)
print(f"Loaded optimal k values from {OPTIMAL_K_SUMMARY_PATH}")

# -----------------------------
# Load distances and PCA
# -----------------------------
print("Loading Gower distance matrix...")
# Opensafley doesn't support .npy files 
D_gower_path = D_GOWER_PATH
if os.path.exists(D_gower_path):
    D_gower = pd.read_csv(D_gower_path, compression="gzip").values
    print(f"Loaded D_gower from {D_gower_path}")
else:
    raise FileNotFoundError(f"Gower distance matrix not found. Run find_optimal_k.py first.")

print("Loading PCA transformation...")
X_pca_path = X_PCA_PATH
if os.path.exists(X_pca_path):
    X_pca = pd.read_csv(X_pca_path, compression="gzip").values
    print(f"Loaded X_pca from {X_pca_path}")
else:
    print(f"Error: {X_pca_path} not found. Run find_optimal_k.py first.")
    raise FileNotFoundError(f"PCA model not found. Run find_optimal_k.py to generate it.")

# -----------------------------
# Utility to evaluate clustering
# -----------------------------
def evaluate(config, X, labels, metric="euclidean"):
    n_clusters = len(np.unique(labels))
    if n_clusters < 2:
        print(f"Warning: {config}: only one cluster — skipping.")
        return None
    sil = silhouette_score(X, labels, metric=metric)
    ch = calinski_harabasz_score(X_pca, labels)  
    print(f"{config}: silhouette={sil:.3f}, calinski_harabasz={ch:.1f}")
    return {"config": config, "silhouette": sil, "calinski_harabasz": ch}

# -----------------------------
# Run all clustering configurations
# -----------------------------
results = []

configs = [
    ("raw_kmedoids_gower", D_gower, run_kmedoids_gower),
    ("raw_agglomerative_gower", D_gower, run_agglomerative_precomputed),
    ("raw_optics", D_gower, run_optics),
    ("pca_kmeans_euclidean", X_pca, run_kmeans),
    ("pca_agglomerative_euclidean", X_pca, run_agglomerative_euclidean),
    ("pca_optics", X_pca, run_optics),
]

print("\nRunning cluster validation...\n")

for cfg, data, fn in configs:
    try:
        # Determine optimal k (if applicable)
        if "optics" not in cfg:
            row = opt_k_df.loc[opt_k_df["config"] == cfg]
            if row.empty or pd.isna(row["k_opt"].values[0]):
                print(f"Warning: no k_opt found for {cfg}, skipping.")
                continue
            k_opt = int(row["k_opt"].values[0])
            print(f"Evaluating {cfg} (k={k_opt})")
            labels = fn(data, k_opt)
        else:
            print(f"Evaluating {cfg} (OPTICS, no k)")
            labels = fn(data)

        # Save cluster labels for later visualization (OpenSAFELY compatible format)
        labels_df = pd.DataFrame({"cluster": labels})
        labels_file = labels_path(cfg)
        labels_df.to_csv(labels_file, index=False, compression="gzip")
        print(f"Saved labels to {labels_file}")

        # Evaluate clustering quality with appropriate metric
        if "raw" in cfg:
            X_eval = D_gower
            metric = "precomputed"
        else:
            X_eval = X_pca
            metric = "euclidean"
        
        res = evaluate(cfg, X_eval, labels, metric=metric)
        if res:
            results.append(res)

    except Exception as e:
        print(f" {cfg} failed: {e}")

# -----------------------------
# Save validation results
# -----------------------------
df = pd.DataFrame(results)
df.to_csv(VALIDATION_RESULTS_PATH, index=False)

print("\n Validation results saved to:", VALIDATION_RESULTS_PATH)
print(df)
print("\n Validation complete.")
