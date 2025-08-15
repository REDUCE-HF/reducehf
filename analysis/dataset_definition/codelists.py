from ehrql import codelist_from_csv


# Ethnicity
ethnicity_codes = codelist_from_csv(
    "codelists/opensafely-ethnicity-snomed-0removed.csv",
    column="code",
    category_column="Grouping_6"
)

# Smoking
smoking_current = codelist_from_csv(
    "codelists/reducehf-current-smoker.csv",
    column="code"
)
smoking_former = codelist_from_csv(
    "codelists/reducehf-former-smoker.csv",
    column="code"
)
smoking_ever = smoking_current + smoking_former


weight_snomed = codelist_from_csv(
    "codelists/opensafely-weight-snomed.csv", column="code"
)
height_snomed = codelist_from_csv(
    "codelists/opensafely-height-snomed.csv",  column="code"
)
bmi_obesity_icd10 = codelist_from_csv(
    "codelists/user-elsie_horne-bmi_obesity_icd10.csv", column="code"
)

bmi_obesity_snomed = codelist_from_csv(
    "codelists/user-elsie_horne-bmi_obesity_snomed.csv", column="code"
)


# BMI
bmi_cod = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-bmival_cod.csv",
    column="code"
)


# Total Cholesterol
cholesterol_snomed = codelist_from_csv(
    "codelists/opensafely-cholesterol-tests-numerical-value.csv",
    column="code"
)

# HDL Cholesterol
hdl_cholesterol_snomed = codelist_from_csv(
    "codelists/bristol-hdl-cholesterol.csv",
    column="code"
)

# Wider Learning Disability
learndis_primis = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-learndis.csv",
    column="code"
)

## All BMI coded terms
bmi_stage_primis = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-bmi_stage.csv",
    column="code"
)

## BMI numeric value
bmi_numeric = codelist_from_csv(
    "codelists/reducehf-body-mass-index-numeric-value.csv",
    column = "code"
)

## Severe Obesity code recorded
sev_obesity_primis = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-sev_obesity.csv",
    column="code"
)

## Chronic Respiratory Disease
resp_primis = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-resp_cov.csv",
    column="code"
)

## Chronic Neurological Disease including Significant Learning Disorder
cns_primis = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-cns_cov.csv",
    column="code"
)

## Diabetes diagnosis codes
diab_primis = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-diab.csv",
    column="code"
)

## Diabetes resolved codes
dmres_primis = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-dmres.csv",
    column="code"
)

## Severe Mental Illness codes
sev_mental_primis = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-sev_mental.csv",
    column="code"
)

## Remission codes relating to Severe Mental Illness
smhres_primis = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-smhres.csv",
    column="code"
)

## Chronic heart disease codes
chd_primis = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-chd_cov.csv",
    column="code"
)

## Chronic kidney disease diagnostic codes
ckd_primis = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-ckd_cov.csv",
    column="code"
)

## Chronic kidney disease codes - all stages
ckd15_primis = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-ckd15.csv",
    column="code"
)

## Chronic kidney disease codes-stages 3 - 5
ckd35_primis = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-ckd35.csv",
    column="code"
)

## Chronic Liver disease codes
cld_primis = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-cld.csv",
    column="code"
)

# Stroke Ischaemic (Ischaemic Stroke)
stroke_isch_snomed = codelist_from_csv(
    "codelists/user-elsie_horne-stroke_isch_snomed.csv",
    column="code"
)

stroke_isch_icd10 = codelist_from_csv(
    "codelists/user-RochelleKnight-stroke_isch_icd10.csv",
    column="code"
)

# Chronic Kidney disease
ckd_snomed = codelist_from_csv(
    "codelists/user-elsie_horne-ckd_snomed.csv",
    column="code"
)

ckd_icd10 = codelist_from_csv(
    "codelists/user-elsie_horne-ckd_icd10.csv",
    column="code"
)

# Hypertension
hypertension_icd10 = codelist_from_csv(
    "codelists/user-elsie_horne-hypertension_icd10.csv",
    column="code"
)
hypertension_drugs_dmd = codelist_from_csv(
    "codelists/user-elsie_horne-hypertension_drugs_dmd.csv",
    column="dmd_id"
)
hypertension_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-hyp_cod.csv",
    column="code"
)

# Diabetes
diabetes_icd10 = codelist_from_csv(
    "codelists/user-elsie_horne-diabetes_icd10.csv",
    column="code"
)

diabetes_drugs_dmd = codelist_from_csv(
    "codelists/user-elsie_horne-diabetes_drugs_dmd.csv",
    column="dmd_id"
)

diabetes_snomed = codelist_from_csv(
    "codelists/user-elsie_horne-diabetes_snomed.csv",
    column="code"
)   

# COPD

copd_ctv3 = codelist_from_csv(
    "codelists/opensafely-current-copd.csv",
    column="CTV3ID"
)

copd_icd10 = codelist_from_csv(
    "codelists/opensafely-copd-secondary-care.csv",
    column="code"
)

