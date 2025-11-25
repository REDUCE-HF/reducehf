from functions.lib import *

###########################
# HF codes - for exclusion
###########################

def fn(dataset, earliest_date, index_date):

    #filter data - use placeholder start date to get all past events
    before_gp_events = filter_gp_events(earliest_date, index_date)
    before_apc_events = filter_apc_events(earliest_date, index_date)
    before_ed_events = filter_ed_events(earliest_date, index_date)

    #any evidence of HF, not just diagnosis codes, before index date
    hf_exclude_primary = last_matching_event_clinical_snomed(
        before_gp_events, hf_exclude
        ).date

    #same but for secondary care
    hf_exclude_apc = last_matching_event_apc(
        before_apc_events,
        hf_icd10, 
        only_prim_diagnoses=False
        ).admission_date

    hf_exclude_ec = last_matching_event_ec(
        before_ed_events, hf_ecds
        ).arrival_date

    dataset.hf_exclude_date = minimum_of(
        hf_exclude_primary,
        hf_exclude_apc,
        hf_exclude_ec
        )

    return dataset
