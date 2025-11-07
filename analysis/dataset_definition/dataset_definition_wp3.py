from ehrql import (
    create_dataset, 
    years,
    minimum_of
)

from ehrql.tables.tpp import (
    patients,
    practice_registrations,
)

from dataset_functions import *

dataset = create_dataset()


#placeholder dates for now
start_date = "2020-01-01"
end_date = "2025-01-01"


#ADD VARIABLES NEEDED FOR INCLUSION/EXCLUSION

#hf diagnosis
dataset = add_hf_diagnosis(dataset, start_date)

#quality assurance
dataset = add_quality_assurance(dataset, start_date)

#core variables derived based on start_date
dataset = add_core(dataset, start_date)


#DEFINE POPULATION (inclusion/exclusion criteria)
#note: this will be different for each WP

#registered for at least 1 year
#practice registration at minimum study end date - 1 year
#exclude historic registrations that ended before start_date

has_registration = practice_registrations.where(
        practice_registrations.start_date.is_on_or_before(end_date - years(1))
    ).except_where(
        practice_registrations.end_date.is_on_or_before(start_date)
    ).exists_for_patient()

dataset.define_population(
    has_registration
    & patients.sex.is_in(['male','female']) #known sex proxy for data quality
    & patients.date_of_birth.is_not_null() #known dob proxy for data quality
    & ~(patients.age_on(end_date) < 45) #remove pts < 45
    & ~(patients.age_on(start_date) >= 110) #remove pts age 110+
    & (patients.is_alive_on(start_date)) #remove pts who died before start
    & ((dataset.hf_diagnosis_date.is_null()) | (dataset.hf_exclude.is_null())|(dataset.hf_diagnosis_date > start_date))
    & dataset.imd10.is_not_null()
    & dataset.rural_urban.is_not_null()
    )
dataset.configure_dummy_data(population_size=100000)

dataset = add_time_dependent_core(dataset, dataset.hf_diagnosis_date)

# date should be date of HF diagnosis
dataset = add_healthservice_use(dataset, dataset.hf_diagnosis_date)


#using date of HF diagnosis as reference -- may need adjusting
dataset = add_comorbidities(dataset, dataset.hf_diagnosis_date)

