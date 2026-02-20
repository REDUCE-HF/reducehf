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

# filter a codelist based on whether its values included a specified set of allowed values (include)
def filter_codes_by_category(codelist, include):
    '''
    Filter a codelist based on whether its values included a specified set of allowed values (include)
    '''
    return {k:v for k,v in codelist.items() if v in include}
