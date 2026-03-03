'''
Codelists as variables
'''

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

#BMI

bmi_weight_snomed = codelist_from_csv(
    "codelists/opensafely-weight-snomed.csv", column="code"
)
bmi_height_snomed = codelist_from_csv(
    "codelists/opensafely-height-snomed.csv",  column="code"
)
bmi_obesity_icd10 = codelist_from_csv(
    "codelists/user-elsie_horne-bmi_obesity_icd10.csv", column="code"
)

bmi_obesity_snomed = codelist_from_csv(
    "codelists/user-elsie_horne-bmi_obesity_snomed.csv", column="code"
)

bmi_code = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-bmival_cod.csv",
    column="code"
)

# Total Cholesterol
cholesterol_total_snomed = codelist_from_csv(
    "codelists/opensafely-cholesterol-tests-numerical-value.csv",
    column="code"
)

# HDL Cholesterol
cholesterol_hdl_snomed = codelist_from_csv(
    "codelists/bristol-hdl-cholesterol.csv",
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
sev_mental_res_primis = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-smhres.csv",
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
diabetes_type1_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-dmtype1_cod.csv",column="code"
    )

diabetes_type1_icd10 = codelist_from_csv(
    "codelists/opensafely-type-1-diabetes-secondary-care.csv",column="icd10_code"
    )

# T2DM
diabetes_type2_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-dmtype2_cod.csv",column="code"
    )

diabetes_type2_icd10 = codelist_from_csv(
    "codelists/user-r_denholm-type-2-diabetes-secondary-care-bristol.csv",column="code"
    )

# Other or non-specific diabetes
diabetes_other_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-otherdmaudit_cod.csv",column="code"
    )

# Gestational diabetes
diabetes_gestational_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-gestdiab_cod.csv",column="code"
                                              )

diabetes_gestational_icd10 = codelist_from_csv(
    "codelists/user-alainamstutz-gestational-diabetes-icd10-bristol.csv",column="code"
    )

# Non-diagnostic diabetes codes
diabetes_diagnostic_snomed = codelist_from_csv(
    "codelists/user-anschaf-diabetes-non-diagnostic-codes.csv",column="code"
                                             )

# HbA1c
test_hba1c_snomed = codelist_from_csv(
    "codelists/opensafely-glycated-haemoglobin-hba1c-tests-numerical-value.csv",column="code"
                                 )

# Antidiabetic drugs
diabetes_insulin_dmd = codelist_from_csv(
    "codelists/opensafely-insulin-medication.csv",column="id"
                                )

diabetes_antidiabetic_drugs_dmd = codelist_from_csv(
    "codelists/opensafely-antidiabetic-drugs.csv",column="id"
                                           )

diabetes_non_metformin_dmd = codelist_from_csv(
    "codelists/user-r_denholm-non-metformin-antidiabetic-drugs_bristol.csv",column="id"
                                      )

# HF 
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

hf_exclude_ = codelist_from_csv(
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

symptom_breathless_snomed = codelist_from_csv(
    "codelists/reducehf-beathlessness4all.csv",
    column="code"
)   

'''
breathlessness: primary care

codelist : reducehf-beathlessness4all

.. python::

    breathless_snomed = codelist_from_csv(
        "codelists/reducehf-beathlessness4all.csv",
        column="code"
    )   
'''

# HF-related oedema

symptom_oedema_snomed = codelist_from_csv(
    "codelists/reducehf-oedema4all.csv",
    column="code"
) 

'''
oedema: primary care

codelist : rreducehf-oedema4all

.. python::

    oedema_snomed = codelist_from_csv(
        "codelists/reducehf-oedema4all.csv",
        column="code"
    ) 
'''

# HF-related fatigue

symptom_fatigue_snomed = codelist_from_csv(
    "codelists/reducehf-fatigue4all.csv",
    column="code"
) 

'''
fatigue: primary care

codelist : reducehf-fatigue4all

.. python::

    fatigue_snomed = codelist_from_csv(
        "codelists/reducehf-fatigue4all.csv",
        column="code"
    ) 
'''

# NP testing 

test_NTpro_snomed = codelist_from_csv(
    "codelists/reducehf-ntpro-num-only.csv",
    column="code"
)
'''
NTpro-BNP test: primary care

codelist : reducehf-ntpro-num-only

.. python::

    NTpro_snomed = codelist_from_csv(
        "codelists/reducehf-ntpro-num-only.csv",
        column="code"
    )

'''


test_NP_snomed = codelist_from_csv(
    "codelists/reducehf-np-any.csv",
    column="code"
) 

'''
NP test: primary care

codelist : reducehf-np-any

.. python::

    NP_snomed = codelist_from_csv(
        "codelists/reducehf-np-any.csv",
        column="code"
    ) 
'''

#Echocardiography referral

echo_ref=codelist_from_csv(
    "codelists/reducehf-echocardiography-referral.csv",
    column="code"
)

'''
ECG referral: primary care

codelist : reducehf-echocardiography-referral

.. python::
    echo_ref=codelist_from_csv(
        "codelists/reducehf-echocardiography-referral.csv",
        column="code"
    )

'''

#Echocardiography has been completed
echo_done=codelist_from_csv(
    "codelists/reducehf-echocardiography-result.csv",
    column="code"
)

'''
ECG done: primary care

codelist: reducehf-echocardiography-result

.. python::
    echo_done=codelist_from_csv(
        "codelists/reducehf-echocardiography-result.csv",
        column="code"
    )

'''

#BP

bp_systolic = codelist_from_csv(
    "codelists/opensafely-systolic-blood-pressure-qof.csv",
    column="code"
)

'''
systolic BP: primary care

codelist: opensafely-systolic-blood-pressure-qof

.. python::

    systolic_bp = codelist_from_csv(
        "codelists/opensafely-systolic-blood-pressure-qof.csv",
        column="code"
    )
'''

bp_diastolic = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-diabp_cod.csv",
    column="code"
)

