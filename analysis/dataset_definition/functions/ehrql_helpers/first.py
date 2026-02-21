'''
Functions to extract the first event where a code 
present in a codelist is recorded.
'''

### PRIMARY CARE
## Date of first primary care event
def matching_event_snomed(gp_events, codelist, where=True):
    '''
    First primary care recording of code in codelist
    .. python::

        def matching_event_snomed(gp_events, codelist, where=True):

            return(
                gp_events.where(where)
                .where(gp_events.snomedct_code.is_in(codelist))
                .sort_by(gp_events.date)
                .first_for_patient()
            )
    '''
    return(
        gp_events.where(where)
        .where(gp_events.snomedct_code.is_in(codelist))
        .sort_by(gp_events.date)
        .first_for_patient()
    )

## HOSPITAL EPISODES
## Date of first hospital event AFTER index date
def matching_event_apc(apc_events, codelist, only_prim_diagnoses=False, where=True):
    '''
    First hospital admission for diagnosis in codelist.

    If only_prim_diagnosis = True, will return the first admission where
    primary diagnosis was in codelist.

    .. python::

        def matching_event_apc(apc_events, codelist, only_prim_diagnoses=False, where=True):

            if only_prim_diagnoses:
                query = apc_events.where(
                    apc_events.primary_diagnosis.is_in(codelist)
                )
            else:
                query = apc_events.where(apc_events.all_diagnoses.contains_any_of(codelist))

            return query.sort_by(query.admission_date).first_for_patient()

    '''
    if only_prim_diagnoses:
        query = apc_events.where(
            apc_events.primary_diagnosis.is_in(codelist)
        )
    else:
        query = apc_events.where(apc_events.all_diagnoses.contains_any_of(codelist))

    return query.sort_by(query.admission_date).first_for_patient()

## Date of first acute hospital event AFTER index date
def matching_event_apc_acute(apc_events, codelist, only_prim_diagnoses=False, where=True):
    
    '''
    First acute hospital admission where primary diagnosis is in codelist

    .. python::

        def matching_event_apc_acute(apc_events, codelist, only_prim_diagnoses=False, where=True):

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

## Date of first medication prescribing AFTER index date
def matching_med_dmd(med_events, codelist, where=True):

    '''
    First medication prescribing where medication in codelist

    .. python::

        def matching_med_dmd(med_events, codelist, where=True):

            return(
                med_events.where(where)
                .where(med_events.dmd_code.is_in(codelist))
                .sort_by(med_events.date)
                .first_for_patient()
            )
    '''
    return(
        med_events.where(where)
        .where(med_events.dmd_code.is_in(codelist))
        .sort_by(med_events.date)
        .first_for_patient()
    )

## Date of first A&E event AFTER index date
def matching_event_ec(ed_events, codelist, where=True):
    '''
    First A&E event with primary diagnosis in codelist

    .. python::

        def matching_event_ec(ed_events, codelist, where=True):

            return(
                ed_events.where(where)
                .where(ed_events.diagnosis_01.is_in(codelist))
                .sort_by(ed_events.arrival_date)
                .first_for_patient()
            )
    '''
    return(
        ed_events.where(where)
        .where(ed_events.diagnosis_01.is_in(codelist))
        .sort_by(ed_events.arrival_date)
        .first_for_patient()
    )

## Date of first event in specified date range
def matching_event_ranges_snomed(range_events, codelist, where=True):
    '''
    First primary care recording of code in codelist (ranges table)

    .. python::

        def matching_event_ranges_snomed(range_events, codelist, where=True):

            return(
                range_events.where(where)
                .where(range_events.snomedct_code.is_in(codelist))
                .sort_by(range_events.date)
                .first_for_patient()
            )
    '''
    return(
        range_events.where(where)
        .where(range_events.snomedct_code.is_in(codelist))
        .sort_by(range_events.date)
        .first_for_patient()
    )
