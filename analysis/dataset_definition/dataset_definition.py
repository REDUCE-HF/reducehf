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

#using these dates for now
project_index_date = '2017-01-01'
end_date = '2025-01-01'

#ADD VARIABLES TO DATASET

#will need to define this more thoroughly
dataset = add_hf_diagnosis(dataset, project_index_date)

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
    practice_registrations.start_date <= end_date - years(1)
    ).except_where(
    practice_registrations.end_date < project_index_date
    ).exists_for_patient()

dataset.define_population(
    has_registration
    & patients.sex.is_in(['male','female']) #known sex proxy for data quality
    & patients.date_of_birth.is_not_null() #known dob proxy for data quality
    & ~(patients.age_on(end_date) < 45) #remove pts < 45
    & ~(patients.age_on(project_index_date) >= 110) #remove pts age 110+
    & (patients.is_alive_on(project_index_date)) #remove pts who died before start
    & ((dataset.hf_diagnosis_date.is_null()) | (dataset.hf_diagnosis_date > project_index_date))
   )




