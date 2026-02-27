#!/usr/bin/env python3
# ============================================
# 06_heatmaps.py
# Visualise HS utilisation patterns using heatmaps
# Uses cluster labels saved in 04_validate_clusters.py
# ============================================

import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from config import (
    OUTPUT_DIR,
    OPTIMAL_K_SUMMARY_PATH,
    RAW_PATH,
    SCALED_PATH,
    VALIDATION_RESULTS_PATH,
    labels_path,
    heatmap_path,
)
from clustering_helpers import load_data, load_feature_names, get_best_config

# -----------------------------------------
# Setup
# -----------------------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Loading datasets...")
X_raw, _ = load_data(RAW_PATH, SCALED_PATH)

# Rebuild DataFrames with feature names for labeling
feature_names = load_feature_names(RAW_PATH)
raw_df = pd.DataFrame(X_raw, columns=feature_names)

# -----------------------------------------
# Load metadata
# -----------------------------------------
val_df = pd.read_csv(VALIDATION_RESULTS_PATH)
# opt_k_df = pd.read_csv(OPTIMAL_K_SUMMARY_PATH)

# -----------------------------------------
# Select best configuration
# -----------------------------------------
from clustering_helpers import get_best_config

print("Selecting best configuration...")
best_config = get_best_config(VALIDATION_RESULTS_PATH)
print(f"Best configuration: {best_config}")

# -----------------------------------------
# Load labels for the best config
# -----------------------------------------
labels_file = labels_path(best_config)
if not os.path.exists(labels_file):
    raise FileNotFoundError(f"No labels found for {best_config}")

labels_df = pd.read_csv(labels_file, compression="gzip")
labels = labels_df["cluster"].values

# Visualize clusters on raw features DataFrame
df = raw_df.copy()
df["cluster"] = labels

# -----------------------------------------
# Compute cluster-level means
# -----------------------------------------
print("Computing cluster-wise utilisation means...")

cluster_means = df.groupby("cluster").mean()

# Sort clusters by size
cluster_sizes = df["cluster"].value_counts().sort_values(ascending=False)
cluster_means = cluster_means.loc[cluster_sizes.index]

# -----------------------------------------
# Plot heatmap
# -----------------------------------------
plt.figure(figsize=(12, 8))
sns.heatmap(
    cluster_means,
    cmap="viridis",
    linewidths=0.3,
    cbar_kws={"label": "Mean utilisation"}
)

title = f"HS Utilisation Heatmap - {best_config}"
plt.title(title, fontsize=13)
plt.xlabel("Variable")
plt.ylabel("Cluster")

plt.tight_layout()
out_path = heatmap_path(best_config)
plt.savefig(out_path, dpi=300, bbox_inches="tight")
plt.close()

print(f"Saved heatmap to: {out_path}")
print("Heatmap generation complete.")
