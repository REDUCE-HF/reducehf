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

# Weight and height
weight_snomed = codelist_from_csv(
    "codelists/opensafely-weight-snomed.csv",
    column="code"
)
height_snomed = codelist_from_csv(
    "codelists/opensafely-height-snomed.csv",
    column="code"
)

# Obesity
bmi_obesity_icd10 = codelist_from_csv(
    "codelists/reducehf-obesity-icd10.csv",
    column="code"
)
bmi_obesity_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-bmiobese_cod.csv",
    column="code"
)

# Recorded BMI 
bmi_cod = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-bmival_cod.csv",
    column="code"
)

## BMI numeric value
bmi_numeric = codelist_from_csv(
    "codelists/reducehf-body-mass-index-numeric-value.csv",
    column = "code"
)

# Total Cholesterol
cholesterol_snomed = codelist_from_csv(
    "codelists/opensafely-cholesterol-tests-numerical-value.csv",
    column="code"
)

# HDL Cholesterol
hdl_cholesterol_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-hdlcchol_cod.csv",
    column="code"
)

# Wider Learning Disability
learndis_primis = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-learndis.csv",
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

# Ischaemic Stroke
stroke_isch_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-ostr_cod.csv",
    column="code"
)

stroke_isch_icd10 = codelist_from_csv(
    "codelists/user-RochelleKnight-stroke_isch_icd10.csv",
    column="code"
)

# Chronic Kidney disease
ckd_snomed_12 = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-ckd1and2_cod.csv",
    column="code"
)

ckd_snomed_345 = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-ckd_cod.csv",
    column="code"
)

ckd_snomed = ckd_snomed_12 + ckd_snomed_345

ckd_icd10 = codelist_from_csv(
    "codelists/reducehf-ckd-icd10.csv",
    column="code"
)

# Hypertension
hypertension_icd10 = codelist_from_csv(
    "codelists/reducehf-hypertension-icd10.csv",
    column="code"
)
hypertension_drugs_dmd = codelist_from_csv(
    "codelists/nhs-drug-refsets-antihyp_cod.csv",
    column="code"
)
hypertension_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-hyp_cod.csv",
    column="code"
)

# COPD
copd_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-copd_cod.csv",
    column="code"
)

copd_icd10 = codelist_from_csv(
    "codelists/opensafely-copd-secondary-care.csv",
    column="code"
)

copd_medications = codelist_from_csv(
  "codelists/opensafely-copd-medications-new-dmd.csv",
  column = "dmd_id"
)

# COPD Exacerbations
copd_exacerbations_snomed = codelist_from_csv(
    "codelists/bristol-copd-exacerbations.csv",
    column = "code"
)

copd_exacerbations_icd10 = codelist_from_csv(
    "codelists/opensafely-copd-exacerbation.csv",
    column = "code"
)

# Ischaemic heart diseae (ihd)
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
    "codelists/reducehf-atrial-fibrillation-and-flutter-icd10.csv",
    column ="code"
)

# DIABETES
# T1DM
diabetes_type1_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-dmtype1_cod.csv",
    column="code"
)

diabetes_type1_icd10 = codelist_from_csv(
    "codelists/reducehf-type-1-diabetes-icd10.csv",
    column="code"
)

# T2DM
diabetes_type2_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-dmtype2_cod.csv",
    column="code"
)

diabetes_type2_icd10 = codelist_from_csv(
    "codelists/reducehf-type-2-diabetes-icd10.csv",
    column="code"
)

# Other or non-specific diabetes
diabetes_other_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-otherdmaudit_cod.csv",
    column="code"
)

# Gestational diabetes
diabetes_gestational_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-gestdiab_cod.csv",
    column="code"
)

diabetes_gestational_icd10 = codelist_from_csv(
    "codelists/user-alainamstutz-gestational-diabetes-icd10-bristol.csv",
    column="code"
)

# Non-diagnostic diabetes codes
diabetes_nondiagnostic_ctv3 = codelist_from_csv(
    "codelists/reducehf-non-diagnostic-diabetes-codes-clone.csv",
    column="code"
)

