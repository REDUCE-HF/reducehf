from .lib import *

###########################
# Core variables:
# independent of index date
##########################

def core(dataset, start_date, end_date='2025-01-01'):

    '''
    core variables don't differ between WPs
    they depend on project_index_date only

    parameters:

    dataset: dataset object initialised using create_dataset()
    start_date: for our project, 01-01-2017
    end_date: project / follow-up end date
    '''
    dataset.sex = patients.sex
    dataset.dob = patients.date_of_birth
    

    # Ethnicity in 6 categories
    ethnicity_snomed = (
        clinical_events.where(clinical_events.snomedct_code.is_in(ethnicity_codes))
        .sort_by(clinical_events.date)
        .last_for_patient()
        .snomedct_code.to_category(ethnicity_codes)
        )

    ethnicity_sus = ethnicity_from_sus.code

    dataset.ethnicity_cat = case(
        when((ethnicity_snomed == "1") | 
            ((ethnicity_snomed.is_null()) & (ethnicity_sus.is_in(["A", "B", "C"])))
            ).then("White"),
        when((ethnicity_snomed == "2") | 
            ((ethnicity_snomed.is_null()) & (ethnicity_sus.is_in(["D", "E", "F", "G"])))
            ).then("Mixed"),
        when((ethnicity_snomed == "3") | 
            ((ethnicity_snomed.is_null()) & (ethnicity_sus.is_in(["H", "J", "K", "L"])))
            ).then("Asian"),
        when((ethnicity_snomed == "4") | 
            ((ethnicity_snomed.is_null()) & (ethnicity_sus.is_in(["M", "N", "P"])))
            ).then("Black"),
        when((ethnicity_snomed == "5") | 
            ((ethnicity_snomed.is_null()) & (ethnicity_sus.is_in(["R", "S"])))
            ).then("Other"),
        otherwise="Unknown", 
        )

    #earliest practice registration
    first_practice = (
        practice_registrations.where(
            practice_registrations.end_date.is_after(start_date))
        .sort_by(
            practice_registrations.start_date,
            practice_registrations.end_date,
            practice_registrations.practice_pseudo_id)
        .first_for_patient()
        )

    #patient index date latest of:
    # - project start
    # - practice registration + 1 year (to allow for coding of variables)
    # - 45th birthday

    dataset.patient_index_date = maximum_of(start_date,
        first_practice.start_date + years(1),
        dataset.dob + years(45))

    # practice registration on patient_index_date
    practice = (
        practice_registrations.where(
            practice_registrations.start_date.is_on_or_before(
                dataset.patient_index_date
                )
            ).sort_by(practice_registrations.start_date)
        .last_for_patient()
        )

    # add practice ID and registration date at patient_index
    dataset.practice_id = practice.practice_pseudo_id
    dataset.practice_registration_date = practice.start_date

    #add area level details at patient_index
    dataset.practice_stp = practice.practice_stp
    dataset.region = practice.practice_nuts1_region_name

    # add practice deregistration / end of follow-up in tpp
    last_practice = (
        practice_registrations.where(
            practice_registrations.end_date.is_after(start_date))
        .sort_by(
            practice_registrations.start_date,
            practice_registrations.end_date,
            practice_registrations.practice_pseudo_id)
        .last_for_patient()
    )
    dataset.practice_deregistration_date = last_practice.end_date

    #add location details at patient_index
    location = addresses.for_patient_on(dataset.patient_index_date)
    dataset.imd10 = location.imd_decile
    dataset.rural_urban = location.rural_urban_classification

    # date of death
    dataset.death_date = minimum_of(patients.date_of_death, ons_deaths.date)

    #Household size
    dataset.household_size = household_memberships_2020.household_size

    return dataset

######################
# Core variables:
# depend on index date
######################

