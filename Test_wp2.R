# Test_wp2.R
rm(v)
rm(list=ls()) 

# Load packages
library(lubridate)
library(dplyr)

# Load data 
# This is dummy data and not including the final set of variables   
df <- read.csv("/workspace/test/dataset_wp2.csv.gz", header=TRUE)


# Data cleanging
# Currently not clear what will be done before the final dataset is delivered

# WP2.1 

# Patient index date (eligibility date) is the latest of date of age 45 years, study start date and registration date minus 1 year.

# Cohort entry date is date of first symptom between patient index date and study end date


#d1 <- subset(df, select=c("patient_id", "first_oedema_date_primary", "first_fatigue_date_primary",
#                           "first_breathless_date_primary","first_hfsymptom_date", "hf_diagnosis_date"))

# Rename date variables
df <- df %>% rename(patient_index_date=patient_index)
df <- df %>% rename(date_of_birth=dob)

#   Convert character to date format
#   Extracts all columns with "date" in their name    
datevars <- names(df)[grep("date",names(df))]
#   For each column, replaces the character date to a Date format   
for (i in 1:length(datevars)){
  df[,datevars[i]] <- ymd(df[,datevars[i]])
  rm(i)
}
rm(datevars)



# Convert characters for missing values to NA
df$hf_diagnosis_date[df$hf_diagnosis_date==""] <- NA
df$first_hfsymptom_date[df$first_hfsymptom_date==""] <- NA
df$first_oedema_date_primary[df$first_oedema_date_primary==""] <- NA
df$first_fatigue_date_primary[df$first_fatigue_date_primary==""] <- NA
df$first_breathless_date_primary[df$first_breathless_date_primary==""] <- NA
df$dob[df$dob==""] <- NA
df$patient_index[df$patient_index==""] <- NA


# Create date variables
str(df$hf_diagnosis_date)
str(df$diag_date)
df$diag_date <- as.Date(df$hf_diagnosis_date, format="%Y-%m-%d")
df$symp_date <- as.Date(df$first_hfsymptom_date, format="%Y-%m-%d")
df$dob_date <- as.Date(df$dob, format="%Y-%m-%d")
df$patient_index_date <- as.Date(df$patient_index, format="%Y-%m-%d")
df$age<- as.numeric(difftime(df$patient_index_date,df$dob_date, units="days"))/365.25
df$npdate <- as.Date(df$np_date,format="%Y-%m-%d")
df$nt1date <- as.Date(df$nt1_date,format="%Y-%m-%d")
df$oedema1 <- as.Date(df$first_oedema_date_primary,format="%Y-%m-%d")
df$fatigue1 <- as.Date(df$first_fatigue_date_primary,format="%Y-%m-%d")
df$breathless1 <- as.Date(df$first_breathless_date_primary,format="%Y-%m-%d")


# Create binary variables to indicate missing or present symptom and HF diagnosis dates

df$diag <- ifelse(is.na(df$diag_date),0,1)
df$symp <- ifelse(is.na(df$symp_date),0,1)
table(df$diag)
table(df$symp)

df$had_np <- ifelse(is.na(df$npdate),0,1)
table(df$had_np)

df$symp1 <- ifelse(is.na(df$oedema1),0,1)
df$symp2 <- ifelse(is.na(df$fatigue1),0,1)
df$symp3 <- ifelse(is.na(df$breathless1),0,1)
table(df$symp1)
table(df$symp2)
table(df$symp3)

df$countsymp <- df$symp1+df$symp2+df$symp3
table(df$countsymp)
str(df$countsymp)

df$hadsymp <- ifelse(df$countsymp>0,1,0)

d2 <-subset(df, select=c(symp1, symp2, symp3, countsymp) )
table(df$diag)
table(df$symp)
table(df$diag, df$symp) 

# Compare dates of HF-related symptoms and HF diagnosis
sum(df$symp_date<df$diag_date, na.rm=TRUE)
sum(df$symp_date==df$diag_date, na.rm=TRUE)
sum(df$symp_date>df$diag_date, na.rm=TRUE)
sum(df$hadsymp==1 & is.na(df$diag_date))

# QUERY - only have one symptom. Is that expected or are the data scrambled so can't tell?

# Set dates of intervals

Covid_start <- as.Date("2021-01-03")
Covid_end <- as.Date("2023-01-04")

# Define cohorts





# WP2.2. 
# Cohort entry date is date of first NP-pro test between patient index date and study end date

# Convert characters for missing values to NA

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

