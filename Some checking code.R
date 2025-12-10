# Some checking code.R


# Convert characters for missing values to NA - Check other script

df$nt1_date[df$nt1_date==""] <- NA
df$np_date[df$np_date==""] <- NA




# Check ranges
summary(df$nt1_result)
summary(df$np_result)
summary(df$age)


# Check ranges
# DON'T DELETE 

# List variables and data types
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

# Age
df$age<- as.numeric(difftime(df$patient_index_date,df$dob, units="days"))/365.25
summary(df$age)

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
vars <- c("age","nt1_result")
# df %>%
#   summarise(across(any_of(vars), list(min = ~min(.x, na.rm = TRUE))))
# 
# df %>%
#   summarise(across(any_of(vars), list(max = ~max(.x, na.rm = TRUE))))


df %>%
  summarise(across(any_of(vars), list(min = ~min(.x, na.rm = TRUE),
                                      max = ~max(.x, na.rm = TRUE))))

