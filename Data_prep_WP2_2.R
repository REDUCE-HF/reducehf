# Data_prep_WP2_2.R
# Script to prepare data for WP2_2 of the REDUCE HF project
# KS Taylor

rm(v)
rm(list=ls()) 

# Load packages
library(lubridate)
library(dplyr)

# Load data 
# This is dummy data and not including the final set of variables   
df <- read.csv("/workspace/test/tmp_dataset_wp2_2.csv.gz", header=TRUE)


# Data cleaning
# Currently not clear what will be done for the final dataset

# WP2.2 

# Patient index date (eligibility date) is the latest of date of age 45 years, study start date and registration date plus 1 year.

# Cohort entry date is date of first NP-pro test between patient index date and study end date




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

