from functions.lib import *


def demog(dataset, start_date, end_date='2025-02-01'):

    '''
    Purpose
    =======

    Add demographic variables.

    **Parameters**

        - ``dataset`` : dataset object initialised using ehrql.create_dataset()
        - `start_date` : str (e.g.'01-02-2019'), project start date
        - `end_date` : str, project / follow-up end date
    
    **Variables added**

        - ``sex`` : patient sex (male / female)
        - ``dob`` : patient date of birth 
        - ``ethnicity_cat`` : ethnicity category (white / mixed / asian / black / other / unknown)
        - ``patient_index_date`` : latest of project start, practice registration + 1 year, 45th birthday 
        - ``practice_deregistration_date`` : date patient is no longer registered in TPP
        - ``death_date`` : date of death
        - ``household_size`` : number of people patient lived with in 2022

    **Returns**

        - ``dataset`` : input dataset modified to include variables added 
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

    # date of death
    dataset.death_date = minimum_of(patients.date_of_death, ons_deaths.date)

    #Household size
    dataset.household_size = household_memberships_2020.household_size

    return dataset


def location(dataset, index_date, suffix=''):

    '''
    Purpose
    =======
    Add variables that depend on patient/practice location.

    **Parameters**

        - ``dataset`` : dataset object initialised using ehrql.create_dataset()
        - ``index_date`` : str, the date that a patient enters the cohort (defined in `demog`)

    **Variables added**

        - ``practice_id`` : unique identifier of practice where the patient registered at index date
        - ``practice_registration_date`` : date patient registered at ``practice_id``
        - ``practice_stp`` : sustainability and transformation partnership of ``practice_id``
        - ``region`` : NHS region of ``practice_id``
        - ``imd_quintile``: IMD quintile of patient's home address at index date
        - ``rural_urban`` : rural - urban classification of patient's home address at index date
        - ``msoa`` : middle super output area of patient's home address at index date 
    
    **Returns**

        - ``dataset`` : input dataset modified to include variables added
    '''


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


def time_dependent(dataset, index_date, suffix='', wp=None, earliest_date = None):

    '''
    Purpose
    =======
    Add variables that are time dependent. For these variables, we only 
    use EHR data for the 1 year prior to index_date.

    **Parameters**

        - ``dataset`` : dataset object initialised using ``ehrql.create_dataset()``
        - ``index_date`` : str, the date that a patient enters the cohort (defined in `demog`)

    **Variables added**

        - ``smoking`` : patient's smoking status. Categorical (S: current smoker, E: ex-smoker, N: never)
        - ``sysbp_date`` : date of most recent systolic blood pressure reading
        - ``sysbp_value`` : value of most recent systolic blood pressure reading
        - ``diasbp_date`` : date of most recent diastolic blood pressure reading
        - ``diasbp_value`` : value of most recent diastolic blood pressure reading
        - ``bmi_date`` : date of most recent BMI measurement
        - ``bmi_value``: value of most recent BMI measurement
        - ``last_hdl_cholesterol_date`` : date of most recent HDL cholesterol measurement
        - ``last_hdl_cholesterol_value``: value of most recent HDL cholesterol measurement
        - ``last_cholesterol_date`` : date of most recent total cholesterol measurement
        - ``last_cholesterol_value``: value of most recent total cholesterol measurement
        - ``obesity_primary_date`` : date of most recent coding of obesity in primary care
        - ``obesity_sus_date`` : date of most recent coding of obesity in secondary care
        - ``weight`` : most recent weight recorded
        - ``weight_date`` : date of most recent weight recording
        - ``height`` : most recent height recorded

    **Returns**

        - ``dataset`` : input dataset modified to include variables added
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

  
def underserved(dataset, earliest_date, index_date, end_date, suffix='', iter=0):

    '''
    Purpose
    =======
    Add variables to define underserved groups.

    **Parameters**

        - ``dataset`` : dataset object initialised using ``ehrql.create_dataset()``
        - `earliest_date` : str, the earliest date to look back in a patient's EHR data  
        - ``index_date`` : str, the date that a patient enters the cohort (defined in `demog`)
        - `end_date` : str, project / follow-up end date

    **Variables added**

        - ``carehome_at_index`` : whether patient's home address at index date was a care home
        - ``migrant`` : whether patient has migrant code recorded in GP record prior to index date
        - ``non_english_speaking`` : whether patient has non english speaking code recorded in GP record prior to index date
        - ``learndis`` : whether patient has learning disability recorded in GP record prior to index date
        - ``smi`` : whether patient has severe mental illness recorded in GP record prior to index date and it has not been recorded as in remission at index date
        - ``substance_abuse`` : whether patient has substance abuse recorded in GP record in the 12 months prior to index date
        - ``homeless`` : whether patient has homeless recorded in GP record in the 12 months prior to index date
        - ``housebound`` : whether patient has housebound recorded in GP record in the 12 months prior to index date

    **Returns**

        - ``dataset`` : input dataset modified to include variables added
    '''
    
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


