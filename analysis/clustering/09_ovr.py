import os
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier

from clustering_helpers import get_best_config
from config import (
    INPUT_DATA_PATH,
    VALIDATION_RESULTS_PATH,
    VARIANCE_OF_MEANS_PATH,
    labels_path
)


def train_ovr(X, labels, max_depth=3, min_samples_leaf=50, random_state=42):
    """Train one-vs-rest decision trees and return combined importance+means table."""
    # drop -1 cluster and keep indices aligned  
    X = X.loc[labels != -1].reset_index(drop=True)
    labels = labels[labels != -1].reset_index(drop=True)

    clusters = sorted(labels.unique())

    all_rows = []
    for k in clusters:
        y = (labels == k).astype(int)

        dt = DecisionTreeClassifier(
            max_depth=max_depth,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state
        )
        dt.fit(X, y)

        gini = pd.Series(dt.feature_importances_, index=X.columns)

        mean_in = X[y == 1].mean(axis=0)
        mean_out = X[y == 0].mean(axis=0)

        tmp = pd.DataFrame({
            "cluster": k,
            "feature": X.columns,
            "gini_importance": gini.values,
            "mean_in_cluster": mean_in.values,
            "mean_outside_cluster": mean_out.values,
        })
        tmp["mean_difference"] = tmp["mean_in_cluster"] - tmp["mean_outside_cluster"]
        tmp["distinguishing_feature"] = np.where(tmp["mean_difference"] > 0, "presence",
                                                 np.where(tmp["mean_difference"] < 0, "absence", "equal"))
        all_rows.append(tmp)

    out = pd.concat(all_rows, ignore_index=True)
    return out.sort_values(["cluster", "gini_importance"], ascending=[True, False])


def main():
    best_config = get_best_config(VALIDATION_RESULTS_PATH)
    labels_df = pd.read_csv(labels_path(best_config), compression="gzip")

    output_dir = os.path.dirname(VARIANCE_OF_MEANS_PATH)

    # Load membership features 
    membership_path = os.path.join(output_dir, "membership_features.csv")
    if not os.path.exists(membership_path):
        raise FileNotFoundError(f"{membership_path} not found. Run 08_vom.py first.")

    membership = pd.read_csv(membership_path)
    
    df = membership.merge(labels_df, on="patient_id", how="inner")
    print(f"Merged {len(df)} patients with cluster labels")
    
    labels = df["cluster"]  
    
    # One-hot encode (same as VoM)
    X = pd.get_dummies(
        df.drop(columns=["patient_id", "cluster"]), 
        dummy_na=True, 
        drop_first=False
    )
    
    # Remove continuous variables until we decide on how to handle them??? 
    continuous_vars = ['household_size', 'mltc_count']
    X = X.drop(columns=[col for col in continuous_vars if col in X.columns])
    
    # Fill NaN with 0 for binary features (same as VoM)
    X = X.fillna(0)
    
    print(f"Using {len(X.columns)} binary features for {len(X)} patients")

    combined = train_ovr(X, labels)

    out_all = os.path.join(output_dir, "ovr_feature_importance_all.csv")
    out_top = os.path.join(output_dir, "ovr_feature_importance_top15_per_cluster.csv")

    combined.to_csv(out_all, index=False)
    (combined.groupby("cluster").head(15)).to_csv(out_top, index=False)

    print(f"Saved: {out_all}")
    print(f"Saved: {out_top}")


if __name__ == "__main__":
    main()
