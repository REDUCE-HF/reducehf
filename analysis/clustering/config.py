#!/usr/bin/env python3
"""
Shared clustering configuration: paths, feature names, and common constants.
"""

import os

# -------------------
# Paths
# -------------------
# Detect if using synthetic data
USE_SYNTHETIC_INPUTS = os.getenv("USE_SYNTHETIC_INPUTS", "0") == "1"

# Real data directories
REAL_OUTPUT_DIR = "output/clustering/real"
# Synthetic data directories
SYNTHETIC_OUTPUT_DIR = "output/clustering/synthetic"

# Use appropriate output directory
OUTPUT_DIR = SYNTHETIC_OUTPUT_DIR if USE_SYNTHETIC_INPUTS else REAL_OUTPUT_DIR

# File names (same for both real and synthetic)
RAW_FILE = "clustering_raw.csv.gz"
SCALED_FILE = "clustering_scaled.csv.gz"
SYNTHETIC_LABELS_FILE = "clustering_true_labels.csv.gz"

# Real data paths
REAL_RAW_PATH = os.path.join(REAL_OUTPUT_DIR, RAW_FILE)
REAL_SCALED_PATH = os.path.join(REAL_OUTPUT_DIR, SCALED_FILE)

# Synthetic data paths
SYNTHETIC_RAW_PATH = os.path.join(SYNTHETIC_OUTPUT_DIR, RAW_FILE)
SYNTHETIC_SCALED_PATH = os.path.join(SYNTHETIC_OUTPUT_DIR, SCALED_FILE)
SYNTHETIC_LABELS_PATH = os.path.join(SYNTHETIC_OUTPUT_DIR, SYNTHETIC_LABELS_FILE)

# Dynamic paths that switch based on USE_SYNTHETIC_INPUTS
RAW_PATH = SYNTHETIC_RAW_PATH if USE_SYNTHETIC_INPUTS else REAL_RAW_PATH
SCALED_PATH = SYNTHETIC_SCALED_PATH if USE_SYNTHETIC_INPUTS else REAL_SCALED_PATH

# Input data path (for real data)
INPUT_DATA_PATH = "output/dataset_wp3.csv.gz"

# All other paths use OUTPUT_DIR (which switches automatically)
FEATURE_NAMES_PATH = os.path.join(OUTPUT_DIR, "clustering_features.txt")
D_GOWER_PATH = os.path.join(OUTPUT_DIR, "D_gower.csv.gz")
X_PCA_PATH = os.path.join(OUTPUT_DIR, "X_pca.csv.gz")
OPTIMAL_K_RESULTS_PATH = os.path.join(OUTPUT_DIR, "optimal_k_results.csv")
OPTIMAL_K_SUMMARY_PATH = os.path.join(OUTPUT_DIR, "optimal_k_summary.csv")
OPTICS_TUNING_RESULTS_PATH = os.path.join(OUTPUT_DIR, "optics_tuning_results.csv")
VALIDATION_RESULTS_PATH = os.path.join(OUTPUT_DIR, "validation_results.csv")
VISUALIZATION_SUMMARY_PATH = os.path.join(OUTPUT_DIR, "visualization_summary.csv")

# Synthetic validation results path
SYNTHETIC_VALIDATION_RESULTS_PATH = os.path.join(SYNTHETIC_OUTPUT_DIR, "synthetic_validation_results.csv")

# path to variance of means table
VARIANCE_OF_MEANS_PATH = os.path.join(OUTPUT_DIR, "variance_of_means.csv")
# path to one-hot encoded membership features
ENCODED_MEMBERSHIP_PATH = os.path.join(OUTPUT_DIR, "membership_features_encoded.csv")

def labels_path(config_name: str) -> str:
    return os.path.join(OUTPUT_DIR, f"labels_{config_name}.csv.gz")


def umap_path(config_name: str) -> str:
    return os.path.join(OUTPUT_DIR, f"umap_{config_name}.png")


def heatmap_path(config_name: str) -> str:
    return os.path.join(OUTPUT_DIR, f"heatmap_{config_name}.png")

# -------------------
# Synthetic generation parameters
# -------------------
N_SAMPLES = 10000 
N_CENTERS = 5
RANDOM_STATE = 42

FEATURE_NAMES = [
    "ed_attendances_pre_0_3m",
    "ed_attendances_pre_3_6m",
    "ed_attendances_pre_6_9m",
    "ed_attendances_pre_9_12m",
    "primary_care_attendances_pre_0_3m",
    "primary_care_attendances_pre_3_6m",
    "primary_care_attendances_pre_6_9m",
    "primary_care_attendances_pre_9_12m",
    "hospital_admissions_pre_0_3m",
    "hospital_admissions_pre_3_6m",
    "hospital_admissions_pre_6_9m",
    "hospital_admissions_pre_9_12m",
    "prescriptions_pre_0_3m",
    "prescriptions_pre_3_6m",
    "prescriptions_pre_6_9m",
    "prescriptions_pre_9_12m",
    "asthma_review_bin",
    "copd_review_bin",
    "med_review_bin",
]

# Simple min/max ranges for non-binary features (used after min-max scaling)
FEATURE_RANGES = {
    "ed_attendances_pre_0_3m": (0, 5),
    "ed_attendances_pre_3_6m": (0, 5),
    "ed_attendances_pre_6_9m": (0, 5),
    "ed_attendances_pre_9_12m": (0, 5),
    "primary_care_attendances_pre_0_3m": (0, 20),
    "primary_care_attendances_pre_3_6m": (0, 20),
    "primary_care_attendances_pre_6_9m": (0, 20),
    "primary_care_attendances_pre_9_12m": (0, 20),
    "hospital_admissions_pre_0_3m": (0, 4),
    "hospital_admissions_pre_3_6m": (0, 4),
    "hospital_admissions_pre_6_9m": (0, 4),
    "hospital_admissions_pre_9_12m": (0, 4),
    "prescriptions_pre_0_3m": (0, 10),
    "prescriptions_pre_3_6m": (0, 10),
    "prescriptions_pre_6_9m": (0, 10),
    "prescriptions_pre_9_12m": (0, 10),
}

