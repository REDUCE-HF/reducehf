# Data_prep_WP2_2.R
# Script to prepare data for WP2_2 of the REDUCE HF project
# KS Taylor

rm(v)
rm(list=ls()) 

# Load packages
library(lubridate)
library(dplyr)
library(readr)
library(feather)

# Load data 
# This is dummy data and not including the final set of variables   
#df <- read.csv("/workspace/test/tmp_dataset_wp2_2.csv.gz", header=TRUE)
# old datafile

# Select dataset
# COVID
df <- read_csv(here::here("output", "tmp_dataset_wp2_2.csv.gz"),show_col_types = FALSE)
# Post-COVID
# df <-.....    

# TEMP CODE - FOR DUMMY DATASET ONLY ###########################################
set.seed(123)
n <- nrow(df)

summary(df$bmi_value)
df$bmi_value <- ifelse(
  runif(n)<0.2,
  NA,
  runif(n, min=18, max=35)
)
summary(df$bmi_value)

summary(df$weight)
df$weight <- runif(n, min=45, max=80)
summary(df$weight)

summary(df$height)
df$height <- runif(n, min=1.45, max=1.95)
summary(df$height)

summary(df$last_cholesterol_value)
df$last_cholesterol_value <- ifelse(
  runif(n)<0.1,
  NA,
  runif(n, min=1, max=10)
)
summary(df$last_cholesterol_value)

summary(df$diasbp_value)

df$diasbp_value<-ifelse(
  runif(n)<0.05,
  NA,
  runif(n, min=60, max=140)
)

summary(df$sysbp_value)

df$sysbp_value<-ifelse(
  runif(n)<0.05,
  NA,
  runif(n, min=100, max=145)
)

df$obesity_sus_date <- as.Date("2019-03-30")
df$obesity_primary_date <- as.Date("2019-01-30")
# approx 50% missing
df$obesity_sus_date[runif(n)<0.5] <- NA
df$obesity_primary_date[runif(n)<0.5] <- NA

df$first_copd_date <- as.Date("2019-03-30")
# approx 40% missing
df$first_copd_date[runif(n)<0.4] <- NA

nrow(df)

df2 <- df
df3 <- df
df4 <- df
df5 <- df
df6 <- df
df7 <- df

df <- bind_rows(df, df2, df3, df4, df5, df6, df7)
nrow(df)
df8 <- df
df8$sex <- "female"
df <- bind_rows(df,df8)


# END OF TEMP CODE #############################################################




# Start date and end dates define the population - applied by Charlotte 
# COVID start date 1/1/20, end date 31/3/24  
# Post-COVID start date 1/4/24, end date 1/4/27 (currently set at 1/5/25) 
# Starts one year after 1/4/23 to allow for recovery from pandemic. 
# QUERY - reference for 1/4/23
df$Covid_start <- as.Date("2020-01-01")
df$Covid_end <- as.Date("2024-03-31")
# Dates TBC

sum(is.na(df$nt1_result))
# All have NP testing

# Data cleaning
# Currently not clear what will be done for the final dataset

# patient_index_date (eligibility date) is the latest of date of age 45 years, study start date and registration date plus 1 year.

# nt1_date_ranges (cohort entry date) is the date of first NP-pro test between patient index date and study end date
# "range" refers to more efficient coding

# Additional exclusions for WP2_2

# NP testing before patient_index_date
sum(df$np_pre_index==TRUE)
df <-df[df$np_pre_index==FALSE,]
# 0

# HF diagnosis before cohort entry date
sum(!is.na(df$hf_diagnosis_date) & !is.na(df$nt1_date) & df$hf_diagnosis_date<df$nt1_date)
# 5
df <-df[!(!is.na(df$hf_diagnosis_date) & !is.na(df$nt1_date) & df$hf_diagnosis_date<df$nt1_date),]

# BNP test between the eligibility date and cohort entry
sum(!is.na(df$nt1_date) & !is.na(df$np_date) & df$np_date<df$nt1_date)
df <- df[!(!is.na(df$nt1_date) & !is.na(df$np_date) & df$np_date<df$nt1_date),]

# Reads dates as characters if all are NA
# # Convert character dates to date format
# # Extracts all columns with "date" in their name    
# datevars <- names(df)[grep("date",names(df))]
# #   For each column, replace the character date with a Date format   
# for (i in 1:length(datevars)){
#   df[,datevars[i]] <- ymd(df[,datevars[i]])
#   rm(i)
# }
# rm(datevars)
# Shorten names

df <- df %>% 
  rename(
    diag_date=hf_diagnosis_date,
    bmi=bmi_value,
    cholesterol=last_cholesterol_value,
    sbp=sysbp_value,
    dbp=diasbp_value
  )


# Age
df$age<- as.numeric(difftime(df$patient_index_date,df$dob, units="days"))/365.25
summary(df$age)

# BMI
summary(df$bmi)


# Calculate bmi from height and weight if possible
df <- df %>%
  mutate(bmi = case_when(
    !is.na(bmi) ~ bmi,
    is.na(weight) | is.na(height) ~ NA_real_,
    TRUE ~ weight / (height^2)
  ))


# Systolic BP
summary(df$sbp)

# Diastolic BP
summary(df$dbp)

# Ethnicity
table(df$ethnicity_cat)

# Sex
table(df$sex)

# Cholesterol
summary(df$cholesterol)