#ischaemic heart diseae (ihd)
ihd_snomed = codelist_from_csv(
    "codelists/bristol-ischaemic-heart-disease-snomed.csv",
    column="code"
)

ihd_icd10 = codelist_from_csv(
    "codelists/bristol-ischaemic-heart-disease-icd10.csv",
    column="code"
)

#Atrial fibrillation (af)
af_snomed = codelist_from_csv(
    "codelists/bristol-atrial-fibrillation-snomed.csv",
    column="code"
)

af_icd10 = codelist_from_csv (
    "codelists/bristol-atrial-fibrillation-icd10.csv",
    column ="code"
)

# DIABETES
# T1DM
diabetes_type1_ctv3 = codelist_from_csv(
    "codelists/user-hjforbes-type-1-diabetes.csv",column="code"
    )

diabetes_type1_icd10 = codelist_from_csv(
    "codelists/opensafely-type-1-diabetes-secondary-care.csv",column="icd10_code"
    )

# T2DM
diabetes_type2_ctv3 = codelist_from_csv(
    "codelists/user-hjforbes-type-2-diabetes.csv",column="code"
    )

diabetes_type2_icd10 = codelist_from_csv(
    "codelists/user-r_denholm-type-2-diabetes-secondary-care-bristol.csv",column="code"
    )

# Other or non-specific diabetes
diabetes_other_ctv3 = codelist_from_csv(
    "codelists/user-hjforbes-other-or-nonspecific-diabetes.csv",column="code"
    )

# Gestational diabetes
diabetes_gestational_ctv3 = codelist_from_csv(
    "codelists/user-hjforbes-gestational-diabetes.csv",column="code"
                                              )

diabetes_gestational_icd10 = codelist_from_csv(
    "codelists/user-alainamstutz-gestational-diabetes-icd10-bristol.csv",column="code"
    )

# Non-diagnostic diabetes codes
diabetes_diagnostic_ctv3 = codelist_from_csv(
    "codelists/user-hjforbes-nondiagnostic-diabetes-codes.csv",column="code"
                                             )

# HbA1c
hba1c_snomed = codelist_from_csv(
    "codelists/opensafely-glycated-haemoglobin-hba1c-tests-numerical-value.csv",column="code"
                                 )

# Antidiabetic drugs
insulin_dmd = codelist_from_csv(
    "codelists/opensafely-insulin-medication.csv",column="id"
                                )

antidiabetic_drugs_dmd = codelist_from_csv(
    "codelists/opensafely-antidiabetic-drugs.csv",column="id"
                                           )

non_metformin_dmd = codelist_from_csv(
    "codelists/user-r_denholm-non-metformin-antidiabetic-drugs_bristol.csv",column="id"
                                      )

# HF (for script development)

hf_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-hf_cod.csv",
    column = "code"
)


hf_icd10 = codelist_from_csv(
    "codelists/reducehf-heart-failure-secondary-care.csv",
    column = "code"
)

hf_ecds = codelist_from_csv(
    "codelists/reducehf-heart-failure-ae.csv",
    column = "code"
)

hf_exclude = codelist_from_csv(
    "codelists/reducehf-heart-failure-broad-for-excluding-people.csv",
    column = "code"
)


# Quality assurance

prostate_cancer_snomed = codelist_from_csv(
    "codelists/user-RochelleKnight-prostate_cancer_snomed.csv",
    column="code"
)
prostate_cancer_icd10 = codelist_from_csv(
    "codelists/user-RochelleKnight-prostate_cancer_icd10.csv",
    column="code"
)
pregnancy_snomed = codelist_from_csv(
    "codelists/user-RochelleKnight-pregnancy_and_birth_snomed.csv",
    column="code"
)
cocp_dmd = codelist_from_csv(
    "codelists/user-elsie_horne-cocp_dmd.csv",
    column="dmd_id"
)
hrt_dmd = codelist_from_csv(
    "codelists/user-elsie_horne-hrt_dmd.csv",
    column="dmd_id"
)

# HF-related breathlessness

breathlessness_snomed = codelist_from_csv(
    "codelists/reducehf-breathlessness4all.csv",
    column="code"
)   
# HF-related oedema

oedema_snomed = codelist_from_csv(
    "codelists/reducehf-oedema4all.csv",
    column="code"
) 
# HF-related fatigue

fatigue_snomed = codelist_from_csv(
    "codelists/reducehf-fatigue4all.csv",
    column="code"
) 

# NP testing - need to split into BNP and NT-proBNP for WP(2)

NP_snomed = codelist_from_csv(
    "codelists/reducehf-np-testing-4all.csv",
    column="code"
) 

NP_ctv3 = codelist_from_csv(
    "codelists/reducehf-np-testing-read.csv",
    column="code"
)

#BP

systolic_bp = codelist_from_csv(
    "codelists/opensafely-systolic-blood-pressure-qof.csv",
    column="code"
)
