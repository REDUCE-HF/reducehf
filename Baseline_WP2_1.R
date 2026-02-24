# Baseline_WP2_1.R
# Script to analyse data for WP2_1 of the REDUCE HF project
# KSTaylor


rm(v)
rm(list=ls()) 


today=Sys.Date()

#install.packages("tableone")

# Load packages
library(lubridate)
library(dplyr)
library(tableone)
library(feather)

#string <-"/workspace/test/"


#variable is df$symp
# To add NP2symp (cts) and NP2symp_cat

# COVID
df <- read_feather(here::here("test", "file4analysisWP2_1_COVID.feather"))
COVID <- 1
# Post_COVID
#df <- read_feather(here::here("test", "file4analysisWP2_1_postCOVID.feather"))
#COVID <- 0

Vars <- c("age", "sex",  "ethnicity_cat", "smoking","ihd", "copd","sbp","dbp",
          "cholesterol", "hypertension", "ckd", "obesity", "diabetes", "deprived", 
          "homeless", "carehome", "LD", "housebound", "NP2symp","near_echo", "near_echoref",
          "substance_abuse", "smi", "non_english_sp", "NP2symp_cat", "near_np")
convar <- c("age", "sbp", "dbp","cholesterol", "NP2symp")
FactorVars <-  c("sex", "ethnicity_cat","smoking", "ihd", "copd", 
                 "hypertension", "ckd", "obesity", "deprived",
                 "homeless", "carehome", "LD", "housebound", 
                 "substance_abuse", "smi", "non_english_sp",
                 "NP2symp_cat","near_echo", "near_echoref","near_np"
                 )

# QUERY To add MLTCs
df1 <- subset(df, symp==1) 
df2 <- subset(df, symp==1 & copd==1)
df3 <- subset(df, symp==1 & copd==0)
df4 <- subset(df, symp==1 & hypertension==1)
df5 <- subset(df, symp==1 & hypertension==0)
df6 <- subset(df, symp==1 & diabetes==1)
df7 <- subset(df, symp==1 & diabetes==0)
df8 <- subset(df, symp==1 & deprived=="Bottom quintile")
df9 <- subset(df, symp==1 & deprived=="Not deprived")
df10 <- subset(df, symp==1 & obesity==1)
df11 <- subset(df, symp==1 & obesity==0)

datasets <- list(df1=df1, df2=df2,
                 df3=df3, df4=df4,
                 df5=df5, df6=df6,
                 df7=df7, df8=df8,
                 df9=df9, df10=df10,
                 df11=df11
                 )

table(df$deprived) 
for (nm in names(datasets)) {
  
  dat <- datasets[[nm]]
# includeNA=TRUE includes NA as a regular factor level and not missing
  Table <- CreateTableOne(vars=Vars, strata="sex", factorVars = FactorVars, data=dat,
                          test=FALSE, smd=F)
  tab1 <- print(Table, quote=FALSE, smd=F, nonnormal=convar,cramVars="sex")
  
  write.csv(tab1,paste0("/workspace/test/",nm,"_baseline table WP2_1, COVID_",COVID,"_",Sys.Date(),".csv")) 

}
df1 <- subset(df, symp==1) 
Table <- CreateTableOne(vars=Vars, strata="sex", factorVars = FactorVars, data=dat,
                        test=FALSE, smd=F)
tab1 <- print(Table, quote=FALSE, smd=F, nonnormal=convar,cramVars="sex")

  
# PREVIOUS CODE 
  

# # Select dataset
# # QUERY missing obesity and MLTCs - TO ADD
#dta <- subset(df, symp==1) 
# dta <- subset(df, symp==1 & copd==1)
# dta <- subset(df, symp==1 & copd==0)
# dta <- subset(df, symp==1 & hypertension==1)
# dta <- subset(df, symp==1 & hypertension==0)
# dta <- subset(df, symp==1 & diabetes==1)
# dta <- subset(df, symp==1 & diabetes==0)
# dta <- subset(df, symp==1 & deprived=="Bottom quintile")
# dta <- subset(df, symp==1 & deprived=="Not deprived")
# 
# 
# #Select table name
# btable<-"Baseline table for all for WP2_1 COVID"
# btable<-"Baseline table for people with COPD for WP2_1 COVID"
# btable<-"Baseline table for people without COPD for WP2_1 COVID"
# btable<-"Baseline table for people with hypertension for WP2_1 COVID"
# btable<-"Baseline table for people without hypertension for WP2_1 COVID"
# btable<-"Baseline table for people with diabetes for WP2_1 COVID"
# btable<-"Baseline table for people without diabetes for WP2_1 COVID"
# btable<-"Baseline table for people in bottom deprivation quintile for WP2_1 COVID"
# btable<-"Baseline table for people without deprivation for WP2_1 COVID"
# 
#Table <- CreateTableOne(vars=Vars, strata="sex", factorVars = FactorVars, data=dta,
#                         test=FALSE, smd=F)
# tab1 <- print(Table, quote=FALSE, smd=F, nonnormal=convar,cramVars="sex")
# 
# write.csv(tab1,paste0("/workspace/test/",btable," ", Sys.Date(),".csv")) 
