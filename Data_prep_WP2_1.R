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

#df <- read.csv("/workspace/test/tmp_dataset_wp2_2.csv.gz", header=TRUE)
# Reads dates as characters if all are NR
# # Convert character dates to date format
# # Extracts all columns with "date" in their name    
# datevars <- names(df)[grep("date",names(df))]
# #   For each column, replace the character date with a Date format   
# for (i in 1:length(datevars)){
#   df[,datevars[i]] <- ymd(df[,datevars[i]])
#   rm(i)
# }
# rm(datevars)

# df <- read_csv(here::here("test", "tmp_dataset_wp2_2.csv.gz"),show_col_types = FALSE)
# old datafile

df <- read_csv(here::here("output", "tmp_dataset_wp2_1.csv.gz"),show_col_types = FALSE)
sum(is.na(df$first_hfsymptom_date))
# All have symptoms
d1<- subset(df, select=c("patient_index_date", "first_hfsymptom_date"))
# Data cleaning
# Currently not clear what will be done for the final dataset

# WP2.1 

# patient_index_date (eligibility date) is the latest of date of age 45 years, study start date and registration date plus 1 year.

# first_hfsymptom_date (cohort entry date) is the date of first HF symptom between patient index date and study end date

#d1 <- subset(df, select=c("patient_id", "first_oedema_date_primary", "first_fatigue_date_primary",
#                           "first_breathless_date_primary","first_hfsymptom_date", "hf_diagnosis_date"))

# Additional exclusions for WP2_1
# HF symptom before patient_index_date
sum(df$symptom_pre_index==TRUE)
# 61
df <-df[df$symptom_pre_index==FALSE,]

# HF diagnosis before cohort entry date
sum(!is.na(df$hf_diagnosis_date) & !is.na(df$first_hfsymptom_date) & df$hf_diagnosis_date<df$first_hfsymptom_date)
# 78
df <-df[!(!is.na(df$hf_diagnosis_date) & !is.na(df$first_hfsymptom_date) & df$hf_diagnosis_date<df$first_hfsymptom_date),]

# Set period of interest as.Date(Y-M-D) witho
df$Covid_start <- as.Date("2020-03-23")
# QUERY - TBC. It might be the start date
df$Covid_end <- as.Date("2023-04-01")
table(ifelse(is.na(df$first_hfsymptom_date),0,1))

# SELECT period
# For COVID analysis - exclude those with first HF symptom after end of COVID
#sum(df$first_hfsymptom_date>df$Covid_end)
#df <-df[df$first_hfsymptom_date>df$Covid_end,]

# For non-COVID analysis - exclude those with first HF symptom before end of COVID
sum(df$first_hfsymptom_date<df$Covid_end)
df <-df[df$first_hfsymptom_date<df$Covid_end,]

# Shorten names
df <- df %>% 
  rename(
    diag_date=hf_diagnosis_date,
    symp_date=first_hfsymptom_date,
   # oedema1date=first_oedema_date_primary,
  # fatigue1date=first_fatigue_date_primary,
  # breathless1date=first_breathless_date_primary,
  #np_date=np_near_symptom_first
    bmi=bmi_value,
    cholesterol=last_cholesterol_value,
    sbp=sysbp_value,
    dbp=diasbp_value
    )


any(grepl("breath",names(df)))
# QUERY - Missing vars first_oedema_date_primary, first_fatigue_date_primary,first_breathless_date_primary
# Emailed charlotte 27 Nov

# Assuming dates of chronic diseases are at baseline so all are before HD diagnosis

# Derive age
df$age<- as.numeric(difftime(df$patient_index_date,df$dob, units="days"))/365.25
summary(df$age)


# BMI
d1 <- subset(df, select=c("patient_id", "bmi", "weight", "height"))
# QUERY- Currently all NR
rm(d1)


# Calculate bmi from height and weight if possible
df <- df %>%
  mutate(bmi = case_when(
    !is.na(bmi) ~ bmi,
    is.na(weight) | is.na(height) ~ NA_real_,
    TRUE ~ weight / (height^2)
  ))

summary(df$sbp)
summary(df$dbp)

table(df$ethnicity_cat)


# Create binary variables 
df$symp <- ifelse(is.na(df$symp_date),0,1)
table(df$symp)
#df$symp <- factor(df$symp, levels=0:1, labels=c("no symptoms", "with symptoms"))
#table(df$symp)

