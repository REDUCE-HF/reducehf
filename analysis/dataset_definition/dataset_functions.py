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
    last_matching_event_apc_before,
    first_matching_event_clinical_snomed_before,
    last_matching_event_clinical_snomed_before,
    last_matching_event_clinical_ctv3_before,
    first_matching_med_dmd_before,
    last_matching_med_dmd_before,
    last_matching_event_clinical_snomed_between,
    last_matching_event_apc_between,
    first_matching_event_apc_before,
    count_matching_event_clinical_ctv3_before,
    count_matching_event_apc_before,
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
    
# No Ethnicity from sus ? 
    ethnicity = (
        clinical_events.where(clinical_events.snomedct_code.is_in(ethnicity_snomed))
        .where(clinical_events.date.is_on_or_before(project_index_date))
        .sort_by(clinical_events.date)
        .last_for_patient()
        .snomedct_code
    )

    dataset.ethnicity = ethnicity.to_category(ethnicity_snomed)

    #earliest practice registration
    first_practice = (
        practice_registrations.where(practice_registrations.end_date.is_after(project_index_date))
        .sort_by(
            practice_registrations.start_date,
            practice_registrations.end_date,
            practice_registrations.practice_pseudo_id)
        .first_for_patient()
    )

    #patient index date latest of:
    # - project start
    # - practice registration - 1 year (to allow for coding of variables)
    # - 45th birthday

    dataset.patient_index = maximum_of(project_index_date,
        first_practice.start_date + years(1),
        dataset.dob + years(45))

    # practice registration on patient_index_date
    practice = (
        practice_registrations.where(practice_registrations.start_date.is_on_or_before(dataset.patient_index))
        .sort_by(practice_registrations.start_date)
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
        practice_registrations.where(practice_registrations.end_date.is_after(project_index_date))
        .sort_by(
            practice_registrations.start_date,
            practice_registrations.end_date,
            practice_registrations.practice_pseudo_id)
        .last_for_patient()
    )
    dataset.practice_deregistration_date = last_practice.end_date

    #add location details at patient_index
    location = addresses.for_patient_on(dataset.patient_index)
    dataset.imd10 = location.imd_decile
    dataset.rural_urban = location.rural_urban_classification

    # date of death
    dataset.death_date = minimum_of(patients.date_of_death, ons_deaths.date)

    #Household size
    dataset.household_size = household_memberships_2020.household_size

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


