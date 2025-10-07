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

dataset.configure_dummy_data(population_size=100000)

#placeholder dates for now
start_date = "2017-01-01"
end_date = "2025-01-01"


#ADD VARIABLES NEEDED FOR INCLUSION/EXCLUSION


#core variables 
dataset = add_core(dataset, start_date)

#hf diagnosis
dataset = add_hf_diagnosis(dataset, dataset.patient_index_date)

#quality assurance
dataset = add_quality_assurance(dataset, start_date)


#DEFINE POPULATION (inclusion/exclusion criteria)
#note: this will be different for each WP

#registered for at least 1 year
#practice registration at minimum study end date - 1 year
#exclude historic registrations that ended before project_index_date

has_registration = practice_registrations.where(
        practice_registrations.start_date.is_on_or_before(end_date - years(1))
    ).except_where(
        practice_registrations.end_date.is_on_or_before(start_date)
    ).exists_for_patient()

dataset.define_population(
    has_registration
    & (patients.is_alive_on(start_date)) #remove pts who died before start
    & ((dataset.hf_diagnosis_date.is_null())|(dataset.hf_diagnosis_date > dataset.patient_index_date))
    )