def time_dependent(dataset, index_date, suffix='', wp=None):

    '''
     and core variables that depend on index_date
    and therefore differ between WPs
    variables to be added:
    -  smoking status
    -  BMI
    -  systolic BP*
    -  diastolic BP*
    -  total cholesterol*
    *(date of most recent test/reading prior to index date and value)

    '''

    # Smoking status
    # THIS COULD PROBABLY BE WRITTEN MORE EFFICIENTLY!
    last_smoking_former_date = (
        last_matching_event_clinical_snomed_before(smoking_former, index_date)
        ).date
    
    last_smoking_current_date = (
        last_matching_event_clinical_snomed_before(smoking_current, index_date)
        ).date
    
    last_smoking_current = (
        (last_smoking_current_date.is_not_null() 
            & last_smoking_former_date.is_not_null() 
            & (last_smoking_current_date > last_smoking_former_date)
            ) |
        (last_smoking_current_date.is_not_null() 
            & last_smoking_former_date.is_null()
            )
        )

    last_smoking_former = (
        (last_smoking_former_date.is_not_null() 
            & last_smoking_current_date.is_not_null() 
            & (last_smoking_former_date > last_smoking_current_date)
            ) | 
        (last_smoking_former_date.is_not_null() 
            & last_smoking_current_date.is_null()
            )
        )
    
    dataset.add_column('smoking' + suffix, case(
            when(last_smoking_current == True).then("S"),
            when(last_smoking_former == True).then("E"),
            otherwise="N"
            )
        )


    # systolic BP
    bp = last_matching_event_clinical_ranges_snomed_before(
        systolic_bp, index_date
        )
    dataset.add_column('bp_date' + suffix, bp.date)
    dataset.add_column('bp_value' + suffix, bp.numeric_value)


    # BMI
    bmi = last_matching_event_clinical_ranges_snomed_before(
        bmi_cod, index_date
        )
    dataset.add_column('bmi_date' + suffix, bmi.date)
    dataset.add_column('bmi_value' + suffix, bmi.numeric_value)

    # HDL cholesterol 
    hdl_cholesterol = last_matching_event_clinical_ranges_snomed_before(
        hdl_cholesterol_snomed, index_date 
        )
    
    dataset.add_column('last_hdl_cholesterol_date' + suffix, 
        hdl_cholesterol.date
        )
    dataset.add_column('last_hdl_cholesterol_value' + suffix,
         hdl_cholesterol.numeric_value
        )
    
    #Total cholesterol
    cholesterol = last_matching_event_clinical_ranges_snomed_before(
        cholesterol_snomed, index_date
        )

    dataset.add_column('last_cholesterol_date' + suffix, cholesterol.date)
    dataset.add_column('last_cholesterol_value' + suffix, cholesterol.numeric_value)

    # Obesity
    obesity_primary_date = last_matching_event_clinical_snomed_between(
        bmi_obesity_snomed, index_date - days(365), index_date
        ).date

    dataset.add_column('obesity_primary_date' + suffix, obesity_primary_date)

    obesity_sus_date = last_matching_event_apc_between(
        bmi_obesity_icd10, index_date - days(365), index_date
        ).admission_date

    dataset.add_column('obesity_sus_date' + suffix, obesity_sus_date)   

    # weight
    # Do we need to check icd10 codes ?
    weight = last_matching_event_clinical_snomed_between(
        weight_snomed, index_date - days(365), index_date
        ).numeric_value
    weight_date  = last_matching_event_clinical_snomed_between(
        weight_snomed, index_date - days(365), index_date
        ).date
  
    # height
    # Do we need to check icd10 codes ?
    height = last_matching_event_clinical_snomed_before (
        height_snomed, index_date
        ).numeric_value

    dataset.add_column('weight' + suffix, weight)
    dataset.add_column('weight_date' + suffix, weight_date)
    dataset.add_column('height' + suffix, height)

    # only needed for WP4 (?) -- CHECK
    if wp==4:

        # Hba1c latest for pcp-hf
        last_hba1c = last_matching_event_clinical_ranges_snomed_before(
            hba1c_snomed, index_date - years(1)
            )
        dataset.last_hba1c_value = last_hba1c.numeric_value
        dataset.last_hba1c_date = last_hba1c.date
    
   
        # latest hypertension medications date for pcp-hf
        dataset.last_hypertension_date_med = last_matching_med_dmd_before(
            hypertension_drugs_dmd, index_date - years(1)
            ).date
    
        # latest diabetes medications date for pcp-hf 
        last_insulin_dmd_date = last_matching_med_dmd_before(
            insulin_dmd, index_date - years(1)
            ).date
        last_antidiabetic_drugs_dmd_date = last_matching_med_dmd_before(
            antidiabetic_drugs_dmd, index_date - years(1)
            ).date
        last_nonmetform_drugs_dmd_date = last_matching_med_dmd_before(
            non_metformin_dmd, index_date - years(1)
            ).date

        # Identify last date  that any diabetes medication was prescribed
        dataset.last_diabetes_medication_date = maximum_of(
            last_insulin_dmd_date,
            last_antidiabetic_drugs_dmd_date,
            last_nonmetform_drugs_dmd_date
            )
    
    return dataset


