'''
Functions for REDUCE-HF heart failure variables
'''

from functions.lib import *

def hf_diagnosis(dataset, index_date, end_date):

    '''
    Purpose
    =======

    Derive variables to define new heart failure diagnosis after ``index_date``

    **Parameters**

        - ``dataset`` : dataset object initialised using ``ehrql.create_dataset()``
        - ``index_date`` : str, the date that a patient enters the cohort (defined in `demog`)
        - `end_date` : str, project / follow-up end date

    **Variables added**

        - ``hf_diagnosis_primary_date`` : date of first HF diagnosis in primary care after index_date
        - ``hf_diagnosis_apc_date`` : date of first hospital admission after index_date where HF was recorded as primary diagnosis
        - ``hf_diagnosis_ec_date`` : date of first ED attendance for HF after index_date
        - ``hf_death_date``: date of death where cause of death is HF
        - ``hf_diagnosis_emerg_date`` : date of emergency HF diagnosis (earliest of ``hf_diagnosis_apc_date``, ``hf_diagnosis_ec_date`` and ``hf_death_date``)
        - ``hf_mi_diagnosis_apc_date`` : date of first hospital admission where HF is secondary diagnosis to primary diagnosis of Myocardial Infarction
        - ``hf_diagnosis_date`` : date of HF diagnosis (earliest of ``hf_diagnosis_primary_date`` and ``hf_diagnosis_emerg_date``)

    **Returns**

        - ``dataset`` : input dataset modified to include variables added

    .. python::

        def hf_diagnosis(dataset, index_date, end_date):

            # Filter raw data to everything after index date
            after_gp_events = filter.gp_events(index_date, end_date)
            after_apc_events = filter.apc_events(index_date, end_date)
            after_ed_events = filter.ed_events(index_date, end_date)

            #primary care
            dataset.hf_diagnosis_primary_date = first.matching_event_snomed(after_gp_events, hf_snomed).date

            #secondary care - hospital admission (primary OR secondary), or A&E visit
            dataset.hf_diagnosis_apc_date = first.matching_event_apc_acute(
                after_apc_events,
                hf_icd10, 
                only_prim_diagnoses=True
                ).admission_date
            
            dataset.hf_diagnosis_ec_date = first.matching_event_ec(
                after_ed_events,
                hf_ecds
                ).arrival_date
            
            #as cause of death
            dataset.hf_death_date = when(ons_deaths.cause_of_death_is_in(hf_icd10))
                .then(ons_deaths.date)
                .otherwise(None)

            #earliest date of "emergency" HF diagnosis
            dataset.hf_diagnosis_emerg_date = minimum_of(
                dataset.hf_diagnosis_apc_date, 
                dataset.hf_diagnosis_ec_date,
                dataset.hf_death_date
                )

            #sensitivity analysis - in same admission as MI
            mi_diagnosis_apc = after_apc_events.where(
                after_apc_events.admission_method.is_in(
                    ["21","2A","22","23","24","25","2D","28","2B"]
                    )
                & after_apc_events.primary_diagnosis.is_in(mi_icd10)
                )
            
            dataset.hf_mi_diagnosis_apc_date = mi_diagnosis_apc.where(
                mi_diagnosis_apc.all_diagnoses.contains_any_of(hf_icd10)
                ).sort_by(mi_diagnosis_apc.admission_date).first_for_patient().admission_date
            
            dataset.hf_diagnosis_date = minimum_of(
                dataset.hf_diagnosis_primary_date,
                dataset.hf_diagnosis_emerg_date
            )
            
            return dataset

    '''

    # Filter raw data to everything after index date
    after_gp_events = filter.gp_events(index_date, end_date)
    after_apc_events = filter.apc_events(index_date, end_date)
    after_ed_events = filter.ed_events(index_date, end_date)

    #primary care
    dataset.hf_diagnosis_primary_date = first.matching_event_snomed(after_gp_events, hf_snomed).date

    #secondary care - hospital admission (primary OR secondary), or A&E visit
    dataset.hf_diagnosis_apc_date = first.matching_event_apc_acute(
        after_apc_events,
        hf_icd10, 
        only_prim_diagnoses=True
        ).admission_date
    
    dataset.hf_diagnosis_ec_date = first.matching_event_ec(
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
    
    dataset.hf_diagnosis_date = minimum_of(
        dataset.hf_diagnosis_primary_date,
        dataset.hf_diagnosis_emerg_date
    )
    
    return datase


def hf_exclude(dataset, earliest_date, index_date):

    '''
    Purpose
    =======
    Derive variables to define pre-existing heart failure 
    (heart failure before ``index_date``)

    **Parameters**

        - ``dataset`` : dataset object initialised using ``ehrql.create_dataset()``
        - `earliest_date` : str, the earliest date to look back in a patient's EHR data
        - ``index_date`` : str, the date that a patient enters the cohort (defined in `demog`)

    **Variables added**

        - ``hf_exclude_primary`` : date of most recent HF diagnosis in primary care prior to index_date
        - ``hf_exclude_apc`` : date of most recent hospital admission prior to index_date where HF was recorded as primary diagnosis
        - ``hf_exclude_ec`` : date of most recent ED attendance for HF prior to index_date
        - ``hf_exclude_date`` : date of HF diagnosis (earliest of ``hf_exclude_primary``, ``hf_exclude_apc`` and ``hf_exclude_ec``)

    **Returns**

        - ``dataset`` : input dataset modified to include variables added

    .. python::

        def hf_exclude(dataset, earliest_date, index_date):

            #filter data - use placeholder start date to get all past events
            before_gp_events = filter.gp_events(earliest_date, index_date)
            before_apc_events = filter.apc_events(earliest_date, index_date)
            before_ed_events = filter.ed_events(earliest_date, index_date)

            #any evidence of HF, not just diagnosis codes, before index date
            hf_exclude_primary = last.matching_event_snomed(
                before_gp_events, hf_exclude_
                ).date

            #same but for secondary care
            hf_exclude_apc = last.matching_event_apc(
                before_apc_events,
                hf_icd10, 
                only_prim_diagnoses=False
                ).admission_date

            hf_exclude_ec = last.matching_event_ec(
                before_ed_events, hf_ecds
                ).arrival_date

            dataset.hf_exclude_date = minimum_of(
                hf_exclude_primary,
                hf_exclude_apc,
                hf_exclude_ec
                )

            return dataset
    '''


    #filter data - use placeholder start date to get all past events
    before_gp_events = filter.gp_events(earliest_date, index_date)
    before_apc_events = filter.apc_events(earliest_date, index_date)
    before_ed_events = filter.ed_events(earliest_date, index_date)

    #any evidence of HF, not just diagnosis codes, before index date
    hf_exclude_primary = last.matching_event_snomed(
        before_gp_events, hf_exclude_
        ).date

    #same but for secondary care
    hf_exclude_apc = last.matching_event_apc(
        before_apc_events,
        hf_icd10, 
        only_prim_diagnoses=False
        ).admission_date

    hf_exclude_ec = last.matching_event_ec(
        before_ed_events, hf_ecds
        ).arrival_date

    dataset.hf_exclude_date = minimum_of(
        hf_exclude_primary,
        hf_exclude_apc,
        hf_exclude_ec
        )

    return dataset
t
