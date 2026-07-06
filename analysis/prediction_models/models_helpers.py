import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path

sys.path.insert(0, '..')

from clustering.config import (
    
    HOUSEHOLD_BINS,
    HOUSEHOLD_LABELS,
    HS_COLS,
    OBESITY_BMI_THRESHOLD,
    DIABETES_UNLIKELY_VALUE
)

from config_models import (
    DATE_COLS,
    CATEGORICAL_COLS,
    MEASURE_LIMITS,
    MEASURES_COLS,
    MLTC_COLS,
    UNDERSERVED_COLS,
    COPD_HSU_COLS,
    DUMMY_MEASURE_PARAMS,
)


def build_predictor_features(df):
    """
    Build predictor features for WP4 prediction models.Primary-care diagnosis only
    """

    out = pd.DataFrame({"patient_id": df["patient_id"]}, index=df.index)

    dates_df = {
        col: pd.to_datetime(df[col], errors="coerce")
        for col in DATE_COLS
    }

    index_date = dates_df["index_date"]

    # Age (Should be no missings)
    age = np.floor(
        (index_date - dates_df["birth_date"]).dt.days / 365.25
    )

    out["age"] = age
    

    # Household size
    hs_numeric = pd.to_numeric(df["household_size"], errors="coerce") # Remove this one ? 

    out["cat_household_size"] = pd.cut(
        hs_numeric,
        bins=HOUSEHOLD_BINS,
        labels=HOUSEHOLD_LABELS,
        right=True,
        include_lowest=True,
    ).astype("object")

    out.loc[
        hs_numeric.isna() | (hs_numeric <= 0),
        "cat_household_size"
    ] = "unknown"

    #  categorical predictors
    derived_cols = {"cat_household_size"}
    for col in CATEGORICAL_COLS:
        if col not in derived_cols:
            out[col] = df[col].astype("object")

    #  clinical measures
    for col in MEASURES_COLS:
        out[col] = pd.to_numeric(df[col], errors="coerce")

    # Primary-care MLTCs
    out["copd"] = dates_df["tmp_copd_date_primary"].notna().astype(int)

    out["hypertension"] = dates_df["hypertension_date_primary"].notna().astype(int)

    out["af"] = dates_df["af_date_primary"].notna().astype(int)

    out["ihd"] = dates_df["ihd_date_primary"].notna().astype(int)

    out["ckd"] = dates_df["ckd_date_primary"].notna().astype(int)

    # Diabetes
    out["has_diabetes"] = ((df["cat_diabetes"] != DIABETES_UNLIKELY_VALUE) & (df["cat_diabetes"].notna())).astype(int)

    # Obesity: primary-care code OR BMI >= 30 
    obesity_from_code = dates_df["obesity_primary_date"].notna()

    bmi_numeric = pd.to_numeric(df["bmi_value"], errors="coerce")
    bmi_lower, bmi_upper = MEASURE_LIMITS["bmi_value"]

    obesity_from_bmi = (
        (bmi_numeric >= OBESITY_BMI_THRESHOLD) & 
        (bmi_numeric >= bmi_lower) & 
        (bmi_numeric <= bmi_upper)
    )

    out["obesity"] = (obesity_from_code | obesity_from_bmi).astype(int)

    # Medication/treatment flags
    out["bp_treatment"] = (
        dates_df["last_hypertension_date_med"].notna().astype(int)
    )

    out["diabetes_treatment"] = (
        dates_df["last_diabetes_medication_date"].notna().astype(int)
    )

    # Multi-morbidity Keep both for now ? 
    out["mltc_count"] = out[MLTC_COLS].sum(axis=1)
    out["has_mltc"] = (out["mltc_count"] >= 2).astype(int)

    # Under-served groups
    for col in UNDERSERVED_COLS:
        out[col] = (
            pd.to_numeric(df[col], errors="coerce")
            .fillna(0)
            .astype(int)
        )

    out["n_underserved"] = out[UNDERSERVED_COLS].sum(axis=1)
    out["any_underserved"] = (
    out["n_underserved"] >= 1
    ).astype(int)

    # Review indicators
    out["asthma_review"] = dates_df["asthma_review_date"].notna().astype(int)
    out["copd_review"] = dates_df["copd_review_date"].notna().astype(int)
    out["med_review"] = dates_df["med_review_date"].notna().astype(int)

    # Pre-index healthcare utilisation
    for col in HS_COLS:
        out[col] = (
                pd.to_numeric(df[col], errors="coerce")
                .fillna(0)
            )

    # COPD-specific utilisation
    for col in COPD_HSU_COLS:
        out[col] = (
            pd.to_numeric(df[col], errors="coerce")
            .fillna(0)
            
        )

    out = out.drop(columns=["has_diabetes"])

    return out


def clean_measure_values(df):
    """
    Clean unplausible measurement values.
    """

    out = df.copy()


    # Swap systolic and diastolic BP if diastolic > systolic
    swap_bp = (
        out["sysbp_value"].notna()
        & out["diasbp_value"].notna()
        & (out["diasbp_value"] > out["sysbp_value"])
    )

    out.loc[swap_bp, ["sysbp_value", "diasbp_value"]] = (
        out.loc[swap_bp, ["diasbp_value", "sysbp_value"]].to_numpy()
    )

    for col, limits in MEASURE_LIMITS.items():

        lower, upper = limits

        out.loc[
            (out[col] < lower) | (out[col] > upper),
            col
        ] = np.nan

    invalid_bp = (
        out["sysbp_value"].notna()
        & out["diasbp_value"].notna()
        & (out["diasbp_value"] == out["sysbp_value"])
    )

    out.loc[
        invalid_bp,
        ["sysbp_value", "diasbp_value"]
    ] = np.nan

    return out

def is_binary_column(s):
    """
    check if a column is binary"""

    if s.dtype in ['object', 'category']:
        return False
    
    numeric_values = pd.to_numeric(s, errors='coerce')
    unique_values = set(numeric_values.dropna().unique())
    
    # Check if all values are 0 or 1 
    return len(unique_values) > 0 and all(v in (0, 1) for v in unique_values)

def fill_dummy_measure_values(df, missing_prop=0.2, seed=42):
    """ Fill measures values with plausible values + noise + random missing values.
      Otherwise, they are removed from the dataset. """
    
    rng = np.random.default_rng(seed)
    out = df.copy()

    

    for col, params in DUMMY_MEASURE_PARAMS.items():
        

        mean, sd, lower, upper = params

        values = rng.normal(mean, sd, len(out))
        values = np.clip(values, lower, upper)

        missing_mask = rng.random(len(out)) < missing_prop
        values[missing_mask] = np.nan

        out[col] = values

    
    invalid_bp = (
        out["sysbp_value"].notna()
        & out["diasbp_value"].notna()
        & (out["diasbp_value"] >= out["sysbp_value"])
    )

    out.loc[invalid_bp, "diasbp_value"] = (
        out.loc[invalid_bp, "sysbp_value"]
        - rng.uniform(20, 60, invalid_bp.sum())
    )

    out["diasbp_value"] = out["diasbp_value"].clip(lower=20, upper=200)

    return out