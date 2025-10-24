from functions.lib import *

##########################
# WP2 - exclusion criteria
##########################

def fn(dataset, index_date, end_date, objective):

    if objective == 1:

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


    elif objective==2:

        #evidence of NTPro test prior to index date
        nt_pre = first_matching_event_clinical_snomed_before(
            NTpro_snomed,index_date
            ).exists_for_patient()

        dataset.nt_pre_index = nt_pre

        first_nt = first_matching_event_clinical_snomed_between(
            NTpro_snomed,index_date, end_date
            )

        dataset.nt1_date = first_nt.date
        dataset.nt1_result = first_nt.numeric_value


    else:

        raise ValueError ('Unknown objective')


    return dataset
