## Date of last event in BEFORE index date
def last_matching_event_clinical_ranges_snomed(range_events, codelist, where=True):
    '''
    Most recent primary care recording of code in codelist (ranges table)
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
    First primary care recording of code in codelist (ranges table)
    '''
    return(
        range_events.where(where)
        .where(range_events.snomedct_code.is_in(codelist))
        .sort_by(range_events.date)
        .first_for_patient()
    )
