CORE_COLS = [
    "patient_id",
    "index_date",
    "birth_date",
]

PREDICTOR_RAW_COLS = [
    "sex",
    "ethnicity_cat",
    "imd_quintile",
    "rural_urban",
    "region",
    "practice_stp",
    "msoa",
    "household_size",
    "smoking",
    "sysbp_value",
    "diasbp_value",
    "bmi_value",
    "last_hdl_cholesterol_value",
    "last_cholesterol_value",
    "last_hba1c_value",
    "last_hypertension_date_med",
    "last_diabetes_medication_date",
    "tmp_copd_date_primary",
    "hypertension_date_primary",
    "obesity_primary_date",
    "af_date_primary",
    "ihd_date_primary",
    "ckd_date_primary",
    "cat_diabetes",
    "learndis",
    "carehome_at_index",
    "non_english_speaking",
    "smi",
    "housebound",
    "substance_abuse",
    "homeless",
    "migrant",
    "ed_attendances_pre_0_3m",
    "primary_care_attendances_pre_0_3m",
    "hospital_admissions_pre_0_3m",
    "prescriptions_pre_0_3m",
    "ed_attendances_pre_3_6m",
    "primary_care_attendances_pre_3_6m",
    "hospital_admissions_pre_3_6m",
    "prescriptions_pre_3_6m",
    "ed_attendances_pre_6_9m",
    "primary_care_attendances_pre_6_9m",
    "hospital_admissions_pre_6_9m",
    "prescriptions_pre_6_9m",
    "ed_attendances_pre_9_12m",
    "primary_care_attendances_pre_9_12m",
    "hospital_admissions_pre_9_12m",
    "prescriptions_pre_9_12m",
    "copd_ed_attendances_pre_12m",
    "copd_primary_care_attendances_pre_12m",
    "copd_hospital_admissions_pre_12m",
    "copd_prescriptions_pre12m",
    "asthma_review_date",
    "copd_review_date",
    "med_review_date",
]

NOT_AVAILABLE_COLS = [
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
    "sex",
    "ethnicity_cat",
    "imd_quintile",
    "region",
    "rural_urban",
    "practice_stp",
    "msoa",
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
LTC_COLS = [
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

# COPD-specific pre-index healthcare utilisation columns
COPD_HSU_COLS = [
    "copd_ed_attendances_pre_12m",
    "copd_primary_care_attendances_pre_12m",
    "copd_hospital_admissions_pre_12m",
    "copd_prescriptions_pre12m",
]