def comorbidities(dataset, earliest_date, index_date):

    '''
    Purpose
    =======
    Add variables to define comorbidities.

    **Parameters**

        - ``dataset`` : dataset object initialised using ``ehrql.create_dataset()``
        - `earliest_date` : str, the earliest date to look back in a patient's EHR data
        - ``index_date`` : str, the date that a patient enters the cohort (defined in `demog`)

    **Variables added**

    complete

    **Returns**

        - ``dataset`` : input dataset modified to include variables added
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

    ## Diabetes diagnostic codes
    # First date
    dataset.tmp_poccdm_date = first_matching_event_clinical_snomed(
        before_gp_events,
        diabetes_diagnostic_snomed
        ).date
    # Count codes
    dataset.tmp_poccdm_ctv3_count_num = count_matching_event_clinical_snomed(
        before_gp_events,
        diabetes_diagnostic_snomed
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


def hf_diagnosis(dataset, index_date, end_date):

    '''
    Purpose
    =======

    Add variables to define new heart failure diagnosis after index_date.

    **Parameters**

        - ``dataset`` : dataset object initialised using ``ehrql.create_dataset()``
        - ``index_date`` : str, the date that a patient enters the cohort (defined in `demog`)
        - `end_date` : str, project / follow-up end date

    **Variables added**

        - ``hf_diagnosis_primary_date`` : date of first HF diagnosis in primary care after index_date
        - ``hf_diagnosis_apc_date`` : date of first hospital admission after index_date where HF was recorded as primary diagnosis
        - ``hf_diagnosis_ec_date`` : date of first ED attendance for HF after index_date
        - ``hf_death_date``: date of death where cause of death is HF
        - ``hf_diagnosis_emerg_date`` : date of emergency HF diagnosis (earliest of ``hf_diagnosis_apc_date``, ``hf_diagnosis_ec_date`` and ``hf_death_date``)
        - ``hf_mi_diagnosis_apc_date`` : date of first hospital admission where HF is secondary diagnosis to primary diagnosis of Myocardial Infarction
        - ``hf_diagnosis_date`` : date of HF diagnosis (earliest of ``hf_diagnosis_primary_date`` and ``hf_diagnosis_emerg_date``)

    **Returns**

        - ``dataset`` : input dataset modified to include variables added
    '''

    # Filter raw data to everything after index date
    after_gp_events = filter_gp_events(index_date, end_date)
    after_apc_events = filter_apc_events(index_date, end_date)
    after_ed_events = filter_ed_events(index_date, end_date)

    #primary care
    dataset.hf_diagnosis_primary_date = first_matching_event_clinical_snomed(after_gp_events, hf_snomed).date

    #secondary care - hospital admission (primary OR secondary), or A&E visit
    dataset.hf_diagnosis_apc_date = first_matching_event_apc_acute(
        after_apc_events,
        hf_icd10, 
        only_prim_diagnoses=True
        ).admission_date
    
    dataset.hf_diagnosis_ec_date = first_matching_event_ec(
        after_ed_events,
        hf_ecds
        ).arrival_date
    
    #as cause of death
    dataset.hf_death_date = when(ons_deaths.cause_of_death_is_in(hf_icd10)).then(ons_deaths.date).otherwise(None)

    #earliest date of "emergency" HF diagnosis
    dataset.hf_diagnosis_emerg_date = minimum_of(
        dataset.hf_diagnosis_apc_date, 
        dataset.hf_diagnosis_ec_date,
        dataset.hf_death_date
        )

    #sensitivity analysis - in same admission as MI
    mi_diagnosis_apc = after_apc_events.where(
        after_apc_events.admission_method.is_in(["21","2A","22","23","24","25","2D","28","2B"])
        & after_apc_events.primary_diagnosis.is_in(mi_icd10)
        )
    
    dataset.hf_mi_diagnosis_apc_date = mi_diagnosis_apc.where(
        mi_diagnosis_apc.all_diagnoses.contains_any_of(hf_icd10)
        ).sort_by(mi_diagnosis_apc.admission_date).first_for_patient().admission_date
    
    dataset.hf_diagnosis_date = minimum_of(
        dataset.hf_diagnosis_primary_date,
        dataset.hf_diagnosis_emerg_date
    )
    
    return dataset


def hf_exclude(dataset, earliest_date, index_date):

    '''
    Purpose
    =======
    Add variables to define pre-existing heart failure (heart failure before index_date).

    **Parameters**

        - ``dataset`` : dataset object initialised using ``ehrql.create_dataset()``
        - `earliest_date` : str, the earliest date to look back in a patient's EHR data
        - ``index_date`` : str, the date that a patient enters the cohort (defined in `demog`)

    **Variables added**

        - ``hf_exclude_primary`` : date of most recent HF diagnosis in primary care prior to index_date
        - ``hf_exclude_apc`` : date of most recent hospital admission prior to index_date where HF was recorded as primary diagnosis
        - ``hf_exclude_ec`` : date of most recent ED attendance for HF prior to index_date
        - ``hf_exclude_date`` : date of HF diagnosis (earliest of ``hf_exclude_primary``, ``hf_exclude_apc`` and ``hf_exclude_ec``)

    **Returns**

        - ``dataset`` : input dataset modified to include variables added
    '''


    #filter data - use placeholder start date to get all past events
    before_gp_events = filter_gp_events(earliest_date, index_date)
    before_apc_events = filter_apc_events(earliest_date, index_date)
    before_ed_events = filter_ed_events(earliest_date, index_date)

    #any evidence of HF, not just diagnosis codes, before index date
    hf_exclude_primary = last_matching_event_clinical_snomed(
        before_gp_events, hf_exclude_
        ).date

    #same but for secondary care
    hf_exclude_apc = last_matching_event_apc(
        before_apc_events,
        hf_icd10, 
        only_prim_diagnoses=False
        ).admission_date

    hf_exclude_ec = last_matching_event_ec(
        before_ed_events, hf_ecds
        ).arrival_date

    dataset.hf_exclude_date = minimum_of(
        hf_exclude_primary,
        hf_exclude_apc,
        hf_exclude_ec
        )

    return dataset


def quality_assurance(dataset, earliest_date, end_date):

    '''
    Purpose
    =======
    Add variables needed for quality assurance.

    **Parameters**

        - ``dataset`` : dataset object initialised using ``ehrql.create_dataset()``
        - `earliest_date` : str, the earliest date to look back in a patient's EHR data
        - `end_date` : str, project / follow-up end date

    **Variables added**

        - ``prostate_cancer`` : earliest date prostate cancer is recorded
        - ``pregnancy`` : date of most recent recording of pregnancy
        - ``hrtcocp`` : date of most recent prescription for HRT or combined oral contraception

    **Returns**

        - ``dataset`` : input dataset modified to include variables added
    '''


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

