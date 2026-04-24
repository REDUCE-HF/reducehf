## ============================================
# 03_tune_optics.py
# Grid search tuning for OPTICS parameters
# ============================================

import os
import numpy as np
import pandas as pd
from sklearn.cluster import OPTICS
import matplotlib.pyplot as plt
from config import (
    D_GOWER_PATH,
    OPTICS_TUNING_RESULTS_PATH,
    OUTPUT_DIR,
    RAW_PATH,
    SCALED_PATH,
    X_PCA_PATH,
    labels_path,
    PLOTS_DIR
)
from clustering_helpers import load_data, evaluate_clustering

# -------------------
# Load data
# -------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Create plots directory
os.makedirs(PLOTS_DIR, exist_ok=True)

print("Loading dataset...")
X_raw, X_scaled,patient_ids = load_data(RAW_PATH, SCALED_PATH)

print("Loading precomputed Gower distance matrix...")
D_gower = pd.read_csv(D_GOWER_PATH, compression="gzip").values
print(f"Loaded D_gower from {D_GOWER_PATH}")


print("Loading precomputed PCA transformation...")
X_pca = pd.read_csv(X_PCA_PATH, compression="gzip").values
print(f"Loaded X_pca from {X_PCA_PATH}")

# -------------------
# Dynamic parameter grid
# -------------------
n, d = X_scaled.shape

min_samples_list= [d+1, 2*d,  3*d] #  heuristcs  (d+1, 2d–3d)

xi_list = [0.02, 0.05, 0.1]
max_eps_list = [2.0, 5.0, np.inf]  
#If this is too much we can run on sample of the data or restrict to max(min_samples_list)??
results = []
# -------------------
# Run grid for both data types
# -------------------
for distance_name, X, metric in [
    ("raw_gower", D_gower, "precomputed"),
    ("pca_euclidean", X_pca, "euclidean")
]:
    print(f"\nTuning OPTICS on {distance_name}...")
    for min_s in min_samples_list:
        for xi in xi_list:
            for eps in max_eps_list:
                print(f"  min_samples={min_s}, xi={xi}, max_eps={eps}")

                optics = OPTICS(min_samples=min_s, xi=xi, max_eps=eps, metric=metric).fit(X)
                labels = optics.labels_
                n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
                noise_frac = np.mean(labels == -1)

                cfg_name = f"{distance_name}_ms{min_s}_xi{xi}_eps{eps}"
                metrics = evaluate_clustering(cfg_name, X, labels, metric=metric)

                results.append({
                    "data": distance_name,
                    "min_samples": min_s,
                    "xi": xi,
                    "max_eps": eps,
                    "n_clusters": n_clusters,
                    "noise_fraction": round(noise_frac, 3),
                    "silhouette": metrics["silhouette"] ,
                    "calinski_harabasz": metrics["calinski_harabasz"],
                    "config": cfg_name,
                })


               
                

# -------------------
# Save results
# -------------------
df = pd.DataFrame(results)
df.to_csv(OPTICS_TUNING_RESULTS_PATH, index=False)
print(f"\nSaved results to: {OPTICS_TUNING_RESULTS_PATH}")

# -------------------
# Best parameters summary
# -------------------
best_silhouette = df.loc[df.groupby("data")["silhouette"].idxmax()]
best_ch = df.loc[df.groupby("data")["calinski_harabasz"].idxmax()]

print("\nBest config per dataset by Silhouette:")
print(best_silhouette[["data", "min_samples", "xi", "max_eps", "n_clusters", "silhouette", "calinski_harabasz"]])

print("\nBest config per dataset by Calinski-Harabasz:")
print(best_ch[["data", "min_samples", "xi", "max_eps", "n_clusters", "silhouette", "calinski_harabasz"]])

# -------------------
# Save best labels. 
# -------------------
data_map = {
    "raw_gower":     (D_gower, "precomputed"),
    "pca_euclidean": (X_pca,   "euclidean"),
}
for _, row in best_silhouette.iterrows():
    data_name = row["data"]
    X, metric = data_map[data_name]
    cfg_key = "raw_optics" if "raw" in data_name else "pca_optics"

    best_optics = OPTICS(
        min_samples=int(row["min_samples"]),
        xi=row["xi"],
        max_eps=row["max_eps"],
        metric=metric,
    ).fit(X)

    (
        pd.DataFrame({"patient_id": patient_ids, "cluster": best_optics.labels_})
        .to_csv(labels_path(cfg_key), index=False, compression="gzip")
    )
    print(f"  {cfg_key} -> saved to {labels_path(cfg_key)}")



# -------------------
# Reachability plot
# -------------------
cluster_colors = ["g.", "r.", "b.", "y.", "c.", "m."]
TOP_N = 1  # number of top results to show 

top_rows = (
    df
    .groupby("data", group_keys=False)
    .apply(lambda g: g.nlargest(TOP_N, "silhouette"))
    .reset_index(drop=True)
)

for _, row in top_rows.iterrows():
    data_name = row["data"]
    X, metric = data_map[data_name]

    best_optics = OPTICS(
        min_samples=int(row["min_samples"]),
        xi=row["xi"],
        max_eps=row["max_eps"],
        metric=metric
    ).fit(X)

    reachability = best_optics.reachability_[best_optics.ordering_]
    labels_ord   = best_optics.labels_[best_optics.ordering_]
    space        = np.arange(len(reachability))

    fig, ax = plt.subplots(figsize=(12, 4))
    fig.suptitle(
        f"{data_name} | min_samples={int(row['min_samples'])}, xi={row['xi']}, "
        f"max_eps={row['max_eps']} | n_clusters={int(row['n_clusters'])}, "
        f"noise={row['noise_fraction']:.1%}, sil={row['silhouette']:.3f}",
        fontsize=10
    )

    for klass, color in zip(sorted(set(labels_ord) - {-1}), cluster_colors):
        mask = labels_ord == klass
        ax.plot(space[mask], reachability[mask], color, alpha=0.5, label=f"Cluster {klass}")
    ax.plot(space[labels_ord == -1], reachability[labels_ord == -1], "k.", alpha=0.3, label="Noise")
    ax.set_xlabel("Points (ordered)")
    ax.set_ylabel("Reachability (epsilon distance)")
    ax.set_title("Reachability Plot")
    ax.legend(loc="upper right", fontsize=8)

    plt.tight_layout()
    reachability_plot_path = os.path.join(PLOTS_DIR, "reachability_figure.png")
    fig.savefig(reachability_plot_path, dpi=200, bbox_inches="tight")
    plt.show()
