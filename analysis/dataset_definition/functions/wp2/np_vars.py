from functions.lib import *

###################
# WP2 -- NP testing
###################

def fn(dataset, index_date, end_date, objective):


    if objective==1:
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


    elif objective==2:

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
