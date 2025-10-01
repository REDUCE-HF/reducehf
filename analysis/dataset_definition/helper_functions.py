import operator
from functools import reduce # for function building, e.g. any_of
from ehrql.tables.tpp import (
    apcs, 
    clinical_events,
    clinical_events_ranges, 
    medications, 
    ons_deaths,
    ec,
    emergency_care_attendances as eca
)


def ed_attendances(start_date, end_date, where=True):
    return (
        ec.where(where)
        .where(ec.arrival_date.is_on_or_between(start_date, end_date))
        .ec_ident        
        .count_distinct_for_patient()
    )

def primary_care_attendances(start_date, end_date, where=True):
    return (
        clinical_events.where(where)
        .where(clinical_events.date.is_on_or_between(start_date, end_date))
        .consultation_id
        .count_distinct_for_patient()
    )


def hospital_admissions(start_date, end_date, where=True):
    return (
        apcs.where(where)
        .where(apcs.admission_date.is_on_or_between(start_date, end_date))
        .apcs_ident        
        .count_distinct_for_patient()
    )

def prescriptions_count (start_date, end_date, where= True): 
    return(
<<<<<<< Updated upstream
        medications.where(where)
        .where(medications.date.is_on_or_between(start_date, end_date))
=======
        prescriptions.where(where)
        .where(prescriptions.date.is_on_or_between(start_date, end_date))
>>>>>>> Stashed changes
        .count_for_patient()
    )
## In Primary care From diabetes algo reusable action 

def count_matching_event_clinical_ctv3_before(codelist, index_date, where=True):
    return(
        clinical_events.where(where)
        .where(clinical_events.ctv3_code.is_in(codelist))
        .where(clinical_events.date.is_on_or_before(index_date))
        .count_for_patient()
    )

## In SECONDARY CARE (Hospital Episodes) From diabetes algo reusable action 
def count_matching_event_apc_before(codelist, baseline_date, only_prim_diagnoses=False, where=True):
    query = apcs.where(where).where(apcs.admission_date.is_on_or_before(baseline_date))
    if only_prim_diagnoses:
        # If set to True, then check only primary diagnosis field
        query = query.where(
            apcs.primary_diagnosis.is_in(codelist)
        )
    else:
        # Else, check all diagnoses (default, i.e. when only_prim_diagnoses argument not defined)
        query = query.where(apcs.all_diagnoses.contains_any_of(codelist))
    return query.count_for_patient()

def ever_matching_event_clinical_ctv3_before(codelist, start_date, where=True):
    return(
        clinical_events.where(where)
        .where(clinical_events.ctv3_code.is_in(codelist))
        .where(clinical_events.date.is_before(start_date))
    )

def first_matching_event_clinical_snomed_after(codelist, start_date, where=True):
    return(
        clinical_events.where(where)
        .where(clinical_events.snomedct_code.is_in(codelist))
        .where(clinical_events.date.is_on_or_after(start_date))
        .sort_by(clinical_events.date)
        .first_for_patient()
    )

def first_matching_event_clinical_ctv3_before(codelist, start_date, where=True):
    return(
        clinical_events.where(where)
        .where(clinical_events.ctv3_code.is_in(codelist))
        .where(clinical_events.date.is_before(start_date))
        .sort_by(clinical_events.date)
        .first_for_patient()
    )

def first_matching_event_clinical_snomed_before(codelist, start_date, where=True):
    return(
        clinical_events.where(where)
        .where(clinical_events.snomedct_code.is_in(codelist))
        .where(clinical_events.date.is_before(start_date))
        .sort_by(clinical_events.date)
        .first_for_patient()
    )


def last_matching_event_clinical_ctv3_before(codelist, start_date, where=True):
    return(
        clinical_events.where(where)
        .where(clinical_events.ctv3_code.is_in(codelist))
        .where(clinical_events.date.is_before(start_date))
        .sort_by(clinical_events.date)
        .last_for_patient()
    )

def last_matching_event_clinical_ranges_snomed_before(codelist, start_date, where=True):
    return(
        clinical_events_ranges.where(where)
        .where(clinical_events_ranges.snomedct_code.is_in(codelist))
        .where(clinical_events_ranges.date.is_before(start_date))
        .sort_by(clinical_events_ranges.date)
        .last_for_patient()
    )


