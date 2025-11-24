from functions.lib import *
###################
# Quality assurance
###################

# Best to look over entire period - given this is about quality assurance, and not about defining study variables
def fn(dataset, earliest_date, end_date):

    #filter data - use placeholder start date to get all past events
    before_gp_events = filter_gp_events(earliest_date, end_date)
    before_apc_events = filter_apc_events(earliest_date, end_date)
    before_med_events = filter_med_events(earliest_date, end_date)

    # Prostate cancer
    dataset.prostate_cancer = minimum_of(
        last_matching_event_clinical_snomed(
            before_gp_events,
            prostate_cancer_snomed
            ).date,
        last_matching_event_apc(
            before_apc_events,
            prostate_cancer_icd10
            ).admission_date
        )

    # Pregnancy
    dataset.pregnancy = last_matching_event_clinical_snomed(
        before_gp_events,
        pregnancy_snomed
        ).date


    # COCP or HRT medication
    dataset.hrtcocp = last_matching_med_dmd(
        before_med_events,
        cocp_dmd + hrt_dmd
        ).date

    return dataset

