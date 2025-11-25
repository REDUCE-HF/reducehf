import operator
from ehrql.tables.tpp import (
    medications,
    clinical_events,
    clinical_events_ranges,
    apcs,
    emergency_care_attendances as eca
    )
from functools import reduce # for function building, e.g. any_of

### Data filtering (for efficiency)
def filter_gp_events(start_date, end_date):
    return clinical_events.where(clinical_events.date.is_on_or_between(start_date, end_date))

def filter_med_events(start_date, end_date):
    return medications.where(medications.date.is_on_or_between(start_date, end_date))

def filter_apc_events(start_date, end_date):
    return apcs.where(apcs.admission_date.is_on_or_between(start_date, end_date))

def filter_ed_events(start_date, end_date):
    return eca.where(eca.arrival_date.is_on_or_between(start_date, end_date))

def filter_range_events(start_date, end_date):
    return clinical_events_ranges.where(clinical_events_ranges.date.is_on_or_between(start_date, end_date))


### Health service utilisation
# Primary care consultations 
def primary_care_attendances(gp_events, start_date, end_date, where=True):
    '''
    Note - need to define date range for gp_events table using filter_gp_events(start_date, end_date) 
    '''
    return (
        gp_events.where(where)
        .where(gp_events.date.is_on_or_between(start_date, end_date))
        .consultation_id
        .count_distinct_for_patient()
    )

# A&E attendances
def ed_attendances(ed_events, start_date, end_date, where=True):
    '''
    Note - need to define date range for ed_events table using filter_ed_events(start_date, end_date) 
    '''
    return (
        ed_events.where(where)
        .where(ed_events.arrival_date.is_on_or_between(start_date, end_date))
        .id       
        .count_distinct_for_patient()
    )

# Number of hospital admissions between start and end dates
def hospital_admissions(apc_events, start_date, end_date, where=True):
    '''
    Note - need to define apc_events table using filter_apc_events(start_date, end_date)
    '''
    return (
        apc_events.where(where)
        .where(apc_events.admission_date.is_on_or_between(start_date, end_date))
        .apcs_ident        
        .count_distinct_for_patient()
    )

# Number of prescriptions between start and end dates
def prescriptions_count (med_events, start_date, end_date, where= True): 
    '''
    Note - need to define date range for med_events table using filter_med_events(start_date, end_date) 
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
    Note - need to define date range for gp_events table using filter_gp_events(start_date, end_date) 
    '''
    return(
        gp_events.where(where)
        .where(gp_events.snomedct_code.is_in(codelist))
        .count_for_patient()
    )

