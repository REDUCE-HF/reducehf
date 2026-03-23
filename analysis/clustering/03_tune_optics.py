# ============================================
# 03_tune_optics.py
# Grid search tuning for OPTICS parameters
# ============================================

import os
import numpy as np
import pandas as pd
from sklearn.cluster import OPTICS
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import matplotlib.pyplot as plt
from config import (
    D_GOWER_PATH,
    OPTICS_TUNING_RESULTS_PATH,
    OUTPUT_DIR,
    RAW_PATH,
    SCALED_PATH,
    X_PCA_PATH,
)
from clustering_helpers import load_data

# -------------------
# Load data
# -------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Loading dataset...")
X_raw, X_scaled = load_data(RAW_PATH, SCALED_PATH)

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
max_eps_list = [np.inf, 2.0, 5.0]  
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

                # Pass the distance matrix for precomputed metrics for Silhouette Score
                score_input = X if metric == "precomputed" else X_pca
                sil = silhouette_score(score_input, labels, metric=metric)
                ch = calinski_harabasz_score(X_pca, labels) 
                

                results.append({
                    "data": distance_name,
                    "min_samples": min_s,
                    "xi": xi,
                    "max_eps": eps,
                    "n_clusters": n_clusters,
                    "noise_fraction": round(noise_frac, 3),
                    "silhouette": sil,
                    "calinski_harabasz": ch
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
best_rows = df.loc[df.groupby("data")["silhouette"].idxmax()]
print("\nBest parameters per dataset:")
print(best_rows[["data", "min_samples", "xi", "max_eps", "n_clusters", "silhouette"]])

# -------------------
# Reachibility Plots
# -------------------
#TODO test on synthetic data
data_map = {
    "raw_gower":     (D_gower, "precomputed"),
    "pca_euclidean": (X_pca,   "euclidean"),
}

cluster_colors = ["g.", "r.", "b.", "y.", "c.", "m."]
TOP_N = 3  # number of top results to show 

top_rows = (
    df.dropna(subset=["silhouette"])
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
    plt.show()
