from functions.lib import *
######################
# Core variables:
# depend on index date
######################

def fn(dataset, index_date, suffix='', wp=None):

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
    dataset.sysbp_date = bp.date
    dataset.sysbp_value = bp.numeric_value

    # diastolic bp
    bp = last_matching_event_clinical_ranges_snomed_before(
        diastolic_bp, index_date
        )
    dataset.diasbp_date = bp.date
    dataset.diasbp_value = bp.numeric_value

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
