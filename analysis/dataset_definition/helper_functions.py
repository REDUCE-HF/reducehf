import operator
from functools import reduce # for function building, e.g. any_of
from ehrql.tables.tpp import (
    apcs, 
    clinical_events, 
    medications, 
    ons_deaths,
    emergency_care_attendances as eca
)


def ed_attendances(start_date, end_date, where=True):
    return (
        eca.where(where)
        .where(eca.arrival_date.is_on_or_between(start_date, end_date))
        .count_for_patient()
    )


def primary_care_attendances(start_date, end_date, where=True):
    return (
        clinical_events.where(where)
        .where(clinical_events.date.is_on_or_between(start_date, end_date))
        .count_for_patient()
    )


def hospital_admissions(start_date, end_date, where=True):
    return (
        apcs.where(where)
        .where(apcs.admission_date.is_on_or_between(start_date, end_date))
        .count_for_patient()
    )

def ever_matching_event_clinical_ctv3_before(codelist, start_date, where=True):
    return(
        clinical_events.where(where)
        .where(clinical_events.ctv3_code.is_in(codelist))
        .where(clinical_events.date.is_before(start_date))
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

def last_matching_event_clinical_snomed_before(codelist, start_date, where=True):
    return(
        clinical_events.where(where)
        .where(clinical_events.snomedct_code.is_in(codelist))
        .where(clinical_events.date.is_before(start_date))
        .sort_by(clinical_events.date)
        .last_for_patient()
    )

# filter a codelist based on whether its values included a specified set of allowed values (include)
def filter_codes_by_category(codelist, include):
    return {k:v for k,v in codelist.items() if v in include}