def add_underserved(dataset, index_date):

    practice = practice_registrations.sort_by(
        practice_registrations.start_date,
        practice_registrations.end_date,
        practice_registrations.practice_pseudo_id).last_for_patient()
    
    #Care home status

    location = addresses.for_patient_on(dataset.patient_index)
    
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
    - codelists to be changed
    '''
    ### Diabetes 
    dataset.ethnicity_cat = case(
        when(dataset.ethnicity == "1").then("White"),
        when(dataset.ethnicity == "2").then("Mixed"),
        when(dataset.ethnicity == "3").then("Asian"),
        when(dataset.ethnicity == "4").then("Black"),
        when(dataset.ethnicity == "5").then("Other"),
        otherwise="Unknown",
)
    
## Type 1 Diabetes 
# First date from primary+secondary, but also primary care date separately for diabetes algo
    dataset.tmp_t1dm_ctv3_date = first_matching_event_clinical_ctv3_before(diabetes_type1_ctv3, index_date).date
    dataset.t1dm_date = minimum_of(
    (first_matching_event_clinical_ctv3_before(diabetes_type1_ctv3, index_date).date),
    (first_matching_event_apc_before(diabetes_type1_icd10, index_date).admission_date)
)
# Count codes (individually and together, for diabetes algo)
    tmp_t1dm_ctv3_count = count_matching_event_clinical_ctv3_before(diabetes_type1_ctv3, index_date)
    tmp_t1dm_hes_count = count_matching_event_apc_before(diabetes_type1_icd10, index_date)
    dataset.tmp_t1dm_count_num = tmp_t1dm_ctv3_count + tmp_t1dm_hes_count

## Type 2 Diabetes
# First date from primary+secondary, but also primary care date separately for diabetes algo)
    dataset.tmp_t2dm_ctv3_date = first_matching_event_clinical_ctv3_before(diabetes_type2_ctv3, index_date).date
    dataset.t2dm_date = minimum_of(
        (first_matching_event_clinical_ctv3_before(diabetes_type2_ctv3, index_date).date),
        (first_matching_event_apc_before(diabetes_type2_icd10, index_date).admission_date)
    )
# Count codes (individually and together, for diabetes algo)
    tmp_t2dm_ctv3_count = count_matching_event_clinical_ctv3_before(diabetes_type2_ctv3, index_date)
    tmp_t2dm_hes_count = count_matching_event_apc_before(diabetes_type2_icd10, index_date)
    dataset.tmp_t2dm_count_num = tmp_t2dm_ctv3_count + tmp_t2dm_hes_count

## Diabetes unspecified/other
# First date
    dataset.otherdm_date = first_matching_event_clinical_ctv3_before(diabetes_other_ctv3, index_date).date
# Count codes
    dataset.tmp_otherdm_count_num = count_matching_event_clinical_ctv3_before(diabetes_other_ctv3, index_date)

## Gestational diabetes
# First date from primary+secondary
    dataset.gestationaldm_date = minimum_of(
    (first_matching_event_clinical_ctv3_before(diabetes_gestational_ctv3, index_date).date),
    (first_matching_event_apc_before(diabetes_gestational_icd10, index_date).admission_date)
)

## Diabetes diagnostic codes
# First date
    dataset.tmp_poccdm_date = first_matching_event_clinical_ctv3_before(diabetes_diagnostic_ctv3, index_date).date
# Count codes
    dataset.tmp_poccdm_ctv3_count_num = count_matching_event_clinical_ctv3_before(diabetes_diagnostic_ctv3, index_date)

### Other variables needed to define diabetes
## HbA1c
# Maximum HbA1c measure (in the same period)
    dataset.tmp_max_hba1c_mmol_mol_num = (
  clinical_events.where(
    clinical_events.snomedct_code.is_in(hba1c_snomed))
    .where(clinical_events.date.is_on_or_before(index_date))
    .numeric_value.maximum_for_patient()
)
# Date of first maximum HbA1c measure
    dataset.tmp_max_hba1c_date = ( 
  clinical_events.where(
    clinical_events.snomedct_code.is_in(hba1c_snomed))
    .where(clinical_events.date.is_on_or_before(index_date)) # this line of code probably not needed again
    .where(clinical_events.numeric_value == dataset.tmp_max_hba1c_mmol_mol_num)
    .sort_by(clinical_events.date)
    .first_for_patient() 
    .date
)

## Diabetes drugs
# First dates
    dataset.tmp_insulin_dmd_date = first_matching_med_dmd_before(insulin_dmd, index_date).date
    dataset.tmp_antidiabetic_drugs_dmd_date = first_matching_med_dmd_before(antidiabetic_drugs_dmd, index_date).date
    dataset.tmp_nonmetform_drugs_dmd_date = first_matching_med_dmd_before(non_metformin_dmd, index_date).date

# Identify first date (in same period) that any diabetes medication was prescribed
    dataset.tmp_diabetes_medication_date = minimum_of(dataset.tmp_insulin_dmd_date, dataset.tmp_antidiabetic_drugs_dmd_date)

    # Identify first date (in same period) that any diabetes diagnosis codes were recorded
    dataset.tmp_first_diabetes_diag_date = minimum_of(
    dataset.t1dm_date, 
    dataset.t2dm_date,
    dataset.otherdm_date,
    dataset.gestationaldm_date,
    dataset.tmp_poccdm_date,
    dataset.tmp_diabetes_medication_date,
    dataset.tmp_nonmetform_drugs_dmd_date
    )
 
 ### Obesity 

    dataset.obesity_primary_date = last_matching_event_clinical_snomed_between(
        bmi_obesity_snomed, index_date - days(365), index_date
    ).date
        
    dataset.obesity_sus_date = last_matching_event_apc_between(
        bmi_obesity_icd10, index_date - days(365), index_date    
            ).admission_date
        
#     dataset.bmi_date= last_matching_event_clinical_snomed_between(
#     bmi_primis, index_date - days(365), index_date
# ).date
#     dataest.bmi= last_matching_event_clinical_snomed_between(
#     bmi_primis, index_date - days(365), index_date
# ).numeric_value
    

    # weight 
    # Do we need to check icd10 codes ? 

    dataset.weight = last_matching_event_clinical_snomed_between(
    weight_snomed, index_date - days(365), index_date
).numeric_value
    dataset.weight_date  = last_matching_event_clinical_snomed_between(
    weight_snomed, index_date - days(365), index_date
).date
   

    # height
    # Do we need to check icd10 codes ? 
    dataset.height = last_matching_event_clinical_snomed_before (
        height_snomed, index_date
    ).numeric_value

    
    
### COPD
    '''
  Shall we just derive primary and sus dates ? 
  or take the earliest and tag them as tmp to remove them from 
  the dataset later ? 
    ''' 
    
    dataset.tmp_copd_date_primary = first_matching_event_clinical_ctv3_before(
    copd_ctv3, index_date
).date
    dataset.tmp_copd_date_sus = first_matching_event_apc_before(
    copd_icd10, index_date
).admission_date
# Combine to earliest date
    dataset.first_copd_date    = minimum_of(
    dataset.tmp_copd_date_primary,
    dataset.tmp_copd_date_sus
)
### Hypertension

    dataset.hypertension_date_primary = first_matching_event_clinical_snomed_before(
            hypertension_snomed, index_date
        ).date
    dataset.hypertension_date_med = first_matching_med_dmd_before(
            hypertension_drugs_dmd, index_date
        ).date
    dataset.hypertension_date_sus = first_matching_event_apc_before(
            hypertension_icd10, index_date
        ).admission_date
    #systolic BP* diastolic BP* will be defined in time dependent variables
#
 ### Atrial fibrillation
    dataset.af_date_primary = first_matching_event_clinical_snomed_before(
           af_snomed, index_date
        ).date

    dataset.af_date_sus = first_matching_event_apc_before(
           af_icd10, index_date
        ).admission_date

### Ischeamic heart disease
     
     #Are we sure we need to remove binary vars ? 
    # Keep just primary and sus dates or derive earliest date ? 
    
    # dataset.ihd_bin = (
    #     (first_matching_event_clinical_snomed_before(
    #        ihd_snomed, index_date
    #     ).exists_for_patient()) |
    #     (first_matching_event_apc_before(
    #        ihd_icd10, index_date
    #     ).exists_for_patient())
    # )
    dataset.ihd_date_primary = first_matching_event_clinical_snomed_before(
        ihd_snomed, index_date
    ).date
    dataset.ih_date_sus = first_matching_event_apc_before(
        ihd_icd10, index_date
    ).admission_date

 ### Chronic kidney disease (CKD)
    # dataset.ckd_bin = (
    #     frist_matching_event_clinical_snomed_before(
    #         ckd_snomed, index_date
    #     ).exists_for_patient()) |
    #     (first_matching_event_apc_before(
    #         ckd_icd10, index_date
    #     ).exists_for_patient())
    dataset.ckd_date_primary = first_matching_event_clinical_snomed_before(
        ckd_snomed, index_date
    ).date
    dataset.ckd_date_sus = first_matching_event_apc_before(
        ckd_icd10, index_date
    ).admission_date


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