####################
# Underserved groups
####################

  
def underserved(dataset, index_date, end_date, suffix='', iter=0):
    
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

##############
# HF diganosis
##############

def hf_exclusion(dataset, index_date):

    #any evidence of HF, not just diagnosis codes, before index date
    hf_exclude_primary = last_matching_event_clinical_snomed_before(
        hf_exclude, index_date
        ).date

    #same but for secondary care
    hf_exclude_apc = last_matching_event_apc_before(
        hf_icd10, index_date,
        only_prim_diagnoses=False
        ).admission_date

    hf_exclude_ec = last_matching_event_ec_before(
        hf_ecds, index_date
        ).arrival_date

    dataset.hf_exclude = minimum_of(
        hf_exclude_primary,
        hf_exclude_apc,
        hf_exclude_ec
        )

    return dataset

def hf_diagnosis(dataset, index_date):

    #primary care
    dataset.hf_diagnosis_primary_date = first_matching_event_clinical_snomed_after(
        hf_snomed, index_date
        ).date

    #secondary care - hospital admission (primary OR secondary), or A&E visit
    dataset.hf_diagnosis_apc_date = first_matching_event_apc_acute_after(
        hf_icd10, index_date, 
        only_prim_diagnoses=True
        ).admission_date
    
    dataset.hf_diagnosis_ec_date = first_matching_event_ec_after(
        hf_ecds, index_date
        ).arrival_date
    
    dataset.hf_diagnosis_secondary_date = minimum_of(
        dataset.hf_diagnosis_apc_date, 
        dataset.hf_diagnosis_ec_date
        )

    #either primary or secondary
    dataset.hf_diagnosis_date = minimum_of(
        dataset.hf_diagnosis_primary_date, 
        dataset.hf_diagnosis_secondary_date
        )

    #in same admission as MI
    mi_diagnosis_apc = apcs.where(
        apcs.admission_date.is_on_or_after(index_date)
        & apcs.admission_method.is_in(["21","2A","22","23","24","25","2D","28","2B"])
        & apcs.primary_diagnosis.is_in(mi_icd10)
        )
    
    dataset.hf_mi_diagnosis_apc_date = mi_diagnosis_apc.where(
        mi_diagnosis_apc.all_diagnoses.contains_any_of(hf_icd10)
        ).sort_by(mi_diagnosis_apc.admission_date).first_for_patient().admission_date

    return dataset

###############
# Comorbidities
###############

def comorbidities(dataset, end_date):

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


###################
# Quality assurance
###################

def quality_assurance(dataset, index_date):

    # Prostate cancer
    dataset.prostate_cancer = minimum_of(
        last_matching_event_clinical_snomed_before(
            prostate_cancer_snomed, index_date
            ).date ,
        last_matching_event_apc_before(
            prostate_cancer_icd10, index_date
            ).admission_date
        )

    # Pregnancy
    dataset.pregnancy = last_matching_event_clinical_snomed_before(
        pregnancy_snomed, index_date
        ).date


    # COCP or HRT medication
    dataset.hrtcocp = last_matching_med_dmd_before(
        cocp_dmd + hrt_dmd, index_date
        ).date

    return dataset