## Number of coding events in hospital episodes BEFORE index date 
def count_matching_event_apc(apc_events, codelist, only_prim_diagnoses=False, where=True):
    '''
    Note - need to define date range for apc_events table using filter_apc_events(start_date, end_date) 
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


### PRIMARY CARE 
## Date of first primary care event 
def first_matching_event_clinical_snomed(gp_events, codelist, where=True):
    '''
    Note - need to define date range for gp_events table using filter_gp_events(start_date, end_date) 
    '''
    return(
        gp_events.where(where)
        .where(gp_events.snomedct_code.is_in(codelist))
        .sort_by(gp_events.date)
        .first_for_patient()
    )

## Date of last primary care event 
def last_matching_event_clinical_snomed(gp_events, codelist, where=True):
    '''
    Note - need to define date range for gp_events table using filter_gp_events(start_date, end_date) 
    '''
    return(
        gp_events.where(where)
        .where(gp_events.snomedct_code.is_in(codelist))
        .sort_by(gp_events.date)
        .last_for_patient()
    )

## HOSPITAL EPISODES
## Date of first hospital event AFTER index date
def first_matching_event_apc(apc_events, codelist, only_prim_diagnoses=False, where=True):
    '''
    Note - need to define date range for apc_events table using filter_apc_events(start_date, end_date) 
    '''
    if only_prim_diagnoses:
        query = apc_events.where(
            apc_events.primary_diagnosis.is_in(codelist)
        )
    else:
        query = apc_events.where(apc_events.all_diagnoses.contains_any_of(codelist))

    return query.sort_by(query.admission_date).first_for_patient()

## Date of last hospital event 
def last_matching_event_apc(apc_events, codelist, only_prim_diagnoses=False, where=True):
    '''
    Note - need to define date range for apc_events table using filter_apc_events(start_date, end_date) 
    '''
    if only_prim_diagnoses:
        query = apc_events.where(
            apc_events.primary_diagnosis.is_in(codelist)
        )
    else:
        query = apc_events.where(apc_events.all_diagnoses.contains_any_of(codelist))
    return query.sort_by(query.admission_date).last_for_patient()

## Date of first acute hospital event AFTER index date
def first_matching_event_apc_acute(apc_events, codelist, only_prim_diagnoses=False, where=True):
    '''
    Note - need to define date range for apc_events table using filter_apc_events(start_date, end_date) 
    '''
    query = apc_events.where(where).where(
        #emergency admissions only (excludes elective care: https://docs.opensafely.org/data-sources/apc/)
        apc_events.admission_method.is_in(["21","2A","22","23","24","25","2D","28","2B"])
        )
    if only_prim_diagnoses:
        query = query.where(
            query.primary_diagnosis.is_in(codelist)
        )
    else:
        query = query.where(
            query.all_diagnoses.contains_any_of(codelist))

    return query.sort_by(query.admission_date).first_for_patient()

## RANGES DATA (contains comparators)
## Date of last event in BEFORE index date
def last_matching_event_clinical_ranges_snomed(range_events, codelist, where=True):
    '''
    Note - need to define date range for range_events table using filter_range_events(start_date, end_date) 
    '''
    return(
        range_events.where(where)
        .where(range_events.snomedct_code.is_in(codelist))
        .sort_by(range_events.date)
        .last_for_patient()
    )

## Date of first event in specified date range
def first_matching_event_clinical_ranges_snomed(range_events, codelist, where=True):
    '''
    Note - need to define date range for range_events table using filter_range_events(start_date, end_date) 
    '''
    return(
        range_events.where(where)
        .where(range_events.snomedct_code.is_in(codelist))
        .sort_by(range_events.date)
        .first_for_patient()
    )

## MEDICATIONS DATA
## Date of last medication prescribing BEFORE index date
def last_matching_med_dmd(med_events, codelist, where=True):
    '''
    Note - need to define date range for med_events table using filter_med_events(start_date, end_date) 
    '''
    return(
        med_events.where(where)
        .where(med_events.dmd_code.is_in(codelist))
        .sort_by(med_events.date)
        .last_for_patient()
    )
    
## Date of first medication prescribing AFTER index date
def first_matching_med_dmd(med_events, codelist, where=True):
    '''
    Note - need to define date range for med_events table using filter_med_events(start_date, end_date) 
    '''
    return(
        med_events.where(where)
        .where(med_events.dmd_code.is_in(codelist))
        .sort_by(med_events.date)
        .first_for_patient()
    )

## A&E DATA
## Date of last A&E event BEFORE index date
def last_matching_event_ec(ed_events, codelist, where=True):
    '''
    Note - need to define date range for ed_events table using filter_ed_events(start_date, end_date) 
    '''
    return(
        ed_events.where(where)
        .where(ed_events.diagnosis_01.is_in(codelist))
        .sort_by(ed_events.arrival_date)
        .last_for_patient()
    )

## Date of first A&E event AFTER index date
def first_matching_event_ec(ed_events, codelist, where=True):
    '''
    Note - need to define date range for ed_events table using filter_ed_events(start_date, end_date) 
    '''
    return(
        ed_events.where(where)
        .where(ed_events.diagnosis_01.is_in(codelist))
        .sort_by(ed_events.arrival_date)
        .first_for_patient()
    )

## OTHER
# filter a codelist based on whether its values included a specified set of allowed values (include)
def filter_codes_by_category(codelist, include):
    return {k:v for k,v in codelist.items() if v in include}
