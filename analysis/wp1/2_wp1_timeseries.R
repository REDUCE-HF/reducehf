
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

dir_create(here::here("output", "wp1"), recurse = TRUE)
source(here::here("analysis", "wp1", "utilities", "functions.R"))


wp1_all <- read_csv(here::here("output","wp1","wp1_ts_all.csv"))

# Helper function to summarise HF data by grouping variables
summarise_hf <- function(data, ...) {
  group_vars <- enquos(...)
  
  data %>%
    group_by(year, !!!group_vars) %>%
    summarise(
      hf_emerg   = rounding(sum(hf_diagnosis_emerg    == TRUE, na.rm = TRUE)),
      hf_primary = rounding(sum(hf_diagnosis_primary  == TRUE, na.rm = TRUE)),
      hf_any     = rounding(sum(hf_diagnosis_any      == TRUE, na.rm = TRUE)),
      hf_ae      = rounding(sum(hf_diagnosis_ec       == TRUE, na.rm = TRUE)),
      hf_death   = rounding(sum(hf_death              == TRUE, na.rm = TRUE)),
      pop        = rounding(n()),
      .groups    = "drop"
    ) %>%
    select(year, !!!group_vars, hf_emerg, hf_primary, hf_any, pop) %>%
    mutate(
      hf_emerg_rate   = hf_emerg   / pop * 100000,
      hf_primary_rate = hf_primary / pop * 100000,
      hf_any_rate = hf_any / pop * 100000
    )
}

wp1_ts_all <- summarise_hf(wp1_all) %>%
  mutate(age_group = "All", sex = "All", ethnicity_cat = "All")
wp1_ts_age <- summarise_hf(wp1_all, age_group)%>%
  mutate(sex = "All", ethnicity_cat = "All")
wp1_ts_sex <- summarise_hf(wp1_all, sex)%>%
  mutate(age_group = "All", ethnicity_cat = "All")
wp1_ts_eth <- summarise_hf(wp1_all, ethnicity_cat)%>%
  mutate(age_group = "All", sex = "All")
wp1_ts_age_sex <- summarise_hf(wp1_all, age_group, sex)%>%
  mutate(ethnicity_cat = "All")
wp1_ts_age_sex_eth <- summarise_hf(wp1_all, age_group, sex, ethnicity_cat)
wp1_ts_eth_age <- summarise_hf(wp1_all, age_group, ethnicity_cat)%>%
  mutate(sex = "All")

wp1_ts <- bind_rows(wp1_ts_all, wp1_ts_age, wp1_ts_sex, wp1_ts_eth, wp1_ts_age_sex, wp1_ts_age_sex_eth,
                wp1_ts_eth_age)


write.csv(wp1_ts, here::here("output","wp1","wp1_timeseries.csv"))

