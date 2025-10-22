from functions.lib import *
###################
# Quality assurance
###################

def fn(dataset, index_date):

    # Prostate cancer
    dataset.prostate_cancer = minimum_of(
        last_matching_event_clinical_snomed_before(
            prostate_cancer_snomed, index_date
            ).date ,
        last_matching_event_apc_before(
            prostate_cancer_icd10, index_date
            ).admission_date
        )

    # Pregnancy
    dataset.pregnancy = last_matching_event_clinical_snomed_before(
        pregnancy_snomed, index_date
        ).date


    # COCP or HRT medication
    dataset.hrtcocp = last_matching_med_dmd_before(
        cocp_dmd + hrt_dmd, index_date
        ).date

    return dataset

