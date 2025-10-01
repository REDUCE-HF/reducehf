from ehrql import (
    create_dataset, 
    years,
)

from ehrql.tables.tpp import (
    patients, 
    practice_registrations, 
)

from dataset_functions import *

dataset = create_dataset()

dataset.configure_dummy_data(population_size=1000)


#placeholder dates for now
start_date = "2020-01-01"
end_date = "2025-01-01"


#ADD VARIABLES TO DATASET

#core variables derived based on start_date - although some are based on patient_index_date (defined within)
dataset = add_core(dataset, start_date)

#patient_index_date is currently defined in add(core) 
dataset = add_time_dependent_core(dataset, dataset.patient_index_date)

# will need to define this more thoroughly
dataset = add_hf_diagnosis(dataset, start_date)

# HF symptoms and tests at eligibility (patient_index) date
dataset=add_np_vars(dataset,dataset.patient_index_date, end_date)

# date should be date of HF diagnosis
dataset = add_healthservice_use(dataset, dataset.hf_diagnosis_date)

# using date of HF diagnosis as reference -- may need adjusting
dataset = add_comorbidities(dataset, dataset.hf_diagnosis_date)

#quality assurance

dataset = add_quality_assurance(dataset, start_date)


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

# Need to define age at cohort entry date (date of first np pro test) - Need a dataset_functions.py, add_core() for WP2_2 as patient_index_date is set there
# and imd10 and rural urban are defined by patient_index_date (eligibility date) and should also be defined at the cohort entry date!!!
dataset.define_population(
    has_registration
    & patients.sex.is_in(['male','female']) #known sex proxy for data quality
    & patients.date_of_birth.is_not_null() #known dob proxy for data quality
    & ~(patients.age_on(end_date) < 45) #remove pts < 45
    & ~(patients.age_on(dataset.patient_index_date) >= 110) #remove pts age 110+
    & (patients.is_alive_on(start_date)) #remove pts who died before start
    & ((dataset.hf_diagnosis_date.is_null()) | (dataset.hf_exclude.is_null())|(dataset.hf_diagnosis_date > start_date))
    & dataset.imd10.is_not_null() 
    & dataset.rural_urban.is_not_null()
     )
