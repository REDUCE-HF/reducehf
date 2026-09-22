import os


# Project root: reducehf/
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)


# WP4 dataset
WP4_DATASET_PATH = os.path.join(
    PROJECT_ROOT,
    "output/dataset_wp4.csv.gz"
)

main_cols = [
    "patient_id",
    "sex",
    "ethnicity_cat",
    "index_date",
    "birth_date",
    "sysbp_value",
    "bmi_value",
    "last_cholesterol_value",
    "last_hdl_cholesterol_value",
    "last_hba1c_value",
    "smoking",
    "last_hypertension_date_med",
    "last_diabetes_medication_date",
    "hf_diagnosis_date",
    "hf_diagnosis_primary_date",
    "hf_diagnosis_apc_date",
    "hf_diagnosis_ec_date",
    "fasting_blood_glucose_value",
    "imd_quintile"
]

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output/validation")

