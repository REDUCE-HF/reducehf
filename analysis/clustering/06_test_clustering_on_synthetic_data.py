#!/usr/bin/env python3
# ============================================
# 07_test_clustering_on_synthetic_data.py
# Validate clustering algorithms on synthetic data with known clusters
# ============================================

import os
import numpy as np
import pandas as pd
import gower_exp as gower
import config
from clustering_helpers import (
    run_pca,
    run_kmedoids_gower,
    run_agglomerative_precomputed,
    run_kmeans,
    run_agglomerative_euclidean,
    evaluate_clustering,
)

# -------------------
# Setup
# -------------------

os.makedirs(config.SYNTHETIC_OUTPUT_DIR, exist_ok=True)

print("=" * 70)
print("CLUSTERING VALIDATION ON SYNTHETIC DATA")
print("=" * 70)

# Load synthetic data
print("\nLoading synthetic data...")

if not os.path.exists(config.SYNTHETIC_RAW_PATH):
    print("ERROR: Synthetic data not found. Run 00_generate_synthetic_test_data.py first.")
    exit(1)

X_raw = pd.read_csv(config.SYNTHETIC_RAW_PATH, compression="gzip").drop(columns=["patient_id"]).values
X_scaled = pd.read_csv(config.SYNTHETIC_SCALED_PATH, compression="gzip").drop(columns=["patient_id"]).values

# Load true labels
y_true = pd.read_csv(config.SYNTHETIC_LABELS_PATH, compression="gzip")["cluster_true"].values

print(f"Synthetic data shape: {X_raw.shape}")
print(f"True clusters: {np.unique(y_true)}")
print(f"Cluster distribution: {np.bincount(y_true)}")

# Compute Gower distance and PCA
print("\nPreparing distance matrices and transformations...")
D_gower = gower.gower_matrix(X_raw)
print(f"Gower distance matrix: {D_gower.shape}")

X_pca, var_explained = run_pca(X_scaled)
print(f"PCA transformed to {X_pca.shape[1]} components ({var_explained:.1%} variance)")

# -------------------
# Clustering Configurations
# -------------------
configs = {
    "raw_kmedoids_gower": (D_gower, run_kmedoids_gower, config.N_CENTERS),
    "raw_agglomerative_gower": (D_gower, run_agglomerative_precomputed, config.N_CENTERS),
    "pca_kmeans_euclidean": (X_pca, run_kmeans, config.N_CENTERS),
    "pca_agglomerative_euclidean": (X_pca, run_agglomerative_euclidean, config.N_CENTERS),
}

# -------------------
# Run Clustering & Validation
# -------------------
print("\n" + "=" * 70)
print("RUNNING CLUSTERING ALGORITHMS")
print("=" * 70)

results = []

for config_name, (X, cluster_fn, k) in configs.items():
    print(f"\n{config_name}:")
    labels = cluster_fn(X, k)

    metrics = evaluate_clustering(config_name, X, labels)
    results.append({
        "config": config_name,
        "k": k,
        "silhouette": metrics["silhouette"],
        "calinski_harabasz": metrics["calinski_harabasz"],
        "n_clusters_found": len(np.unique(labels[labels != -1])),
    })
    print(f"  sil={metrics['silhouette']:.3f} | CH={metrics['calinski_harabasz']:.1f}")

# -------------------
# Save Results
# -------------------
results_df = pd.DataFrame(results)
results_df.to_csv(config.SYNTHETIC_VALIDATION_RESULTS_PATH, index=False)
print("\nSummary:")
print(results_df.to_string(index=False))
print(f"\nResults saved to: {config.SYNTHETIC_VALIDATION_RESULTS_PATH}")
