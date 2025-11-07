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
from clustering_helpers import load_data, compute_gower, run_pca
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
OUTPUT_DIR = "output/clustering/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Loading datasets...")
X_raw, X_scaled, raw_df, scaled_df = load_data(
    os.path.join(OUTPUT_DIR, "clustering_raw.csv.gz"),
    os.path.join(OUTPUT_DIR, "clustering_scaled.csv.gz")
)

# Drop patient_id column if present
for df in [raw_df, scaled_df]:
    if "patient_id" in df.columns:
        df.drop(columns=["patient_id"], inplace=True)

# -----------------------------
# Load optimal K values
# -----------------------------
opt_k_path = os.path.join(OUTPUT_DIR, "optimal_k_summary.csv")
opt_k_df = pd.read_csv(opt_k_path)
print(f"Loaded optimal k values from {opt_k_path}")

# -----------------------------
# Compute distances and PCA
# -----------------------------
print("Computing Gower distance matrix for raw data...")
D_gower = compute_gower(raw_df)

print("Running PCA transformation...")
X_pca, _ = run_pca(scaled_df)

# -----------------------------
# Utility to evaluate clustering
# -----------------------------
def evaluate(config, X, labels):
    n_clusters = len(np.unique(labels))
    if n_clusters < 2:
        print(f"Warning: {config}: only one cluster — skipping.")
        return None
    sil = silhouette_score(X, labels)
    ch = calinski_harabasz_score(X, labels)
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

        # Save cluster labels for later visualization
        labels_path = os.path.join(OUTPUT_DIR, f"labels_{cfg}.npy")
        np.save(labels_path, labels)
        print(f"Saved labels to {labels_path}")

        # Evaluate clustering quality
        X_eval = raw_df.values if "raw" in cfg else X_pca
        res = evaluate(cfg, X_eval, labels)
        if res:
            results.append(res)

    except Exception as e:
        print(f" {cfg} failed: {e}")

# -----------------------------
# Save validation results
# -----------------------------
df = pd.DataFrame(results)
out_path = os.path.join(OUTPUT_DIR, "validation_results.csv")
df.to_csv(out_path, index=False)

print("\n Validation results saved to:", out_path)
print(df)
print("\n Validation complete.")
