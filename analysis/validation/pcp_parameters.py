

import pandas as pd
import numpy as np

# pcp_parameters.py

WHITE_MALE = {
    "ln_age": 42.50,
    "ln_age_squared": -0.97,
    "ln_treated_sbp": 0.97,
    "ln_age_x_ln_treated_sbp": None,
    "ln_untreated_sbp": 0.85,
    "ln_age_x_ln_untreated_sbp": None,
    "current_smoker": 0.73,
    "ln_age_x_current_smoker": None,
    "ln_treated_glucose": 0.92,
    "ln_untreated_glucose": 0.80,
    "ln_total_cholesterol": 0.46,
    "ln_hdl": -0.42,
    "ln_bmi": 37.0,
    "ln_age_x_ln_bmi": -8.77,
    "mean_cv": 169.25,
    "baseline_survival": 0.98743,
}

WHITE_FEMALE = {
    "ln_age": 18.15,
    "ln_age_squared": None,
    "ln_treated_sbp": 10.85,
    "ln_age_x_ln_treated_sbp": -2.47,
    "ln_untreated_sbp": 9.71,
    "ln_age_x_ln_untreated_sbp": -2.21,
    "current_smoker": 10.95,
    "ln_age_x_current_smoker": -2.50,
    "ln_treated_glucose": 1.03,
    "ln_untreated_glucose": 0.90,
    "ln_total_cholesterol": None,
    "ln_hdl": -0.07,
    "ln_bmi": 1.37,
    "ln_age_x_ln_bmi": None,
    "mean_cv": 85.03,
    "baseline_survival": 0.99331,
}

BLACK_MALE = {
    "ln_age": 2.99,
    "ln_age_squared": None,
    "ln_treated_sbp": 2.40,
    "ln_age_x_ln_treated_sbp": None,
    "ln_untreated_sbp": 2.26,
    "ln_age_x_ln_untreated_sbp": None,
    "current_smoker": 1.49,
    "ln_age_x_current_smoker": -0.21,
    "ln_treated_glucose": 0.63,
    "ln_untreated_glucose": 0.55,
    "ln_total_cholesterol": None,
    "ln_hdl": -0.80,
    "ln_bmi": 1.21,
    "ln_age_x_ln_bmi": None,
    "mean_cv": 26.30,
    "baseline_survival": 0.98297,
}

BLACK_FEMALE = {
    "ln_age": 50.32,
    "ln_age_squared": None,
    "ln_treated_sbp": 29.0,
    "ln_age_x_ln_treated_sbp": -6.57,
    "ln_untreated_sbp": 28.09,
    "ln_age_x_ln_untreated_sbp": -6.37,
    "current_smoker": 0.75,
    "ln_age_x_current_smoker": None,
    "ln_treated_glucose": 0.99,
    "ln_untreated_glucose": 0.83,
    "ln_total_cholesterol": 0.26,
    "ln_hdl": None,
    "ln_bmi": 19.75,
    "ln_age_x_ln_bmi": -4.60,
    "mean_cv": 223.05,
    "baseline_survival": 0.99241,
}

PCP_MODELS = {
    ("white", "male"): WHITE_MALE,
    ("white", "female"): WHITE_FEMALE,
    ("black", "male"): BLACK_MALE,
    ("black", "female"): BLACK_FEMALE,
}

def calculate_pcp_hf_risk(df, params):
    """
    Calculate PCP-HF predicted risk for one sex/ethnicity subgroup.
    """

    out = df.copy()

    # Unit conversions to mg/dL
    glucose_mgdl = out["fasting_blood_glucose_value"] * 18.0182
    cholesterol_mgdl = out["last_cholesterol_value"] * 38.67
    hdl_mgdl = out["last_hdl_cholesterol_value"] * 38.67

    # Log-transformed predictors
    ln_age = np.log(out["age"])
    ln_sbp = np.log(out["sysbp_value"])
    ln_glucose = np.log(glucose_mgdl)
    ln_cholesterol = np.log(cholesterol_mgdl)
    ln_hdl = np.log(hdl_mgdl)
    ln_bmi = np.log(out["bmi_value"])

    # Start linear predictor
    indx = params["ln_age"] * ln_age

    # Add terms only if present in that subgroup model
    if params["ln_age_squared"] is not None:
        indx += params["ln_age_squared"] * (ln_age ** 2)

    # SBP
    indx += np.where(
        out["bp_treatment"] == 1,
        params["ln_treated_sbp"] * ln_sbp,
        params["ln_untreated_sbp"] * ln_sbp
    )

    if params["ln_age_x_ln_treated_sbp"] is not None:
        indx += np.where(
            out["bp_treatment"] == 1,
            params["ln_age_x_ln_treated_sbp"] * ln_age * ln_sbp,
            0
        )

    if params["ln_age_x_ln_untreated_sbp"] is not None:
        indx += np.where(
            out["bp_treatment"] == 0,
            params["ln_age_x_ln_untreated_sbp"] * ln_age * ln_sbp,
            0
        )

    # Smoking
    indx += params["current_smoker"] * out["smoking"]

    if params["ln_age_x_current_smoker"] is not None:
        indx += (
            params["ln_age_x_current_smoker"]
            * ln_age
            * out["smoking"]
        )

    # Glucose
    indx += np.where(
        out["diabetes_treatment"] == 1,
        params["ln_treated_glucose"] * ln_glucose,
        params["ln_untreated_glucose"] * ln_glucose
    )

    # Cholesterol
    if params["ln_total_cholesterol"] is not None:
        indx += params["ln_total_cholesterol"] * ln_cholesterol

    # HDL
    if params["ln_hdl"] is not None:
        indx += params["ln_hdl"] * ln_hdl

    # BMI
    indx += params["ln_bmi"] * ln_bmi

    if params["ln_age_x_ln_bmi"] is not None:
        indx += (
            params["ln_age_x_ln_bmi"]
            * ln_age
            * ln_bmi
        )

    # Absolute PCP-HF risk
    out["pcp_hf_prediction"] = (
        1
        - params["baseline_survival"]
        ** np.exp(indx - params["mean_cv"])
    )

    return out