'''
diastolic BP: primary care

codelist: nhsd-primary-care-domain-refsets-diabp_cod

.. python::

    diastolic_bp = codelist_from_csv(
        "codelists/nhsd-primary-care-domain-refsets-diabp_cod.csv",
        column="code"
    )
'''

# Annual reviews

review_asthma = codelist_from_csv(
    "codelists/opensafely-asthma-annual-review-qof.csv",
    column="code"
)

'''
asthma annual review: primary care

codelist: opensafely-asthma-annual-review-qof

.. python::

    asthma_review = codelist_from_csv(
        "codelists/opensafely-asthma-annual-review-qof.csv",
        column="code"
    )
'''

review_copd = codelist_from_csv(
    "codelists/opensafely-chronic-obstructive-pulmonary-disease-copd-review-qof.csv",
    column="code"
)
'''
COPD annual review: primary care

codelist: opensafely-chronic-obstructive-pulmonary-disease-copd-review-qof

.. python::
    copd_review = codelist_from_csv(
        "codelists/opensafely-chronic-obstructive-pulmonary-disease-copd-review-qof.csv",
        column="code"
    )

'''

review_med = codelist_from_csv(
    "codelists/opensafely-care-planning-medication-review-simple-reference-set-nhs-digital.csv",
    column="code"
)

'''
medication annual review: primary care

codelist: opensafely-care-planning-medication-review-simple-reference-set-nhs-digital

.. python::

    med_review = codelist_from_csv(
        "codelists/opensafely-care-planning-medication-review-simple-reference-set-nhs-digital.csv",
        column="code"
    )

'''


#Underserved

migrant = codelist_from_csv(
    "codelists/user-YaminaB-migration-status.csv",
    column="code"
)

'''
migrant: primary care

codelist: user-YaminaB-migration-status

.. python::

    migrant = codelist_from_csv(
        "codelists/user-YaminaB-migration-status.csv",
        column="code"
    )
'''

non_english_speaking = codelist_from_csv(
    "codelists/reducehf-non-english-speaking.csv",
    column="code"
)

'''
non english speaking: primary care

codelist: reducehf-non-english-speaking

.. python::

    non_english_speaking = codelist_from_csv(
        "codelists/reducehf-non-english-speaking.csv",
        column="code"
    )

'''

substance_abuse = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-illsub_cod.csv",
    column="code"
)

'''
substance abuse: primary care

codelist: nhsd-primary-care-domain-refsets-illsub_cod

.. python::

    substance_abuse = codelist_from_csv(
        "codelists/nhsd-primary-care-domain-refsets-illsub_cod.csv",
        column="code"
    )
'''

housebound = codelist_from_csv(
    "codelists/opensafely-house-bound.csv",
    column="code"
)

'''
housebound: primary care

codelist: opensafely-house-bound

.. python::

    housebound = codelist_from_csv(
        "codelists/opensafely-house-bound.csv",
        column="code"
    )

'''

no_longer_housebound = codelist_from_csv(
    "codelists/opensafely-not-house-bound.csv",
    column="code"
)
'''
housebound resolved: primary care

codelist: opensafely-not-house-bound

.. python::

    no_longer_housebound = codelist_from_csv(
        "codelists/opensafely-not-house-bound.csv",
        column="code"
    )
'''

homeless = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-homeless_cod.csv",
    column="code"
)

'''
homeless: primary care

codelist: nhsd-primary-care-domain-refsets-homeless_cod

.. python::

    homeless = codelist_from_csv(
        "codelists/nhsd-primary-care-domain-refsets-homeless_cod.csv",
        column="code"
    )
'''

