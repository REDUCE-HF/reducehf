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
study_end_date = '2025-01-01'

# Define population and cohort entry date for this WP 
# date of first incidence of any of the three HF-related symptoms

dataset.temp_breathless_date_primary=first_matching_event_clinical_snomed_in(
   breathlessness_snomed, project_index_date, end_date
).date

dataset.temp_oedema_date_primary=first_matching_event_clinical_snomed_in(
   oedema_snomed,project_index_date, end_date
).date

dataset.temp_fatigue_date_primary=first_matching_event_clinical_snomed_in(
   fatigue_snomed, project_index_date, end_date
).date

# combine to find the earliest date of any symptom
dataset.first_hfsymptom.date = minimum_of(
dataset.temp_breathless_date_primary,
dataset.temp_oedema_date_primary,
dataset.temp_fatigue_date_primary
)
    '''
    Not using the following as not specific to HF. Using codelists based on previous studies (HF-related). A/w clincial input
    -  breathlesness: https://www.opencodelists.org/codelist/nhsd-primary-care-domain-refsets/breathlessness-codes/20241205/
    -  oedema: not currently available - need to create
    -  fatigue: https://www.opencodelists.org/codelist/opensafely/symptoms-fatigue/0e9ac677/
    '''

# testing if np test date (BNP or NT-proBNP) closely preceded or followed  hf-related symptoms

dataset.np_near_symptom =clinical_events.where(
    clinical_events.snomedct_code.is_in(NP_snomed)
).where(
    clinical_events.date.is_on_or_between(dataset.first_hfsymptom.date-30, dataset.first_hfsymptom.dat+90)
).exists_for_patient()


#DEFINE POPULATION (inclusion/exclusion criteria)
#note: this will be different for each WP

#registered for at least 1 year
#practice registration at minimum study end date - 1 year
#exclude historic registrations that ended before project_index_date

has_registration = practice_registrations.where(
        practice_registrations.start_date.is_on_or_before(end_date - years(1))
    ).except_where(
        practice_registrations.end_date.is_on_or_before(project_index_date)
    ).exists_for_patient()


# Need to define age at cohort entry date
dataset.define_population(
    has_registration
    & patients.sex.is_in(['male','female']) #known sex proxy for data quality
    & patients.date_of_birth.is_not_null() #known dob proxy for data quality
    & ~(patients.age_on(project_index_date) < 45) #remove pts < 45
    #& ~(patients.age_on(project_index_date) >= 110) #remove pts age 110+
    & (patients.is_alive_on(project_index_date)) #remove pts who died before start
    #& ((dataset.hf_diagnosis_date.is_null()) | (dataset.hf_diagnosis_date > project_index_date))
    & dataset.where(first_hfsymptom_date.is_not_null()
 )  

dataset.cohort_entry_date = dataset.first_symptom.date  

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

#quality assurance

dataset = add_quality_assurance(dataset, dataset.hf_diagnosis_date)

)




