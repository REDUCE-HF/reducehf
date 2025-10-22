from functions.lib import *
###############
# Comorbidities
###############

def fn(dataset, end_date):

    '''
    add comorbidities. 
    all variables derived as date of first event before end_date
    each WP needs to derived binary variables relative to index dates
    '''

    ### Diabetes
    ## Type 1 Diabetes 
    # First date from primary+secondary, but also primary care date separately for diabetes algo
    dataset.tmp_t1dm_ctv3_date = first_matching_event_clinical_ctv3_before(
        diabetes_type1_ctv3, 
        end_date
        ).date
    dataset.t1dm_date = minimum_of(
        (first_matching_event_clinical_ctv3_before(
                diabetes_type1_ctv3, 
                end_date
                ).date
            ),
        (first_matching_event_apc_before(
                diabetes_type1_icd10, 
                end_date
                ).admission_date
            )
        )

    # Count codes (individually and together, for diabetes algo)
    tmp_t1dm_ctv3_count = count_matching_event_clinical_ctv3_before(
        diabetes_type1_ctv3, 
        end_date
        )
    tmp_t1dm_hes_count = count_matching_event_apc_before(
        diabetes_type1_icd10, 
        end_date
        )
    
    dataset.tmp_t1dm_count_num = tmp_t1dm_ctv3_count + tmp_t1dm_hes_count

    ## Type 2 Diabetes
    # First date from primary+secondary, but also primary care date separately for diabetes algo)
    dataset.tmp_t2dm_ctv3_date = first_matching_event_clinical_ctv3_before(
        diabetes_type2_ctv3, 
        end_date
        ).date
    dataset.t2dm_date = minimum_of(
        (first_matching_event_clinical_ctv3_before(
                diabetes_type2_ctv3, 
                end_date
                ).date
            ),
        (first_matching_event_apc_before(
                diabetes_type2_icd10, 
                end_date
                ).admission_date
            )
        )
    # Count codes (individually and together, for diabetes algo)
    tmp_t2dm_ctv3_count = count_matching_event_clinical_ctv3_before(
        diabetes_type2_ctv3, 
        end_date
        )
    tmp_t2dm_hes_count = count_matching_event_apc_before(
        diabetes_type2_icd10, 
        end_date
        )
    
    dataset.tmp_t2dm_count_num = tmp_t2dm_ctv3_count + tmp_t2dm_hes_count

    ## Diabetes unspecified/other
    # First date
    dataset.otherdm_date = first_matching_event_clinical_ctv3_before(
        diabetes_other_ctv3, 
        end_date
        ).date
    # Count codes
    dataset.tmp_otherdm_count_num = count_matching_event_clinical_ctv3_before(
        diabetes_other_ctv3, 
        end_date
        )

    ## Gestational diabetes
    # First date from primary+secondary
    dataset.gestationaldm_date = minimum_of(
        (first_matching_event_clinical_ctv3_before(
                diabetes_gestational_ctv3, 
                end_date
                ).date
            ),
        (first_matching_event_apc_before(
                diabetes_gestational_icd10,
                end_date
                ).admission_date
            )
        )

    ## Diabetes diagnostic codes
    # First date
    dataset.tmp_poccdm_date = first_matching_event_clinical_ctv3_before(
        diabetes_diagnostic_ctv3, 
        end_date
        ).date
    # Count codes
    dataset.tmp_poccdm_ctv3_count_num = count_matching_event_clinical_ctv3_before(
        diabetes_diagnostic_ctv3, 
        end_date
        )

    ### Other variables needed to define diabetes
    ## HbA1c
    # Maximum HbA1c measure (in the same period)
    dataset.tmp_max_hba1c_mmol_mol_num = (
        clinical_events.where(
            clinical_events.snomedct_code.is_in(hba1c_snomed))
        .where(clinical_events.date.is_on_or_before(end_date))
        .numeric_value.maximum_for_patient()
        )
    
    # Date of first maximum HbA1c measure
    dataset.tmp_max_hba1c_date = ( 
        clinical_events.where(
            clinical_events.snomedct_code.is_in(hba1c_snomed))
        .where(clinical_events.date.is_on_or_before(end_date)) # this line of code probably not needed again
        .where(clinical_events.numeric_value == dataset.tmp_max_hba1c_mmol_mol_num)
        .sort_by(clinical_events.date)
        .first_for_patient() 
        .date
        )

    ## Diabetes drugs
    # First dates
    dataset.tmp_insulin_dmd_date = first_matching_med_dmd_before(
        insulin_dmd, end_date
        ).date
    dataset.tmp_antidiabetic_drugs_dmd_date = first_matching_med_dmd_before(
        antidiabetic_drugs_dmd, end_date
        ).date
    dataset.tmp_nonmetform_drugs_dmd_date = first_matching_med_dmd_before(
        non_metformin_dmd, end_date
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
    dataset.tmp_copd_date_primary = first_matching_event_clinical_ctv3_before(
        copd_ctv3, end_date
        ).date
    dataset.tmp_copd_date_sus = first_matching_event_apc_before(
        copd_icd10, end_date
        ).admission_date
    # Combine to earliest date
    dataset.first_copd_date = minimum_of(
        dataset.tmp_copd_date_primary,
        dataset.tmp_copd_date_sus
        )

    ### Hypertension
    dataset.hypertension_date_primary = first_matching_event_clinical_snomed_before(
        hypertension_snomed, end_date
        ).date
    dataset.hypertension_date_med = first_matching_med_dmd_before(
        hypertension_drugs_dmd, end_date
        ).date
    dataset.hypertension_date_sus = first_matching_event_apc_before(
        hypertension_icd10, end_date
        ).admission_date
    #systolic BP* diastolic BP* will be defined in time dependent variables

    ### Atrial fibrillation
    dataset.af_date_primary = first_matching_event_clinical_snomed_before(
        af_snomed, end_date
        ).date

    dataset.af_date_sus = first_matching_event_apc_before(
        af_icd10, end_date
        ).admission_date

    ### Ischeamic heart disease
    dataset.ihd_date_primary = first_matching_event_clinical_snomed_before(
        ihd_snomed, end_date
        ).date
    dataset.ih_date_sus = first_matching_event_apc_before(
        ihd_icd10, end_date
        ).admission_date

    ### CKD
    dataset.ckd_date_primary = first_matching_event_clinical_snomed_before(
        ckd_snomed, end_date
        ).date
    dataset.ckd_date_sus = first_matching_event_apc_before(
        ckd_icd10, end_date
        ).admission_date

    return dataset

