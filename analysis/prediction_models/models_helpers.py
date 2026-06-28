import pandas as pd
import numpy as np
import sys

sys.path.insert(0, '..')

from clustering.config import (
    AGE_BINS,
    AGE_LABELS,
    HOUSEHOLD_BINS,
    HOUSEHOLD_LABELS,
    HS_COLS,
    REVIEW_COLS,
    OBESITY_BMI_THRESHOLD,
    DIABETES_UNLIKELY_VALUE,
)

from config_models import (
    DATE_COLS,
    CATEGORICAL_COLS,
    MEASURE_LIMITS,
    MEASURES_COLS,
    MLTC_COLS,
    UNDERSERVED_COLS,
    COPD_HSU_COLS,
    MEASURE_LIMITS,

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

    # Age
    age = np.floor(
        (index_date - dates_df["birth_date"]).dt.days / 365.25
    )

    out["age"] = age

    out["age_band"] = pd.cut(
        age,
        bins=AGE_BINS,
        labels=AGE_LABELS,
        right=False,
        include_lowest=True,
    ).astype("object")

    # Household size
    hs_numeric = pd.to_numeric(df["household_size"], errors="coerce")

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
    for col in CATEGORICAL_COLS:
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
    out["has_diabetes"] = (df["cat_diabetes"] != DIABETES_UNLIKELY_VALUE).astype(int)

    # Obesity: primary-care code OR BMI >= 30
    obesity_from_code = dates_df["obesity_primary_date"].notna()

    obesity_from_bmi = (
        pd.to_numeric(df["bmi_value"], errors="coerce")
        .ge(OBESITY_BMI_THRESHOLD)
        .fillna(False)
    )

    out["obesity"] = (
        obesity_from_code | obesity_from_bmi
    ).astype(int)

    # Medication/treatment flags
    out["bp_treatment"] = (
        dates_df["last_hypertension_date_med"].notna().astype(int)
    )

    out["diabetes_treatment"] = (
        dates_df["last_diabetes_medication_date"].notna().astype(int)
    )

    # Multi-morbidity
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

    # COPD-specific pre-index utilisation
    for col in COPD_HSU_COLS:
        out[col] = (
            pd.to_numeric(df[col], errors="coerce")
            .fillna(0)
            
        )

    return out


def clean_measure_values(df):
    """
    Clean unplausible measurement values.
    https://github.com/Exeter-Diabetes/EHRBiomarkr/blob/main/data-raw/qrisk2_constants.yaml
    
    """

    out = df.copy()

    for col, limits in MEASURE_LIMITS.items():
        
        lower, upper = limits
        out[col] = pd.to_numeric(out[col], errors="coerce")
        out.loc[
            (out[col] < lower) | (out[col] > upper),
            col
        ] = np.nan

    #check if diasbp >sysbp
    invalid_bp = (
        out["sysbp_value"].notna()
        & out["diasbp_value"].notna()
        & (out["diasbp_value"] > out["sysbp_value"])
    )

    out.loc[
        invalid_bp,
        ["sysbp_value", "diasbp_value"]
    ] = np.nan

    return out

def is_binary_column(s):
    
    numeric_values = pd.to_numeric(s, errors='coerce')
    unique_values = set(numeric_values.dropna().unique())
    
    # Check if all values are 0 or 1 
    return len(unique_values) > 0 and all(v in (0, 1) for v in unique_values)
