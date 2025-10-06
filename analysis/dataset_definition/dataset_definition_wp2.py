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
start_date = "2017-01-01"
end_date = "2025-01-01"

#NOTE: when running from terminal, increase the memory allocation (-m flag)
#or decrease population_size. Default memory is 4G.
dataset.configure_dummy_data(population_size=1000000, timeout=500)


#ADD VARIABLES NEEDED FOR INCLUSION/EXCLUSION

#core variables derived based on start_date
dataset = add_core(dataset, start_date)

#quality assurance
dataset = add_quality_assurance(dataset, dataset.patient_index_date)

#hf diagnosis
dataset = add_hf_diagnosis(dataset, dataset.patient_index_date)

#exclusion vars for WP2 only
dataset = add_wp2_exclusion(dataset, dataset.patient_index_date, end_date)

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
    (has_registration)
    & (patients.sex.is_in(['male','female'])) #known sex proxy for data quality
    & (patients.date_of_birth.is_not_null()) #known dob proxy for data quality
    & ~(patients.age_on(end_date) < 45) #remove pts < 45
    & ~(patients.age_on(dataset.patient_index_date) >= 110) #remove pts age 110+
    & (dataset.patient_index_date < dataset.death_date) #remove pts who died before start
#####################
# If we include quality assurance conditions  when generating dummy data, no data generated
# Assuming because the data is such low fidelity
# Commenting out until working with real data
####################
#    & ~((dataset.sex == 'male') & (dataset.hrtcocp.is_not_null())) #remove males with hrt / cocp codes
#    & ~((dataset.sex == 'male') & (dataset.pregnancy.is_not_null())) #remove males with pregnancy codes
#    & ~((dataset.sex == 'female') & (dataset.prostate_cancer.is_not_null())) #remove females with prostate cancer codes
###################
    & dataset.imd10.is_not_null() # remove pts with unknown IMD
    & dataset.rural_urban.is_not_null() # remove pts with unknown rural/urban
    & dataset.hf_exclude.is_null() # remove pts with evidence of HF prior (including diagnosis??) to patient_index_date
##################
# WP SPECIFIC CRITERIA
##################
# exclude people with no HF symptoms after patient_index_date AND no NP test after patient_index_date
    & ~((dataset.first_hfsymptom_date.is_null()) & (dataset.np_date.is_null())) 
)

# ADD VARIABLES NEEDED FOR WP2

dataset = add_np_vars(dataset, dataset.patient_index_date, end_date)

dataset = add_comorbidities(dataset, end_date)

dataset = add_time_dependent_core(dataset, dataset.first_hfsymptom_date, suffix = '_wp2_1')
dataset = add_time_dependent_core(dataset, dataset.np_date, suffix = '_wp2_2')

# add_underserved() function still in progress
#dataset = add_underserved(dataset, dataset.patient_index_date, end_date)
