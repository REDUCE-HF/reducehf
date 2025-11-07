import config

from ehrql.tables.tpp import (
    patients,
    practice_registrations,
    ons_deaths
    )

from ehrql import (
    create_dataset,
    years,
    days,
    get_parameter,
    minimum_of
    )

from functions.core import(
    location,
    hf_exclude,
    time_dependent,
    underserved,
    )

dataset = create_dataset()

start_date = config.start_date
end_date = config.end_date

dataset.configure_dummy_data(
    population_size=100000,
    timeout=500
    )

dataset.death_date = minimum_of(patients.date_of_death, ons_deaths.date)

cohort_index_date = get_parameter("cohort_index_date", type = str, default = "2019-02-01")

#ADD VARIABLES NEEDED FOR INCLUSION/EXCLUSION


#registered for at least one year prior to index date
has_registration = practice_registrations.spanning(
    cohort_index_date - years(1), 
    cohort_index_date
    ).exists_for_patient()


#hf diagnosis
dataset = location.fn(dataset, cohort_index_date)
dataset = time_dependent.fn(dataset, cohort_index_date)
dataset = underserved.fn(dataset, cohort_index_date, end_date, iter=iter)

dataset.define_population(
    (has_registration)
    & (patients.sex.is_in(['male','female'])) #known sex proxy for data quality
    & (patients.date_of_birth.is_not_null()) #known dob proxy for data quality
    & ~(patients.age_on(cohort_index_date) < 45) #remove pts < 45
    & ~(patients.age_on(cohort_index_date) >= 110) #remove pts age 110+
    & ((cohort_index_date < dataset.death_date)|(dataset.death_date.is_null())) #remove pts who died before start
)

#####################
# If we include quality assurance conditions  when generating dummy data, no data generated
# Assuming because the data is such low fidelity
# Commenting out until working with real data
####################
#    & ~((dataset.sex == 'male') & (dataset.hrtcocp.is_not_null())) #remove males with hrt / cocp codes
#    & ~((dataset.sex == 'male') & (dataset.pregnancy.is_not_null())) #remove males with pregnancy codes
#    & ~((dataset.sex == 'female') & (dataset.prostate_cancer.is_not_null())) #remove females with prostate cancer codes
###################
##################
# WP SPECIFIC CRITERIA
##################
# WP1 has no extra criteria


# ADD VARIABLES NEEDED FOR WP1
# WP1 needs cohorts with different start dates



