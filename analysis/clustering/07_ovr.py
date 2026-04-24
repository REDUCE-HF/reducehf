import os
import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score
from clustering_helpers import get_best_config,train_ovr
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import roc_auc_score
from config import (
    INPUT_DATA_PATH,
    VALIDATION_RESULTS_PATH,
    VARIANCE_OF_MEANS_PATH,
    MEMBERSHIP_PATH,
    ENCODED_MEMBERSHIP_PATH,
    OVR_FEATURE_IMPORTANCE_ALL_PATH,
    OUTPUT_DIR,
    PLOTS_DIR,
    labels_path
)

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Patch

# Create plots directory
os.makedirs(PLOTS_DIR, exist_ok=True)

best_config = get_best_config(VALIDATION_RESULTS_PATH)
labels_df = pd.read_csv(labels_path(best_config), compression="gzip")
print(best_config)

X = pd.read_csv(ENCODED_MEMBERSHIP_PATH)
patients_ids = X["patient_id"]
X= X.drop(columns=["patient_id"])
y = labels_df["cluster"].reset_index(drop=True)


print(f"Prepared OVR input: X_model shape={X.shape}, y shape={y.shape}")
print(f"Cluster distribution:\n{y.value_counts().sort_index()}")

combined = train_ovr(X, y, OUTPUT_DIR)
combined.to_csv(OVR_FEATURE_IMPORTANCE_ALL_PATH, index=False)
print(f"Saved to {OVR_FEATURE_IMPORTANCE_ALL_PATH}") 

# plot
top10 = combined.groupby("cluster", group_keys=False).head(10).copy()

# 1) Top features per cluster (horizontal bar charts)
clusters = sorted(top10["cluster"].unique())
fig, axes = plt.subplots(len(clusters), 1, figsize=(14, max(5, 3.5 * len(clusters))))
if len(clusters) == 1:
    axes = [axes]

# Use a professional color palette
palette = {"presence": "#2E7D32", "absence": "#C62828", "equal": "#757575"}

for ax, c in zip(axes, clusters):
    d = top10[top10["cluster"] == c].sort_values("gini_importance", ascending=True)
    colors = d["distinguishing_feature"].map(palette)
    ax.barh(d["feature"], d["gini_importance"], color=colors, edgecolor='white', linewidth=0.5)
    ax.set_title(f"Cluster {int(c)}: Top 10 Features", fontsize=12, fontweight='bold', pad=10)
    ax.set_xlabel("Gini Importance", fontsize=11)
    ax.tick_params(axis="y", labelsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# Add legend
legend_elements = [
    Patch(facecolor=palette["presence"], label="Presence distinguishes", edgecolor='white'),
    Patch(facecolor=palette["absence"], label="Absence distinguishes", edgecolor='white'),
    Patch(facecolor=palette["equal"], label="Equal", edgecolor='white')
]
fig.legend(handles=legend_elements, loc="upper right", bbox_to_anchor=(0.98, 0.98), frameon=True)

plt.tight_layout()
plot1_path = os.path.join(PLOTS_DIR, "ovr_top_features_by_cluster.png")
fig.savefig(plot1_path, dpi=300, bbox_inches='tight', facecolor='white')
print("Saved")
plt.show()

# 2) Heatmap of mean differences for top OVR features
top15 = combined.groupby("cluster", group_keys=False).head(15).copy()
features = (
    top15.groupby("feature")["gini_importance"]
    .max()
    .sort_values(ascending=False)
    .index
)
hm = (
    combined[combined["feature"].isin(features)]
    .pivot(index="cluster", columns="feature", values="mean_difference")
    .sort_index()
)

fig, ax = plt.subplots(figsize=(max(12, 0.5 * hm.shape[1]), max(7, 0.9 * hm.shape[0] + 2)))
sns.heatmap(
    hm,
    cmap="RdBu_r",
    center=0,
    linewidths=0.5,
    linecolor='white',
    cbar_kws={"label": "Mean Difference (in-cluster - out-cluster)", "shrink": 0.8},
    ax=ax
)
ax.set_title("Feature Mean Differences by Cluster (Top OVR Features)", 
             fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel("Feature", fontsize=11)
ax.set_ylabel("Cluster", fontsize=11)
plt.xticks(rotation=45, ha="right", fontsize=9)
plt.yticks(rotation=0, fontsize=10)
plt.tight_layout()

plot2_path = os.path.join(PLOTS_DIR, "ovr_feature_heatmap.png")
fig.savefig(plot2_path, dpi=300, bbox_inches='tight', facecolor='white')
print("Saved:")
plt.show()