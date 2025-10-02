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
# QUERY 
# Should the baseline characteristics table (in our papers) include variables measured at the eligibility date or cohort entry date?
# Assume cohort entry as that is why we have this function but some variables included in a baseline table (imd10 and rural) are only defined at the eligibility date.   
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
# QUERY 
# Why does the population vary across WPs when they all have the same eligibility criteria?

#registered for at least 1 year
#practice registration at minimum study end date - 1 year
#exclude historic registrations that ended before start_date

has_registration = practice_registrations.where(
        practice_registrations.start_date.is_on_or_before(end_date - years(1))
    ).except_where(
        practice_registrations.end_date.is_on_or_before(start_date)
    ).exists_for_patient()

# QUERIES
# Assuming this is the eligible population so variables should be defined at the eligibility date (patient_index_date) and currently true 
# for imd10 and rural_urban), why remove those who died before start_date and not died before the patient_index _date?
# 
# Shouldn't exclusions in consort diagram match those in the population? Currently don't (but work in progress)
#
# Shouldn’t we remove patients who are over 109 years at the end of the study? (some may age and become ineligible at cohort entry date).
#
#Do we just ignore the possibility of someone improving their imd10 status or changing region by the time they entered the cohort and assume this is fixed?    

dataset.define_population(
    has_registration
    & patients.sex.is_in(['male','female']) #known sex proxy for data quality
    & patients.date_of_birth.is_not_null() #known dob proxy for data quality
    & ~(patients.age_on(end_date) < 45) #remove pts < 45
    & ~(patients.age_on(end_date) >= 110) #remove pts age 110+
    & (patients.is_alive_on(start_date)) #remove pts who died before start
    & ((dataset.hf_diagnosis_date.is_null()) | (dataset.hf_exclude.is_null())|(dataset.hf_diagnosis_date > start_date))
    & dataset.imd10.is_not_null() 
    & dataset.rural_urban.is_not_null()
     )
