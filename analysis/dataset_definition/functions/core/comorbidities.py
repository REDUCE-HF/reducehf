from functions.lib import *
###############
# Comorbidities
###############

def fn(dataset, earliest_date, index_date):

    '''
    add comorbidities. 
    all variables derived as date of first event before index_date
    each WP needs to derived binary variables relative to index dates
    '''

    # Filter data for efficiency - extract everything before index date
    before_gp_events = filter_gp_events(earliest_date, index_date)
    before_apc_events = filter_apc_events(earliest_date, index_date)
    before_med_events = filter_med_events(earliest_date, index_date)

    ### Diabetes
    ## Type 1 Diabetes 
    # First date from primary+secondary, but also primary care date separately for diabetes algo
    dataset.tmp_t1dm_ctv3_date = first_matching_event_clinical_snomed(
        before_gp_events,
        diabetes_type1_snomed
        ).date
    dataset.t1dm_date = minimum_of(
        (first_matching_event_clinical_snomed(
            before_gp_events,
            diabetes_type1_snomed
            ).date),
        (first_matching_event_apc(
            before_apc_events,
            diabetes_type1_icd10
            ).admission_date)
        )

    # Count codes (individually and together, for diabetes algo)
    tmp_t1dm_ctv3_count = count_matching_event_clinical_snomed(
        before_gp_events,
        diabetes_type1_snomed
        )
    tmp_t1dm_hes_count = count_matching_event_apc(
        before_apc_events,
        diabetes_type1_icd10
        )
    
    dataset.tmp_t1dm_count_num = tmp_t1dm_ctv3_count + tmp_t1dm_hes_count

    ## Type 2 Diabetes
    # First date from primary+secondary, but also primary care date separately for diabetes algo)
    dataset.tmp_t2dm_ctv3_date = first_matching_event_clinical_snomed(
        before_gp_events,
        diabetes_type2_snomed
        ).date
    dataset.t2dm_date = minimum_of(
        first_matching_event_clinical_snomed(
            before_gp_events,
            diabetes_type2_snomed
            ).date,
        first_matching_event_apc(
            before_apc_events,
            diabetes_type2_icd10
            ).admission_date
        )
    
    # Count codes (individually and together, for diabetes algo)
    tmp_t2dm_ctv3_count = count_matching_event_clinical_snomed(
        before_gp_events,
        diabetes_type2_snomed
        )
    tmp_t2dm_hes_count = count_matching_event_apc(
        before_apc_events,
        diabetes_type2_icd10
        )
    
    dataset.tmp_t2dm_count_num = tmp_t2dm_ctv3_count + tmp_t2dm_hes_count

    ## Diabetes unspecified/other
    # First date
    dataset.otherdm_date = first_matching_event_clinical_snomed(
        before_gp_events,
        diabetes_other_snomed
        ).date
    # Count codes
    dataset.tmp_otherdm_count_num = count_matching_event_clinical_snomed(
        before_gp_events,
        diabetes_other_snomed
        )

    ## Gestational diabetes
    # First date from primary+secondary
    dataset.gestationaldm_date = minimum_of(
        first_matching_event_clinical_snomed(
            before_gp_events,
            diabetes_gestational_snomed
            ).date,
        first_matching_event_apc(
            before_apc_events,
            diabetes_gestational_icd10
            ).admission_date
        )

    ## Diabetes non-diagnostic codes
    # First date
    dataset.tmp_poccdm_date = first_matching_event_clinical_ctv3(
        before_gp_events,
        diabetes_nondiagnostic_ctv3
        ).date
    # Count codes
    dataset.tmp_poccdm_ctv3_count_num = count_matching_event_clinical_ctv3(
        before_gp_events,
        diabetes_nondiagnostic_ctv3
        )

    ### Other variables needed to define diabetes
    ## HbA1c
    # Maximum HbA1c measure (in the same period)
    dataset.tmp_max_hba1c_mmol_mol_num = (
        before_gp_events.where(
            before_gp_events.snomedct_code.is_in(hba1c_snomed))
        .numeric_value.maximum_for_patient()
        )
    
    # Date of first maximum HbA1c measure
    dataset.tmp_max_hba1c_date = ( 
        before_gp_events.where(
            before_gp_events.snomedct_code.is_in(hba1c_snomed))
        .where(before_gp_events.numeric_value == dataset.tmp_max_hba1c_mmol_mol_num)
        .sort_by(before_gp_events.date)
        .first_for_patient() 
        .date
        )

    ## Diabetes drugs
    # First dates
    dataset.tmp_insulin_dmd_date = first_matching_med_dmd(
        before_med_events,
        insulin_dmd
        ).date
    dataset.tmp_antidiabetic_drugs_dmd_date = first_matching_med_dmd(
        before_med_events,
        antidiabetic_drugs_dmd
        ).date
    dataset.tmp_nonmetform_drugs_dmd_date = first_matching_med_dmd(
        before_med_events,
        non_metformin_dmd
        ).date

    # Identify first date (in same period) that any diabetes medication was prescribed
    dataset.tmp_diabetes_medication_date = minimum_of(
        dataset.tmp_insulin_dmd_date, 
        dataset.tmp_antidiabetic_drugs_dmd_date
        )

    # Identify first date (in same period) that any diabetes diagnosis codes were recorded
    dataset.tmp_first_diabetes_diag_date = minimum_of(
        dataset.t1dm_date, 
        dataset.t2dm_date,
        dataset.otherdm_date,
        dataset.gestationaldm_date,
        dataset.tmp_poccdm_date,
        dataset.tmp_diabetes_medication_date,
        dataset.tmp_nonmetform_drugs_dmd_date
        )
    
    ### COPD
    '''
    Shall we just derive primary and sus dates ? 
    or take the earliest and tag them as tmp to remove them from 
    the dataset later ? 
    '''     
    dataset.tmp_copd_date_primary = first_matching_event_clinical_snomed(
        before_gp_events,
        copd_snomed
        ).date
    dataset.tmp_copd_date_sus = first_matching_event_apc(
        before_apc_events,
        copd_icd10
        ).admission_date
    # Combine to earliest date
    dataset.first_copd_date = minimum_of(
        dataset.tmp_copd_date_primary,
        dataset.tmp_copd_date_sus
        )

    ### Hypertension
    dataset.hypertension_date_primary = first_matching_event_clinical_snomed(
        before_gp_events,
        hypertension_snomed
        ).date
    dataset.hypertension_date_med = first_matching_med_dmd(
        before_med_events,
        hypertension_drugs_dmd
        ).date
    dataset.hypertension_date_sus = first_matching_event_apc(
        before_apc_events,
        hypertension_icd10
        ).admission_date
    #systolic BP* diastolic BP* will be defined in time dependent variables

    ### Atrial fibrillation
    dataset.af_date_primary = first_matching_event_clinical_snomed(
        before_gp_events,
        af_snomed
        ).date
    dataset.af_date_sus = first_matching_event_apc(
        before_apc_events,
        af_icd10
        ).admission_date

    ### Ischeamic heart disease
    dataset.ihd_date_primary = first_matching_event_clinical_snomed(
        before_gp_events,
        ihd_snomed
        ).date
    dataset.ihd_date_sus = first_matching_event_apc(
        before_apc_events,
        ihd_icd10
        ).admission_date

    ### CKD
    dataset.ckd_date_primary = first_matching_event_clinical_snomed(
        before_gp_events,
        ckd_snomed
        ).date
    dataset.ckd_date_sus = first_matching_event_apc(
        before_apc_events,
        ckd_icd10
        ).admission_date

    return dataset