df$diag <- ifelse(is.na(df$diag_date),0,1)
table(df$diag)
df$diag <- factor(df$diag, levels=0:1, labels=c("no HF", "with HF"))
table(df$diag)


any(grepl("copd",names(df)))
grep("copd",names(df), value=TRUE)
df$copd <- ifelse(is.na(df$first_copd_date),0,1)
#df$copd <- factor(df$copd, levels=0:1, labels=c("no COPD", "with COPD"))
table(df$copd)

table(df$copd)

any(grepl("diabetes",names(df)))
grep("diabetes",names(df), value=TRUE)
df$diabetes <- ifelse(is.na(df$tmp_first_diabetes_diag_date),0,1)
table(df$diabetes)

any(grepl("asthma",names(df)))
# none

any(grepl("obesity",names(df)))
grep("obesity",names(df), value=TRUE)
df$obesity <- ifelse(is.na(df$obesity_primary_date)& is.na(df$obesity_sus_date),0,1)
table(df$obesity)
# none

any(grepl("hypertension",names(df)))
grep("hypertension",names(df), value=TRUE)
df$hypertension <- ifelse(!is.na(df$hypertension_date_primary)|!is.na(df$hypertension_date_sus)|
                            is.na(df$hypertension_date_med),1,0)
table(df$hypertension)

any(grepl("ihd",names(df)))
grep("ihd",names(df), value=TRUE)
df$ihd <- ifelse(!is.na(df$ihd_date_primary)|!is.na(df$ihd_date_sus),1,0)
table(df$ihd)

any(grepl("ckd",names(df)))
grep("ckd",names(df), value=TRUE)
df$ckd <- ifelse(!is.na(df$ckd_date_primary)|!is.na(df$ckd_date_sus),1,0)
table(df$ckd)

table(df$imd_quintile)
df$deprived <- NA
df$deprived <- ifelse(is.na(df$deprived) & df$imd_quintile=="1 (most deprived)",1,df$deprived)
df$deprived <- ifelse(is.na(df$deprived) & df$imd_quintile!="1 (most deprived)" & df$imd_quintile!="unknown",0,df$deprived)
df$deprived <- ifelse(is.na(df$deprived),2,df$deprived)
df$deprived <- factor(df$deprived, levels=0:2, labels=c("Not deprived", "Deprived", "Unknown"))
table(df$deprived)
prop.table(table(df$deprived))
  
table(df$smoking)
df$smoking <- factor(df$smoking, levels=c("N", "S"), labels=c("Non=smoker","Smoker"))


any(grepl("non_english",names(df)))
grep("non_english",names(df), value=TRUE)
table(df$non_english_speaking)
df$non_english_sp <- factor(df$non_english_speaking, levels=c(FALSE, TRUE), 
                            labels=c("English speaking","Non-english speaking"))
table(df$non_english_sp)

table(df$migrant)
df$migrant <- factor(df$migrant, levels=c(FALSE, TRUE), 
                            labels=c("English speaking","Non-english speaking"))
table(df$learndis)
df$LD <- ifelse(is.na(df$learndis),0,1)
table(df$LD)

table(df$smi)
df$smi <- factor(df$smi, levels=c(FALSE, TRUE), 
                 labels=c("Not","Severe mental illness"))
table (df$smi)

table(df$carehome_at_index)
df$carehome <- factor(df$carehome_at_index, levels=c(FALSE, TRUE), 
                 labels=c("Not","Carehome"))

table(df$substance_abuse)
df$substance_abuse <- factor(df$substance_abuse, levels=c(FALSE, TRUE), 
                      labels=c("Not","Substance abuse"))
table(df$substance_abuse)

table(df$homeless)
df$homeless <- factor(df$homeless, levels=c(FALSE, TRUE), 
                             labels=c("Not","Homeless"))
table(df$homeless)

table(df$housebound)
df$housebound <- factor(df$housebound, levels=c(FALSE, TRUE), 
                      labels=c("Not","Housebound"))
table(df$housebound)




