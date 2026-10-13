"""
Config for the optimisation notebooks (04_x).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdc_helpers import DISCLOSURE_THRESHOLD

from config_models import OUTPUT_DIR, SUBGROUP_COLS


RANDOM_STATE = 42
N_SPLITS = 5

IS_DUMMY_DATA = os.getenv("OPENSAFELY_BACKEND") is None

# Minimum cases and non-cases per class to train (CV folds) and to report
MIN_TRAIN_PER_CLASS = max(N_SPLITS, DISCLOSURE_THRESHOLD + 1)
MIN_TEST_PER_CLASS = 1 if IS_DUMMY_DATA else DISCLOSURE_THRESHOLD + 1

OPTIMISATION_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "optimisation")

# Method names
SUBGROUP_MODELS_METHOD = "subgroup_specific_models"
UNDERSAMPLING_METHOD = "undersampling"
UNDERSAMPLING_COMBINED_METHOD = "undersampling_combined_at_risk"


# undersampling ratios for at-risk vs non-at-risk groups.
NON_RISK_PER_RISK_VALUES = [1, 0.5]





# For undersampling goup by group, undersample each at risk rule.TBC from WP1 results. 
AT_RISK_RULES = {
    # 75+
    "age_band": ["75-79", "80-84", "85-89", "90-94", "95-99", "100+"],
    "sex": ["female"],
    "ethnicity_cat": ["Black", "Asian"],
    # two most deprived quintiles
    "imd_quintile": ["1 (most deprived)", "2"],
    # rural classes: 5-6 rural town and fringe, 7-8 rural village and dispersed
    "rural_urban": [5, 6, 7, 8],
    # TODO: region - pick at-risk regions from WP1 results
    "mltc_count": {"min": 2},
    # binary under-served variables
    "migrant": [1],
    "learndis": [1],
    "non_english_speaking": [1],
    "smi": [1],
    "substance_abuse": [1],
    "homeless": [1],
    "housebound": [1],
}

SUBGROUP_VARS = [
    col for col in SUBGROUP_COLS
    if col not in ["patient_id", "hf_outcome"]
]

GROUP_COUNT_COLS = [
    "n_train",
    "train_events",
    "train_nonevents",
    "n_test",
    "test_events",
    "test_nonevents",
]

CONFUSION_COUNT_COLS = [
    "true_positives",
    "false_positives",
    "true_negatives",
    "false_negatives",
]

METRIC_COLS = [
    "auc",
    "auc_pr",
    "brier",
    "accuracy",
    "precision",
    "recall",
    "f1",
    "sensitivity",
    "specificity",
]

# Common groups (sex, age_band) are left out, because they are big groups. 
# TODO: confirm with WP1 results (rural_urban, region)
COMBINED_AT_RISK_VARS = [
    "ethnicity_cat",
    "imd_quintile",
    "mltc_count",
    "migrant",
    "learndis",
    "non_english_speaking",
    "smi",
    "substance_abuse",
    "homeless",
    "housebound",
]

# # For combined at-risk undersampling: A patient is in the combined at-risk set if they are in ANY of these groups.
COMBINED_AT_RISK_RULES = {}
for var in COMBINED_AT_RISK_VARS:
    COMBINED_AT_RISK_RULES[var] = AT_RISK_RULES[var]