# COPD
any(grepl("copd",names(df)))
grep("copd",names(df), value=TRUE)
df$copd <- ifelse(is.na(df$first_copd_date),0,1)
table(df$copd)


# Diabetes
any(grepl("diabetes",names(df)))
grep("diabetes",names(df), value=TRUE)
df$diabetes <- ifelse(is.na(df$tmp_first_diabetes_diag_date),0,1)
table(df$diabetes)

# Asthma
any(grepl("asthma",names(df)))
# none

# Obesity
any(grepl("obesity",names(df)))
grep("obesity",names(df), value=TRUE)
df$obesity <- ifelse(is.na(df$obesity_primary_date) & is.na(df$obesity_sus_date),0,1)
table(df$obesity)


# Hypertension
any(grepl("hypertension",names(df)))
grep("hypertension",names(df), value=TRUE)
df$hypertension <- ifelse(!is.na(df$hypertension_date_primary)|!is.na(df$hypertension_date_sus)|
                            is.na(df$hypertension_date_med),1,0)
table(df$hypertension)

# IHD
any(grepl("ihd",names(df)))
grep("ihd",names(df), value=TRUE)
df$ihd <- ifelse(!is.na(df$ihd_date_primary)|!is.na(df$ihd_date_sus),1,0)
table(df$ihd)

# CKD
any(grepl("ckd",names(df)))
grep("ckd",names(df), value=TRUE)
df$ckd <- ifelse(!is.na(df$ckd_date_primary)|!is.na(df$ckd_date_sus),1,0)
table(df$ckd)

# IMD
table(df$imd_quintile)
df$deprived <- NA
df$deprived <- ifelse(is.na(df$deprived) & df$imd_quintile=="1 (most deprived)",1,df$deprived)
df$deprived <- ifelse(is.na(df$deprived) & df$imd_quintile!="1 (most deprived)" & df$imd_quintile!="unknown",0,df$deprived)
df$deprived <- ifelse(is.na(df$deprived),2,df$deprived)
df$deprived <- factor(df$deprived, levels=0:2, labels=c("Not deprived", "Bottom quintile", "Unknown"))
table(df$deprived)
prop.table(table(df$deprived))

# Smoking  
table(df$smoking)
df$smoking <- factor(df$smoking, levels=c("N", "S"), labels=c("Non=smoker","Smoker"))

# Non-English speaker
any(grepl("non_english",names(df)))
grep("non_english",names(df), value=TRUE)
table(df$non_english_speaking)
df$non_english_sp <- factor(df$non_english_speaking, levels=c(FALSE, TRUE), 
                            labels=c("English speaking","Non-english speaking"))
table(df$non_english_sp)

# Migrant status
table(df$migrant)
df$migrant <- factor(df$migrant, levels=c(FALSE, TRUE), 
                     labels=c("Not","Migrant status"))
# Learning disability
table(df$learndis)
df$LD <- ifelse(is.na(df$learndis),0,1)
table(df$LD)

# Severe mental illness
table(df$smi)
df$smi <- factor(df$smi, levels=c(FALSE, TRUE), 
                 labels=c("Not","Severe mental illness"))
table (df$smi)

# Carehome resident
table(df$carehome_at_index)
df$carehome <- factor(df$carehome_at_index, levels=c(FALSE, TRUE), 
                      labels=c("Not","Carehome"))

# Substance abuse
table(df$substance_abuse)
df$substance_abuse <- factor(df$substance_abuse, levels=c(FALSE, TRUE), 
                             labels=c("Not","Substance abuse"))
table(df$substance_abuse)

# Homeless
table(df$homeless)
df$homeless <- factor(df$homeless, levels=c(FALSE, TRUE), 
                      labels=c("Not","Homeless"))
table(df$homeless)

# Housebound
table(df$housebound)
df$housebound <- factor(df$housebound, levels=c(FALSE, TRUE), 
                        labels=c("Not","Housebound"))
table(df$housebound)

# HF diagnosis
df$diag <- ifelse(is.na(df$diag_date),0,1)
table(df$diag)

# NTpro testing
df$NT <- ifelse(is.na(df$nt1_date),0,1)
table(df$NT)

# Time between the first NTPro test and the HF diagnosis
# Code time 1 month before to <2weeks after as 0 days
# also categorise <2 weeks, 2 to <6 weeks, 6-12 weeks


df$NT2HF<- as.numeric(difftime(df$diag_date,df$nt1_date, units="days"))
str(df$NT2HF)

summary(df$NT2HF)
df$NT2HF_cat <- NA
df$NT2HF_cat <- ifelse(is.na(df$NT2HF_cat) & df$NT2HF<14, 0, df$NT2HF_cat)
df$NT2HF_cat <- ifelse(is.na(df$NT2HF_cat) & df$NT2HF<42, 1, df$NT2HF_cat)
df$NT2HF_cat <- ifelse(is.na(df$NT2HF_cat) & df$NT2HF>=42, 2, df$NT2HF_cat)
df$NT2HF_cat <- factor(df$NT2HF_cat, levels = 0:2, labels = c("< 2 weeks","2-6 weeks",">= 6 weeks"))
prop.table(table(df$NT2HF_cat))*100
table(df$NT2HF_cat)

# May only select certain variables
# keep <- c(......)
# df <- df[,keep]

# Save file for analysis
# Using feather as it compresses and preserves column types
write_feather(df,"/workspace/test/file4analysisWP2_2_COVID.feather")
#write_feather(df,"/workspace/test/file4analysisWP2_2_postCOVID.feather")


