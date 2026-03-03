'''
Functions for REDUCE-HF work package 3
'''

from functions.lib import *

####################
# Health Service Use
####################

def hsu(dataset, earliest_date, index_date):

    '''
    Purpose
    =======
    Add variables measuring health service use.

    **Parameters**

        - ``dataset`` : dataset object initialised using ehrql.create_dataset()
        - `earliest_date` : str, the earliest date to look back in a patient's EHR data
        - ``index_date`` : str, the date that a patient enters the cohort (defined in `demog`)

    **Codelists**

        - `copd_exacerbations_snomed`
        - `copd_exacerbations_icd10`
        - `copd_medications`

    **Variables added**

    *COPD specific*

        - ``copd_ed_attendances_pre_*`` : Number of ED attendances with primary diagnosis of COPD exacerbation in time period before HF diagnosis
        - ``copd_ed_attendances_post_*`` : Number of ED attendances with primary diagnosis of COPD exacerbation in time period after HF diagnosis
        
        - ``copd_primary_care_attendances_pre_*`` : Number of primary care attendances with primary diagnosis of COPD exacerbation in time period before HF diagnosis
        - ``copd_primary_care_attendances_post_*`` : Number of primary care attendances with primary diagnosis of COPD exacerbation in time period after HF diagnosis

        - ``copd_hospital_admissions_pre_*`` : Number of inpatient admissions with primary diagnosis of COPD exacerbation in time period before HF diagnosis
        - ``copd_hospital_admissions_post_*`` : Number of inpatient admissions with primary diagnosis of COPD exacerbation in time period after HF diagnosis

        - ``copd_prescriptions_pre_*`` : Number of prescriptions for COPD medications in time period before HF diagnosis
        - ``copd_prescriptions_post_*`` : Number of prescriptions for COPD medications in time period after HF diagnosis

    *General*

        - ``ed_attendances_pre_*`` : Number of ED attendances in time period before HF diagnosis
        - ``ed_attendances_post_*`` : Number of ED attendancesin time period after HF diagnosis
        
        - ``primary_care_attendances_pre_*`` : Number of primary care attendances in time period before HF diagnosis
        - ``primary_care_attendances_post_*`` : Number of primary care attendances in time period after HF diagnosis

        - ``hospital_admissions_pre_*`` : Number of inpatient admissions in time period before HF diagnosis
        - ``hospital_admissions_post_*`` : Number of inpatient admissions in time period after HF diagnosis

        - ``prescriptions_pre_*`` : Number of prescriptions in time period before HF diagnosis
        - ``prescriptions_post_*`` : Number of prescriptions in time period after HF diagnosis

   
    *Annual reviews*

        - ``asthma_review_date`` : date of most recent asthma review prior to HF diagnosis
        - ``copd_review_date`` : date of most recent COPD review prior to HF diagnosis
        - ``med_review_date`` : date of most recent medication review prior to HF diagnosis

    **Returns**

        - ``dataset`` : input dataset modified to include variables added

    .. python::

        def hsu(dataset, earliest_date, index_date):

            # Filter datasets for better efficiency
            before_gp_events = filter_gp_events(earliest_date, index_date)

            time = years(2)

            ed_events_1 = filter_ed_events(index_date, index_date + time)
            apc_events_1 = filter_apc_events(index_date, index_date + time)
            gp_events_1 = filter_gp_events(index_date, index_date + time)
            med_events_1 = filter_med_events(index_date, index_date + time)

            ed_events_2 = filter_ed_events(index_date - time, index_date)
            apc_events_2 = filter_apc_events(index_date - time, index_date)
            gp_events_2 = filter_gp_events(index_date - time, index_date)
            med_events_2 = filter_med_events(index_date - time, index_date)

            ## Objective  3.1
            time_periods = {
                '3m': days(90),
                '6m': days(180),
                '12m': days(360),
                '24m': years(2)
            }

            for time_name, time in time_periods.items():

                #use in time period after index_date - COPD specific
                dataset.add_column('copd_ed_attendances_post_'+time_name,
                    count_ed_attendances(
                        ed_events_1, index_date, index_date + time,
                        where=eca.diagnosis_01.is_in(copd_exacerbations_snomed)
                        )
                    )
                dataset.add_column('copd_primary_care_attendances_post_'+time_name,
                    count_primary_care_attendances(
                        gp_events_1, index_date, index_date + time,
                        where=clinical_events.snomedct_code.is_in(copd_exacerbations_snomed)
                        )
                    )
                dataset.add_column('copd_hospital_admissions_post_'+time_name,
                    count_hospital_admissions(
                        apc_events_1, index_date, index_date + time,
                        where=apcs.primary_diagnosis.is_in(copd_exacerbations_icd10)
                        )
                    )
                dataset.add_column('copd_prescriptions_post_' + time_name,
                    count_prescriptions(
                        med_events_1, index_date, index_date + time,
                        where=medications.dmd_code.is_in(copd_medications)
                        )
                    )

                #use in time period after index_date - general
                dataset.add_column('ed_attendances_post_'+time_name, 
                    count_ed_attendances(
                        ed_events_1, index_date, index_date + time
                        )
                    )
                dataset.add_column('primary_care_attendances_post_'+time_name, 
                    count_primary_care_attendances(
                        gp_events_1, index_date, index_date + time
                        )
                    )
                dataset.add_column('hospital_admissions_post_'+time_name, 
                    count_hospital_admissions(
                        apc_events_1, index_date, index_date + time
                        )
                    )

                #use in time period before index_date - general
                dataset.add_column('ed_attendances_pre_'+time_name, 
                    count_ed_attendances(
                        ed_events_2, index_date - time, index_date
                        )
                    )
                dataset.add_column('primary_care_attendances_pre_'+time_name, 
                    count_primary_care_attendances(
                        gp_events_2, index_date - time, index_date
                        )
                    )
                dataset.add_column('hospital_admissions_pre_'+time_name, 
                    count_hospital_admissions(
                        apc_events_2, index_date - time, index_date
                        )
                    )

                #use in time period before index_date - COPD specific
                dataset.add_column('copd_ed_attendances_pre_'+time_name,
                    count_ed_attendances(
                        ed_events_2, index_date - time, index_date,
                        where=eca.diagnosis_01.is_in(copd_exacerbations_snomed)
                        )
                    )
                dataset.add_column('copd_primary_care_attendances_pre_'+time_name,
                    count_primary_care_attendances(
                        gp_events_2, index_date - time, index_date,
                        where=clinical_events.snomedct_code.is_in(copd_exacerbations_snomed)
                        )
                    )
                dataset.add_column('copd_hospital_admissions_pre_'+time_name,
                    count_hospital_admissions(
                        apc_events_2, index_date - time, index_date,
                        where=apcs.primary_diagnosis.is_in(copd_exacerbations_icd10)
                        )
                    )
                dataset.add_column('copd_prescriptions_pre' + time_name,
                    count_prescriptions(
                        med_events_2, index_date - time, index_date,
                        where=medications.dmd_code.is_in(copd_medications)
                        )
                    )
                
            ## Objective 3.2
            periods = {
                "post_0_3m": (index_date, index_date + days(90)),
                "post_3_6m": (index_date + days(90), index_date + days(180)),
                "post_6_9m": (index_date + days(180), index_date + days(270)),
                "post_9_12m": (index_date + days(270), index_date + days(360)),
                "pre_0_3m": (index_date - days(90), index_date),
                "pre_3_6m": (index_date - days(180), index_date - days(90)),
                "pre_6_9m": (index_date - days(270), index_date - days(180)),
                "pre_9_12m": (index_date - days(360), index_date - days(270)),
            }
        

            for time_name, (start,end) in periods.items():

                if time_name.split('_')[0] == 'post':
                    #use in time period after index_date
                    dataset.add_column('ed_attendances_'+time_name, 
                        count_ed_attendances(ed_events_2, start, end)
                        )
                    dataset.add_column('primary_care_attendances_'+time_name, 
                        count_primary_care_attendances(gp_events_2, start,end)
                        )
                    dataset.add_column('hospital_admissions_'+time_name,
                        count_hospital_admissions(apc_events_2, start,end)
                        )
                    dataset.add_column('prescriptions_' + time_name, 
                        count_prescriptions(med_events_2, start, end)
                        )
                    
                else:
                    #use in time period before index date
                    dataset.add_column('ed_attendances_'+time_name, 
                        count_ed_attendances(ed_events_1, start, end)
                        )
                    dataset.add_column('primary_care_attendances_'+time_name, 
                        count_primary_care_attendances(gp_events_1, start,end)
                        )
                    dataset.add_column('hospital_admissions_'+time_name,
                        count_hospital_admissions(apc_events_1, start,end)
                        )
                    dataset.add_column('prescriptions_' + time_name, 
                        count_prescriptions(med_events_1, start, end)
                        )
                    
            ## annual reviews
            # Asthma
            asthma_review_ = last_matching_event_clinical_snomed(
                before_gp_events,
                review_asthma
                )
            dataset.asthma_review_date = asthma_review_.date
            
            # COPD
            copd_review_ = last_matching_event_clinical_snomed(
                before_gp_events,
                review_copd
                )
            dataset.copd_review_date = copd_review_.date

            # Medications (any)
            med_review_ = last_matching_event_clinical_snomed(
                before_gp_events,
                review_med
                )
            dataset.med_review_date = med_review_.date


            return dataset

    '''


    # Filter datasets for better efficiency
    before_gp_events = filter.gp_events(earliest_date, index_date)

    time = years(2)

    ed_events_1 = filter.ed_events(index_date, index_date + time)
    apc_events_1 = filter.apc_events(index_date, index_date + time)
    gp_events_1 = filter.gp_events(index_date, index_date + time)
    med_events_1 = filter.med_events(index_date, index_date + time)

    ed_events_2 = filter.ed_events(index_date - time, index_date)
    apc_events_2 = filter.apc_events(index_date - time, index_date)
    gp_events_2 = filter.gp_events(index_date - time, index_date)
    med_events_2 = filter.med_events(index_date - time, index_date)

    ## Objective  3.1
    time_periods = {
        '3m': days(90),
        '6m': days(180),
        '12m': days(360),
        '24m': years(2)
    }

    for time_name, time in time_periods.items():

        #use in time period after index_date - COPD specific
        dataset.add_column('copd_ed_attendances_post_'+time_name,
            count.ed_attendances(
                ed_events_1, index_date, index_date + time,
                where=eca.diagnosis_01.is_in(copd_exacerbations_snomed)
                )
            )
        dataset.add_column('copd_primary_care_attendances_post_'+time_name,
            count.primary_care_attendances(
                gp_events_1, index_date, index_date + time,
                where=clinical_events.snomedct_code.is_in(copd_exacerbations_snomed)
                )
            )
        dataset.add_column('copd_hospital_admissions_post_'+time_name,
            count.hospital_admissions(
                apc_events_1, index_date, index_date + time,
                where=apcs.primary_diagnosis.is_in(copd_exacerbations_icd10)
                )
            )
        dataset.add_column('copd_prescriptions_post_' + time_name,
            count.prescriptions(
                med_events_1, index_date, index_date + time,
                where=medications.dmd_code.is_in(copd_medications)
                )
            )

        #use in time period after index_date - general
        dataset.add_column('ed_attendances_post_'+time_name, 
            count.ed_attendances(
                ed_events_1, index_date, index_date + time
                )
            )
        dataset.add_column('primary_care_attendances_post_'+time_name, 
            count.primary_care_attendances(
                gp_events_1, index_date, index_date + time
                )
            )
        dataset.add_column('hospital_admissions_post_'+time_name, 
            count.hospital_admissions(
                apc_events_1, index_date, index_date + time
                )
            )

        #use in time period before index_date - general
        dataset.add_column('ed_attendances_pre_'+time_name, 
            count.ed_attendances(
                ed_events_2, index_date - time, index_date
                )
            )
        dataset.add_column('primary_care_attendances_pre_'+time_name, 
            count.primary_care_attendances(
                gp_events_2, index_date - time, index_date
                )
            )
        dataset.add_column('hospital_admissions_pre_'+time_name, 
            count.hospital_admissions(
                apc_events_2, index_date - time, index_date
                )
            )

        #use in time period before index_date - COPD specific
        dataset.add_column('copd_ed_attendances_pre_'+time_name,
            count.ed_attendances(
                ed_events_2, index_date - time, index_date,
                where=eca.diagnosis_01.is_in(copd_exacerbations_snomed)
                )
            )
        dataset.add_column('copd_primary_care_attendances_pre_'+time_name,
            count.primary_care_attendances(
                gp_events_2, index_date - time, index_date,
                where=clinical_events.snomedct_code.is_in(copd_exacerbations_snomed)
                )
            )
        dataset.add_column('copd_hospital_admissions_pre_'+time_name,
            count.hospital_admissions(
                apc_events_2, index_date - time, index_date,
                where=apcs.primary_diagnosis.is_in(copd_exacerbations_icd10)
                )
            )
        dataset.add_column('copd_prescriptions_pre' + time_name,
            count.prescriptions(
                med_events_2, index_date - time, index_date,
                where=medications.dmd_code.is_in(copd_medications)
                )
            )
        
    ## Objective 3.2
    periods = {
        "post_0_3m": (index_date, index_date + days(90)),
        "post_3_6m": (index_date + days(90), index_date + days(180)),
        "post_6_9m": (index_date + days(180), index_date + days(270)),
        "post_9_12m": (index_date + days(270), index_date + days(360)),
        "pre_0_3m": (index_date - days(90), index_date),
        "pre_3_6m": (index_date - days(180), index_date - days(90)),
        "pre_6_9m": (index_date - days(270), index_date - days(180)),
        "pre_9_12m": (index_date - days(360), index_date - days(270)),
    }
   

    for time_name, (start,end) in periods.items():

        if time_name.split('_')[0] == 'post':
            #use in time period after index_date
            dataset.add_column('ed_attendances_'+time_name, 
                count.ed_attendances(ed_events_2, start, end)
                )
            dataset.add_column('primary_care_attendances_'+time_name, 
                count.primary_care_attendances(gp_events_2, start,end)
                )
            dataset.add_column('hospital_admissions_'+time_name,
                count.hospital_admissions(apc_events_2, start,end)
                )
            dataset.add_column('prescriptions_' + time_name, 
                count.prescriptions(med_events_2, start, end)
                )
            
        else:
            #use in time period before index date
            dataset.add_column('ed_attendances_'+time_name, 
                count.ed_attendances(ed_events_1, start, end)
                )
            dataset.add_column('primary_care_attendances_'+time_name, 
                count.primary_care_attendances(gp_events_1, start,end)
                )
            dataset.add_column('hospital_admissions_'+time_name,
                count.hospital_admissions(apc_events_1, start,end)
                )
            dataset.add_column('prescriptions_' + time_name, 
                count.prescriptions(med_events_1, start, end)
                )
            
    ## annual reviews
    # Asthma
    asthma_review_ = last.matching_event_snomed(
        before_gp_events,
        asthma_review
        )
    dataset.asthma_review_date = asthma_review_.date
    
    # COPD
    copd_review_ = last.matching_event_snomed(
        before_gp_events,
        copd_review
        )
    dataset.copd_review_date = copd_review_.date

    # Medications (any)
    med_review_ = last.matching_event_snomed(
        before_gp_events,
        med_review
        )
    dataset.med_review_date = med_review_.date


    return dataset

