'''
Functions to extract the most recent event where a code present 
in a codelist is recorded.
'''

### Primary care
## Date of last primary care event
def matching_event_snomed(gp_events, codelist, where=True):

    '''
    Most recent primary care recording of code in codelist

    .. python::

        def matching_event_snomed(gp_events, codelist, where=True):

            return(
                gp_events.where(where)
                .where(gp_events.snomedct_code.is_in(codelist))
                .sort_by(gp_events.date)
                .last_for_patient()
            )
    '''
    return(
        gp_events.where(where)
        .where(gp_events.snomedct_code.is_in(codelist))
        .sort_by(gp_events.date)
        .last_for_patient()
    )

### Hospital
## Date of last hospital event
def matching_event_apc(apc_events, codelist, only_prim_diagnoses=False, where=True):
    '''
    Most recent hospital admission where primary diagnosis is in codelist

    .. python::

        def matching_event_apc(apc_events, codelist, only_prim_diagnoses=False, where=True):

            if only_prim_diagnoses:
                query = apc_events.where(
                    apc_events.primary_diagnosis.is_in(codelist)
                )
            else:
                query = apc_events.where(apc_events.all_diagnoses.contains_any_of(codelist))
            
            return query.sort_by(query.admission_date).last_for_patient()
    '''
    if only_prim_diagnoses:
        query = apc_events.where(
            apc_events.primary_diagnosis.is_in(codelist)
        )
    else:
        query = apc_events.where(apc_events.all_diagnoses.contains_any_of(codelist))
    return query.sort_by(query.admission_date).last_for_patient()


## MEDICATIONS DATA
## Date of last medication prescribing BEFORE index date
def matching_med_dmd(med_events, codelist, where=True):

    '''
    Most recent medication prescribing where medication in codelist

    .. python::

        def matching_med_dmd(med_events, codelist, where=True):

            return(
                med_events.where(where)
                .where(med_events.dmd_code.is_in(codelist))
                .sort_by(med_events.date)
                .last_for_patient()
            )
    '''
    return(
        med_events.where(where)
        .where(med_events.dmd_code.is_in(codelist))
        .sort_by(med_events.date)
        .last_for_patient()
    )

## A&E DATA
## Date of last A&E event BEFORE index date
def matching_event_ec(ed_events, codelist, where=True):
    '''
    Most recent A&E event with primary diagnosis in codelist

    .. python::

        def matching_event_ec(ed_events, codelist, where=True):

            return(
                ed_events.where(where)
                .where(ed_events.diagnosis_01.is_in(codelist))
                .sort_by(ed_events.arrival_date)
                .last_for_patient()
            )
    '''
    return(
        ed_events.where(where)
        .where(ed_events.diagnosis_01.is_in(codelist))
        .sort_by(ed_events.arrival_date)
        .last_for_patient()
    )

## Date of last event in BEFORE index date
def matching_event_ranges_snomed(range_events, codelist, where=True):
    '''
    Most recent primary care recording of code in codelist (ranges table)

    .. python::

        def matching_event_ranges_snomed(range_events, codelist, where=True):

            return(
                range_events.where(where)
                .where(range_events.snomedct_code.is_in(codelist))
                .sort_by(range_events.date)
                .last_for_patient()
            )

    '''
    return(
        range_events.where(where)
        .where(range_events.snomedct_code.is_in(codelist))
        .sort_by(range_events.date)
        .last_for_patient()
    )
