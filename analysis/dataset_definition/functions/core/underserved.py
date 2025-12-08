from functions.lib import *
####################
# Underserved groups
####################

  
def fn(dataset, earliest_date, index_date, end_date, suffix='', iter=0):
    
    gp_events = filter_gp_events(earliest_date, index_date)

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
        dataset.migrant = last_matching_event_clinical_snomed(
            gp_events,
            migrant,
            where=True
            ).exists_for_patient()

        # Non english speaking
        dataset.non_english_speaking = last_matching_event_clinical_snomed(
            gp_events,
            non_english_speaking,
            where=True
            ).exists_for_patient()

        #learning disability
        dataset.learndis = last_matching_event_clinical_snomed(
            gp_events,
            learndis_primis
            ).date
    

    #severe mental illness
    smi_code = last_matching_event_clinical_snomed(
            gp_events,
            sev_mental_primis
            ).date

    smi_code_remission = last_matching_event_clinical_snomed(
            gp_events,
            smhres_primis 
            ).date

    smi_ = (
        (smi_code.is_not_null() & smi_code_remission.is_before(smi_code)) |
        (smi_code.is_not_null() & smi_code_remission.is_null())
        )
    dataset.add_column('smi' + suffix, smi_)

    # Records from one year before index only
    gp_events_1yr = gp_events.where(
        gp_events.date.is_on_or_between(
            index_date - years(1), index_date
            )
        )

    # Substance abuse
    substance_abuse_ = last_matching_event_clinical_snomed(
        gp_events_1yr,
        substance_abuse, 
        where=True
        ).exists_for_patient()
    dataset.add_column('substance_abuse' + suffix, substance_abuse_)

    # Homeless
    homeless_ = last_matching_event_clinical_snomed(
        gp_events_1yr,
        homeless, 
        where=True
        ).exists_for_patient()
    dataset.add_column('homeless' + suffix, homeless_)

    # Housebound
    housebound_date = last_matching_event_clinical_snomed(
        gp_events_1yr,
        housebound, 
        where=True
        ).date

    not_housebound_date = last_matching_event_clinical_snomed(
        gp_events_1yr,
        no_longer_housebound, 
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
