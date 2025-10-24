from functions.lib import *

###########################
# Location variables:
# based on of index date
##########################

def fn(dataset, index_date):

    # practice registration on index_date
    practice = (
        practice_registrations.where(
            practice_registrations.start_date.is_on_or_before(
                index_date
                )
            ).sort_by(practice_registrations.start_date)
        .last_for_patient()
        )

    # add practice ID and registration date at index date
    dataset.practice_id = practice.practice_pseudo_id
    dataset.practice_registration_date = practice.start_date

    #add area level details at patient_index
    dataset.practice_stp = practice.practice_stp
    dataset.region = practice.practice_nuts1_region_name

    #add location details at index date
    location = addresses.for_patient_on(index_date)
    dataset.imd_quintile = location.imd_quintile
    dataset.rural_urban = location.rural_urban_classification
    dataset.msoa = location.msoa_code

    return dataset
