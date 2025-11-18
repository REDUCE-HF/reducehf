# Analysis_WP2_1.R
# Script to analyse data for WP2_1 of the REDUCE HF project
# KS Taylor

rm(v)
rm(list=ls()) 


today=Sys.Date()

#install.packages("tableone")

# Load packages
library(lubridate)
library(dplyr)
library(tableone)

string <-"/workspace/test/"

#variable is df$symp

df <- read_feather(here::here("test", "file4analysisWP1.feather"))

Vars <- c("age", "sex", "bmi", "ethnicity_cat", "smoking","sbp", "np2diag", "asthma")
convar <- c("age","bmi", "sbp", "np2diag")
FactorVars <-  c("sex", "ethnicity_cat","smoking", "asthma")

# Select dataset
#dta <- subset(df, symp==1) 
#dta <- subset(df, symp==1 & during==1) - too few
dta <- subset(df, symp==1 & after==1)
#dta <- subset(df, symp==1 & asthma==1)
# No patients
# Asthma is used temporarily until we have COPD, hypertension and obesity 
#btable<-"Baseline table, with symptoms, during"
btable<-"Baseline table, with symptoms, after"

#btable<-"Baseline table for asthma subset of those with symptoms"


Table <- CreateTableOne(vars=Vars, strata="sex", factorVars = FactorVars, data=dta,
                        test=FALSE, smd=F)
tab1 <- print(Table, quote=FALSE, smd=F, nonnormal=convar,cramVars="sex")

write.csv(tab1,paste0("/workspace/test/",btable," ", Sys.Date(),".csv")) 
