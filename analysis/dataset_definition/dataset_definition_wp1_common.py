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

dataset = create_dataset()

#placeholder dates for now
start_date = config.start_date
end_date = config.end_date
earliest_date = config.earliest_date

dataset.configure_dummy_data(
    population_size=10000,
    timeout=500
    )

#ADD VARIABLES NEEDED FOR INCLUSION/EXCLUSION

#demographic variables derived based on start_date
dataset = demog(dataset, start_date, end_date)

#quality assurance
dataset = quality_assurance(dataset, earliest_date, end_date)

## For the following - extract earliest possible date to be 
##   used to define eligibility for each cohort

#hf diagnosis
dataset = hf_diagnosis(dataset, start_date, end_date)

#hf exclude 
dataset = hf_exclude(dataset, earliest_date, end_date)

dataset = comorbidities(dataset, earliest_date, end_date)

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
    & ~(patients.age_on(end_date) < 45) #remove pts < 45 at latest possible date
    & ~(patients.age_on(start_date) >= 110) #remove pts age 110+ at earliest possible start date
    & ((start_date < dataset.death_date)|(dataset.death_date.is_null())) #remove pts who died before start
#    & ~((dataset.sex == 'male') & (dataset.hrtcocp.is_not_null())) #remove males with hrt / cocp codes
#    & ~((dataset.sex == 'male') & (dataset.pregnancy.is_not_null())) #remove males with pregnancy codes
#    & ~((dataset.sex == 'female') & (dataset.prostate_cancer.is_not_null())) #remove females with prostate cancer codes
    & ~(dataset.hf_exclude_date < start_date)
)



