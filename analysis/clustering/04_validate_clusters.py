# ============================================
# 04_validate_clusters.py
# Validate clustering results using silhouette and CH scores
# Uses optimal k from find_optimal_k.py
# Saves cluster labels for later visualization
# ============================================

import os
import numpy as np
import pandas as pd
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
from clustering_helpers import (
    load_data,
    
    evaluate_clustering,
)
# -----------------------------
# Setup
# -----------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Loading datasets...")
X_raw, X_scaled,patient_ids = load_data(RAW_PATH, SCALED_PATH)

# -----------------------------
# Load optimal K values
# -----------------------------
opt_k_df = pd.read_csv(OPTIMAL_K_SUMMARY_PATH)
print(f"Loaded optimal k values from {OPTIMAL_K_SUMMARY_PATH}")
# -----------------------------
# Load distances and PCA
# -----------------------------
print("Loading Gower distance matrix...")
D_gower_path = D_GOWER_PATH
D_gower = pd.read_csv(D_gower_path, compression="gzip").values
print(f"Loaded D_gower from {D_gower_path}")

print("Loading PCA transformation...")
X_pca = pd.read_csv(X_PCA_PATH, compression="gzip").values
print(f"Loaded X_pca from {X_PCA_PATH}")


# -----------------------------
# Run all clustering configurations
# -----------------------------
results = []

configs = [
    ("raw_kmedoids_gower", D_gower),
    ("raw_agglomerative_gower", D_gower),
    ("raw_optics", D_gower),
    ("pca_kmeans_euclidean", X_pca),
    ("pca_agglomerative_euclidean", X_pca),
    ("pca_optics", X_pca),
]

print("\nRunning cluster validation...\n")

for cfg, data in configs:
    labels_file = labels_path(cfg)
    labels_df = pd.read_csv(labels_file, compression="gzip")
    labels = labels_df["cluster"].values
    print(f"Loaded labels for {cfg}")

    # Evaluate clustering quality (excluding -1 noise clusters)
    labels_eval = labels[labels != -1]
    if "raw" in cfg:
        X_eval = data[labels != -1][:, labels != -1]
        metric = "precomputed"
    else:
        X_eval = data[labels != -1]
        metric = "euclidean"

    res = evaluate_clustering(cfg, X_eval, labels_eval, metric=metric)
    results.append(res)
# -----------------------------
# Save validation results
# -----------------------------
df = pd.DataFrame(results)
df.to_csv(VALIDATION_RESULTS_PATH, index=False)

print("\n Validation results saved to:", VALIDATION_RESULTS_PATH)
print(df)
print("\n Validation complete.")
#TODO test on synthetic data
import matplotlib.pyplot as plt
import numpy as np

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# --- Silhouette (sort descending) ---
sil_sorted = df.sort_values("silhouette", ascending=False)
axes[0].barh(sil_sorted["config"], sil_sorted["silhouette"], color="steelblue")
axes[0].set_xlabel("Silhouette Score")
axes[0].set_title("Silhouette Score by Config")
axes[0].invert_yaxis()
for i, v in enumerate(sil_sorted["silhouette"]):
        axes[0].text(v, i, f" {v:.3f}", va="center", fontsize=8)

# --- Calinski-Harabasz (log scale, sort descending) ---
ch_sorted = df.sort_values("calinski_harabasz", ascending=False)
ch_vals = ch_sorted["calinski_harabasz"].values
axes[1].barh(ch_sorted["config"], ch_vals, color="darkorange")
axes[1].set_xscale("log")
axes[1].set_xlabel("Calinski-Harabasz Score (log scale)")
axes[1].set_title("Calinski-Harabasz Score by Config")
axes[1].invert_yaxis()
for i, v in enumerate(ch_vals):
    
    axes[1].text(v, i, f" {v:.1f}", va="center", fontsize=8)

plt.suptitle("Clustering Validation Scores", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.show()