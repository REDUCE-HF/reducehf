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
from clustering_helpers import load_data

# -----------------------------------------
# Setup
# -----------------------------------------
OUTPUT_DIR = "output/clustering/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Loading datasets...")
X_raw, X_scaled, raw_df, scaled_df = load_data(
    os.path.join(OUTPUT_DIR, "clustering_raw.csv.gz"),
    os.path.join(OUTPUT_DIR, "clustering_scaled.csv.gz")
)

# Drop ID column if present
if "patient_id" in raw_df.columns:
    raw_df = raw_df.drop(columns=["patient_id"])
if "patient_id" in scaled_df.columns:
    scaled_df = scaled_df.drop(columns=["patient_id"])

# -----------------------------------------
# Load metadata
# -----------------------------------------
val_path = os.path.join(OUTPUT_DIR, "validation_results.csv")
opt_k_path = os.path.join(OUTPUT_DIR, "optimal_k_summary.csv")

val_df = pd.read_csv(val_path)
opt_k_df = pd.read_csv(opt_k_path)

print("Selecting best configuration...")
# Rank by silhouette + CH
val_df["rank"] = val_df["silhouette"].rank(ascending=False) + \
                 val_df["calinski_harabasz"].rank(ascending=False)

best_config = val_df.sort_values("rank").iloc[0]["config"]
print(f"Best configuration: {best_config}")

# -----------------------------------------
# Load labels for the best config
# -----------------------------------------
labels_path = os.path.join(OUTPUT_DIR, f"labels_{best_config}.npy")
if not os.path.exists(labels_path):
    raise FileNotFoundError(f"No labels found for {best_config}")

labels = np.load(labels_path)

# Determine which dataframe to use for heatmap
if best_config.startswith("raw"):
    data = raw_df
else:
    data = scaled_df

# Attach labels
df = data.copy()
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
out_path = os.path.join(OUTPUT_DIR, f"heatmap_{best_config}.png")
plt.savefig(out_path, dpi=300, bbox_inches="tight")
plt.close()

print(f"Saved heatmap to: {out_path}")
print("Heatmap generation complete.")
