# Setup
from ehrql import codelist_from_csv


# Ethnicity
ethnicity_snomed = codelist_from_csv(
    "codelists/opensafely-ethnicity-snomed-0removed.csv",
    column="code",
    category_column="Grouping_6"
)

# Smoking
smoking_clear = codelist_from_csv(
    "codelists/opensafely-smoking-clear.csv",
    column="CTV3Code",
    category_column="Category"
)

# BMI
bmi_obesity_snomed = codelist_from_csv(
    "codelists/user-elsie_horne-bmi_obesity_snomed.csv",
    column="code"
)

bmi_obesity_icd10 = codelist_from_csv(
    "codelists/user-elsie_horne-bmi_obesity_icd10.csv",
    column="code"
)

bmi_primis = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-bmi.csv",
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

# HF (for script development)

hf_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-hf_cod.csv",
    column = "code"
)

# HF-related breathlessness

breathlessness_snomed = codelist_from_csv(
    "codelists/reducehf-breathnessness4all-6d0c1be7.csv",
    column="code"
)   
# HF-related oedema

oedema_snomed = codelist_from_csv(
    "codelists/reducehf-oedema4all-2efcdccd.csv",
    column="code"
) 
# HF-related fatigue

fatigue_snomed = codelist_from_csv(
    "codelists/reducehf-fatigue4all-7cddf662.csv",
    column="code"
) 

# NP testing - need to split into BNP and NT-proBNP for WP(2)

NP_snomed = codelist_from_csv(
    "codelists/reducehf-np-testing-4all-63ce832d.csv",
    column="code"
) 
NP_ctv3 = codelist_from_csv(
    "codelists/reducehf-np-testing-read-678a6104.csv",
    column="code"
) 