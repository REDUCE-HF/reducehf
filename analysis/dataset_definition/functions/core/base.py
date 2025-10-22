from functions.lib import *

###########################
# Core variables:
# independent of index date
##########################

def fn(dataset, start_date, end_date='2025-01-01'):

    '''
    core variables don't differ between WPs
    they depend on project_index_date only

    parameters:

    dataset: dataset object initialised using create_dataset()
    start_date: for our project, 01-01-2017
    end_date: project / follow-up end date
    '''
    dataset.sex = patients.sex
    dataset.dob = patients.date_of_birth
    

    # Ethnicity in 6 categories
    ethnicity_snomed = (
        clinical_events.where(clinical_events.snomedct_code.is_in(ethnicity_codes))
        .sort_by(clinical_events.date)
        .last_for_patient()
        .snomedct_code.to_category(ethnicity_codes)
        )

    ethnicity_sus = ethnicity_from_sus.code

    dataset.ethnicity_cat = case(
        when((ethnicity_snomed == "1") | 
            ((ethnicity_snomed.is_null()) & (ethnicity_sus.is_in(["A", "B", "C"])))
            ).then("White"),
        when((ethnicity_snomed == "2") | 
            ((ethnicity_snomed.is_null()) & (ethnicity_sus.is_in(["D", "E", "F", "G"])))
            ).then("Mixed"),
        when((ethnicity_snomed == "3") | 
            ((ethnicity_snomed.is_null()) & (ethnicity_sus.is_in(["H", "J", "K", "L"])))
            ).then("Asian"),
        when((ethnicity_snomed == "4") | 
            ((ethnicity_snomed.is_null()) & (ethnicity_sus.is_in(["M", "N", "P"])))
            ).then("Black"),
        when((ethnicity_snomed == "5") | 
            ((ethnicity_snomed.is_null()) & (ethnicity_sus.is_in(["R", "S"])))
            ).then("Other"),
        otherwise="Unknown", 
        )

    #earliest practice registration
    first_practice = (
        practice_registrations.where(
            practice_registrations.end_date.is_after(start_date))
        .sort_by(
            practice_registrations.start_date,
            practice_registrations.end_date,
            practice_registrations.practice_pseudo_id)
        .first_for_patient()
        )

    #patient index date latest of:
    # - project start
    # - practice registration + 1 year (to allow for coding of variables)
    # - 45th birthday

    dataset.patient_index_date = maximum_of(start_date,
        first_practice.start_date + years(1),
        dataset.dob + years(45))

    # practice registration on patient_index_date
    practice = (
        practice_registrations.where(
            practice_registrations.start_date.is_on_or_before(
                dataset.patient_index_date
                )
            ).sort_by(practice_registrations.start_date)
        .last_for_patient()
        )

    # add practice ID and registration date at patient_index
    dataset.practice_id = practice.practice_pseudo_id
    dataset.practice_registration_date = practice.start_date

    #add area level details at patient_index
    dataset.practice_stp = practice.practice_stp
    dataset.region = practice.practice_nuts1_region_name

    # add practice deregistration / end of follow-up in tpp
    last_practice = (
        practice_registrations.where(
            practice_registrations.end_date.is_after(start_date))
        .sort_by(
            practice_registrations.start_date,
            practice_registrations.end_date,
            practice_registrations.practice_pseudo_id)
        .last_for_patient()
    )
    dataset.practice_deregistration_date = last_practice.end_date

    #add location details at patient_index
    location = addresses.for_patient_on(dataset.patient_index_date)
    dataset.imd10 = location.imd_decile
    dataset.rural_urban = location.rural_urban_classification

    # date of death
    dataset.death_date = minimum_of(patients.date_of_death, ons_deaths.date)

    #Household size
    dataset.household_size = household_memberships_2020.household_size

    return dataset
