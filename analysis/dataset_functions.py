#this script contains functions to add variables to dataset
#variables are grouped by type, and whether they are WP specific

from ehrql import (
    case,
    when,
    years,
    days,
    maximum_of,
    minimum_of,
)

from ehrql.tables.tpp import (
    patients,
    practice_registrations,
    clinical_events,
    addresses,
    apcs,
    household_memberships_2020,
    ons_deaths,
)

from helper_functions import (
    ed_attendances,
    primary_care_attendances,
    hospital_admissions,
    ever_matching_event_clinical_ctv3_before,
    first_matching_event_clinical_ctv3_before,
    first_matching_event_clinical_snomed_before,
    last_matching_event_clinical_snomed_before,
    last_matching_event_clinical_ctv3_before,
    filter_codes_by_category
)

from codelists import *

def add_core(dataset, project_index_date, end_date='2025-01-01'):


    '''
    core variables don't differ between WPs
    they depend on project_index_date only

    parameters:

    dataset: dataset object initialised using create_dataset()
    project_index_date: for our project, 01-01-2017
    end_date: project / follow-up end date
    '''


    dataset.sex = patients.sex
    dataset.dob = patients.date_of_birth

    #add practice details
    # most recent practice registration

    practice = practice_registrations.sort_by(
        practice_registrations.start_date,
        practice_registrations.end_date,
        practice_registrations.practice_pseudo_id).last_for_patient()

    dataset.practice_id = practice.practice_pseudo_id
    dataset.practice_registration_date = practice.start_date
    dataset.practice_deregistration_date = practice.end_date

    #patient index date latest of:
    # - project start
    # - practice registration - 1 year (to allow for coding of variables)
    # - 45th birthday

    dataset.patient_index = maximum_of(project_index_date,
        dataset.practice_registration_date - years(1),
        dataset.dob + years(45))

    #add area level details

    dataset.practice_stp = practice.practice_stp
    dataset.region = practice.practice_nuts1_region_name

    location = addresses.for_patient_on(dataset.patient_index)

    dataset.imd10 = location.imd_decile

    dataset.rural_urban = location.rural_urban_classification

    #was address at patient index date a care home    
    dataset.carehome_at_start = (
        location.care_home_is_potential_match |
        location.care_home_requires_nursing |
        location.care_home_does_not_require_nursing
    )

    #was address at deregistration or study end date a care home
    location = addresses.for_patient_on(maximum_of(practice.end_date, end_date))
    dataset.carehome_at_end = (
        location.care_home_is_potential_match |
        location.care_home_requires_nursing |
        location.care_home_does_not_require_nursing
    )

    # date of death
    dataset.death_date = minimum_of(patients.date_of_death, ons_deaths.date)


    return dataset



def add_time_dependent_core(dataset, index_date):

    '''
    add core variables that depend on index date
    and therefore differ between WPs
    variables to be added:
    -  smoking status
    -  household size
    -  BMI
    -  systolic BP*
    -  diastolic BP*
    -  total cholesterol*
    *(date of most recent test/reading prior to index date and value)
    '''

    # Smoking status
    tmp_most_recent_smoking_cat = (
        last_matching_event_clinical_ctv3_before(smoking_clear, index_date)
        .ctv3_code.to_category(smoking_clear)
    )
    tmp_ever_smoked = ever_matching_event_clinical_ctv3_before(
        (filter_codes_by_category(smoking_clear, include=["S", "E"])), index_date
        ).exists_for_patient()

    dataset.smoking = case(
        when(tmp_most_recent_smoking_cat == "S").then("S"),
        when((tmp_most_recent_smoking_cat == "E") | ((tmp_most_recent_smoking_cat == "N") 
            & (tmp_ever_smoked == True))).then("E"),
        when((tmp_most_recent_smoking_cat == "N") & (tmp_ever_smoked == False)).then("N"),
        otherwise="M"
    )

    #Household size
    #NOTE this doesnt depend on index date -- should be in core function
    dataset.household_size = household_memberships_2020.household_size
    
    # BMI
    dataset.bmi_date = last_matching_event_clinical_snomed_before(
        bmi_primis, index_date
        ).date

    dataset.bmi_value = last_matching_event_clinical_snomed_before(
        bmi_primis, index_date
        ).numeric_value


    #Cholesterol
    dataset.last_cholesterol_date = last_matching_event_clinical_snomed_before(
        cholesterol_snomed, index_date
        ).date

    dataset.last_cholesterol_value = last_matching_event_clinical_snomed_before(
        cholesterol_snomed, index_date
        ).numeric_value

    return dataset


