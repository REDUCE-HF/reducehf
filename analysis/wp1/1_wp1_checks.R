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
library('reshape2')
library('dplyr')
library('fs')
library('ggplot2')
library('here')

# Run the original checks for either dataset, saving outputs separately.
run_wp1_checks <- function(input_file, cohort) {
  check_dir <- here::here("output", "wp1", "checks", cohort)
  dir_create(check_dir, recurse = TRUE)
  dir_create(file.path(check_dir, "figures"), recurse = TRUE)

  # Read in cleaned data
  wp1_checks <- read_csv(input_file) %>%
    mutate(time_index_to_death = (death_date - patient_index_date),
           died_before_index = ifelse((death_date <= patient_index_date) %in% TRUE, "Yes", "No")) 

  # Preserve the factor conversion from wp1_checks.R, but only for columns present.
  factor_vars <- c("region", "imd_quintile", "rural", "smoking", "died_during_study",
                   "migrant", "non_english_speaking", "smi", "substance_abuse", "homeless",
                   "learndisability", "housebound", "sex", "hf_diagnosis_primary",
                   "hf_diagnosis_emerg", "hf_diagnosis_any", "ethnicity_cat", "copd",
                   "bmi_cat", "hypertension", "af", "ihd", "ckd", "t2dm", "age_group",
                   "bmi_missing")

  # Frequency distribution for categorical variables
  vars <- unique(c("sex", "region", "imd_quintile", "rural", "rural_urban", "smoking",
                   "migrant", "non_english_speaking", "smi", "substance_abuse", "homeless",
                   "ethnicity_cat", "copd", "hypertension", "af", "ihd", "ckd", "t2dm", "t1dm",
                   "age_group", "learndisability", "learndis", "housebound",
                   "died_during_study", "died_before_index", "bmi_missing", "bmi_cat"))
  vars <- intersect(vars, names(wp1_checks))
  
  categorical_freq <- wp1_checks %>%
    mutate(across(all_of(vars), as.character)) %>%
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

  write.csv(categorical_freq, file.path(check_dir, "check_categorical_dist.csv"))


  # Summary statistics/histograms for continuous variables
  is_continuous <- function(x) {
    (is.numeric(x) && length(unique(na.omit(x))) > 2) 
  }

  vars_to_summarise <- wp1_checks %>%
    select(where(is_continuous)) %>%
    select(-any_of(c("year", "patient_id"))) %>%
    names()

  if (length(vars_to_summarise) > 0) {
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

  write.csv(continuous_summ, file.path(check_dir, "check_summary_stats.csv"))

  # Histograms
  continuous_plot <- wp1_checks %>%
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

  ggsave(file.path(check_dir, "check_summary_stats.png"), plot = continuous_plot, units = "cm", 
         height = 30, width = 30)



  }

  # Summary statistics/histograms for dates
  dates_to_summarise <- wp1_checks %>%
    select(where(is.Date)) %>%
    names()

  if (length(dates_to_summarise) > 0) {
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

  write.csv(dates_summ, file.path(check_dir, "check_dates.csv"))

  # Histograms
  plots <- wp1_checks %>%
    select(year, all_of(dates_to_summarise)) %>%
    pivot_longer(
      cols = all_of(dates_to_summarise),
      names_to = "variable",
      values_to = "value"
    ) %>%
    subset(!is.na(value)) %>%
    split(.$variable) %>%
    lapply(function(d) {
      ggplot(d, aes(x = value)) +
        geom_histogram(bins = 30, colour = "white") +
        facet_wrap( ~ year, scales = "free_x", ncol = 4) +
        theme_minimal() +
        labs(
          x = NULL,
          y = "Count"
        )    
    })

  for (v in names(plots)) {
    filename <- paste0("plot_", v, ".png")
  
    ggsave(filename = file.path(check_dir, "figures", filename),
           plot = plots[[v]],
           width = 8, height = 4, units = "in")
  }
  }
  }



# Same checks on the main and yearly/time-series datasets.
run_wp1_checks(here::here("output", "wp1", "wp1_main.csv"), "main")
run_wp1_checks(here::here("output", "wp1", "wp1_ts_all.csv"), "ts")
