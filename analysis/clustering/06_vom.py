# ----------------
# import libraries
# ----------------
import os
import importlib 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from clustering_helpers import get_best_config, build_membership_features, variance_of_means
from config import (
    INPUT_DATA_PATH,
    VALIDATION_RESULTS_PATH,
    VARIANCE_OF_MEANS_PATH,
    ENCODED_MEMBERSHIP_PATH,
    MEMBERSHIP_PATH,
    PLOTS_DIR,
    labels_path
)

print(f"Config loaded.")

# Create plots directory
os.makedirs(PLOTS_DIR, exist_ok=True)

# -------------------------
# load best config and data
# -------------------------

best_config = get_best_config(VALIDATION_RESULTS_PATH)
print(f"Best configuration: {best_config}")

labels_df = pd.read_csv(labels_path(best_config), compression="gzip")
wp3_df = pd.read_csv(INPUT_DATA_PATH)
df = wp3_df.merge(labels_df, on="patient_id", how="inner")
del wp3_df, labels_df

print(f"Merged {len(df)} patients with cluster labels")

#build membership features
membership = build_membership_features(df)
print(f"Built {len(membership.columns)-1} membership features")

membership.to_csv(MEMBERSHIP_PATH, index=False, compression="gzip")
print(f"Saved membership features")

# -----------------------
# one-hot-encode features
# -----------------------

# One-hot encode categorical variables
X = pd.get_dummies(membership.drop(columns="patient_id"), dummy_na=True, drop_first=False)

# Identify continuous vs dummy columns
continuous_cols = [col for col in X.columns if col in ['mltc_count']]
dummy_cols = [col for col in X.columns if col not in continuous_cols]

print(f"After one-hot encoding: {len(X.columns)} features "
        f"({len(continuous_cols)} continuous, {len(dummy_cols)} dummy)")

# Set type to int
for col in dummy_cols:
    if col in X.columns:
        X[col] = X[col].astype(int)

# Remove continuous variables
X = X.drop(columns=[col for col in continuous_cols if col in X.columns])

# Re_attach patient_id
X_with_id = pd.concat([
    membership[["patient_id"]].reset_index(drop=True),
    X.reset_index(drop=True)
], axis=1)

X_with_id.to_csv(ENCODED_MEMBERSHIP_PATH, index=False, compression="gzip")
print(f"Saved one-hot encoded features with patient_id")
del X_with_id  

# ---------------------------
# Calculate variance of means
# ---------------------------

vom = variance_of_means(df["cluster"], X)
vom_sorted = vom.sort_values(ascending=False)
vom_sorted.to_csv(VARIANCE_OF_MEANS_PATH, header=["variance_of_means"])
print(f"\nSaved")

# ----------
# Plot
# ----------

# Plot all variance-of-means values
fig_height = max(6, 0.25 * len(vom_sorted))
fig, ax = plt.subplots(figsize=(12, fig_height))
ax.barh(vom_sorted.index, vom_sorted.values, color="#1f77b4")
ax.invert_yaxis()
ax.set_title("Variance of Means by Feature")
ax.set_xlabel("Variance of Cluster Means")
ax.set_ylabel("Feature")
fig.tight_layout()

vom_plot_path = os.path.join(PLOTS_DIR, "vom_figure.png")
fig.savefig(vom_plot_path, dpi=200, bbox_inches="tight")
plt.show()
plt.close(fig)
print(f"Saved plot")