from functions.lib import *

##########################
# WP2 - exclusion criteria
##########################

def fn(dataset, earliest_date, index_date, end_date, objective):

    before_gp_events = filter_gp_events(earliest_date, index_date)
    after_gp_events = filter_gp_events(index_date, end_date)
    
    if objective == 1:

        #date of first incidence of any of the three HF-related symptoms prior to index date
        tmp_breathless_date_primary = first_matching_event_clinical_snomed(
            before_gp_events,
            breathless_snomed
            ).date

        tmp_oedema_date_primary = first_matching_event_clinical_snomed(
            before_gp_events,
            oedema_snomed
            ).date

        tmp_fatigue_date_primary = first_matching_event_clinical_snomed(
            before_gp_events,
            fatigue_snomed
            ).date

        #add indicator which is true if any symptom reported before index date
        dataset.symptom_pre_index = (
            tmp_breathless_date_primary.is_not_null() |
            tmp_oedema_date_primary.is_not_null() |
            tmp_fatigue_date_primary.is_not_null()
            )

        #evidence of NTPro test prior to index date
        nt_pre = first_matching_event_clinical_snomed(
            before_gp_events,
            NTpro_snomed
            ).exists_for_patient()

        dataset.nt_pre_index = nt_pre

        #date of first incidence of any of the three HF-related symptoms
        tmp_breathless_date_primary = first_matching_event_clinical_snomed(
            after_gp_events,
            breathless_snomed, 
            ).date

        tmp_oedema_date_primary = first_matching_event_clinical_snomed(
            after_gp_events,
            oedema_snomed, 
            ).date

        tmp_fatigue_date_primary = first_matching_event_clinical_snomed(
            after_gp_events,
            fatigue_snomed, 
            ).date

        #combine to find the earliest date of any symptom
        dataset.first_hfsymptom_date = minimum_of(
            tmp_breathless_date_primary,
            tmp_oedema_date_primary,
            tmp_fatigue_date_primary
            )

    elif objective==2:

        #evidence of NTPro test prior to index date
        nt_pre = first_matching_event_clinical_snomed(
            before_gp_events,
            NTpro_snomed,
            ).exists_for_patient()

        dataset.nt_pre_index = nt_pre

        first_nt = first_matching_event_clinical_snomed(
            after_gp_events,
            NTpro_snomed
            )

        dataset.nt1_date = first_nt.date
        dataset.nt1_result = first_nt.numeric_value


    else:

        raise ValueError ('Unknown objective')


    return dataset
