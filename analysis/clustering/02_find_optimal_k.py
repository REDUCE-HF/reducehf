# ============================================
# Find optimal number of clusters (k)
# using Prediction Strength (Tibshirani & Walther, 2005)
# ============================================

from ast import main
import os
import gower
import numpy as np
import pandas as pd
from sklearn.metrics import pairwise_distances
from config import (
    D_GOWER_PATH,
    OPTIMAL_K_RESULTS_PATH,
    OPTIMAL_K_SUMMARY_PATH,
    OUTPUT_DIR,
    RAW_PATH,
    SCALED_PATH,
    X_PCA_PATH,
)
from clustering_helpers import (
    load_data,
    run_pca,
    run_kmedoids_gower,
    run_agglomerative_precomputed,
    run_kmeans,
    run_agglomerative_euclidean,
    run_optics,
    compute_prediction_strength
)



os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------
# Load data and prepare feature matrices
# -------------------
print("Loading clustering datasets...")
X_raw, X_scaled = load_data(RAW_PATH, SCALED_PATH)

print("Computing Gower distance for raw data...")
D_gower = gower.gower_matrix(X_raw)

print("Running PCA on scaled data...")
X_pca, var_explained = run_pca(X_scaled)
print(f"PCA reduced to {X_pca.shape[1]} components (explaining {var_explained:.1%} variance)")

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
results_df.to_csv(OPTIMAL_K_RESULTS_PATH, index=False)
print(f"\nSaved detailed PS results to: {OPTIMAL_K_RESULTS_PATH}")

# Determine optimal k
summary = []
THRESHOLD = 0.8  # PS + SE rule

for cfg in results_df["config"].unique():
    sub = results_df[results_df["config"] == cfg]
    if "optics" in cfg:
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
summary_df.to_csv(OPTIMAL_K_SUMMARY_PATH, index=False)
print("\nSaved optimal k summary.")

# -------------------
# Save D_gower and X_pca for downstream use
# -------------------
pd.DataFrame(D_gower).to_csv(D_GOWER_PATH, index=False, compression="gzip")
print(f"Saved Gower distance matrix to: {D_GOWER_PATH}")

pd.DataFrame(X_pca).to_csv(X_PCA_PATH, index=False, compression="gzip")
print(f"Saved PCA-transformed data to: {X_PCA_PATH}")

print("Done.")


 