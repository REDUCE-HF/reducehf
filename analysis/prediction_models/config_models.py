CORE_COLS = [
    "patient_id",
    "index_date",
    "birth_date",
]

# PREDICTOR_RAW_COLS = [
#     "sex",
#     "ethnicity_cat",
#     "imd_quintile",
#     "rural_urban",
#     "region",
#     "practice_stp",
#     "msoa",
#     "household_size",
#     "smoking",
#     "sysbp_value",
#     "diasbp_value",
#     "bmi_value",
#     "last_hdl_cholesterol_value",
#     "last_cholesterol_value",
#     "last_hba1c_value",
#     "last_hypertension_date_med",
#     "last_diabetes_medication_date",
#     "tmp_copd_date_primary",
#     "hypertension_date_primary",
#     "obesity_primary_date",
#     "af_date_primary",
#     "ihd_date_primary",
#     "ckd_date_primary",
#     "cat_diabetes",
#     "learndis",
#     "carehome_at_index",
#     "non_english_speaking",
#     "smi",
#     "housebound",
#     "substance_abuse",
#     "homeless",
#     "migrant",
#     "ed_attendances_pre_0_3m",
#     "primary_care_attendances_pre_0_3m",
#     "hospital_admissions_pre_0_3m",
#     "prescriptions_pre_0_3m",
#     "ed_attendances_pre_3_6m",
#     "primary_care_attendances_pre_3_6m",
#     "hospital_admissions_pre_3_6m",
#     "prescriptions_pre_3_6m",
#     "ed_attendances_pre_6_9m",
#     "primary_care_attendances_pre_6_9m",
#     "hospital_admissions_pre_6_9m",
#     "prescriptions_pre_6_9m",
#     "ed_attendances_pre_9_12m",
#     "primary_care_attendances_pre_9_12m",
#     "hospital_admissions_pre_9_12m",
#     "prescriptions_pre_9_12m",
#     "copd_ed_attendances_pre_12m",
#     "copd_primary_care_attendances_pre_12m",
#     "copd_hospital_admissions_pre_12m",
#     "copd_prescriptions_pre12m",
#     "asthma_review_date",
#     "copd_review_date",
#     "med_review_date",
# ]

NOT_AVAILABLE_COLS = [ #TODO: Check with Charlotte,
    "coastal",
    "icb",
    "loop_diuretics",
    "np_bnp_ntprobnp_testing",
    "ntprobnp_test_result",
    "suspected_hf_code",
    "hf_related_breathlessness_oedema_fatigue",
    "copd_severity_marker_1",
    "copd_severity_marker_2",
    "cardio_respiratory_admission_rate",
    "fasting_glucose",
    "qrs_duration",
    "depression",
]

# Date columns for feature derivation
DATE_COLS = [
    "index_date",
    "birth_date",
    "tmp_copd_date_primary",
    "hypertension_date_primary",
    "obesity_primary_date",
    "af_date_primary",
    "ihd_date_primary",
    "ckd_date_primary",
    "last_hypertension_date_med",
    "last_diabetes_medication_date",
    "asthma_review_date",
    "copd_review_date",
    "med_review_date",
]

# Categorical predictors
CATEGORICAL_COLS = [
    "age_band",
    "cat_household_size",
    "sex",
    "ethnicity_cat",
    "imd_quintile",
    "region",
    "rural_urban",
    "practice_stp",#likely to be removed 
    "msoa",#likely to be removed
    "cat_diabetes",
    "smoking",
]


# Clinical measurement columns
MEASURES_COLS = [
    "sysbp_value",
    "diasbp_value",
    "bmi_value",
    "last_hdl_cholesterol_value",
    "last_cholesterol_value",
    "last_hba1c_value",
]

# Long-term condition columns
MLTC_COLS = [
    "copd",
    "hypertension",
    "has_diabetes",
    "obesity",
    "af",
    "ihd",
    "ckd",
]

# Under-served populations columns
UNDERSERVED_COLS = [
    "learndis",
    "carehome_at_index",
    "housebound",
    "smi",
    "homeless",
    "substance_abuse",
    "migrant",
    "non_english_speaking",
]

# COPD healthcare utilisation columns
COPD_HSU_COLS = [
    "copd_ed_attendances_pre_12m",
    "copd_primary_care_attendances_pre_12m",
    "copd_hospital_admissions_pre_12m",
    "copd_prescriptions_pre12m",
]

#https://github.com/Exeter-Diabetes/EHRBiomarkr/blob/main/data-raw/qrisk2_constants.yaml
MEASURE_LIMITS = {
    "sysbp_value": (40, 270),
    "diasbp_value": (20, 200),
    "bmi_value": (15, 100),
    "last_hdl_cholesterol_value": (0.2, 10),
    "last_cholesterol_value": (0.5, 20),
    "last_hba1c_value": (20, 195),
}

DUMMY_MEASURE_PARAMS = {
        "sysbp_value": (130, 20, 40, 270),
        "diasbp_value": (80, 12, 20, 200),
        "bmi_value": (28, 6, 15, 100),
        "last_hdl_cholesterol_value": (1.3, 0.4, 0.2, 10),
        "last_cholesterol_value": (5.0, 1.2, 0.5, 20),
        "last_hba1c_value": (45, 15, 20, 195),
    }

# Output paths for prepared datasets
TEST_DATA_PATH = "../../output/models/test_data.csv.gz"
TRAIN_DATA_PATH = "../../output/models/train_data.csv.gz" 