#df$np <- ifelse(is.na(df$npdate),0,1)
#df$symp1 <- ifelse(is.na(df$oedema1date),0,1)
#df$symp2 <- ifelse(is.na(df$fatigue1date),0,1)
#df$symp3 <- ifelse(is.na(df$breathless1date),0,1)
# table(df$np)
# table(df$symp1)
# table(df$symp2)
# table(df$symp3)
# Count symptoms
# 
# df$countsymp <- df$symp1+df$symp2+df$symp3
# table(df$countsymp)
# str(df$countsymp)
# QUERY - only had one symptom. Is that expected or are the data scrambled so can't tell?


# Timings of HF-related symptoms relative to HF diagnosis
# Symptom before HF diagnosis
sum(df$symp_date<df$diag_date, na.rm=TRUE)
# 53
# Symptom at the same time as HF diagnosis
sum(df$symp_date==df$diag_date, na.rm=TRUE)
# 0
# Symptom after HF diagnosis
sum(df$symp_date>df$diag_date, na.rm=TRUE)
# 0
# With symptoms and no HF diagnosis
sum(df$diag==0)
# 593

# NP measurement near first HF symptoms
table(df$np_near_symptom)
df$near <- as.numeric(df$np_near_symptom)
table(df$near)
# None

# Echo done near symptom
table(df$echo_done_near_symptom)
# None

# Echo referral near symptom
table(df$echo_ref_near_symptom)
# None

table(df$np_near_symptom)
str(df$np_near_symptom) 

# QUERY - no NP, echo completed or referral for echo near symptom
# Emailed Emily, Andrea and Will to check

# QUERY - Need the time of the NP test near the first HF symptom
# df$NP2symp -the time between the first near NP test and the first HF symptom
# Code time 1 month before to <2weeks after as 0 days
# also categorise <2 weeks, 2 to <6 weeks, 6-12 weeks
# df$NP2symp_cat

# Time of NP test near first HF symptom
# New variable df$near_date
#Temp var
#sample(-30,90,1)
df$near_date <- df$symp_date+20

df$NP2symp<- as.numeric(difftime(df$near_date,df$symp_date, units="days"))
summary(df$NP2symp)
#d1 <- subset(df, select=c("symp_date","near_date", "NP2symp"))
df$NP2symp_cat <- NA
df$NP2symp_cat <- ifelse(is.na(df$NP2symp_cat) & df$NP2symp<0, 0, df$NP2symp_cat)
df$NP2symp_cat <- ifelse(is.na(df$NP2symp_cat) & df$NP2symp<14, 0, df$NP2symp_cat)
df$NP2symp_cat <- ifelse(is.na(df$NP2symp_cat) & df$NP2symp<42, 1, df$NP2symp_cat)
df$NP2symp_cat <- ifelse(is.na(df$NP2symp_cat) & df$NP2symp>=42, 2, df$NP2symp_cat)
df$NP2symp_cat <- factor(df$NP2symp_cat, levels = 0:2, labels = c("< 2 weeks","2-6 weeks",">= 6 weeks"))
prop.table(table(df$NP2symp_cat))*100


# # first HF symptom before covid pandemic   
# df$before <- ifelse(
#   is.na(df$symp_date), 99,
#   ifelse(df$symp_date < df$Covid_start, 1, 0)
# )
# table(df$before)
# 
# # first HF symptom during covid pandemic   
# df$during <- ifelse(
#   is.na(df$symp_date), 99,
#   ifelse(df$symp_date >= df$Covid_start & df$symp_date < df$Covid_end, 1, 0)
#   )
# table(df$during)
# 
# # first symptom after covid pandemic 
# df$after <-ifelse(
#   is.na(df$symp_date), 99,
#   ifelse(df$symp_date >= df$Covid_end, 1, 0)
# )
# table(df$after)
# 
# #check <- df[df$before==1,]
# #var <- c("symp_date", "Covid_start", "Covid_end")
# #check <- subset(check,select=var)
# #nrow(check)
# 
# check <- df[df$during==1,]
# var <- c("symp_date", "Covid_start", "Covid_end")
# check <- subset(check,select=var)
# nrow(check)
# 
# check <- df[df$after==1,]
# var <- c("symp_date", "Covid_end")
# check <- subset(check,select=var)
# nrow(check)

# Define cohort
# QUERY will Charlotte have applied all the exclusion criteria?

# To complete
# May only select certain variables
# keep <- c(......)
# df <- df[,keep]

# Save file for analysis
# Using feather as it compresses and preserves column types
write_feather(df,"/workspace/test/file4analysisWP1.feather")
