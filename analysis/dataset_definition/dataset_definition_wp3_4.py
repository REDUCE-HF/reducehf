from functions.lib import *

from functions.core import(
    base,
    quality_assurance,
    hf_exclude,
    hf_diagnosis,
    time_dependent,
    underserved,
    comorbidities
    )

from functions.wp3 import hsu

dataset = create_dataset()

dataset.configure_dummy_data(population_size=100000)

#placeholder dates for now
start_date = "2017-01-01"
end_date = "2025-01-01"


#ADD VARIABLES NEEDED FOR INCLUSION/EXCLUSION

#core variables derived based on start_date
dataset = base.fn(dataset, start_date)

#quality assurance
dataset = quality_assurance.fn(dataset, dataset.patient_index_date)

#hf diagnosis
dataset = hf_exclude.fn(dataset, dataset.patient_index_date)



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
    & (dataset.imd10.is_not_null()) # remove pts with unknown IMD
    & (dataset.rural_urban.is_not_null()) # remove pts with unknown rural/urban
    & (dataset.hf_exclude.is_null()) # remove pts with evidence of HF prior (including diagnosis??) to patient_index_date
##################
# WP SPECIFIC CRITERIA
##################
#    & dataset.hf_diagnosis_date.is_not_null()  	#for WP3 only want people with HF diagnisis
)

dataset.index_date = case(
    when(
        dataset.hf_diagnosis_date.is_not_null()
        ).then(dataset.hf_diagnosis_date),
    otherwise = end_date - years(2)
    )

# ADD VARIABLES NEEDED FOR WP3

dataset = time_dependent.fn(dataset, dataset.index_date)

# date should be date of HF diagnosis for WP3
dataset = hsu.fn(dataset, dataset.index_date)

#using date of HF diagnosis as reference for WP3 only
dataset = comorbidities.fn(dataset, end_date)

dataset = underserved.fn(dataset, dataset.patient_index_date, end_date)
