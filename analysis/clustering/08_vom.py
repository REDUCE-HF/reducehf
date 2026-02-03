import os
import pandas as pd
import numpy as np

from clustering_helpers import get_best_config, build_membership_features, variance_of_means
from config import (
    INPUT_DATA_PATH,
    VALIDATION_RESULTS_PATH,
    VARIANCE_OF_MEANS_PATH,
    labels_path
)


best_config = get_best_config(VALIDATION_RESULTS_PATH)
print(f"Best configuration: {best_config}")

labels_df = pd.read_csv(labels_path(best_config), compression="gzip")
wp3_df = pd.read_csv(INPUT_DATA_PATH)

df = wp3_df.merge(labels_df, on="patient_id", how="inner")
print(f"Merged {len(df)} patients with cluster labels")

membership = build_membership_features(df)
print(f"Built {len(membership.columns)-1} membership features")

# Define output directory from VARIANCE_OF_MEANS_PATH
output_dir = os.path.dirname(VARIANCE_OF_MEANS_PATH)
os.makedirs(output_dir, exist_ok=True)

membership_path = os.path.join(output_dir, "membership_features.csv")
membership.to_csv(membership_path, index=False)
print(f"Saved membership features to {membership_path}")

# One-hot encode categorical variables
X = pd.get_dummies(membership.drop(columns="patient_id"), dummy_na=True, drop_first=False)

# Identify continuous vs dummy columns
continuous_vars = ['mltc_count']
continuous_cols = [col for col in X.columns if col in continuous_vars]
dummy_cols = [col for col in X.columns if col not in continuous_cols]

print(f"After one-hot encoding: {len(X.columns)} features "
        f"({len(continuous_cols)} continuous, {len(dummy_cols)} dummy)")

#set type to int 
for col in dummy_cols:
    if col in X.columns:
        X[col] = X[col].astype(int)

# Remove continuous variables and fill NaNs
X = X.drop(columns=[col for col in continuous_vars if col in X.columns])

encoded_path = os.path.join(output_dir, "membership_features_encoded.csv")
X.to_csv(encoded_path, index=False)
print(f"Saved one-hot encoded features to {encoded_path}")

# Calculate variance of means
vom = variance_of_means(df["cluster"], X)
vom.sort_values(ascending=False).to_csv(VARIANCE_OF_MEANS_PATH, header=["variance_of_means"])

print(f"\nSaved: {VARIANCE_OF_MEANS_PATH}")
print(f"\nTop 10 most discriminative features:")
print(vom.sort_values(ascending=False).head(10))
  
