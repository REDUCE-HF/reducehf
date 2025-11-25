from functions.lib import *
######################
# Core variables:
# depend on index date
######################

def fn(dataset, index_date, suffix='', wp=None, earliest_date = None):

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

    # Filter raw data to everything 1 year before index date (can be changed if necessary)
    gp_events = filter_gp_events(index_date - years(1), index_date)
    apc_events = filter_apc_events(index_date - years(1), index_date)
    med_events = filter_med_events(index_date - years(1), index_date)
    
    # Smoking status
    # two year lookback - can be changed
    last_smoking_former_date = last_matching_event_clinical_snomed(
        gp_events,
        smoking_former
        ).date

    last_smoking_current_date = last_matching_event_clinical_snomed(
        gp_events,
        smoking_current
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
    sysbp = last_matching_event_clinical_snomed(
        gp_events,
        systolic_bp)

    dataset.add_column('sysbp_date' + suffix, sysbp.date)
    dataset.add_column('sysbp_value' + suffix, sysbp.numeric_value)

    # diastolic bp
    diasbp = last_matching_event_clinical_snomed(
        gp_events,
        diastolic_bp)
    
    dataset.add_column('diasbp_date' + suffix, diasbp.date)
    dataset.add_column('diasbp_value' + suffix, diasbp.numeric_value)

    # BMI
    bmi = last_matching_event_clinical_snomed(
        gp_events, 
        bmi_cod)

    dataset.add_column('bmi_date' + suffix, bmi.date)
    dataset.add_column('bmi_value' + suffix, bmi.numeric_value)

    # HDL cholesterol 
    hdl_cholesterol = last_matching_event_clinical_snomed(
        gp_events,
        hdl_cholesterol_snomed)
    
    dataset.add_column('last_hdl_cholesterol_date' + suffix, 
        hdl_cholesterol.date
        )
    dataset.add_column('last_hdl_cholesterol_value' + suffix,
         hdl_cholesterol.numeric_value
        )
    
    #Total cholesterol
    cholesterol = last_matching_event_clinical_snomed(
        gp_events,
        cholesterol_snomed)

    dataset.add_column('last_cholesterol_date' + suffix, cholesterol.date)
    dataset.add_column('last_cholesterol_value' + suffix, cholesterol.numeric_value)

    # Obesity
    obesity_primary_date = last_matching_event_clinical_snomed(
        gp_events,
        bmi_obesity_snomed).date

    dataset.add_column('obesity_primary_date' + suffix, obesity_primary_date)

    obesity_sus_date = last_matching_event_apc(
        apc_events,
        bmi_obesity_icd10 
        ).admission_date

    dataset.add_column('obesity_sus_date' + suffix, obesity_sus_date)   

    # weight
    # Do we need to check icd10 codes ? 
    # There are ICD codes for obesity, but not for height/weight/BMI value
    weight = last_matching_event_clinical_snomed(
        gp_events,
        weight_snomed
        ).numeric_value
    weight_date  = last_matching_event_clinical_snomed(
        gp_events,
        weight_snomed
        ).date
  
    # height
    # Do we need to check icd10 codes ? No
    height = last_matching_event_clinical_snomed(
        gp_events,
        height_snomed
        ).numeric_value

    dataset.add_column('weight' + suffix, weight)
    dataset.add_column('weight_date' + suffix, weight_date)
    dataset.add_column('height' + suffix, height)

    # only needed for WP4 (?) -- CHECK
    if wp==4:

        # Filter raw data 
        gp_events_2 = filter_gp_events(earliest_date, index_date - years(1))
        med_events_2 = filter_med_events(earliest_date, index_date - years(1))

        # Hba1c latest for pcp-hf
        last_hba1c = last_matching_event_clinical_snomed(
            gp_events_2,
            hba1c_snomed)
        dataset.last_hba1c_value = last_hba1c.numeric_value
        dataset.last_hba1c_date = last_hba1c.date

        # latest hypertension medications date for pcp-hf
        dataset.last_hypertension_date_med = last_matching_med_dmd(
            med_events_2,
            hypertension_drugs_dmd
            ).date
    
        # latest diabetes medications date for pcp-hf 
        last_insulin_dmd_date = last_matching_med_dmd(
            med_events_2,
            insulin_dmd
            ).date
        last_antidiabetic_drugs_dmd_date = last_matching_med_dmd(
            med_events_2,
            antidiabetic_drugs_dmd
            ).date
        last_nonmetform_drugs_dmd_date = last_matching_med_dmd(
            med_events_2,
            non_metformin_dmd
            ).date

        # Identify last date  that any diabetes medication was prescribed
        dataset.last_diabetes_medication_date = maximum_of(
            last_insulin_dmd_date,
            last_antidiabetic_drugs_dmd_date,
            last_nonmetform_drugs_dmd_date
            )
    
    return dataset
