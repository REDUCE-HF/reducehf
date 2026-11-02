
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

# read in data with common variables
wp1_common <- read_csv(here::here("output", "dataset_wp1_common.csv.gz"))


####


# Main data file - i.e. index date is 1 Jan 2023
wp1_main <- merge.fn(2023) %>%
  clean.fn(as.Date("2023-01-01"), 3) %>%
  mutate(person_days = as.numeric(as.Date(patient_end_date) - as.Date(patient_index_date)),
    year = 2023)

write.csv(wp1_main, here::here("output", "wp1", "wp1_main.csv"), row.names = FALSE)


####

# Data file for time series analysis

wp1_2019 <- merge.fn(2019) %>%
  clean.fn(as.Date("2019-01-01"), 1) %>%
  mutate(year = 2019) 

wp1_2020 <- merge.fn(2020) %>%
  clean.fn(as.Date("2020-01-01"), 1) %>%
  mutate(year = 2020)

wp1_2021 <- merge.fn(2021) %>%
  clean.fn(as.Date("2021-01-01"), 1) %>%
  mutate(year = 2021)

wp1_2022 <- merge.fn(2022) %>%
  clean.fn(as.Date("2022-01-01"), 1) %>%
  mutate(year = 2022)

wp1_2023 <- merge.fn(2023) %>%
  clean.fn(as.Date("2023-01-01"), 1) %>%
  mutate(year = 2023)

wp1_2024 <- merge.fn(2024) %>%
  clean.fn(as.Date("2024-01-01"), 1) %>%
  mutate(year = 2024)

wp1_2025 <- merge.fn(2025) %>%
  clean.fn(as.Date("2025-01-01"), 1) %>%
  mutate(year = 2025)

wp1_ts_all <- rbind(wp1_2019, wp1_2020, wp1_2021, wp1_2022, wp1_2023, wp1_2024, wp1_2025) 

write.csv(wp1_ts_all, here::here("output", "wp1", "wp1_ts_all.csv"), row.names = FALSE)
