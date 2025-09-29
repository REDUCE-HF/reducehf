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

# Create binary variables to indicate missing or present symptom and HF diagnosis dates

d1$diag <- ifelse(is.na(df$hf_diagnosis_date),0,1)
d1$symp <- ifelse(is.na(df$first_hfsymptom_date),0,1)

table(d1$diag)
table(d1$symp)
table(d1$diag, d1$symp) 

# QUERY - only have one symptom. Is that expected?

# WP2.2. 
# Cohort entry date is date of first NP-pro test between patient index date and study end date