from functions.lib import *
##############
# HF diganosis
##############

def fn(dataset, index_date):

    #any evidence of HF, not just diagnosis codes, before index date
    hf_exclude_primary = last_matching_event_clinical_snomed_before(
        hf_exclude, index_date
        ).date

    #same but for secondary care
    hf_exclude_apc = last_matching_event_apc_before(
        hf_icd10, index_date,
        only_prim_diagnoses=False
        ).admission_date

    hf_exclude_ec = last_matching_event_ec_before(
        hf_ecds, index_date
        ).arrival_date

    dataset.hf_exclude = minimum_of(
        hf_exclude_primary,
        hf_exclude_apc,
        hf_exclude_ec
        )

    return dataset
