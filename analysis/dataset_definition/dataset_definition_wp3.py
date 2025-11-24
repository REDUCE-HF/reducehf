import config

from ehrql.tables.tpp import (
    patients,
    practice_registrations,
    )

from ehrql import (
    create_dataset,
    years
    )

from functions.core import(
    demog,
    location,
    quality_assurance,
    hf_exclude,
    hf_diagnosis,
    time_dependent,
    underserved,
    comorbidities
    )

from functions.wp3 import hsu

dataset = create_dataset()

#placeholder dates for now
start_date = config.start_date
end_date = config.end_date
earliest_date = config.earliest

dataset.configure_dummy_data(
    population_size=10000,
    timeout=500
    )


#ADD VARIABLES NEEDED FOR INCLUSION/EXCLUSION

#demographic variables derived based on start_date
dataset = demog.fn(dataset, start_date, end_date)

#quality assurance
dataset = quality_assurance.fn(dataset, earliest_date, dataset.patient_index_date)

#hf exclude
dataset = hf_exclude.fn(dataset, earliest_date, dataset.patient_index_date)

#hf diagnosis
dataset = hf_diagnosis.fn(dataset, dataset.patient_index_date, end_date)

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
    & ((dataset.patient_index_date < dataset.death_date)|(dataset.death_date.is_null())) #remove pts who died before start
#####################
# If we include quality assurance conditions  when generating dummy data, no data generated
# Assuming because the data is such low fidelity
# Commenting out until working with real data
####################
#    & ~((dataset.sex == 'male') & (dataset.hrtcocp.is_not_null())) #remove males with hrt / cocp codes
#    & ~((dataset.sex == 'male') & (dataset.pregnancy.is_not_null())) #remove males with pregnancy codes
#    & ~((dataset.sex == 'female') & (dataset.prostate_cancer.is_not_null())) #remove females with prostate cancer codes
###################
    & (dataset.hf_exclude_date.is_null()) # remove pts with evidence of HF prior (including diagnosis??) to patient_index_date
##################
# WP SPECIFIC CRITERIA
##################
    & (dataset.hf_diagnosis_date.is_not_null())  	#for WP3 only want people with HF diagnisis
)

# ADD VARIABLES NEEDED FOR WP3

dataset = location.fn(dataset, dataset.hf_diagnosis_date)

dataset = time_dependent.fn(dataset, dataset.hf_diagnosis_date)

dataset = hsu.fn(dataset, earliest_date, dataset.hf_diagnosis_date)

dataset = comorbidities.fn(dataset, earliest_date, end_date)

dataset = underserved.fn(dataset, earliest_date, dataset.hf_diagnosis_date, end_date)
