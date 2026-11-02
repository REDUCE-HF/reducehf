

# Import libraries #
library('tidyverse')
library('lubridate')
library('arrow')
library('here')
library('reshape2')
library('dplyr')
library('fs')
library('gtsummary')
library('gt')


# For running locally only #
#setwd("C:/Users/aschaffer/OneDrive - Nexus365/Documents/GitHub/reducehf")
#getwd()

## Custom functions
source(here::here("analysis", "wp1", "utilities", "functions.R"))

wp1_main <- read_csv(here::here("output","wp1","wp1_main.csv"))

for_combos <- wp1_main %>%
  mutate(age_1 = (age_group == "40-54 years"),
         age_2 = (age_group == "55-64 years"),
         age_3 = (age_group == "65-74 years"),
         age_4 = (age_group == "75-84 years"),
         age_5 = (age_group == ">=85 years"),
         
         eth_white = (ethnicity_cat == "White"),
         eth_nonwhite = (ethnicity_cat %in% c("Black","Asian","Mixed","Other")),
         eth_black = (ethnicity_cat == "Black"),
         eth_asian = (ethnicity_cat == "Asian"),
         eth_mixed = (ethnicity_cat == "Mixed"),
         eth_other = (ethnicity_cat == "Other"),
         eth_missing = (ethnicity_cat == "Unknown"),
         
         bmi_obese = (bmi_cat == "Obese"),
         bmi_overweight = (bmi_cat == "Overweight"),
         bmi_normal = (bmi_cat == "Normal"),
         bmi_underweight = (bmi_cat == "Underweight"),
         bmi_missing = (bmi_cat == "Missing"),
         
         region_london = (region == "London"),
         region_neast = (region == "North East"),
         region_nwest = (region == "North West"),
         region_yorkshire = (region == "Yorkshire and the Humber"),
         region_seast = (region == "South East"),
         region_swest = (region == "South West"),
         region_wmidlands = (region == "West Midlands"),
         region_east = (region == "East"),
         region_emidlands = (region == "East Midlands"),
         
         male = (sex == "Male"), 
         
         smok_never = (smoking = "N"),
         smok_ever = (smoking = "E"),
         smok_curr = (smoking = "C"))
         
  

copd <- for_combos %>% subset(copd == TRUE)

combos <- for_combos %>%
  group_by(across(c(imd_quintile, rural, 
                    migrant, non_english_speaking, smi, 
                    substance_abuse, homeless,
                    learndisability, housebound, male,
                    hypertension, af, ihd, ckd, t2dm, 
                    age_1, age_2, age_3, age_4, age_5,
                    eth_white, eth_nonwhite, 
                    bmi_obese, bmi_overweight, bmi_underweight))) %>%
  summarise(pop = rounding(n()),
            pdays =  sum(person_days), 
            hf_emerg = rounding(sum(hf_diagnosis_type == "Emergency diagnosis", na.rm = TRUE)),
            .groups = "drop") %>%
  distinct() %>%
  subset(pop > 100)

write.csv(combos, here::here("output", "wp1", "wp1_combinations.csv"), row.names = FALSE)

