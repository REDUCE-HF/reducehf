import os
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import roc_auc_score

from clustering_helpers import get_best_config
from config import (
    INPUT_DATA_PATH,
    VALIDATION_RESULTS_PATH,
    VARIANCE_OF_MEANS_PATH,
    ENCODED_MEMBERSHIP_PATH,
    labels_path
)


def train_ovr(X, labels, output_dir, random_state=42):
    """Train one-vs-rest decision trees with GridSearchCV and return combined importance+means table."""
    # drop -1 cluster and keep indices aligned  
    X = X.loc[labels != -1].reset_index(drop=True)
    labels = labels[labels != -1].reset_index(drop=True)

    clusters = sorted(labels.unique())
    
    
    param_grid = {
        'max_depth': [5, 10, 50, 100],
        'min_samples_leaf': [5, 10, 50]
    }

    all_rows = []
    all_cv_results = []
    
    for k in clusters:
        y = (labels == k).astype(int)

        dt = DecisionTreeClassifier(random_state=random_state)
        grid_search = GridSearchCV(
            dt,
            param_grid=param_grid,
            scoring='roc_auc',
            cv=5,
            return_train_score=True,
            n_jobs=-1
        )
        grid_search.fit(X, y)
        
        best_dt = grid_search.best_estimator_
        
        # Calculate training AUC on the full dataset for the best decision treee
        y_pred_train = best_dt.predict_proba(X)[:, 1]
        train_auc = roc_auc_score(y, y_pred_train)
        
        cv_results_df = pd.DataFrame(grid_search.cv_results_)
        cv_results_df['cluster'] = k
        
        # Add training AUC to the results dataframe
        cv_results_df['train_auc'] = np.nan
        best_estimator_index = grid_search.best_index_
        cv_results_df.loc[best_estimator_index, 'train_auc'] = train_auc
        
        all_cv_results.append(cv_results_df)
        
        print(
            f"Cluster {k}: Best params = {grid_search.best_params_}, "
            f"Mean Test AUC = {grid_search.best_score_:.3f}, "
            f"Train AUC = {train_auc:.3f}"
        )

        gini = pd.Series(best_dt.feature_importances_, index=X.columns)

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

    cv_results_all = pd.concat(all_cv_results, ignore_index=True)
    cv_results_path = os.path.join(output_dir, "ovr_gridsearch_cv_results.csv")
    cv_results_all.to_csv(cv_results_path, index=False)
    print(f"Saved GridSearchCV results to {cv_results_path}")

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
    # Load one-hot encoded features
    X = pd.read_csv(ENCODED_MEMBERSHIP_PATH)

    combined = train_ovr(X, labels, output_dir)

    out_all = os.path.join(output_dir, "ovr_feature_importance_all.csv")
    out_top = os.path.join(output_dir, "ovr_feature_importance_top15_per_cluster.csv")

    combined.to_csv(out_all, index=False)
    (combined.groupby("cluster").head(15)).to_csv(out_top, index=False)

    print(f"Saved: {out_all}")
    print(f"Saved: {out_top}")


if __name__ == "__main__":
    main()
