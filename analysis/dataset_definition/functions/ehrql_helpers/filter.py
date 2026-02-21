'''
Functions to filter OpenSAFELY tables and extract all events within a date range.

This can help efficiency.
'''

import operator
from ehrql.tables.tpp import (
    medications,
    clinical_events,
    clinical_events_ranges,
    apcs,
    emergency_care_attendances as eca
    )


### Data filtering (for efficiency)
def gp_events(start_date, end_date):

    '''
    Filter the clinical_events table (``ehrql.tables.tpp.clinical_events``) to extract all events 
    between ``start_date`` and ``end_date``.

    .. python::
        def gp_events(start_date, end_date):

            return clinical_events.where(clinical_events.date.is_on_or_between(start_date, end_date))

    '''
    return clinical_events.where(clinical_events.date.is_on_or_between(start_date, end_date))

def med_events(start_date, end_date):

    '''
    Filter the medications table (``ehrql.tables.tpp.medications``) to extract all events 
    between ``start_date`` and ``end_date``.

    .. python::
        def med_events(start_date, end_date):

            return medications.where(medications.date.is_on_or_between(start_date, end_date))
            
    '''
    return medications.where(medications.date.is_on_or_between(start_date, end_date))

def apc_events(start_date, end_date):

    '''
    Filter the apcs table (``ehrql.tables.tpp.apcs``) to extract all events 
    between ``start_date`` and ``end_date``.

    .. python::
        def apc_events(start_date, end_date):

            return apcs.where(admission_date.is_on_or_between(start_date, end_date))
            
    '''
    return apcs.where(apcs.admission_date.is_on_or_between(start_date, end_date))

def ed_events(start_date, end_date):

    '''
    Filter the eca table (``ehrql.tables.tpp.eca``) to extract all events 
    between ``start_date`` and ``end_date``.

    .. python::
        def ed_events(start_date, end_date):

            return eca.where(arrival_date.is_on_or_between(start_date, end_date))
            
    '''
    return eca.where(eca.arrival_date.is_on_or_between(start_date, end_date))

def range_events(start_date, end_date):

    '''
    Filter the clinical events ranges table (``ehrql.tables.tpp.clinical_events_ranges``) 
    to extract all events between ``start_date`` and ``end_date``.

    .. python::
        def range_events(start_date, end_date):

            return clinical_events_ranges.where(clinical_events_ranges.date.is_on_or_between(start_date, end_date))
            
    '''

    return clinical_events_ranges.where(clinical_events_ranges.date.is_on_or_between(start_date, end_date))

# filter a codelist based on whether its values included a specified set of allowed values (include)
def codes_by_category(codelist, include):
    '''
    Filter a codelist based on whether its values included a specified set of allowed values (include)
    
    .. python::

        def codes_by_category(codelist, include):

            return {k:v for k,v in codelist.items() if v in include}

    '''
    return {k:v for k,v in codelist.items() if v in include}
