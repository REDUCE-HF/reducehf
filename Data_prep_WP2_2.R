# Data_prep_WP2_2.R
# Script to prepare data for WP2_2 of the REDUCE HF project
# KS Taylor

rm(v)
rm(list=ls()) 

# Load packages
library(lubridate)
library(dplyr)
library(readr)

# Load data 
# This is dummy data and not including the final set of variables   
#df <- read.csv("/workspace/test/tmp_dataset_wp2_2.csv.gz", header=TRUE)

df <- read_csv(here::here("output", "tmp_dataset_wp2_2.csv.gz"),show_col_types = FALSE)
sum(is.na(df$nt1_result))

# Data cleaning
# Currently not clear what will be done for the final dataset

# WP2.2 

# patient_index_date (eligibility date) is the latest of date of age 45 years, study start date and registration date plus 1 year.

# nt1_date_ranges (cohort entry date) is the date of first NP-pro test between patient index date and study end date
# "range" refers to more efficient coding

# Additional exclusions for WP2_2

# NP testing before index date
sum(df$nt_pre_index==TRUE)
df <-df[df$nt_pre_index==FALSE,]
# 0
# QUERY - s/b NP not NTPro  
# Emailed charlotte 27 Nov

# HF diagnosis before cohort entry date
sum(!is.na(df$hf_diagnosis_date) & !is.na(df$nt1_date) & df$hf_diagnosis_date<df$nt1_date)
# 6
df <-df[!(!is.na(df$hf_diagnosis_date) & !is.na(df$nt1_date) & df$hf_diagnosis_date<df$nt1_date),]

# BNP test between the eligibility date and cohort entry
# QUERY - need to create another variable first_np so can exclude if BNP test between index date and cohort entry date (first NT prodate)  
# Emailed charlotte 27 Nov
# Would need to exclude if first np date was before nt1_date_ranges 


# Convert characters for missing values to NA - Check other script

df$nt1_date[df$nt1_date==""] <- NA
df$np_date[df$np_date==""] <- NA

table(df$echo_ref_near_symptom)
table(df$echo_done_near_symptom)
table(df$np_near_symptom)


# Check ranges
summary(df$nt1_result)
summary(df$np_result)
summary(df$age)


# Check ranges

# List variables
ls()
custom_glimpse <- function(df) {
  data.frame(
    col_name = colnames(df),
    col_index = 1:ncol(df),
    col_class = sapply(df, class),
    row.names = NULL
  )
}

custom_glimpse(df)


check <- subset(df, select=c("age", "nt1_result","bmi_value","weight", "height","last_cholesterol_value"))

tab <- sapply(check, function(x) sum(is.na(x)))
print(tab)
# QUERY - lots of missing data
check2 <- subset(df, select=c("age", "nt1_result","bmi_value","height","last_cholesterol_value"))

tab <- t(sapply(check2, function(x) c(Minimum=min(x, na.rm=TRUE), Maximum=max(x, na.rm=TRUE,sum(is.na(x))))))

print(tab)

summary(df$weight)
df$wt <- as.numeric(df$weight)
summary(df$wt)
# QUERY - all missing weight

hist(df$age, breaks=15, freq=TRUE)
hist(df$nt1_result, breaks=15, freq=TRUE)
hist(df$bmi_value, breaks=15, freq=TRUE)
hist(df$height, breaks=15, freq=TRUE)
hist(df$last_cholesterol_value, breaks=15, freq=TRUE)



# library(dplyr)
# library(tidyr)
# 
# vars <- c("age","nt1_result", "bmi_value")
# df %>%
#   summarise(across(any_of(vars), list(min = ~min(.x, na.rm = TRUE))))
# 
# df %>%
#   summarise(across(any_of(vars), list(max = ~max(.x, na.rm = TRUE))))


df %>%
  summarise(across(any_of(vars), list(min = ~min(.x, na.rm = TRUE),
                                      max = ~max(.x, na.rm = TRUE))))

