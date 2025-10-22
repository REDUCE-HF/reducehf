from functions.lib import *

####################
# Health Service Use
####################

def fn(dataset, index_date):

    '''
    add variables measuring health service use
    only needed for WP3 (?)

    '''

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
            ed_attendances(index_date,
                index_date + time,
                where=eca.diagnosis_01.is_in(copd_exacerbations_snomed)
                )
            )
        dataset.add_column('copd_primary_care_attendances_post_'+time_name,
            primary_care_attendances(index_date,
                index_date + time,
                where=clinical_events.snomedct_code.is_in(copd_exacerbations_snomed)
                )
            )
        dataset.add_column('copd_hospital_admissions_post_'+time_name,
            hospital_admissions(index_date,
                index_date + time,
                where=apcs.primary_diagnosis.is_in(copd_exacerbations_icd10)
                )
            )
        dataset.add_column('copd_prescriptions_post_' + time_name,
            prescriptions_count(index_date,
                index_date+time,
                where=medications.dmd_code.is_in(copd_medications)
                )
            )

        #use in time period after index_date - general
        dataset.add_column('ed_attendances_post_'+time_name, 
            ed_attendances(
                index_date, index_date + time
                )
            )
        dataset.add_column('primary_care_attendances_post_'+time_name, 
            primary_care_attendances(
                index_date, index_date + time
                )
            )
        dataset.add_column('hospital_admissions_post_'+time_name, 
            hospital_admissions(
                index_date, index_date + time
                )
            )

        #use in time period before index_date - general
        dataset.add_column('ed_attendances_pre_'+time_name, 
            ed_attendances(
                index_date - time, index_date
                )
            )
        dataset.add_column('primary_care_attendances_pre_'+time_name, 
            primary_care_attendances(
                index_date - time, index_date
                )
            )
        dataset.add_column('hospital_admissions_pre_'+time_name, 
            hospital_admissions(
                index_date-time, index_date
                )
            )

        #use in time period before index_date - COPD specific
        dataset.add_column('copd_ed_attendances_pre_'+time_name,
            ed_attendances(index_date - time,
                index_date,
                where=eca.diagnosis_01.is_in(copd_exacerbations_snomed)
                )
            )
        dataset.add_column('copd_primary_care_attendances_pre_'+time_name,
            primary_care_attendances(index_date - time,
                index_date,
                where=clinical_events.snomedct_code.is_in(copd_exacerbations_snomed)
                )
            )
        dataset.add_column('copd_hospital_admissions_pre_'+time_name,
            hospital_admissions(index_date-time,
                index_date,
                where=apcs.primary_diagnosis.is_in(copd_exacerbations_icd10)
                )
            )
        dataset.add_column('copd_prescriptions_pre' + time_name,
            prescriptions_count(index_date-time,
                index_date,
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

        #use in time period after index_date
        dataset.add_column('ed_attendances_'+time_name, 
            ed_attendances(start, end)
            )
        dataset.add_column('primary_care_attendances_'+time_name, 
            primary_care_attendances(start,end)
            )
        dataset.add_column('hospital_admissions_'+time_name,
            hospital_admissions(start,end)
            )
        dataset.add_column('prescriptions_' + time_name, 
            prescriptions_count(start, end)
            )

    ## annual reviews
    # Asthma
    asthma_review_ = last_matching_event_clinical_snomed_before(
        asthma_review, index_date
        )
    dataset.asthma_review_date = asthma_review_.date
    
    # COPD
    copd_review_ = last_matching_event_clinical_snomed_before(
        copd_review, index_date
        )
    dataset.copd_review_date = copd_review_.date

    # Medications (any)
    med_review_ = last_matching_event_clinical_snomed_before(
        med_review, index_date
        )
    dataset.med_review_date = med_review_.date


    return dataset

