# Rate_WP2_1.R
# Script to plot rates of near NP testing for WP2_1 of the REDUCE HF project
# KS Taylor

rm(v)
rm(list=ls()) 

#install.packages("feather")

# Load packages
library(lubridate)
library(dplyr)
library(readr)
library(feather)
library(survival)   # survSplit
library(ggplot2)

# Load data 
# This is dummy data 

# df <- read_csv(here::here("test", "tmp_dataset_wp2_2.csv.gz"),show_col_types = FALSE)
# df <- read.csv("/workspace/test/tmp_dataset_wp2_2.csv.gz", header=TRUE)
# old datafiles


# Select dataset
# COVID
df <- read_feather(here::here("test", "file4analysisWP2_1_COVID.feather"))

# Post-COVID
# df <-.....  

# symp_date is cohort entry date
# np_near_symptom is binary, indicating NP test near HF symptom  
# np_near_symptom_first is the date
table(df$np_near_symptom)


# Temp - may change
study_start <- as.Date("2019-02-01")
study_end <- as.Date("2025-01-01")

# using patient eligibility date as near np date could be before first symptom date
df$start_date<-df$patient_index_date

df$event<-as.integer(df$np_near_symptom)
table(df$event)


# Check end_date (censor or event date) is after the start date
#isTRUE(!is.na(df$np_near_symptom_first) & df$np_near_symptom_first>=df$patient_index_date)
#temp<-df[, c("np_near_symptom_first","np_near_symptom", "patient_index_date")]
#sum(!is.na(df$np_near_symptom_first) & df$np_near_symptom_first>=df$patient_index_date)
sum(!is.na(df$np_near_symptom_first) & df$np_near_symptom_first>=study_start)

df <-df %>% mutate(end_date=pmax(np_near_symptom_first, study_start))

# Set censoring at study end
df <-df %>% mutate(end_date=pmin(end_date, study_end))

# Prepare numeric start/stop for survSplit (days since 1970-01-01)
# survSplit works with numeric times; convert back to Dates later

df <- df %>%
  mutate(
    start_num = as.numeric(start_date),  # days since 1970-01-01
    end_num   = as.numeric(end_date)
  )

# cut points = Jan 1 of each calendar year where you want splits
years <- 2019:2025
cut_points <- as.numeric(as.Date(paste0(years, "-01-01")))

split_df <- survSplit(
  Surv(start_num, end_num, event) ~ .,
  data = df,
  cut = cut_points,
  start = "tstart",
  end   = "tstop",
  episode = "interval_id"
)

# end is the event time variable in survSplit()
# convert tstart/tstop back to Dates and get the calendar year for the interval
split_df <- split_df %>%
  mutate(
    interval_start = as.Date(tstart, origin = "1970-01-01"),
    interval_end   = as.Date(tstop,  origin = "1970-01-01"),
    # assign interval to calendar year by the year in which the interval starts
    year = year(interval_start),
    #    # assign interval to calendar year by the year in which the event occurs
    #    year = year(interval_end),
    # person-time in years for the split interval 
    person_years = (tstop - tstart) / 365.25
  )

# Aggregate to calendar year: total cases and person-years
# (If individuals can have multiple events and you only want first, adjust before split)

annual <- split_df %>%
  group_by(year) %>%
  summarise(
    cases = sum(event, na.rm = TRUE),
    person_years = sum(person_years, na.rm = TRUE)
  ) %>%
  arrange(year)

# Compute rates per 100,000 and exact Poisson 95% CIs (poisson.test)
# poisson.test(x, T = exposure) returns conf.int on rate scale (rate per unit of exposure)
# multiply by 100000 to get per-100k
#-----------------------------------------
mult <- 100000
annual <- annual %>%
  rowwise() %>%
  mutate(
    rate = (cases / person_years) * mult,
    # poisson.test handles cases == 0 (gives lower=0)
    ci = list(poisson.test(cases, T = person_years)$conf.int),
    lower_ci = ci[[1]] * mult,
    upper_ci = ci[[2]] * mult
  ) %>%
  ungroup() %>%
  select(-ci)
# rowwise() treats each row as a group (necessary for poisson.test) and ungroup() drops the grouping
# there is a temporary column (ci) which is removed using select(-ci) 
print(annual)

#-----------------------------------------
# Plot: line + points + shaded ribbon (CI) + errorbars
#-----------------------------------------
p <- ggplot(annual, aes(x = year, y = rate)) +
  geom_line() +
  geom_point(size = 2) +
  geom_ribbon(aes(ymin = lower_ci, ymax = upper_ci), alpha = 0.18) +
  geom_errorbar(aes(ymin = lower_ci, ymax = upper_ci), width = 0.2, alpha = 0.6) +
  scale_x_continuous(breaks = annual$year) +
  labs(
    x = "Calendar year",
    y = paste0("Rate per ", format(mult, scientific=FALSE)),
    #y = paste0("Rate per 100000"),
    title = "Annual incidence rates with 95% Poisson CIs"
  ) +
  theme_minimal()

print(p)

