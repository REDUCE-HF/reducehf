############ THIS IS STILL A WORK IN PROGRESS ! ######################

################################################
# REDUCE-HF project
# Author: Andrea Schaffer
# Bennett Institute for Applied Data Science
# University of Oxford
################################################

# Import libraries #
library('tidyverse')
library('lubridate')
library('arrow')
library('here')
library('reshape2')
library('dplyr')
library('fs')

# For running locally only #
#setwd("C:/Users/aschaffer/OneDrive - Nexus365/Documents/GitHub/reducehf")
#getwd()


# Create directory
dir_create(here::here("output", "wp1", "processed"), showWarnings = FALSE, recurse = TRUE)
dir_create(here::here("analysis", "wp1", "processing"), showWarnings = FALSE, recurse = TRUE)


# Read in file with common variables
wp1_common <- read_csv(here::here("output","wp1","dataset_wp1_common.csv.gz")) 

# Function to merge with year-specific files
merge.fn <- function(year){
  read_csv(paste0(here::here("output","wp1",paste0("dataset_wp1_", year, ".csv.gz")))) %>%
    merge(wp1_common, by = "patient_id") %>%
    select(!death_date.y) %>%
    rename(death_date = death_date.x) %>%
    
    # Exclude if prior evidence of HF
    subset(is.na(hf_exclude_date) | (hf_exclude_date > patient_index_date))
}

