# Test_wp2.R
rm(v)
df <- read.csv("/workspaces/reducehf/test/dataset_wp2.csv.gz", header=TRUE)

# Patient index date is the earliest of date of age 45 years, study start date and registration date minus 1 year.

# WP2.1 
# Cohort entry date is date of first symptom between patient index date and study end date


#d1 <- subset(df, select=c("patient_id", "first_oedema_date_primary", "first_fatigue_date_primary",
#                           "first_breathless_date_primary","first_hfsymptom_date", "hf_diagnosis_date"))

# Convert characters for missing values to NA
df$hf_diagnosis_date[df$hf_diagnosis_date==""] <- NA
df$first_hfsymptom_date[df$first_hfsymptom_date==""] <- NA

df$first_oedema_date_primary[df$first_oedema_date_primary==""] <- NA
df$first_fatigue_date_primary[df$first_fatigue_date_primary==""] <- NA
df$first_breathless_date_primary[df$first_breathless_date_primary==""] <- NA

df$dob[df$dob==""] <- NA
df$patient_index[df$patient_index==""] <- NA


# Create date variables
df$diag_date <- as.Date(df$hf_diagnosis_date, format="%Y-%m-%d")
df$symp_date <- as.Date(df$first_hfsymptom_date, format="%Y-%m-%d")
df$dob_date <- as.Date(df$dob, format="%Y-%m-%d")
df$patient_index_date <- as.Date(df$patient_index, format="%Y-%m-%d")



# Create binary variables to indicate missing or present symptom and HF diagnosis dates

df$diag <- ifelse(is.na(df$hf_diagnosis_date),0,1)
df$symp <- ifelse(is.na(df$first_hfsymptom_date),0,1)

df$symp1 <- ifelse(is.na(df$first_oedema_date_primary),0,1)
df$symp2 <- ifelse(is.na(df$first_fatigue_date_primary),0,1)
df$symp3 <- ifelse(is.na(df$first_breathless_date_primary),0,1)

df$nosymp <- df$symp1+df$symp2+df$symp3
#d2 <-subset(df, select=c("symp1", "symp2", "symp3", "nosymp") )

table(df$nosymp)

table(df$diag)
table(df$symp)
table(df$diag, df$symp) 

# Compare dates of HF-related symptoms and HF diagnosis
sum(df$symp_date<df$diag_date, na.rm=TRUE)
sum(df$symp_date==df$diag_date, na.rm=TRUE)
sum(df$symp_date>df$diag_date, na.rm=TRUE)

# QUERY - only have one symptom. Is that expected or are the data scrambled so can't tell?



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


check <- subset(df, select=c("age", "nt1_result","np_result","bmi_value","weight","height","last_cholesterol_value"))
tab <- t(sapply(check, function(x) c(Minimum=min(x, na.rm=TRUE), Maximum=max(x, na.rm=TRUE))))

print(tab)

summary(df$weight)
df$wt <- as.numeric(df$weight)
summary(df$wt)

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

