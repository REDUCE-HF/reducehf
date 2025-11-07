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
import matplotlib as mpl
import umap

from clustering_helpers import load_data, compute_gower, run_pca

# -----------------------------
# Setup
# -----------------------------
OUTPUT_DIR = "output/clustering/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(" Loading datasets...")
X_raw, X_scaled, raw_df, scaled_df = load_data(
    os.path.join(OUTPUT_DIR, "clustering_raw.csv.gz"),
    os.path.join(OUTPUT_DIR, "clustering_scaled.csv.gz")
)

# Drop ID columns if present
for df in [raw_df, scaled_df]:
    if isinstance(df, pd.DataFrame) and "patient_id" in df.columns:
        df.drop(columns=["patient_id"], inplace=True)

# -----------------------------
# Compute UMAP embedding
# -----------------------------
print(" Computing UMAP embedding on raw data...")
reducer = umap.UMAP(n_components=2, random_state=42, n_neighbors=15, min_dist=0.1)
umap_embedding = reducer.fit_transform(X_raw)
print(" UMAP embedding ready.")

# -----------------------------
# Load metadata
# -----------------------------
opt_k_path = os.path.join(OUTPUT_DIR, "optimal_k_summary.csv")
val_path = os.path.join(OUTPUT_DIR, "validation_results.csv")

opt_k_df = pd.read_csv(opt_k_path)
val_df = pd.read_csv(val_path)
print(f" Loaded {len(opt_k_df)} optimal-k rows and {len(val_df)} validation rows")

# -----------------------------
# Visualization helper
# -----------------------------
def plot_clusters(labels, config_name):
    plt.figure(figsize=(10, 7))

    # Count cluster sizes
    unique, counts = np.unique(labels, return_counts=True)
    cluster_sizes = dict(zip(unique, counts))
    n_clusters = len([x for x in unique if x != -1])

    # Masks
    noise_mask = labels == -1
    cluster_mask = ~noise_mask

    # Normalize colors across all valid cluster IDs
    norm = mpl.colors.Normalize(vmin=min(unique), vmax=max(unique))
    cmap = plt.get_cmap("tab20")

    # Plot noise separately (gray)
    if np.any(noise_mask):
        plt.scatter(
            umap_embedding[noise_mask, 0],
            umap_embedding[noise_mask, 1],
            c="lightgray",
            s=40,
            alpha=0.6,
            label="Noise"
        )

    # Plot clusters
    scatter = plt.scatter(
        umap_embedding[cluster_mask, 0],
        umap_embedding[cluster_mask, 1],
        c=labels[cluster_mask],
        cmap=cmap,
        norm=norm,
        s=50,
        alpha=0.8
    )

    # --- Colorbar with cluster sizes (including noise)
    unique_labels, counts = np.unique(labels, return_counts=True)
    cluster_labels = []
    for l, c in zip(unique_labels, counts):
        if l == -1:
            cluster_labels.append(f"Noise ({c})")
        else:
            cluster_labels.append(f"{int(l)} ({c})")

    cbar = plt.colorbar(scatter, label="Cluster")
    cbar.set_ticks(unique_labels)
    cbar.set_ticklabels(cluster_labels)
    cbar.ax.tick_params(length=0, labelsize=9)

    # --- Title and layout
    cluster_info = ", ".join([f"{'Noise' if k == -1 else int(k)}({v})"
                              for k, v in sorted(cluster_sizes.items())])
    plt.title(
        f"UMAP - {config_name}\nClusters={n_clusters} | Sizes={cluster_info}",
        fontsize=12
    )
    plt.xlabel("UMAP 1")
    plt.ylabel("UMAP 2")
    plt.tight_layout()

    save_path = os.path.join(OUTPUT_DIR, f"umap_{config_name}.png")
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Saved {save_path}")

# -----------------------------
# Main visualization loop
# -----------------------------
summary_out = []
print("\n Generating visualizations...\n")

label_files = [f for f in os.listdir(OUTPUT_DIR)
               if f.startswith("labels_") and f.endswith(".npy")]

for file in sorted(label_files):
    cfg = file.replace("labels_", "").replace(".npy", "")
    labels_path = os.path.join(OUTPUT_DIR, file)
    labels = np.load(labels_path)
    n_clusters = len(np.unique(labels))
    print(f"{cfg}: loaded labels ({n_clusters} clusters)")

    # Plot
    plot_clusters(labels, cfg)

    # Metrics and k_opt
    val_row = val_df[val_df["config"] == cfg]
    sil = val_row["silhouette"].values[0] if not val_row.empty else np.nan
    ch = val_row["calinski_harabasz"].values[0] if not val_row.empty else np.nan

    k_opt = np.nan
    if cfg in opt_k_df["config"].values:
        val = opt_k_df.loc[opt_k_df["config"] == cfg, "k_opt"].values[0]
        k_opt = int(val) if not pd.isna(val) else np.nan

    summary_out.append({
        "config": cfg,
        "k": k_opt,
        "clusters_found": n_clusters,
        "silhouette": sil,
        "calinski_harabasz": ch
    })

# -----------------------------
# Save summary
# -----------------------------
summary_df = pd.DataFrame(summary_out)
summary_path = os.path.join(OUTPUT_DIR, "visualization_summary.csv")
summary_df.to_csv(summary_path, index=False)

print("\n All visualizations complete.")
print(" Summary saved to:", summary_path)
print(" Check images in:", OUTPUT_DIR)