# Function to clean data, create needed variables
clean.fn <- function(df){
  df %>%
    mutate(
          # HF outcome events - flag if within one year of patient index date
          hf_diagnosis_primary = ifelse(
            ((hf_diagnosis_primary_date >= patient_index_date) & 
             (hf_diagnosis_primary_date < patient_index_date + years(1))) %in% TRUE,
            "Yes", "No"),
           
           hf_diagnosis_apc = ifelse(
             ((hf_diagnosis_apc_date >= patient_index_date) & 
             (hf_diagnosis_apc_date < patient_index_date + years(1))) %in% TRUE,
             "Yes", "No"),
           
           hf_diagnosis_ec = ifelse(
             ((hf_diagnosis_ec_date >= patient_index_date) & 
             (hf_diagnosis_ec_date < patient_index_date + years(1))) %in% TRUE,
             "Yes", "No"),
           
           hf_death = ifelse(
             ((hf_death_date >= patient_index_date) & 
             (hf_death_date < patient_index_date + years(1))) %in% TRUE,
             "Yes", "No"),
           
           hf_diagnosis_emerg = ifelse(
             ((hf_diagnosis_emerg_date >= patient_index_date) & 
             (hf_diagnosis_emerg_date < patient_index_date + years(1))) %in% TRUE,
             "Yes", "No"),
           
           hf_diagnosis_any = ifelse(
             (hf_diagnosis_emerg == "Yes" | hf_diagnosis_primary == "Yes") %in% TRUE,
             "Yes", "No"),
           
           # Comorbidities - flag if within 5 years pre index date
           copd = ifelse(
             ((first_copd_date < patient_index_date) &
             (first_copd_date >= (patient_index_date - years(5)))) %in% TRUE,
             "Yes", "No"),
           
           hypertension = ifelse(
             ((hypertension_date_primary < patient_index_date &
                hypertension_date_primary >= (patient_index_date - years(5))) |
               (hypertension_date_sus < patient_index_date &
                  hypertension_date_sus >= (patient_index_date - years(5))) |
               (hypertension_date_med < patient_index_date &
                  (hypertension_date_med >= years(1)))) %in% TRUE,
             "Yes", "No"),
           
           af = ifelse(
             ((af_date_primary < patient_index_date &
               af_date_primary >= (patient_index_date - years(5))) |
             (af_date_sus < patient_index_date &
                af_date_sus >= (patient_index_date - years(5)))) %in% TRUE,
             "Yes", "No"),
          
           ihd = ifelse(
             ((ihd_date_primary < patient_index_date &
                ihd_date_primary >= (patient_index_date - years(5))) |
               (ihd_date_sus < patient_index_date &
                  ihd_date_sus >= (patient_index_date - years(5)))) %in% TRUE,
             "Yes", "No"),
          
           ckd = ifelse(
             ((ckd_date_primary < patient_index_date &
                ckd_date_primary >= (patient_index_date - years(5))) |
               (ckd_date_sus < patient_index_date &
                 ckd_date_sus >= (patient_index_date - years(5)))) %in% TRUE,
             "Yes", "No"),
          
           t2dm = ifelse(
             ((t2dm_date < patient_index_date &
                t2dm_date >= (patient_index_date - years(5))) &
               (cat_diabetes == "T2DM")) %in% TRUE,
             "Yes", "No"),
          
           t1dm = ifelse(
             ((t1dm_date < patient_index_date  &
                t1dm_date >= (patient_index_date - years(5))) &
               (cat_diabetes == "T1DM")) %in% TRUE,
             "Yes", "No"),
          
           learndis = ifelse(
             (learndis < patient_index_date & 
                      learndis >= (patient_index_date - years(5))) %in% TRUE,
             "Yes", "No"),
          
            non_english_speaking = ifelse(non_english_speaking %in% TRUE, "Yes", "No"),
          
          smi = ifelse(smi %in% TRUE, "Yes", "No"),
          
          substance_abuse = ifelse(substance_abuse %in% TRUE, "Yes", "No"),
      
          homeless = ifelse(homeless %in% TRUE, "Yes", "No"),
          
          housebound = ifelse(housebound %in% TRUE, "Yes", "No"), 
          
           # Age
           age =  as.period(interval(birth_date, patient_index_date))$year,
           age_group = case_when(
             40<=age & age<55 ~ "40-54 years",
             55<=age & age<65 ~ "55-64 years",
             65<=age & age<75 ~ "65-74 years",
             75<=age & age<85 ~ "75-84 years",
             85<=age ~ ">=85 years"
           ),
          
           # Patient end date - earliest of death, deregistration
           end_date = pmin(death_date, practice_deregistration_date, na.rm= TRUE),
           followup = as.numeric(end_date - patient_index_date)) %>%
    
    # Drop unneeded columns
  select(c(patient_id, death_date, practice_registration_date, region, imd_quintile,
           rural_urban, smoking, non_english_speaking, learndis, smi, substance_abuse,
           homeless, housebound, sex, patient_index_date, practice_deregistration_date, 
           hf_diagnosis_primary_date, hf_diagnosis_apc_date, hf_diagnosis_emerg_date,
           hf_death_date, hf_mi_diagnosis_apc_date, hf_diagnosis_date, ethnicity_cat,
           hf_diagnosis_primary, hf_diagnosis_emerg, hf_death, hf_diagnosis_any, copd,
           hypertension, af, ihd, ckd, t2dm, t1dm, age, age_group, end_date, followup)) 
  
}

# Merge year-specific files with file containing common variables and process
wp1_2019 <- merge.fn(2019) %>%
  clean.fn() %>%
  mutate(year = 2019)

wp1_2020 <- merge.fn(2020) %>%
  clean.fn() %>%
  mutate(year = 2020)

wp1_2021 <- merge.fn(2021) %>%
  clean.fn() %>%
  mutate(year = 2021)

wp1_2022 <- merge.fn(2022) %>%
  clean.fn() %>%
  mutate(year = 2022)

wp1_2023 <- merge.fn(2023) %>%
  clean.fn() %>%
  mutate(year = 2023)

wp1_2024 <- merge.fn(2024) %>%
  clean.fn() %>%
  mutate(year = 2024)

wp1_2025 <- merge.fn(2025) %>%
  clean.fn() %>%
  mutate(year = 2025)


wp1_all <- rbind(wp1_2019, wp1_2020, wp1_2021, wp1_2022, wp1_2023, wp1_2024, wp1_2025) 

write.csv(wp1_all, here::here("output", "wp1", "processed", "wp1_all.csv.gz"),
          row.names = FALSE)