def add_hf_diagnosis(dataset, index_date):

    '''
    need to define this more thoroughly
    using primary care diagnosis for script development
    function currently returns date of first HF diagnosis in primary care
    function should also return location of first diagnosis
    i.e. community or emergency-hospital
    ''' 

    dataset.hf_diagnosis_date = first_matching_event_clinical_snomed_before(
        hf_snomed, index_date
        ).date

    return dataset

def add_healthservice_use(dataset, index_date):


    '''
    add variables measuring health service use
    only needed for WP3 (?)

    '''

    time_periods = {
        '3m': days(90),
        '6m': days(180),
        '12m': days(360),
        '24m': years(2)
    }

    for time_name, time in time_periods.items():

        #use in time period before index_date
        dataset.add_column('ed_attendances_'+time_name, ed_attendances(index_date, index_date + time))
        dataset.add_column('primary_care_attendances_'+time_name, primary_care_attendances(index_date, index_date + time))
        dataset.add_column('hospital_admissions_'+time_name, hospital_admissions(index_date, index_date + time))

        #use in time period after index_date
        dataset.add_column('ed_attendances_pre_'+time_name, ed_attendances(index_date - time, index_date))
        dataset.add_column('primary_care_attendances_pre_'+time_name, primary_care_attendances(index_date - time, index_date))
        dataset.add_column('hospital_admissions_pre_'+time_name, hospital_admissions(index_date-time, index_date))

    return dataset


def add_comorbidities(dataset, index_date):

    '''
    add comorbidities. using index_date as a parameter
    means we can derive as binary variables rather than dates
    '''

    dataset.copd = first_matching_event_clinical_ctv3_before(
        copd_ctv3, index_date
        ).exists_for_patient()

    dataset.ckd = first_matching_event_clinical_snomed_before(
        ckd_snomed, index_date
        ).exists_for_patient()

    dataset.diabetes = first_matching_event_clinical_snomed_before(
        diabetes_snomed, index_date
        ).exists_for_patient()

    #using latest date for obesity, hypertension, and total cholesterol
    dataset.obesity = last_matching_event_clinical_snomed_before(
        bmi_obesity_snomed, index_date
        ).exists_for_patient()

    dataset.hypertension = last_matching_event_clinical_snomed_before(
        hypertension_snomed, index_date
        ).exists_for_patient()

    return dataset


def add_tests(dataset, index_date):
    
    '''
    derive test dates and results: 
    -  BNP 
    -  NT-proBNP
    '''

    return dataset


def add_symptoms(dataset, start_date, end_date):

    '''
    add first date of recording and whether recorded 
    between start_date and end_date.
    symptoms:
    -  breathlesness
    -  oedema
    -  fatigue
    note: for WP2, index_date == date of BNP / NT-proBNP test

    need to add following codelists:
    -  breathlesness: https://www.opencodelists.org/codelist/nhsd-primary-care-domain-refsets/breathlessness-codes/20241205/
    -  oedema: not currently available - need to create
    -  fatigue: https://www.opencodelists.org/codelist/opensafely/symptoms-fatigue/0e9ac677/
    '''

    return dataset


def add_copd_severity(dataset, index_date):


    '''
    add date of most recent copd annual review
    prior to index_date and values for:
    -  MRC breathlessness score
    -  Number of exacerbations
    
    need to add following codelists:
    -  COPD reviews: https://www.opencodelists.org/codelist/nhsd-primary-care-domain-refsets/copdrvw_cod/20241205/
    -  number of exacerbations: https://www.opencodelists.org/codelist/nhsd-primary-care-domain-refsets/copdexacb_cod/20241205/
    -  MRC breathlessness: https://www.opencodelists.org/codelist/nhsd-primary-care-domain-refsets/mrc_cod/20241205/
    '''

    return dataset


def add_medications(dataset, start_date, end_date):

    '''
    add functions to count number of prescriptions
    for a medication between start_date and end_date
    will need codelists for medications
    can use helper functions from post-covid-events
    '''

    return dataset


def add_referrals(dataset, index_date):

    '''
    add functions to count referrals
    for XX (WP2) prior to index_date
    *maybe also need start_date?
    '''

    return dataset
