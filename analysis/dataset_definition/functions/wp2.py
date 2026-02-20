from functions.lib import *

def np_vars(dataset, index_date, end_date, objective):

    '''
    Purpose
    =======
    Add NP testing and symptom variables needed for work package 2.

    **Parameters**

        - ``dataset`` : dataset object initialised using ehrql.create_dataset()
        - ``index_date`` : str, the date that a patient enters the cohort (defined in `demog`)
        - `end_date` : str, project / follow-up end date
        - ``objective`` : int, work package 2 objective. Possible values [1,2].

    **Variables added**


    **Returns**

        - ``dataset`` : input dataset modified to include variables added
    '''


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


def wp2_exclude(dataset, earliest_date, index_date, end_date, objective):

    '''
    Purpose
    =======
    Add variables needed for work package 2 exclusion criteria.

    **Parameters**

        - ``dataset`` : dataset object initialised using ehrql.create_dataset()
        - `earliest_date` : str, the earliest date to look back in a patient's EHR data
        - ``index_date`` : str, the date that a patient enters the cohort (defined in `demog`)
        - `end_date` : str, project / follow-up end date
        - ``objective`` : int, work package 2 objective. Possible values [1,2].

    **Variables added**


    **Returns**

        - ``dataset`` : input dataset modified to include variables added
    '''



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

        #date of first incidence of any of the three HF-related symptoms
        tmp_breathless_date_primary = first_matching_event_clinical_snomed(
            after_gp_events,
            breathless_snomed,
            ).date
        dataset.breathless_date = tmp_breathless_date_primary

        tmp_oedema_date_primary = first_matching_event_clinical_snomed(
            after_gp_events,
            oedema_snomed,
            ).date
        dataset.oedema_date = tmp_oedema_date_primary

        tmp_fatigue_date_primary = first_matching_event_clinical_snomed(
            after_gp_events,
            fatigue_snomed,
            ).date
        dataset.fatigue_date = tmp_fatigue_date_primary

        #combine to find the earliest date of any symptom
        dataset.first_hfsymptom_date = minimum_of(
            tmp_breathless_date_primary,
            tmp_oedema_date_primary,
            tmp_fatigue_date_primary
            )

    elif objective==2:

        #evidence of NP test prior to index date
        np_pre = first_matching_event_clinical_snomed(
            before_gp_events,
            NP_snomed,
            ).exists_for_patient()

        dataset.np_pre_index = np_pre

        first_np = first_matching_event_clinical_snomed(
            after_gp_events,
            NP_snomed
            )
        dataset.np_date=first_np.date

        first_nt = first_matching_event_clinical_snomed(
            after_gp_events,
            NTpro_snomed
            )

        dataset.nt1_date = first_nt.date
        dataset.nt1_result = first_nt.numeric_value


    else:

        raise ValueError ('Unknown objective')


    return dataset
                       
