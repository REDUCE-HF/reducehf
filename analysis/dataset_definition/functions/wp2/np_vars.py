from functions.lib import *

###################
# WP2 -- NP testing
###################

def fn(dataset, index_date, end_date, objective):

    if objective==1:

        #Subset data once to use in downstream cod (more efficient)
        gp_events = filter_gp_events(
            dataset.first_hfsymptom_date-days(31),
            dataset.first_hfsymptom_date+days(93)
            )
    
        # testing if np test date (BNP or NT-proBNP) closely preceded
        # or followed first hf-related symptoms (near symptoms)
        np_near_symptom_ = first_matching_event_clinical_snomed(
            gp_events,
            NP_snomed
            )
        dataset.np_near_symptom = np_near_symptom_.exists_for_patient()
        dataset.np_near_symptom_first = np_near_symptom_.date

        #echo referral or echo done near first hf-related symptoms
        dataset.echo_ref_near_symptom = gp_events.where(
            gp_events.snomedct_code.is_in(echo_ref)
            ).exists_for_patient()

        dataset.echo_done_near_symptom = gp_events.where(
            gp_events.snomedct_code.is_in(echo_done)
            ).exists_for_patient()

        dataset.has_echo = (
            dataset.echo_ref_near_symptom|dataset.echo_done_near_symptom
            ).when_null_then(False)


    elif objective==2:

        #Subset data once to use in downstream cod (more efficient)
        after_range_events = filter_range_events(index_date, end_date)
        
        #First NTProBNP test following index date and using SNOMED codes
        first_nt = first_matching_event_clinical_ranges_snomed(
            after_range_events, 
            NTpro_snomed)

        dataset.nt1_date_ranges = first_nt.date
        dataset.nt1_result_ranges = first_nt.numeric_value
        dataset.nt1_comparator = first_nt.comparator
        dataset.nt1_lower_bound = first_nt.lower_bound
        dataset.nt1_upper_bound = first_nt.upper_bound


    return dataset
