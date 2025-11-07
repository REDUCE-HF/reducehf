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
import warnings
from clustering_helpers import load_data, compute_gower, run_pca

# -------------------
# Load data
# -------------------
RAW_PATH = "output/clustering/clustering_raw.csv.gz"
SCALED_PATH = "output/clustering/clustering_scaled.csv.gz"
OUTPUT_DIR = "output/clustering/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Loading dataset...")
X_raw, X_scaled, _, _ = load_data(RAW_PATH, SCALED_PATH)
D_gower = compute_gower(X_raw)
X_pca, var = run_pca(X_scaled)
print(f"PCA reduced to {X_pca.shape[1]} components (explaining {var:.1%} variance)")

# -------------------
# Dynamic parameter grid
# -------------------
n, d = X_scaled.shape
base_min = int(np.log(n))
all_min_samples_candidates = list(set([
    2*d,
    base_min,
    base_min*2,
    int(0.01*n),
    int(0.02*n)
]))

# --- FIX: Only use the maximum calculated candidate for min_samples ---
min_samples_list_full = [m for m in all_min_samples_candidates if m <= 500]
min_samples_list = [max(min_samples_list_full)] if min_samples_list_full else [5]
# -------------------------------------------------------------------

xi_list = [0.02, 0.05, 0.1]
max_eps_list = [np.inf, 2.0, 5.0]  # new param

results = []

# -------------------
# Run grid for both data types
# -------------------
for data_name, X, metric in [
    ("raw_gower", D_gower, "precomputed"),
    ("pca_euclidean", X_pca, "euclidean")
]:
    print(f"\nTuning OPTICS on {data_name}...")
    for min_s in min_samples_list:
        for xi in xi_list:
            for eps in max_eps_list:
                print(f"  min_samples={min_s}, xi={xi}, max_eps={eps}")
                try:
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", category=RuntimeWarning)
                        optics = OPTICS(min_samples=min_s, xi=xi, max_eps=eps, metric=metric).fit(X)
                    labels = optics.labels_
                    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
                    noise_frac = np.mean(labels == -1)

                    if n_clusters > 1:
                        # FIX: Pass the distance matrix for precomputed metrics for Silhouette Score
                        score_input = X if metric == "precomputed" else X_pca
                        sil = silhouette_score(score_input, labels, metric=metric)
                        ch = calinski_harabasz_score(X_pca, labels) # CH always uses features (X_pca)
                    else:
                        sil, ch = np.nan, np.nan

                    results.append({
                        "data": data_name,
                        "min_samples": min_s,
                        "xi": xi,
                        "max_eps": eps,
                        "n_clusters": n_clusters,
                        "noise_fraction": round(noise_frac, 3),
                        "silhouette": sil,
                        "calinski_harabasz": ch
                    })

                except Exception as e:
                    results.append({
                        "data": data_name,
                        "min_samples": min_s,
                        "xi": xi,
                        "max_eps": eps,
                        "n_clusters": np.nan,
                        "noise_fraction": np.nan,
                        "silhouette": np.nan,
                        "calinski_harabasz": np.nan
                    })
                    print(f" Error with {data_name}: {e}")

# -------------------
# Save results
# -------------------
df = pd.DataFrame(results)
path = os.path.join(OUTPUT_DIR, "optics_tuning_results.csv")
df.to_csv(path, index=False)
print(f"\nSaved results to: {path}")

# -------------------
# Best parameters summary
# -------------------
best_rows = df.loc[df.groupby("data")["silhouette"].idxmax()]
print("\nBest parameters per dataset:")
print(best_rows[["data", "min_samples", "xi", "max_eps", "n_clusters", "silhouette"]])

# -------------------
# Plot silhouette vs min_samples
# -------------------
# plt.figure(figsize=(8,5))
# for xi in xi_list:
#     subset = df[(df["data"] == "pca_euclidean") & (df["xi"] == xi)]
#     plt.plot(subset["min_samples"], subset["silhouette"], marker="o", label=f"xi={xi}")
# plt.xlabel("min_samples")
# plt.ylabel("Silhouette score")
# plt.title("OPTICS tuning (PCA-Euclidean)")
# plt.legend()
# plt.tight_layout()
# plt.show()
