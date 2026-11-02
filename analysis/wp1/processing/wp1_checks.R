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
library('ggplot2')

# For running locally only #
#setwd("C:/Users/aschaffer/OneDrive - Nexus365/Documents/GitHub/reducehf")
#getwd()


# Create directory
dir_create(here::here("output", "wp1", "processed"), showWarnings = FALSE, recurse = TRUE)
dir_create(here::here("analysis", "wp1", "processing"), showWarnings = FALSE, recurse = TRUE)
dir_create(here::here("output", "wp1", "checks"), showWarnings = FALSE, recurse = TRUE)

# Read in cleaned data
wp1_checks <- read_csv(here::here("output","wp1","processed","wp1_all.csv.gz")) %>%
  mutate(time_index_to_death = (death_date - patient_index_date),
         died_before_index = ifelse((death_date <= patient_index_date) %in% TRUE, "Yes", "No"),
         rural_urban = as.character(rural_urban))
        

# Frequency distribution for caategorical variables
vars <- c("sex", "age_group", "region", "imd_quintile", "rural_urban", "smoking",
          "non_english_speaking", "learndis", "smi", "substance_abuse", "homeless",
          "housebound", "hypertension", "af", "ihd", "ckd", "t2dm", "t1dm", 
          "age_group","died_before_index")

categorical_freq <- wp1_checks %>%
  pivot_longer(all_of(vars), names_to = "variable", values_to = "value") %>%
  count(year, variable, value, name = "n") %>%
  group_by(year, variable) %>%
  mutate(pcent = 100 * n / sum(n)) %>%
  ungroup() %>%
  pivot_wider(
    names_from  = year,
    values_from = c(n, pcent),
    names_glue  = "{.value}_{year}"
  )

write.csv(categorical_freq, here::here("output", "wp1", "checks", "check_categorical_dist.csv"))


# Summary statistics/histograms for continuous variables
is_continuous <- function(x) {
  (is.numeric(x) && length(unique(na.omit(x))) > 2) 
}

vars_to_summarise <- wp1_checks %>%
  select(where(is_continuous)) %>%
  select(!c(patient_id, year)) %>%
  names()

continuous_summ <- wp1_checks %>%
  select(year, all_of(vars_to_summarise)) %>%
  group_by(year) %>%
  summarise(
    across(
      all_of(vars_to_summarise),
      list(
        min = ~ min(.x, na.rm = TRUE),
        p10 = ~ quantile(.x, 0.10, na.rm = TRUE),
        p25 = ~ quantile(.x, 0.25, na.rm = TRUE),
        p50 = ~ quantile(.x, 0.50, na.rm = TRUE),
        p75 = ~ quantile(.x, 0.75, na.rm = TRUE),
        p90 = ~ quantile(.x, 0.90, na.rm = TRUE),
        max = ~ max(.x, na.rm = TRUE)
      ),
      .names = "{.col}__{.fn}"
    ),
    .groups = "drop"
  ) %>%
  pivot_longer(
    cols = -year,
    names_to = c("variable", "stat"),
    names_sep = "__",
    values_to = "value"
  ) %>%
  pivot_wider(
    id_cols = variable,
    names_from = c(year, stat),
    values_from = value,
    names_glue = "{stat}_{year}"
  ) %>%
  arrange(variable)

write.csv(continuous_summ, here::here("output", "wp1", "checks", "check_summary_stats.csv"))

# Histograms
wp1_checks %>%
  select(year, all_of(vars_to_summarise)) %>%
  pivot_longer(
    cols = all_of(vars_to_summarise),
    names_to = "variable",
    values_to = "value"
  ) %>%
  ggplot(aes(x = value)) +
  geom_histogram(bins = 30, colour = "white") +
  facet_grid(variable ~ year, scales = "free_x") +
  theme_minimal() +
  labs(
    x = NULL,
    y = "Count"
  )

ggsave(here::here("output", "wp1", "checks", "check_summary_stats.png"), units = "cm", 
       height = 30, width = 30)



# Summary statistics/histograms for dates
dates_to_summarise <- wp1_checks %>%
  select(where(is.Date)) %>%
  names()

dates_summ <- wp1_checks %>%
  select(year, all_of(dates_to_summarise)) %>%
  group_by(year) %>%
  summarise(
    across(
      all_of(dates_to_summarise),
      list(
        min = ~ min(.x, na.rm = TRUE),
        max = ~ max(.x, na.rm = TRUE)
      ),
      .names = "{.col}__{.fn}"
    ),
    .groups = "drop"
  ) %>%
  pivot_longer(
    cols = -year,
    names_to = c("variable", "stat"),
    names_sep = "__",
    values_to = "value"
  ) %>%
  pivot_wider(
    id_cols = variable,
    names_from = c(year, stat),
    values_from = value,
    names_glue = "{stat}_{year}"
  ) %>%
  arrange(variable)

write.csv(dates_summ, here::here("output", "wp1", "checks", "check_dates.csv"))

# Histograms
wp1_checks %>%
  select(year, all_of(dates_to_summarise)) %>%
  pivot_longer(
    cols = all_of(dates_to_summarise),
    names_to = "variable",
    values_to = "value"
  ) %>%
  ggplot(aes(x = value)) +
  geom_histogram(bins = 30, colour = "white") +
  facet_grid(variable ~ year, scales = "free_x") +
  theme_minimal() +
  labs(
    x = NULL,
    y = "Count"
  )

ggsave(here::here("output", "wp1", "checks", "check_dates.png"), units = "cm", 
       height = 30, width = 30)