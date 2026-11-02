# Functions
rounding <- function(vars) {
  case_when(vars == 0 ~ 0,
            vars > 7 ~ round(vars / 5) * 5)
}


merge.fn <- function(year){
  read_csv(paste0("output/dataset_wp1_", year, ".csv.gz")) %>%
    merge(wp1_common, by = "patient_id") %>%
    select(-c(prostate_cancer, pregnancy, hrtcocp, tmp_copd_date_primary, tmp_copd_date_sus,
              otherdm_date, gestationaldm_date, 
              t1dm_date, practice_id, practice_stp, msoa, sysbp_date, sysbp_value,
              diasbp_date, diasbp_value, last_hdl_cholesterol_date, last_hdl_cholesterol_value,
              last_cholesterol_date, last_cholesterol_value, weight, weight_date,
              height, carehome_at_index, death_date.y, household_size)) %>%
    rename(death_date = death_date.x)
}

clean.fn <- function(df, start_date, num_years){
  df %>%
    mutate(patient_end_date = pmin(death_date, 
                                   practice_deregistration_date, 
                                   hf_diagnosis_primary_date,
                                   hf_diagnosis_emerg_date,
                                   as.Date("2026-01-01"), na.rm= TRUE)
           ) %>%
  #  subset(patient_index_date <= start_date & patient_end_date >= start_date) %>%
    mutate(
           copd = first_copd_date < start_date,
           hypertension = (
             (hypertension_date_primary < start_date) |
               (hypertension_date_sus < start_date) |
               ((hypertension_date_med < start_date) & 
                  (hypertension_date_med >= start_date - years(1)))
               ),
           af = (
             (af_date_primary < start_date) |
               (af_date_sus < start_date)
           ),
           ihd = (
             (ihd_date_primary < start_date) |
               (ihd_date_sus < start_date)
           ),
           ckd = (
             (ckd_date_primary < start_date) |
               (ckd_date_sus < start_date)
           ),
           t2dm = (
             (t2dm_date < start_date) &
               (cat_diabetes == "T2DM")
           ),
           age =  as.period(interval(birth_date, start_date))$year,
           age_group = case_when(
             40<=age & age<55 ~ "40-54 years",
             55<=age & age<65 ~ "55-64 years",
             65<=age & age<75 ~ "65-74 years",
             75<=age & age<85 ~ "75-84 years",
             85<=age ~ ">=85 years"
           ),
           learndisability = (
             (learndis < start_date)
           ),
           died_during_study = (
             (death_date > start_date) &
               (death_date <= start_date + years(num_years))
           ),
           bmi = as.numeric(
             ifelse((bmi_date < start_date) &
                    (bmi_date >= (start_date - years(2))), 
                    bmi_value, NA) 
           ),
           bmi_missing = ifelse(is.na(bmi), "Yes", "No"),
           bmi_cat =
             case_when(
               !is.na(bmi) & bmi >= 30 ~ "Obese",
               !is.na(bmi) & bmi >= 25 & bmi < 30 ~ "Overweight",
               !is.na(bmi) & bmi >= 20 & bmi < 25 ~ "Normal",
               !is.na(bmi) & bmi >= 10 & bmi < 20 ~ "Underweight",
               .default = "Missing"
             ),
           rural = (rural_urban >=5 & !is.na(rural_urban)),
           hf_diagnosis_primary = (hf_diagnosis_primary_date >= start_date) & 
             (hf_diagnosis_primary_date < start_date + years(num_years)),
           hf_diagnosis_apc = (hf_diagnosis_apc_date >= start_date) & 
             (hf_diagnosis_apc_date < start_date + years(num_years)),
           hf_diagnosis_ec = (hf_diagnosis_ec_date >= start_date) & 
             (hf_diagnosis_ec_date < start_date + years(num_years)),
           hf_death = (hf_death_date >= start_date) & 
             (hf_death_date < start_date + years(num_years)),
           hf_diagnosis_emerg = (hf_diagnosis_emerg_date >= start_date) & 
             (hf_diagnosis_emerg_date < start_date + years(num_years)),
           hf_diagnosis_any = (hf_diagnosis_emerg | hf_diagnosis_primary),
           
           hf_diagnosis_type = case_when(
             hf_diagnosis_emerg == TRUE ~ "Emergency diagnosis",
             hf_diagnosis_primary == TRUE ~ "Primary care diagnosis",
             .default = "No diagnosis"),
           
           hf_diagnosis_any_date = pmin(hf_diagnosis_primary_date, hf_diagnosis_emerg_date)
           ) %>%
    select(!c(hf_exclude_date, first_copd_date, hypertension_date_primary,
              hypertension_date_med, hypertension_date_sus, af_date_primary,
              af_date_sus, ihd_date_primary, ihd_date_sus, ckd_date_primary,
              ckd_date_sus, t2dm_date, cat_diabetes, bmi_date, obesity_primary_date,
              obesity_sus_date, learndis, bmi_value)) 
  
}
