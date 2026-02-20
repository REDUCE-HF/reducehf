# Primary care consultations
def count_primary_care_attendances(gp_events, start_date, end_date, where=True):
    '''
    Number of primary care attendances between start_date and end_date
    '''
    return (
        gp_events.where(where)
        .where(gp_events.date.is_on_or_between(start_date, end_date))
        .consultation_id
        .count_distinct_for_patient()
    )

# A&E attendances
def count_ed_attendances(ed_events, start_date, end_date, where=True):
    '''
    Number of ED attendances between start_date and end_date
    '''
    return (
        ed_events.where(where)
        .where(ed_events.arrival_date.is_on_or_between(start_date, end_date))
        .id
        .count_distinct_for_patient()
    )

# Number of hospital admissions between start and end dates
def count_hospital_admissions(apc_events, start_date, end_date, where=True):
    '''
    Number of hospital admissions between start_date and end_date
    '''
    return (
        apc_events.where(where)
        .where(apc_events.admission_date.is_on_or_between(start_date, end_date))
        .apcs_ident
        .count_distinct_for_patient()
    )

# Number of prescriptions between start and end dates
def count_prescriptions (med_events, start_date, end_date, where= True):
    '''
    Number of prescriptions between start_date and end_date
    '''
    return(
        med_events.where(where)
        .where(med_events.date.is_on_or_between(start_date, end_date))
        .count_for_patient()
    )

## FOR DIABETES ALGO REUSABLE ACTION
## Number of primary care coding events
def count_matching_event_clinical_snomed(gp_events, codelist, where=True):
    '''
    Number of primary care events with recording of code in codelist
    '''
    return(
        gp_events.where(where)
        .where(gp_events.snomedct_code.is_in(codelist))
        .count_for_patient()
    )

## Number of coding events in hospital episodes BEFORE index date
def count_matching_event_apc(apc_events, codelist, only_prim_diagnoses=False, where=True):
    '''
    Number of hospital admissions for diagnosis in codelist.

    If only_prim_diagnosis = True, will count admissions where
    primary diagnosis was in codelist.
    '''
    if only_prim_diagnoses:
        # If set to True, then check only primary diagnosis field
        query = apc_events.where(
            apc_events.primary_diagnosis.is_in(codelist)
        )
    else:
        # Else, check all diagnoses (default, i.e. when only_prim_diagnoses argument not defined)
        query = apc_events.where(apc_events.all_diagnoses.contains_any_of(codelist))
    return query.count_for_patient()