# HbA1c
hba1c_snomed = codelist_from_csv(
    "codelists/user-anschaf-glycated-haemoglobin-hba1c-tests-numerical-value.csv",
    column="code"
)

# Antidiabetic drugs
insulin_dmd = codelist_from_csv(
    "codelists/reducehf-insulin-dmd.csv",
    column="code"
)

antidiabetic_drugs_dmd = codelist_from_csv(
    "codelists/user-anschaf-antidiabetes-medications-dmd.csv",
    column="code"
)

metformin_dmd = codelist_from_csv(
    "codelists/user-anschaf-metformin-dmd.csv",
    column="code"
)

non_metformin_dmd = set(antidiabetic_drugs_dmd) - set(metformin_dmd)

# HF (for script development)

hf_snomed = codelist_from_csv(
    "codelists/reducehf-heart-failure-primary-outcome.csv",
    column = "code"
)

hf_icd10 = codelist_from_csv(
    "codelists/reducehf-heart-failure-secondary-care.csv",
    column = "code"
)

hf_primary_icd10 = codelist_from_csv(
    "codelists/reducehf-heart-failure-primary-outcome-icd.csv",
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
    "codelists/reducehf-prostate-cancer-snomed.csv",
    column="code"
)
prostate_cancer_icd10 = codelist_from_csv(
    "codelists/reducehf-prostate-cancer-icd10.csv",
    column="code"
)
pregnancy_snomed = codelist_from_csv(
    "codelists/reducehf-pregnancy-and-birth-snomed.csv",
    column="code"
)
cocp_dmd = codelist_from_csv(
    "codelists/user-anschaf-oral-contraceptive-dmd.csv",
    column="code"
)

hrt_dmd = codelist_from_csv(
    "codelists/user-anschaf-hormone-replacement-therapy-dmd.csv",
    column="code"
)

# HF-related breathlessness
breathless_snomed = codelist_from_csv(
    "codelists/reducehf-breathlessness.csv",
    column="code"
)   

# HF-related oedema
oedema_snomed = codelist_from_csv(
    "codelists/reducehf-oedema.csv",
    column="code"
) 

# HF-related fatigue
fatigue_snomed = codelist_from_csv(
    "codelists/reducehf-fatigue.csv",
    column="code"
) 

# NP testing 
NTpro_snomed = codelist_from_csv(
    "codelists/reducehf-ntpro-num-only.csv",
    column="code"
)

NP_snomed = codelist_from_csv(
    "codelists/reducehf-np-any.csv",
    column="code"
) 

#Echocardiography referral
echo_ref=codelist_from_csv(
    "codelists/reducehf-echocardiography-referral.csv",
    column="code"
)

#Echocardiography has been completed
echo_done=codelist_from_csv(
    "codelists/reducehf-echocardiography-result.csv",
    column="code"
)

#BP
systolic_bp = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-sysbp_cod.csv",
    column="code"
)

diastolic_bp = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-diabp_cod.csv",
    column="code"
)

# Annual reviews
asthma_review = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-rev_cod.csv",
    column="code"
)

copd_review = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-copdrvw_cod.csv",
    column="code"
)

med_review = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-medrvw_cod.csv",
    column="code"
)

# Myocardial infarction - secondary care
mi_icd10 = codelist_from_csv(
    "codelists/reducehf-myocardial-infarction-icd10.csv",
    column="code"
)

#underserved
migrant = codelist_from_csv(
    "codelists/opensafely-migration-status.csv",
    column="code"
)

non_english_speaking = codelist_from_csv(
    "codelists/reducehf-non-english-speaking.csv",
    column="code"
)

substance_abuse = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-illsub_cod.csv",
    column="code"
)

housebound = codelist_from_csv(
    "codelists/opensafely-house-bound.csv",
    column="code"
)

no_longer_housebound = codelist_from_csv(
    "codelists/opensafely-not-house-bound.csv",
    column="code"
)

homeless = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-homeless_cod.csv",
    column="code"
)


