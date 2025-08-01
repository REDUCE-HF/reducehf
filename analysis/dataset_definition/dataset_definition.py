from ehrql import (
    create_dataset, 
    years,
    minimum_of
)

from ehrql.tables.tpp import (
    patients, 
    practice_registrations, 
    clinical_events,
    apcs,
    ec
)

import codelists

from helper_functions import *
from dataset_functions import *

def generate_dataset(project_index_date, end_date):

    dataset = create_dataset()

    #ADD VARIABLES TO DATASET
    dataset = add_hf_diagnosis(dataset, project_index_date)

    #any evidence of HF, not just diagnosis codes, before index date
    dataset.hf_exclude = last_matching_event_clinical_snomed_before(codelists.hf_exclude, project_index_date).date

    #core variables derived based on project_index_date
    dataset = add_core(dataset, project_index_date)

    dataset = add_time_dependent_core(dataset, project_index_date)

    # date should be date of HF diagnosis
    dataset = add_healthservice_use(dataset, dataset.hf_diagnosis_date)

    # using date of HF diagnosis as reference -- may need adjusting
    dataset = add_comorbidities(dataset, dataset.hf_diagnosis_date)

    #DEFINE POPULATION (inclusion/exclusion criteria)
    #note: this will be different for each WP

    #registered for at least 1 year
    #practice registration at minimum study end date - 1 year
    #exclude historic registrations that ended before project_index_date

    has_registration = practice_registrations.where(
            practice_registrations.start_date.is_on_or_before(end_date - years(1))
        ).except_where(
            practice_registrations.end_date.is_on_or_before(project_index_date)
        ).exists_for_patient()

    dataset.define_population(
        has_registration
        & patients.sex.is_in(['male','female']) #known sex proxy for data quality
        & patients.date_of_birth.is_not_null() #known dob proxy for data quality
        & ~(patients.age_on(end_date) < 45) #remove pts < 45
        & ~(patients.age_on(project_index_date) >= 110) #remove pts age 110+
        & (patients.is_alive_on(project_index_date)) #remove pts who died before start
        & (dataset.hf_exclude.is_not_null()) #remove pts with any evidence of heart failure 
    )

    return dataset


