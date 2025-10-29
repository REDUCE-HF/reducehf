mport config

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
    quality_assurance,
    hf_exclude,
    )

dataset = create_dataset()

#placeholder dates for now
start_date = config.start_date
end_date = config.end_date

dataset.configure_dummy_data(
    population_size=100000,
    timeout=500,
    )

#ADD VARIABLES NEEDED FOR INCLUSION/EXCLUSION

#demographic variables derived based on start_date
dataset = demog.fn(dataset, start_date, end_date)

#hf exclusion
dataset = hf_exclude.fn(dataset, dataset.patient_index_date)

#quality assurance
dataset = quality_assurance.fn(dataset, start_date)


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
    (has_registration)
    & ((dataset.patient_index_date < dataset.death_date)|(dataset.death_date.is_null())) #remove pts who died before start
    )

