from functions.lib import *

def fn(dataset, start_date, end_date):

    tmp_date_covid_sgss = (
        sgss_covid_all_tests.where(
            sgss_covid_all_tests.specimen_taken_date.is_on_or_between(start_date, end_date)
        )
        .where(sgss_covid_all_tests.is_positive)
        .sort_by(sgss_covid_all_tests.specimen_taken_date)
        .first_for_patient()
        .specimen_taken_date
    )
    tmp_date_covid_gp = (
        clinical_events.where(
            (clinical_events.ctv3_code.is_in(
                covid_primary_care_code + 
                covid_primary_care_positive_test +
                covid_primary_care_sequalae)) &
            clinical_events.date.is_on_or_between(start_date, end_date)
        )
        .sort_by(clinical_events.date)
        .first_for_patient()
        .date
    )

    tmp_date_covid_apc = (
        apcs.where(
            ((apcs.primary_diagnosis.is_in(covid_codes)) | 
             (apcs.secondary_diagnosis.is_in(covid_codes))) & 
            (apcs.admission_date.is_on_or_between(start_date, end_date))
        )
        .sort_by(apcs.admission_date)
        .first_for_patient()
        .admission_date
    )

    tmp_covid_death = (
        ons_deaths.cause_of_death_is_in(covid_codes) 
        & ons_deaths.date.is_on_or_between(start_date, end_date)
        )    
    tmp_date_death = ons_deaths.date
    tmp_date_covid_death = case(
        when(tmp_covid_death).then(tmp_date_death)
    )
    
    date_covid = minimum_of(
        tmp_date_covid_sgss, 
        tmp_date_covid_gp,
        tmp_date_covid_apc,
        tmp_date_covid_death
    )


    dataset.covid_date = date_covid

    return dataset
