from .lib import *

##########################
# WP2 - exclusion criteria
##########################

def exclusion(dataset, index_date, end_date):

    #date of first incidence of any of the three HF-related symptoms prior to index date
    tmp_breathless_date_primary = first_matching_event_clinical_snomed_before(
        breathless_snomed, index_date
        ).date

    tmp_oedema_date_primary = first_matching_event_clinical_snomed_before(
        oedema_snomed, index_date
        ).date

    tmp_fatigue_date_primary = first_matching_event_clinical_snomed_before(
        fatigue_snomed, index_date
        ).date

    #add indicator which is true if any symptom reported before index date
    dataset.symptom_pre_index = (
        tmp_breathless_date_primary.is_not_null() | 
        tmp_oedema_date_primary.is_not_null() | 
        tmp_fatigue_date_primary.is_not_null()
        )

    #evidence of NTPro test prior to index date
    nt_pre = first_matching_event_clinical_snomed_before(
        NTpro_snomed,index_date
        ).exists_for_patient()

    dataset.nt_pre_index = nt_pre

    #date of first incidence of any of the three HF-related symptoms
    tmp_breathless_date_primary = first_matching_event_clinical_snomed_between(
        breathless_snomed, index_date, end_date,
        ).date

    tmp_oedema_date_primary = first_matching_event_clinical_snomed_between(
        oedema_snomed, index_date, end_date
        ).date

    tmp_fatigue_date_primary = first_matching_event_clinical_snomed_between(
        fatigue_snomed, index_date, end_date
        ).date

    #combine to find the earliest date of any symptom
    dataset.first_hfsymptom_date = minimum_of(
        tmp_breathless_date_primary,
        tmp_oedema_date_primary,
        tmp_fatigue_date_primary
        )

    first_nt = first_matching_event_clinical_snomed_between(
        NTpro_snomed,index_date, end_date
        )
    
    dataset.nt1_date = first_nt.date
    dataset.nt1_result = first_nt.numeric_value

    return dataset

###################
# WP2 -- NP testing
###################

def np_vars(dataset, index_date, end_date):


    # testing if np test date (BNP or NT-proBNP) closely preceded
    # or followed first hf-related symptoms (near symptoms)
    dataset.np_near_symptom = clinical_events.where(
        clinical_events.snomedct_code.is_in(NP_snomed)
        ).where(
            clinical_events.date.is_on_or_between(
                dataset.first_hfsymptom_date-days(30),
                dataset.first_hfsymptom_date+days(90)
            )
        ).exists_for_patient()

    #echo referral or echo done near first hf-related symptoms

    dataset.echo_ref_near_symptom =clinical_events.where(
        clinical_events.snomedct_code.is_in(echo_ref)
        ).where(
            clinical_events.date.is_on_or_between(
                dataset.first_hfsymptom_date-days(30), 
                dataset.first_hfsymptom_date+days(90)
            )
        ).exists_for_patient()

    dataset.echo_done_near_symptom =clinical_events.where(
        clinical_events.snomedct_code.is_in(echo_done)
        ).where(
            clinical_events.date.is_on_or_between(
                dataset.first_hfsymptom_date-days(30),
                dataset.first_hfsymptom_date+days(90)
           )
        ).exists_for_patient()

    dataset.has_echo = (
        dataset.echo_ref_near_symptom|dataset.echo_done_near_symptom
        ).when_null_then(False)

    #First NTProBNP test following index date and using SNOMED codes  

    first_nt = first_matching_event_clinical_ranges_snomed_in(
        NTpro_snomed,index_date, end_date,
        )
    dataset.nt1_date_ranges = first_nt.date
    dataset.nt1_result_ranges = first_nt.numeric_value
    dataset.nt1_comparator = first_nt.comparator
    dataset.nt1_lower_bound = first_nt.lower_bound
    dataset.nt1_upper_bound = first_nt.upper_bound


    return dataset
