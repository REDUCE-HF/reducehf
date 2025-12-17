#!/usr/bin/env python3
# ============================================
# 07_test_clustering_on_synthetic_data.py
# Validate clustering algorithms on synthetic data with known clusters
# ============================================

import os
import numpy as np
import pandas as pd
from sklearn.metrics import (
    adjusted_rand_score,
    normalized_mutual_info_score,
    homogeneity_score,
    completeness_score,
    v_measure_score,
    fowlkes_mallows_score
)
import config
from clustering_helpers import (
    load_data,
    compute_gower,
    run_pca,
    run_kmedoids_gower,
    run_agglomerative_precomputed,
    run_kmeans,
    run_agglomerative_euclidean,
    run_optics,
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
D_gower = compute_gower(X_raw)
print(f"Gower distance matrix: {D_gower.shape}")

X_pca, var_explained = run_pca(X_scaled)
print(f"PCA transformed to {X_pca.shape[1]} components ({var_explained:.1%} variance)")

# -------------------
# Clustering Configurations
# -------------------
configs = {
    "raw_kmedoids_gower": (D_gower, run_kmedoids_gower, True, 5),
    "raw_agglomerative_gower": (D_gower, run_agglomerative_precomputed, True, 5),
    "pca_kmeans_euclidean": (X_pca, run_kmeans, False, 5),
    "pca_agglomerative_euclidean": (X_pca, run_agglomerative_euclidean, False, 5),
}

# -------------------
# Evaluation Metrics
# -------------------
def evaluate_clustering(y_pred, y_true, config_name):
    """Calculate clustering quality metrics."""
    
    # Skip if only one cluster
    if len(np.unique(y_pred)) < 2:
        return None
    
    metrics = {
        "config": config_name,
        "n_clusters_found": len(np.unique(y_pred)),
        "n_clusters_true": len(np.unique(y_true)),
    }
    
    # Cluster agreement metrics (higher is better, range 0-1)
    metrics["adjusted_rand_index"] = adjusted_rand_score(y_true, y_pred)
    metrics["normalized_mutual_info"] = normalized_mutual_info_score(y_true, y_pred)
    metrics["v_measure"] = v_measure_score(y_true, y_pred)
    metrics["fowlkes_mallows"] = fowlkes_mallows_score(y_true, y_pred)
    
    # Homogeneity & completeness (range 0-1, higher better)
    metrics["homogeneity"] = homogeneity_score(y_true, y_pred)
    metrics["completeness"] = completeness_score(y_true, y_pred)
    
    return metrics

# -------------------
# Run Clustering & Validation
# -------------------
print("\n" + "=" * 70)
print("RUNNING CLUSTERING ALGORITHMS")
print("=" * 70)

results = []

for config_name, (X, cluster_fn, precomputed, k) in configs.items():
    try:
        print(f"\n{config_name}:")
        print(f"  Running with k={k}...")
        
        if precomputed:
            labels = cluster_fn(X, k)
        else:
            labels = cluster_fn(X, k)
        
        print(f"  Clusters found: {len(np.unique(labels))}")
        print(f"  Cluster sizes: {np.bincount(labels)}")
        
        # Evaluate
        metrics = evaluate_clustering(labels, y_true, config_name)
        if metrics:
            results.append(metrics)
            
            # Print results
            print(f"\n  VALIDATION METRICS:")
            print(f"    Adjusted Rand Index:      {metrics['adjusted_rand_index']:.4f}")
            print(f"    Normalized Mutual Info:   {metrics['normalized_mutual_info']:.4f}")
            print(f"    V-Measure:                {metrics['v_measure']:.4f}")
            print(f"    Fowlkes-Mallows Index:    {metrics['fowlkes_mallows']:.4f}")
            print(f"    Homogeneity:              {metrics['homogeneity']:.4f}")
            print(f"    Completeness:             {metrics['completeness']:.4f}")
    
    except Exception as e:
        print(f"  ERROR: {e}")

# -------------------
# Save Results
# -------------------
if results:
    results_df = pd.DataFrame(results)
    results_df.to_csv(config.SYNTHETIC_VALIDATION_RESULTS_PATH, index=False)
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(results_df.to_string(index=False))
    print(f"\nResults saved to: {config.SYNTHETIC_VALIDATION_RESULTS_PATH}")
    
    # Identify best algorithm
    best_config = results_df.loc[results_df["v_measure"].idxmax()]
    print(f"\nBest algorithm: {best_config['config']} (V-Measure: {best_config['v_measure']:.4f})")
else:
    print("\nNo results to save.")

print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)
print("""
METRICS EXPLANATION:
- Adjusted Rand Index (ARI): Measures cluster agreement, accounts for chance
  Range: [-1, 1], Perfect: 1.0, Random: 0.0
  
- Normalized Mutual Info (NMI): Information-theoretic measure
  Range: [0, 1], Perfect: 1.0, Random: 0.0
  
- V-Measure: Harmonic mean of homogeneity and completeness
  Range: [0, 1], Perfect: 1.0, Random: 0.0
  
- Fowlkes-Mallows Index: Pairwise precision and recall
  Range: [0, 1], Perfect: 1.0, Random: 0.0
  
- Homogeneity: All samples in same true cluster → same predicted cluster
  Range: [0, 1], Perfect: 1.0
  
- Completeness: All samples in same predicted cluster → same true cluster
  Range: [0, 1], Perfect: 1.0

✓ Scores > 0.8 = Excellent algorithm recovery
✓ Scores 0.6-0.8 = Good algorithm recovery
✓ Scores < 0.6 = Poor algorithm recovery
""")

print("Done!")
