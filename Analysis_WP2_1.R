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
# To add NP2symp (cts) and NP2symp_cat


df <- read_feather(here::here("test", "file4analysisWP1.feather"))

Vars <- c("age", "sex",  "ethnicity_cat", "smoking","ihd", "copd","sbp", 
          "hypertension", "ckd", "obesity", "diabetes", "deprived", "homeless", "carehome", "LD", "housebound", 
          "substance_abuse", "smi", "non_english_sp")
convar <- c("age", "sbp")
FactorVars <-  c("sex", "ethnicity_cat","smoking", "ihd", "copd", 
                 "hypertension", "ckd", "obesity", "deprived", 
                 "homeless", "carehome", "LD", "housebound", 
                 "substance_abuse", "smi", "non_english_sp")

# Select dataset
dta <- subset(df, symp==1) 


btable<-"Baseline table for all"


Table <- CreateTableOne(vars=Vars, strata="sex", factorVars = FactorVars, data=dta,
                        test=FALSE, smd=F)
tab1 <- print(Table, quote=FALSE, smd=F, nonnormal=convar,cramVars="sex")

write.csv(tab1,paste0("/workspace/test/",btable," ", Sys.Date(),".csv")) 
