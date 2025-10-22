from functions.lib import *
####################
# Underserved groups
####################

  
def fn(dataset, index_date, end_date, suffix='', iter=0):
    
    #Care home status
    location = addresses.for_patient_on(index_date)
    
    #was address at patient index date a care home
    carehome_at_index_ = (
        location.care_home_is_potential_match |
        location.care_home_requires_nursing |
        location.care_home_does_not_require_nursing
        )
    dataset.add_column('carehome_at_index' + suffix, carehome_at_index_)
    
    if iter==0:
        # Migrant status
        dataset.migrant = last_matching_event_clinical_snomed_before(
            migrant, 
            index_date, 
            where=True
            ).exists_for_patient()

        # Non english speaking
        dataset.non_english_speaking = last_matching_event_clinical_snomed_before(
            non_english_speaking, 
            index_date, 
            where=True
            ).exists_for_patient()

    # Substance abuse
    substance_abuse_ = last_matching_event_clinical_snomed_between(
        substance_abuse, 
        index_date - years(1), 
        index_date, 
        where=True
        ).exists_for_patient()
    dataset.add_column('substance_abuse' + suffix, substance_abuse_)

    # Homeless
    homeless_ = last_matching_event_clinical_snomed_between(
        homeless, 
        index_date - years(1), 
        index_date, where=True
        ).exists_for_patient()
    dataset.add_column('homeless' + suffix, homeless_)

    # Housebound
    housebound_date = last_matching_event_clinical_snomed_between(
        housebound, 
        index_date - years(1), 
        index_date, 
        where=True
        ).date

    not_housebound_date = last_matching_event_clinical_snomed_between(
        no_longer_housebound, 
        index_date - years(1), 
        index_date, 
        where=True
        ).date

    housebound_ = (
        housebound_date.is_not_null() & 
        (housebound_date.is_after(
            not_housebound_date) | 
            not_housebound_date.is_null()
            )
        )
    dataset.add_column('housebound' + suffix, housebound_)

    return dataset
