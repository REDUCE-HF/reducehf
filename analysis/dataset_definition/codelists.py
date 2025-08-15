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

breathless_snomed = codelist_from_csv(
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
    '''
    Not using the following as not specific to HF. Using codelists based on previous studies (HF-related). A/w clincial input
    -  breathlesness: https://www.opencodelists.org/codelist/nhsd-primary-care-domain-refsets/breathlessness-codes/20241205/
    -  oedema: not currently available - need to create
    -  fatigue: https://www.opencodelists.org/codelist/opensafely/symptoms-fatigue/0e9ac677/
    '''
# NP testing 

NP_snomed = codelist_from_csv(
    "codelists/reducehf-np-any-33175fed.csv",
    column="code"
) 

NTpro_snomed = codelist_from_csv(
    "codelists/reducehf-ntpro-num_only-65364657.csv",
    column="code"

#Echocardiography referral
echo_ref=codelist_from_csv(
    "codelists/reducehf-echocardiography-referral-35ca1fe3.csv",
    column="code"

#Echocardiography has been completed
echo_done=codelist_from_csv(
    "codelists/reducehf-echocardiography-result-03ab3979.csv",
    column="code"