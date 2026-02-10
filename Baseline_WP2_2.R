# Baseline_WP2_1.R
# Script to analyse data for WP2_2 of the REDUCE HF project
# KS Taylor

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


#variable is df$NT
# To add NP2HF (cts) and NP2HF_cat

# COVID
df <- read_feather(here::here("test", "file4analysisWP2_2_COVID.feather"))
COVID <- 1
# Post_COVID
#df <- read_feather(here::here("test", "file4analysisWP2_2_postCOVID.feather"))
#COVID <- 0

Vars <- c("age", "sex",  "ethnicity_cat", "smoking","ihd", "copd","sbp","dbp",
          "cholesterol", "hypertension", "ckd", "obesity", "diabetes", "deprived", 
          "homeless", "carehome", "LD", "housebound", "NT2HF", 
          "substance_abuse", "smi", "non_english_sp", "NT2HF_cat")
convar <- c("age", "sbp", "dbp","cholesterol", "NT2HF")
FactorVars <-  c("sex", "ethnicity_cat","smoking", "ihd", "copd", 
                 "hypertension", "ckd", "obesity", "deprived", 
                 "homeless", "carehome", "LD", "housebound", 
                 "substance_abuse", "smi", "non_english_sp","NT2HF_cat")

# QUERY To add MLTCs
# All have NT==1
df1 <- subset(df, NT==1) 
df2 <- subset(df, NT==1 & copd==1)
df3 <- subset(df, NT==1 & copd==0)
df4 <- subset(df, NT==1 & hypertension==1)
df5 <- subset(df, NT==1 & hypertension==0)
df6 <- subset(df, NT==1 & diabetes==1)
df7 <- subset(df, NT==1 & diabetes==0)
df8 <- subset(df, NT==1 & deprived=="Bottom quintile")
df9 <- subset(df, NT==1 & deprived=="Not deprived")
df10 <- subset(df, NT==1 & obesity==1)
df11 <- subset(df, NT==1 & obesity==0)
table(df$deprived, df$sex)
#TEMP
datasets <- list(df1=df1, 
                 df2=df2, df3=df3, df4=df4,
                 df5=df5, df6=df6,
                 df7=df7, 
                #df8=df8,
                 df9=df9, 
                df10=df10,
                 df11=df11
                 )

for (nm in names(datasets)) {
  
  dat <- datasets[[nm]]
# includeNA=TRUE includes NA as a regular factor level and not missing
  
  Table <- CreateTableOne(vars=Vars, strata="sex", factorVars = FactorVars, data=dat,
                          test=FALSE, smd=F)
  tab1 <- print(Table, quote=FALSE, smd=F, nonnormal=convar,cramVars="sex")
  
  write.csv(tab1,paste0("/workspace/test/",nm,"_baseline table WP2_2, COVID_",COVID,"_",Sys.Date(),".csv")) 

}

df1 <- subset(df, NT==1) 
Table <- CreateTableOne(vars=Vars, strata="sex", factorVars = FactorVars, data=dat,
                        test=FALSE, smd=F)
tab1 <- print(Table, quote=FALSE, smd=F, nonnormal=convar,cramVars="sex")

# PREVIOUS CODE 
  

# # Select dataset
# # QUERY missing obesity and MLTCs - TO ADD
# dta <- subset(df, NT==1) 
# dta <- subset(df, NT==1 & copd==1)
# dta <- subset(df, NT==1 & copd==0)
# dta <- subset(df, NT==1 & hypertension==1)
# dta <- subset(df, NT==1 & hypertension==0)
# dta <- subset(df, NT==1 & diabetes==1)
# dta <- subset(df, NT==1 & diabetes==0)
# dta <- subset(df, NT==1 & deprived=="Bottom quintile")
# dta <- subset(df, NT==1 & deprived=="Not deprived")
# 
# 
# #Select table name
# btable<-"Baseline table for all for WP2_2 COVID"
# btable<-"Baseline table for people with COPD for WP2_2 COVID"
# btable<-"Baseline table for people without COPD for WP2_2 COVID"
# btable<-"Baseline table for people with hypertension for WP2_2 COVID"
# btable<-"Baseline table for people without hypertension for WP2_2 COVID"
# btable<-"Baseline table for people with diabetes for WP2_2 COVID"
# btable<-"Baseline table for people without diabetes for WP2_2 COVID"
# btable<-"Baseline table for people in bottom deprivation quintile for WP2_2 COVID"
# btable<-"Baseline table for people without deprivation for WP2_2 COVID"
# 
# Table <- CreateTableOne(vars=Vars, strata="sex", factorVars = FactorVars, data=dta,
#                        test=FALSE, smd=F)
# tab1 <- print(Table, quote=FALSE, smd=F, nonnormal=convar,cramVars="sex")
# 
# write.csv(tab1,paste0("/workspace/test/",btable," ", Sys.Date(),".csv")) 
