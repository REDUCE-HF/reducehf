# Data_prep_WP2_1.R
# Script to prepare data for WP2_1 of the REDUCE HF project
# KS Taylor

rm(v)
rm(list=ls()) 

#install.packages("feather")

# Load packages
library(lubridate)
library(dplyr)
library(readr)
library(data.table)
library(feather)

# Load data 
# This is dummy data and not including the final set of variables   

#df <- read.csv("/workspace/test/tmp_dataset_wp2_2.csv.gz", header=TRUE)
# Reads dates as characters

df <- read_csv(here::here("test", "tmp_dataset_wp2_2.csv.gz"),show_col_types = FALSE)

# Data cleaning
# Currently not clear what will be done for the final dataset

# WP2.1 

# Patient index date (eligibility date) is the latest of date of age 45 years, study start date and registration date plus 1 year.

# Cohort entry date is date of first symptom between patient index date and study end date

#d1 <- subset(df, select=c("patient_id", "first_oedema_date_primary", "first_fatigue_date_primary",
#                           "first_breathless_date_primary","first_hfsymptom_date", "hf_diagnosis_date"))

# Rename date variables
df <- df %>% 
  rename(
    date_of_birth=dob
    )


# # Convert character dates to date format
# # Extracts all columns with "date" in their name    
# datevars <- names(df)[grep("date",names(df))]
# #   For each column, replaces the character date to a Date format   
# for (i in 1:length(datevars)){
#   df[,datevars[i]] <- ymd(df[,datevars[i]])
#   rm(i)
# }
# rm(datevars)

# Derive age
df$age<- as.numeric(difftime(df$patient_index_date,df$date_of_birth, units="days"))/365.25
summary(df$age)


# QUERY check height and weight for missing BMI

# Shorten names
df <- df %>% 
  rename(
    diag_date=hf_diagnosis_date,
    symp_date=first_hfsymptom_date,
    npdate=np_date,
    nt1date=nt1_date,
    oedema1date=first_oedema_date_primary,
    fatigue1date=first_fatigue_date_primary,
    breathless1date=first_breathless_date_primary,
    bmi=bmi_value,
    cholesterol=last_cholesterol_value,
    sbp=bp_value,
    copddate=copd_review_date,
    asthmadate=asthma_review_date
  )
    
# QUERY missing dbp, to load hba1c
# QUERY variables not clear for obesity, diabetes, COPD, hypertension, AF, IHD, CKD 
# 2 dates SUS and primary or multiple variables (COPD)       
# QUERY - Do I need to check if the dates are before HD diagnosis? (aren't they just for baseline)


# Create binary variables 
df$diag <- ifelse(is.na(df$diag_date),0,1)
df$symp <- ifelse(is.na(df$symp_date),0,1)
df$np <- ifelse(is.na(df$npdate),0,1)
df$symp1 <- ifelse(is.na(df$oedema1date),0,1)
df$symp2 <- ifelse(is.na(df$fatigue1date),0,1)
df$symp3 <- ifelse(is.na(df$breathless1date),0,1)
df$copd <- ifelse(is.na(df$copddate),0,1)
df$asthma <-  ifelse(is.na(df$asthmadate),0,1)

table(df$diag)
table(df$symp)
table(df$np)
table(df$symp1)
table(df$symp2)
table(df$symp3)
table(df$copd)
table(df$asthma)
# None with COPD

# Count symptoms
df$countsymp <- df$symp1+df$symp2+df$symp3
table(df$countsymp)
str(df$countsymp)
# QUERY - only had one symptom. Is that expected or are the data scrambled so can't tell?


# Timings of HF-related symptoms relative to HF diagnosis
# Symptom before
sum(df$symp_date<df$diag_date, na.rm=TRUE)
# Symptom at the time
sum(df$symp_date==df$diag_date, na.rm=TRUE)
# Symptom after
sum(df$symp_date>df$diag_date, na.rm=TRUE)
# QUERY - odd to have first HFsymptom after diagnosis of HF
# With symptoms and no diagnosis
sum(df$symp==1 & df$diag==0)

# Time between NP measurement diagnosis (assuming diagnosis follows first symptom)
df$np2diag <-as.numeric(df$diag_date-df$symp_date)
summary(df$np2diag)
#hist(df$np2diag)
# Negative values

# Set dates of intervals
df$Covid_start <- as.Date("2021-01-03")
# TBC
df$Covid_end <- as.Date("2023-01-04")

str(df$Covid_end)
str(df$symp_date)
table(df$symp_date)

# first HF symptom before covid pandemic   
df$before <- ifelse(
  is.na(df$symp_date), 0,
  ifelse(df$symp_date < df$Covid_start, 1, 0)
)
table(df$before)

# first HF symptom during covid pandemic   
df$during <- ifelse(
  is.na(df$symp_date), 0,
  ifelse(df$symp_date >= df$Covid_start & df$symp_date < df$Covid_end, 1, 0)
  )
table(df$during)

# first symptom after covid pandemic 
df$after <-ifelse(
  is.na(df$symp_date), 0,
  ifelse(df$symp_date >= df$Covid_end, 1, 0)
)
table(df$after)

check <- df[df$before==1,]
var <- c("symp_date", "Covid_start", "Covid_end")
check <- subset(check,select=var)
nrow(check)

check <- df[df$during==1,]
var <- c("symp_date", "Covid_start", "Covid_end")
check <- subset(check,select=var)
nrow(check)

check <- df[df$after==1,]
var <- c("symp_date", "Covid_end")
check <- subset(check,select=var)
nrow(check)

# Define cohort
# QUERY will Charlotte have applied all the exclusion criteria?




table(df$np_near_symptom)
str(df$np_near_symptom) 
df$near <- as.numeric(df$np_near_symptom)
table(df$near)
# QUERY Currently none have NP near symptom

# To complete
# May only select certain variables
# keep <- c(......)
# df <- df[,keep]

# Save file for analysis
# Using feather as it compresses and preserves column types
write_feather(df,"/workspace/test/file4analysisWP1.feather")