def last_matching_med_dmd_before(codelist, start_date, where=True):
    return(
        medications.where(where)
        .where(medications.dmd_code.is_in(codelist))
        .where(medications.date.is_before(start_date))
        .sort_by(medications.date)
        .last_for_patient()
    )

def last_matching_event_apc_before(codelist, start_date, only_prim_diagnoses=False, where=True):
    query = apcs.where(where).where(apcs.admission_date.is_before(start_date))
    if only_prim_diagnoses:
        query = query.where(
            apcs.primary_diagnosis.is_in(codelist)
        )
    else:
        query = query.where(apcs.all_diagnoses.contains_any_of(codelist))
    return query.sort_by(apcs.admission_date).last_for_patient()



def last_matching_event_clinical_snomed_before(codelist, start_date, where=True):
    return(
        clinical_events.where(where)
        .where(clinical_events.snomedct_code.is_in(codelist))
        .where(clinical_events.date.is_before(start_date))
        .sort_by(clinical_events.date)
        .last_for_patient()
    )

def first_matching_med_dmd_before(codelist, start_date, where=True):
    return(
        medications.where(where)
        .where(medications.dmd_code.is_in(codelist))
        .where(medications.date.is_before(start_date))
        .sort_by(medications.date)
        .first_for_patient()
    )
def last_matching_med_dmd_before(codelist, start_date, where=True):
    return(
        medications.where(where)
        .where(medications.dmd_code.is_in(codelist))
        .where(medications.date.is_before(start_date))
        .sort_by(medications.date)
        .last_for_patient()
    )


def last_matching_event_clinical_snomed_between(codelist, start_date, end_date, where=True):
    return(
        clinical_events.where(where)
        .where(clinical_events.snomedct_code.is_in(codelist))
        .where(clinical_events.date.is_on_or_between(start_date, end_date))
        .sort_by(clinical_events.date)
        .last_for_patient()
    )

def last_matching_event_apc_between(codelist, start_date, end_date, where=True):
    query = apcs.where(where)
    query = query.where(apcs.primary_diagnosis.is_in(codelist))
    query = query.where(apcs.admission_date.is_on_or_between(start_date, end_date))
    query = query.sort_by(apcs.admission_date)
    return query.last_for_patient()


def first_matching_event_apc_before(codelist, start_date, only_prim_diagnoses=False, where=True):
    query = apcs.where(where).where(apcs.admission_date.is_on_or_before(start_date))
    if only_prim_diagnoses:
        query = query.where(
            apcs.primary_diagnosis.is_in(codelist)
        )
    else:
        query = query.where(apcs.all_diagnoses.contains_any_of(codelist))

    return query.sort_by(apcs.admission_date).first_for_patient()


def first_matching_event_apc_after(codelist, start_date, only_prim_diagnoses=False, where=True):
    query = apcs.where(where).where(apcs.admission_date.is_on_or_after(start_date))
    if only_prim_diagnoses:
        query = query.where(
            apcs.primary_diagnosis.is_in(codelist)
        )
    else:
        query = query.where(apcs.all_diagnoses.contains_any_of(codelist))

    return query.sort_by(apcs.admission_date).first_for_patient()


def first_matching_event_ec_after(codelist, start_date, where=True):
    return(
        eca.where(where)
        .where(eca.diagnosis_01.is_in(codelist))
        .where(eca.arrival_date.is_on_or_after(start_date))
        .sort_by(eca.arrival_date)
        .first_for_patient()
    )





def first_matching_event_clinical_ranges_snomed_between(codelist, start_date, end_date, where=True):
    return(
        clinical_events_ranges.where(where)
        .where(clinical_events_ranges.snomedct_code.is_in(codelist))
        .where(clinical_events_ranges.date.is_on_or_between(start_date, end_date))
        .sort_by(clinical_events_ranges.date)
        .first_for_patient()
    )

def first_matching_event_clinical_snomed_between(codelist, start_date, end_date, where=True):
    return(
        clinical_events.where(where)
        .where(clinical_events.snomedct_code.is_in(codelist))
        .where(clinical_events.date.is_on_or_between(start_date, end_date))
        .sort_by(clinical_events.date)
        .first_for_patient()
    )


# filter a codelist based on whether its values included a specified set of allowed values (include)
def filter_codes_by_category(codelist, include):
    return {k:v for k,v in codelist.items() if v in include}
