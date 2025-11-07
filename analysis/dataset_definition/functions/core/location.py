from functions.lib import *

###########################
# Location variables:
# based on of index date
##########################

def fn(dataset, index_date, suffix=''):

    # practice registration on index_date
    practice = practice_registrations.for_patient_on(index_date) 

    # add practice ID and registration date at index date
    dataset.add_column('practice_id' + suffix, practice.practice_pseudo_id)
    dataset.add_column('practice_registration_date' + suffix, practice.start_date)

    #add area level details at index date
    dataset.add_column('practice_stp' + suffix, practice.practice_stp)
    dataset.add_column('region' + suffix, practice.practice_nuts1_region_name)

    #add location details at index date
    location = addresses.for_patient_on(index_date)
    dataset.add_column('imd_quintile' + suffix, location.imd_quintile)
    dataset.add_column('rural_urban' + suffix, location.rural_urban_classification)
    dataset.add_column('msoa' + suffix, location.msoa_code)

    return dataset
