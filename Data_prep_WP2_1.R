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
# This is dummy data 

# df <- read_csv(here::here("test", "tmp_dataset_wp2_2.csv.gz"),show_col_types = FALSE)
# df <- read.csv("/workspace/test/tmp_dataset_wp2_2.csv.gz", header=TRUE)
# old datafiles


# Select dataset
# COVID
df <- read_csv(here::here("output", "tmp_dataset_wp2_1.csv.gz"),show_col_types = FALSE)
# Post-COVID
# df <-.....    

# Start date and end dates define the population - applied by Charlotte 
# COVID start date 1/1/20, end date 31/3/24  
# Post-COVID start date 1/4/24, end date 1/4/27 (currently set at 1/5/25) 
# Starts one year after 1/4/23 to allow for recovery from pandemic. 
# QUERY - reference for 1/4/23
df$Covid_start <- as.Date("2020-01-01")
df$Covid_end <- as.Date("2024-03-31")
# Dates TBC 

sum(is.na(df$first_hfsymptom_date))
# All have symptoms

# Data cleaning
# Currently not clear what will be done for the final dataset

# patient_index_date (eligibility date) is the latest of date of age 45 years, study start date and registration date plus 1 year.

# first_hfsymptom_date (cohort entry date) is the date of first HF symptom between patient index date and study end date

# Additional exclusions for WP2_1

# HF symptom before patient_index_date
sum(df$symptom_pre_index==TRUE)
# 61
df <-df[df$symptom_pre_index==FALSE,]

# HF diagnosis before cohort entry date
sum(!is.na(df$hf_diagnosis_date) & !is.na(df$first_hfsymptom_date) & df$hf_diagnosis_date<df$first_hfsymptom_date)
# 78
df <-df[!(!is.na(df$hf_diagnosis_date) & !is.na(df$first_hfsymptom_date) & df$hf_diagnosis_date<df$first_hfsymptom_date),]


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

any(grepl("breath",names(df)))
grep("breath",names(df), value=TRUE)

any(grepl("oedema",names(df)))
grep("oedema",names(df), value=TRUE)

any(grepl("fatigue",names(df)))
grep("fatigue",names(df), value=TRUE)


df <- df %>% 
  rename(
    diag_date=hf_diagnosis_date,
    symp_date=first_hfsymptom_date,
    oedema1date=oedema_date,
    fatigue1date=fatigue_date,
    breathless1date=breathless_date,
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
# TEMP- none with bmi
df$bmi <-as.numeric(df$bmi)
df$bmi <-50
d1 <- subset(df, select=c("patient_id", "bmi", "weight", "height"))
rm(d1)

# Systolic BP
summary(df$sbp)

# Diastolic BP
summary(df$dbp)
df$dbp <-as.numeric(df$dbp)
df$dbp <-df$sbp-20
# TEMP none with dbp

# Ethnicity
table(df$ethnicity_cat)

# Sex
table(df$sex)

# Cholesterol
df$cholesterol <- as.numeric(df$cholesterol)
summary(df$cholesterol)
# QUERY all missing
df$cholesterol <-20

# COPD
any(grepl("copd",names(df)))
grep("copd",names(df), value=TRUE)
df$copd <- ifelse(is.na(df$first_copd_date),0,1)
#df$copd <- factor(df$copd, levels=0:1, labels=c("no COPD", "with COPD"))
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
# TEMP none. 
df$obesity<- ifelse(df$patient_id<40000,1,0) 


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


# HF symptoms
df$symp <- ifelse(is.na(df$symp_date),0,1)
table(df$symp)
#df$symp <- factor(df$symp, levels=0:1, labels=c("no symptoms", "with symptoms"))
#table(df$symp)
df$symp1 <- ifelse(is.na(df$oedema1date),0,1)
df$symp2 <- ifelse(is.na(df$fatigue1date),0,1)
df$symp3 <- ifelse(is.na(df$breathless1date),0,1)
table(df$np)
table(df$symp1)
table(df$symp2)
table(df$symp3)

#Count symptoms
df$countsymp <- df$symp1+df$symp2+df$symp3
table(df$countsymp)
str(df$countsymp)

# Timings of HF-related symptoms relative to HF diagnosis
# Symptom before HF diagnosis
sum(df$symp_date<df$diag_date, na.rm=TRUE)
# >0
# Symptom at the same time as HF diagnosis
sum(df$symp_date==df$diag_date, na.rm=TRUE)
# 0
# Symptom after HF diagnosis
sum(df$symp_date>df$diag_date, na.rm=TRUE)
# 0
# With symptoms and no HF diagnosis
sum(df$diag==0)
# >0

# NP measurement near first HF symptoms
any(grepl("np",names(df)))
grep("np",names(df), value=TRUE)

# binary variable
table(df$np_near_symptom)
df$near_np <- as.numeric(df$np_near_symptom)
table(df$near_np)
hist(df$patient_id)
df$near_np <- ifelse(df$patient_id>60000,1,0) 
# TEMP None


# date variable
str(df$np_near_symptom_first)
df$near_npdate <- ymd(df$np_near_symptom_first)
str(df$near_npdate)
table(df$near_npdate)
# TEMP none
df$near_npdate <- df$symp_date+20

# Echo done near symptom
table(df$echo_done_near_symptom)
df$near_echo <- as.numeric(df$np_near_symptom)
table(df$near_echo)
# TEMP None
df$near_echo <- ifelse(df$patient_id>65000,1,0) 

# Echo referral near symptom
table(df$echo_ref_near_symptom)
df$near_echoref <- as.numeric(df$np_near_symptom)
table(df$near_echoref)
# TEMP None
df$near_echoref<- ifelse(df$patient_id>65000,1,0) 

# QUERY - no NP, echo completed or referral for echo near symptom
# Emailed Emily, Andrea and Will to check

# Time between the first near NP test and the first HF symptom
# Code time 1 month before to <2weeks after as 0 days
# also categorise <2 weeks, 2 to <6 weeks, 6-12 weeks

str(df$symp_date)
str(df$near_npdate)

df$NP2symp<- as.numeric(difftime(df$near_npdate,df$symp_date, units="days"))
str(df$NP2symp)

summary(df$NP2symp)

#d1 <- subset(df, select=c("symp_date","near_date", "NP2symp"))
df$NP2symp_cat <- NA
df$NP2symp_cat <- ifelse(is.na(df$NP2symp_cat) & df$NP2symp<0, 0, df$NP2symp_cat)
df$NP2symp_cat <- ifelse(is.na(df$NP2symp_cat) & df$NP2symp<14, 0, df$NP2symp_cat)
df$NP2symp_cat <- ifelse(is.na(df$NP2symp_cat) & df$NP2symp<42, 1, df$NP2symp_cat)
df$NP2symp_cat <- ifelse(is.na(df$NP2symp_cat) & df$NP2symp>=42, 2, df$NP2symp_cat)
df$NP2symp_cat <- factor(df$NP2symp_cat, levels = 0:2, labels = c("< 2 weeks","2-6 weeks",">= 6 weeks"))
prop.table(table(df$NP2symp_cat))*100

# May only select certain variables
# keep <- c(......)
# df <- df[,keep]

# Save file for analysis
# Using feather as it compresses and preserves column types
write_feather(df,"/workspace/test/file4analysisWP2_1_COVID.feather")
#write_feather(df,"/workspace/test/file4analysisWP2_1_postCOVID.feather")
