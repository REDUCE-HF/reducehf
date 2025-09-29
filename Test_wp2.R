# Test_wp2.R
rm(v)
df <- read.csv("/workspaces/reducehf/output/dataset_wp2.csv.gz", header=TRUE)
table(df$sex)

# patient index date is the earliest of date of age 45 years, study start date and registration date minus 1 year.

# WP2.1 
# Cohort entry date is date of first symptom between patient index date and study end date


d1 <- subset(df, select=c("patient_id", "first_oedema_date_primary", "first_fatigue_date_primary",
                           "first_breathless_date_primary","first_hfsymptom_date", "hf_diagnosis_date"))

# Convert characters for missing values to NA
df$hf_diagnosis_date[df$hf_diagnosis_date==""] <- NA
df$first_hfsymptom_date[df$first_hfsymptom_date==""] <- NA

df$first_oedema_date_primary[df$first_oedema_date_primary==""] <- NA
df$first_fatigue_date_primary[df$first_fatigue_date_primary==""] <- NA
df$first_breathless_date_primary[df$first_breathless_date_primary==""] <- NA


# Create binary variables to indicate missing or present symptom and HF diagnosis dates

df$diag <- ifelse(is.na(df$hf_diagnosis_date),0,1)
df$symp <- ifelse(is.na(df$first_hfsymptom_date),0,1)

df$symp1 <- ifelse(is.na(df$first_oedema_date_primary),0,1)
df$symp2 <- ifelse(is.na(df$first_fatigue_date_primary),0,1)
df$symp3 <- ifelse(is.na(df$first_breathless_date_primary),0,1)

df$nosymp <- df$symp1+df$symp2+df$symp3
d2 <-subset(df, select=c("symp1", "symp2", "symp3", "nosymp") )

table(df$nosymp)

table(df$diag)
table(df$symp)
table(df$diag, df$symp) 

df$diag_date <- as.Date(df$hf_diagnosis_date, format="%Y-%m-%d")
df$symp_date <- as.Date(df$first_hfsymptom_date, format="%Y-%m-%d")
sum(df$symp_date<df$diag_date, na.rm=TRUE)
sum(df$symp_date==df$diag_date, na.rm=TRUE)
sum(df$symp_date>df$diag_date, na.rm=TRUE)


# QUERY - only have one symptom. Is that expected?



# WP2.2. 
# Cohort entry date is date of first NP-pro test between patient index date and study end date