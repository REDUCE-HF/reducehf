from functions.lib import *
##############
# HF diganosis
##############
def fn(dataset, index_date):

    #primary care
    dataset.hf_diagnosis_primary_date = first_matching_event_clinical_snomed_after(
        hf_snomed, index_date
        ).date

    #secondary care - hospital admission (primary OR secondary), or A&E visit
    dataset.hf_diagnosis_apc_date = first_matching_event_apc_acute_after(
        hf_icd10, index_date, 
        only_prim_diagnoses=True
        ).admission_date
    
    dataset.hf_diagnosis_ec_date = first_matching_event_ec_after(
        hf_ecds, index_date
        ).arrival_date
    
    dataset.hf_diagnosis_secondary_date = minimum_of(
        dataset.hf_diagnosis_apc_date, 
        dataset.hf_diagnosis_ec_date
        )

    #either primary or secondary
    dataset.hf_diagnosis_date = minimum_of(
        dataset.hf_diagnosis_primary_date, 
        dataset.hf_diagnosis_secondary_date
        )

    #in same admission as MI
    mi_diagnosis_apc = apcs.where(
        apcs.admission_date.is_on_or_after(index_date)
        & apcs.admission_method.is_in(["21","2A","22","23","24","25","2D","28","2B"])
        & apcs.primary_diagnosis.is_in(mi_icd10)
        )
    
    dataset.hf_mi_diagnosis_apc_date = mi_diagnosis_apc.where(
        mi_diagnosis_apc.all_diagnoses.contains_any_of(hf_icd10)
        ).sort_by(mi_diagnosis_apc.admission_date).first_for_patient().admission_date

    return dataset
