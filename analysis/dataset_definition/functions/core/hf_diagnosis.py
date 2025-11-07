################
# HF diagnosis
################

from functions.lib import *

def fn(dataset, index_date, end_date):

    # Filter raw data to everything after index date
    after_gp_events = filter_gp_events(index_date, end_date)
    after_apc_events = filter_apc_events(index_date, end_date)
    after_ed_events = filter_ed_events(index_date, end_date)

    #primary care
    dataset.hf_diagnosis_primary_date = first_matching_event_clinical_snomed(after_gp_events, hf_snomed).date

    #secondary care - hospital admission (primary OR secondary), or A&E visit
    dataset.hf_diagnosis_apc_date = first_matching_event_apc_acute(
        after_apc_events,
        hf_icd10, 
        only_prim_diagnoses=True
        ).admission_date
    
    dataset.hf_diagnosis_ec_date = first_matching_event_ec(
        after_ed_events,
        hf_ecds
        ).arrival_date
    
    #as cause of death
    dataset.hf_death_date = when(ons_deaths.cause_of_death_is_in(hf_icd10)).then(ons_deaths.date).otherwise(None)

    #earliest date of "emergency" HF diagnosis
    dataset.hf_diagnosis_emerg_date = minimum_of(
        dataset.hf_diagnosis_apc_date, 
        dataset.hf_diagnosis_ec_date,
        dataset.hf_death_date
        )

    #sensitivity analysis - in same admission as MI
    mi_diagnosis_apc = after_apc_events.where(
        after_apc_events.admission_method.is_in(["21","2A","22","23","24","25","2D","28","2B"])
        & after_apc_events.primary_diagnosis.is_in(mi_icd10)
        )
    
    dataset.hf_mi_diagnosis_apc_date = mi_diagnosis_apc.where(
        mi_diagnosis_apc.all_diagnoses.contains_any_of(hf_icd10)
        ).sort_by(mi_diagnosis_apc.admission_date).first_for_patient().admission_date
    
    return dataset
