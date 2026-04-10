#!/usr/bin/env python3
# ============================================
# 00_generate_synthetic_test_data.py
# Generate synthetic test data with make_blobs
# Ready for the existing clustering pipeline
# ============================================

import os
import numpy as np
import pandas as pd
from sklearn.datasets import make_blobs
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from clustering_helpers import parse_args
import config



args = parse_args()
if args.synthetic_output_dir:
    config.set_synthetic_output_dir(args.synthetic_output_dir)

os.makedirs(config.SYNTHETIC_OUTPUT_DIR, exist_ok=True)
np.random.seed(config.RANDOM_STATE)

print(
    f"Generating {config.N_SAMPLES:,} samples with "
    f"{len(config.FEATURE_NAMES)} features and {config.N_CENTERS} blobs..."
)

X_base, y_true = make_blobs(
    n_samples=config.N_SAMPLES,
    n_features=len(config.FEATURE_NAMES),
    centers=config.N_CENTERS,
    cluster_std=1.0,
    random_state=config.RANDOM_STATE,
)

# Bring all features to [0, 1] to keep values positive and separable.
unit_scaler = MinMaxScaler()
X_unit = unit_scaler.fit_transform(X_base)

X_synthetic = np.zeros_like(X_unit)
for idx, name in enumerate(config.FEATURE_NAMES):
    if "_bin" in name:
        # Binary flags as 0/1 derived from the blob signal.
        X_synthetic[:, idx] = (X_unit[:, idx] > 0.5).astype(float)
    else:
        f_min, f_max = config.FEATURE_RANGES[name]
        X_synthetic[:, idx] = f_min + X_unit[:, idx] * (f_max - f_min)

df = pd.DataFrame(X_synthetic, columns=config.FEATURE_NAMES)
df.insert(0, "patient_id", np.arange(1, config.N_SAMPLES + 1))
df["cluster_true"] = y_true

df.drop(columns=["cluster_true"]).to_csv(
    config.SYNTHETIC_RAW_PATH, index=False, compression="gzip"
)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[config.FEATURE_NAMES].values)
df_scaled = pd.DataFrame(X_scaled, columns=config.FEATURE_NAMES)
df_scaled.insert(0, "patient_id", df["patient_id"])
df_scaled.to_csv(config.SYNTHETIC_SCALED_PATH, index=False, compression="gzip")

labels_df = pd.DataFrame({"patient_id": df["patient_id"], "cluster_true": y_true})
labels_df.to_csv(config.SYNTHETIC_LABELS_PATH, index=False, compression="gzip")

print(f"Raw data saved to: {config.SYNTHETIC_RAW_PATH}")
print(f"Scaled data saved to: {config.SYNTHETIC_SCALED_PATH}")
print(f"Labels saved to: {config.SYNTHETIC_LABELS_PATH}")
print("\nCluster distribution (true labels):")
print(labels_df["cluster_true"].value_counts().sort_index())



