#!/usr/bin/env python3
# ============================================
# 05_visualize_clusters.py
# Visualize clustering results in UMAP space
# Loads precomputed cluster labels from step 04
# ============================================

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import umap

from config import (
    OPTIMAL_K_SUMMARY_PATH,
    OUTPUT_DIR,
    RAW_PATH,
    SCALED_PATH,
    VALIDATION_RESULTS_PATH,
    VISUALIZATION_SUMMARY_PATH,
)
from clustering_helpers import load_data, plot_clusters_umap

# -----------------------------
# Setup
# -----------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(" Loading datasets...")
X_raw, X_scaled, patient_ids = load_data(RAW_PATH, SCALED_PATH)

# Compute UMAP embedding from raw data
umap_values = umap.UMAP(n_components=2, random_state=42, n_neighbors=15, min_dist=0.1).fit_transform(X_raw)
print (umap_values)

opt_k_df = pd.read_csv(OPTIMAL_K_SUMMARY_PATH)
val_df = pd.read_csv(VALIDATION_RESULTS_PATH)
print(f" Loaded {len(opt_k_df)} optimal-k rows and {len(val_df)} validation rows")
summary_out = []
print("\n Generating visualizations...\n")

label_files = [f for f in os.listdir(OUTPUT_DIR)
               if f.startswith("labels_") and f.endswith(".csv.gz")]

for file in sorted(label_files):
    cfg = file.replace("labels_", "").replace(".csv.gz", "")
    labels_file = os.path.join(OUTPUT_DIR, file)
    labels_df = pd.read_csv(labels_file, compression="gzip")
    labels = labels_df["cluster"].values
    n_clusters = len([x for x in np.unique(labels) if x != -1])
    print(f"{cfg}: loaded labels ({n_clusters} clusters)")

    plot_clusters_umap(umap_values, labels, cfg)

    # summary report
    val_row = val_df[val_df["config"] == cfg]
    sil = val_row["silhouette"].values[0] 
    ch = val_row["calinski_harabasz"].values[0] 

    k_opt_series = opt_k_df.loc[opt_k_df["config"] == cfg, "k_opt"]
    k_opt = int(k_opt_series.values[0]) if not k_opt_series.empty and not pd.isna(k_opt_series.values[0]) else np.nan
    print (k_opt_series)
    
    summary_out.append({
        "config": cfg,
        "k": k_opt,
        "clusters_found": n_clusters,
        "silhouette": sil,
        "calinski_harabasz": ch
    })
summary_df = pd.DataFrame(summary_out)
summary_df.to_csv(VISUALIZATION_SUMMARY_PATH, index=False)

print("\n All visualizations complete.")
print(" Summary saved to:", VISUALIZATION_SUMMARY_PATH)
print(" plots saved to", OUTPUT_DIR)
print(summary_df)

# ----HeatMaps-------
# -------------------
df = pd.read_csv(RAW_PATH).drop(columns=["patient_id"])
for file in sorted(label_files):
    cfg = file.replace("labels_", "").replace(".csv.gz", "")
    labels = pd.read_csv(os.path.join(OUTPUT_DIR, file), compression="gzip")["cluster"].values

    
    df["cluster"] = labels

    
    numeric_cols = df.columns[~df.columns.str.contains("cluster|_bin")]
    binary_cols = df.columns[df.columns.str.contains("_bin")]
   # Sort cluster order by size once so both maps match
    cluster_order = df["cluster"].value_counts().index

    # Numeric Heatmap 
    plt.figure(figsize=(12, 6))
    numeric_means = df.groupby("cluster")[numeric_cols].mean().loc[cluster_order]
    sns.heatmap(numeric_means, cmap="viridis", cbar_kws={'label': 'Average Value'})
    plt.title(f"Numeric Usage Patterns - {cfg}")
    plt.savefig(heatmap_path(f"{cfg}_numeric"))
    plt.show()

    # Binary Heatmap (Percentages)
    plt.figure(figsize=(12, 6))
    binary_means = df.groupby("cluster")[binary_cols].mean().loc[cluster_order]
    
    sns.heatmap(binary_means, cmap="Blues", annot=True, fmt=".2f", vmin=0, vmax=1)
    plt.title(f"Binary Feature Prevalence (0.0 - 1.0) - {cfg}")
    plt.savefig(heatmap_path(f"{cfg}_binary"))
    plt.show()