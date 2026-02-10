# Diagnostic_accuracy_WP2.R
# Script for diagnostic accuracy of NP testing for WP2 of the REDUCE HF project
# KS Taylor

rm(v)
rm(list=ls()) 

#   Load the librairies incl "epitools" package to calculate ratios and 95% CIs
library(epitools)
library(pROC)
library(dplyr)
library(feather)

# Load dataset
# COVID
df <- read_feather(here::here("test", "file4analysisWP2_2_COVID.feather"))

# TEMP
# boost dataset and range of NT values to get code working

td1 <-df
summary(td1$nt1_result)
td1$nt1_result <- td1$nt1_result*12
summary(td1$nt1_result)

td2 <-df
summary(td2$nt1_result)
td2$nt1_result <- td2$nt1_result*7
summary(td2$nt1_result)


td3 <-df
td3$nt1_result <- td3$nt1_result*4

td4 <-df
td4$nt1_result <- td4$nt1_result*2

td5 <-df

td6 <-df
td6$diag<-1

td7 <-df
td8 <-df


merged <-rbind(td1,td2,td3,td4,td5, td6,td7,td8)
df <-merged
# END OF TEMP

# Select dataset
# QUERY To add MLTCs
# All have NT==1
df2 <- subset(df, NT==1) 
# df2 <- subset(df, NT==1 & copd==1)
# df2 <- subset(df, NT==1 & copd==0)
# df2 <- subset(df, NT==1 & hypertension==1)
# df2 <- subset(df, NT==1 & hypertension==0)
# df2 <- subset(df, NT==1 & diabetes==1)
# df2 <- subset(df, NT==1 & diabetes==0)
# df2 <- subset(df, NT==1 & deprived=="Bottom quintile")
# df2 <- subset(df, NT==1 & deprived=="Not deprived")
# df2 <- subset(df, NT==1 & obesity==1)
# df2 <- subset(df, NT==1 & obesity==0)

btable <-"all"
# btable <-"with COPD"
# btable <-"not COPD"
# btable <-"with hypertension"
# btable <-"not hypertension"
# btable <-"with diabetes"
# btable <-"not diabetes"
# btable <-"deprived"
# btable <-"not deprived"
# btable <-"obesity"
# btable <-"not obesity"

# Count those with NTPro readings and of them with a HF diagnosis
  nrow(subset(df2, diag == 1 & !is.na(nt1_result)))
  nrow(subset(df2, !is.na(nt1_result)))

##### Diagnosis of HF
##### For all those with NTpro readings  (rule out <125, rule in >=2000)
  
summary(df2$nt1_result)  
#max =199.43  


t1 <- subset(df2, agecat3=="<50 years")
t2 <- subset(df2, agecat3=="50-75 years")
t3 <- subset(df2, agecat3=="75 years+")

table(t1$diag)
table(t2$diag)
table(t3$diag)


# # debug
# 
# d1 <-subset(t1,nt1_result>=125 & diag==1)
# d2 <-subset(t1,nt1_result>=125 & diag==0)
# d3 <-subset(t1,nt1_result<125 & diag==1)
# d4 <-subset(t1,nt1_result<125 & diag==0)
# 
# nrow(d1)
# nrow(d2)
# nrow(d3)
# nrow(d4)
# 
# d1 <-subset(t2,nt1_result>=125 & diag==1)
# d2 <-subset(t2,nt1_result>=125 & diag==0)
# d3 <-subset(t2,nt1_result<125 & diag==1)
# d4 <-subset(t2,nt1_result<125 & diag==0)
# 
# nrow(d1)
# nrow(d2)
# nrow(d3)
# nrow(d4)
# 
# d1 <-subset(t3,nt1_result>=125 & diag==1)
# d2 <-subset(t3,nt1_result>=125 & diag==0)
# d3 <-subset(t3,nt1_result<125 & diag==1)
# d4 <-subset(t3,nt1_result<125 & diag==0)
# 
# nrow(d1)
# nrow(d2)
# nrow(d3)
# nrow(d4)
# 
# 
# 
# table(df2$agecat3)
# summary(t1$nt1_result)
# summary(t2$nt1_result)
# summary(t3$nt1_result)
# 
# table(t1$diag)
# table(t2$diag)
# table(t3$diag)
  
#   Empty table with diagnostic accuracy parameters
Test <- rep(c("nt1_result"), times = 2)
Cutoff <- c(125,2000)

Agegp <- "All"
tab1 <- data.frame(Test, Cutoff, Agegp, N = NA,
                   TP = NA, FN = NA, FP = NA, TN = NA,
                   Sens = NA, Spec = NA,
                   Prev = NA,
                   PPV = NA, NPV = NA,
                   LR.pos = NA, LR.neg = NA, OR = NA)
#   Fill in the table:
for (i in 1:nrow(tab1)){
  # i <- 2
  te <- Test[i]
  co <- Cutoff[i]
  dat <- subset(df2, is.na(get(te))==FALSE)
  # Subset where there are no NAs for te
  y <- factor(dat$diag, levels = c(1,0), labels = c("D+ (HF)","D- (NO HF)"))
  x <- factor(as.numeric(dat[,te]>=co), levels = c(1,0), labels = paste(c("+ (>=","- (<"),co,")"))
  
  
  z <- table(x,y)
  
  lr.pos <- round(riskratio(t(z)[2:1,2:1])$measure[2,],2)
  lr.pos <- paste0(lr.pos[1]," (",lr.pos[2]," to ",lr.pos[3],")")
  lr.neg <- round(riskratio(t(z)[2:1,])$measure[2,],2)
  lr.neg <- paste0(lr.neg[1]," (",lr.neg[2]," to ",lr.neg[3],")")
  or <- round(oddsratio(t(z)[2:1,2:1])$measure[2,],2)
  or <- paste0(or[1]," (",or[2]," to ",or[3],")")
  
  tab1$N[i] <- sum(z)
  tab1$Prev[i] <- sum(z[,1])/sum(z)
  tab1$TP[i] <- z[1,1]
  tab1$FN[i] <- z[2,1]
  tab1$FP[i] <- z[1,2]
  tab1$TN[i] <- z[2,2]
  
  access <- c("proportion","lower","upper")
  pt <- round(binom.exact(z[1,1],sum(z[,1]))[access]*100,1)
  pt <- paste0(pt[1]," (",pt[2]," to ",pt[3],")")
  tab1$Sens[i] <- pt
  
  access <- c("proportion","lower","upper")
  pt <- round(binom.exact(z[2,2],sum(z[,2]))[access]*100,1)
  pt <- paste0(pt[1]," (",pt[2]," to ",pt[3],")")
  tab1$Spec[i] <- pt
  
  access <- c("proportion","lower","upper")
  pt <- round(binom.exact(sum(z[,1]),sum(z))[access]*100,1)
  pt <- paste0(pt[1]," (",pt[2]," to ",pt[3],")")
  tab1$Prev[i] <- pt
  
  access <- c("proportion","lower","upper")
  pt <- round(binom.exact(z[1,1],sum(z[1,]))[access]*100,1)
  pt <- paste0(pt[1]," (",pt[2]," to ",pt[3],")")
  tab1$PPV[i] <- pt
  
  access <- c("proportion","lower","upper")
  pt <- round(binom.exact(z[2,2],sum(z[2,]))[access]*100,1)
  pt <- paste0(pt[1]," (",pt[2]," to ",pt[3],")")
  tab1$NPV[i] <- pt
  
  tab1$LR.pos[i] <- lr.pos
  tab1$LR.neg[i] <- lr.neg
  tab1$OR[i] <- or
  rm(i,te,co,dat,y,x,z,lr.pos,lr.neg,or,access,pt)
}

View(tab1)
# Warnings due to small sample

####  For all those with NTpro readings, split by age group, separate analysis (rule in, age-adjusted)

#   Empty table with diagnostic accuracy parameters
Test <- rep(c("nt1_result"), times = 3)
Cutoff <- c(125,250,500)

Agegp <- c("<50 years", "50-75 years", "75 years+")
tab2 <- data.frame(Test, Cutoff, Agegp, N = NA, 
                   TP = NA, FN = NA, FP = NA, TN = NA, 
                   Sens = NA, Spec = NA,
                   Prev = NA, 
                   PPV = NA, NPV = NA,
                   LR.pos = NA, LR.neg = NA, OR = NA)


#   Fill in the table:
for (i in 1:nrow(tab2)){
  # i <- 3
  te <- Test[i]
  co <- Cutoff[i]
  ag <- Agegp[i]
  dat <- subset(df2, is.na(get(te))==FALSE & ag==agecat3)
  # Subset where there are no NAs for te
  y <- factor(dat$diag, levels = c(1,0), labels = c("D+ (HF)","D- (NO HF)"))  
  x <- factor(as.numeric(dat[,te]>=co), levels = c(1,0), labels = paste(c("+ (>=","- (<"),co,")"))
  z <- table(x,y)
  
  lr.pos <- round(riskratio(t(z)[2:1,2:1])$measure[2,],2)
  lr.pos <- paste0(lr.pos[1]," (",lr.pos[2]," to ",lr.pos[3],")")
  lr.neg <- round(riskratio(t(z)[2:1,])$measure[2,],2)
  lr.neg <- paste0(lr.neg[1]," (",lr.neg[2]," to ",lr.neg[3],")")
  or <- round(oddsratio(t(z)[2:1,2:1])$measure[2,],2)
  or <- paste0(or[1]," (",or[2]," to ",or[3],")")
  
  tab2$N[i] <- sum(z)
  tab2$Prev[i] <- sum(z[,1])/sum(z)
  tab2$TP[i] <- z[1,1]
  tab2$FN[i] <- z[2,1]
  tab2$FP[i] <- z[1,2]
  tab2$TN[i] <- z[2,2]
  
  access <- c("proportion","lower","upper")
  pt <- round(binom.exact(z[1,1],sum(z[,1]))[access]*100,1)
  pt <- paste0(pt[1]," (",pt[2]," to ",pt[3],")")
  tab2$Sens[i] <- pt
  
  access <- c("proportion","lower","upper")
  pt <- round(binom.exact(z[2,2],sum(z[,2]))[access]*100,1)
  pt <- paste0(pt[1]," (",pt[2]," to ",pt[3],")")
  tab2$Spec[i] <- pt
  
  access <- c("proportion","lower","upper")
  pt <- round(binom.exact(sum(z[,1]),sum(z))[access]*100,1)
  pt <- paste0(pt[1]," (",pt[2]," to ",pt[3],")")
  tab2$Prev[i] <- pt
  
  access <- c("proportion","lower","upper")
  pt <- round(binom.exact(z[1,1],sum(z[1,]))[access]*100,1)
  pt <- paste0(pt[1]," (",pt[2]," to ",pt[3],")")
  tab2$PPV[i] <- pt
  
  access <- c("proportion","lower","upper")
  pt <- round(binom.exact(z[2,2],sum(z[2,]))[access]*100,1)
  pt <- paste0(pt[1]," (",pt[2]," to ",pt[3],")")
  tab2$NPV[i] <- pt
  
  tab2$LR.pos[i] <- lr.pos
  tab2$LR.neg[i] <- lr.neg
  tab2$OR[i] <- or
  rm(i,te,co,dat,ag,y,x,z,lr.pos,lr.neg,or,access,pt)
}

View(tab2)

####    For all those with NTpro readings, split by age group, combined analysis (rule in, age-adjusted combined)


#   Empty table with diagnostic accuracy parameters
Test <- rep(c("nt1_result"), times = 3)
Cutoff <- c(125,250,500)
Agegp <- c("<50 years", "50-75 years", "75 years+")
tab3 <- data.frame(Test, Cutoff, Agegp, N = NA, 
                   TP = NA, FN = NA, FP = NA, TN = NA, 
                   Sens = NA, Spec = NA,
                   Prev = NA, 
                   PPV = NA, NPV = NA,
                   LR.pos = NA, LR.neg = NA, OR = NA)

Test2 <-"nt1_result"
Cutoff2 <-0
Agegp2 <-"All"
tab4 <- data.frame(Test2, Cutoff2, Agegp2, N = NA, 
                   TP = NA, FN = NA, FP = NA, TN = NA, 
                   Sens = NA, Spec = NA,
                   Prev = NA, 
                   PPV = NA, NPV = NA,
                   LR.pos = NA, LR.neg = NA, OR = NA)


#   Fill in the tables:

cTP <- 0
cTN <- 0
cFP <- 0
cFN <- 0

for (i in 1:nrow(tab3)){
  # i <- 3
  te <- Test[i]
  co <- Cutoff[i]
  ag <- Agegp[i]
  dat <- subset(df2, is.na(get(te))==FALSE & ag==agecat3)
  # Subset where there are no NAs for te
  y <- factor(dat$diag, levels = c(1,0), labels = c("D+ (HF)","D- (NO HF)"))  
  x <- factor(as.numeric(dat[,te]>=co), levels = c(1,0), labels = paste(c("+ (>=","- (<"),co,")"))
  z <- table(x,y)
  print(z)
  cTP <- cTP+z[1,1]
  cFN <- cFN+z[2,1]
  cFP <- cFP+z[1,2]
  cTN <- cTN+z[2,2]
  print(cTP)
  print(cFN)
  print(cFP)
  print(cTN)
  
  tab3$N[i] <- sum(z)
  tab3$Prev[i] <- sum(z[,1])/sum(z)
  tab3$TP[i] <- z[1,1]
  tab3$FN[i] <- z[2,1]
  tab3$FP[i] <- z[1,2]
  tab3$TN[i] <- z[2,2]
  
  rm(i,te,co,dat,ag,y,x)
}

# Replace elements of z with the combined results
z[1,1] <- cTP
z[2,1] <- cFN
z[1,2] <- cFP 
z[2,2] <- cTN

tab4$N <- sum(z)
tab4$Prev <- sum(z[,1])/sum(z)
tab4$TP <- z[1,1]
tab4$FN <- z[2,1]
tab4$FP <- z[1,2]
tab4$TN <- z[2,2]

lr.pos <- round(riskratio(t(z)[2:1,2:1])$measure[2,],2)
lr.pos <- paste0(lr.pos[1]," (",lr.pos[2]," to ",lr.pos[3],")")
lr.neg <- round(riskratio(t(z)[2:1,])$measure[2,],2)
lr.neg <- paste0(lr.neg[1]," (",lr.neg[2]," to ",lr.neg[3],")")
or <- round(oddsratio(t(z)[2:1,2:1])$measure[2,],2)
or <- paste0(or[1]," (",or[2]," to ",or[3],")")

access <- c("proportion","lower","upper")
pt <- round(binom.exact(z[1,1],sum(z[,1]))[access]*100,1)
pt <- paste0(pt[1]," (",pt[2]," to ",pt[3],")")
tab4$Sens <- pt

access <- c("proportion","lower","upper")
pt <- round(binom.exact(z[2,2],sum(z[,2]))[access]*100,1)
pt <- paste0(pt[1]," (",pt[2]," to ",pt[3],")")
tab4$Spec <- pt

access <- c("proportion","lower","upper")
pt <- round(binom.exact(sum(z[,1]),sum(z))[access]*100,1)
pt <- paste0(pt[1]," (",pt[2]," to ",pt[3],")")
tab4$Prev <- pt

access <- c("proportion","lower","upper")
pt <- round(binom.exact(z[1,1],sum(z[1,]))[access]*100,1)
pt <- paste0(pt[1]," (",pt[2]," to ",pt[3],")")
tab4$PPV <- pt

access <- c("proportion","lower","upper")
pt <- round(binom.exact(z[2,2],sum(z[2,]))[access]*100,1)
pt <- paste0(pt[1]," (",pt[2]," to ",pt[3],")")
tab4$NPV <- pt

tab4$LR.pos <- lr.pos
tab4$LR.neg <- lr.neg
tab4$OR <- or
rm(z,lr.pos,lr.neg,or,access,pt)

View(tab4)

# Collect results into a single table

tab4 <- tab4 %>% rename("Test"="Test2",
                        "Cutoff" = "Cutoff2",
                        "Agegp" = "Agegp2")
tab5 <- bind_rows(tab1,tab2,tab4)
View(tab5)

# Tidy up and format table
tab5$Cutoff <- as.character(tab5$Cutoff)
tab5$Cutoff[6] <-"Age-adjusted"
tab5$Test <- NULL
tab5 <- tab5[,c(1:3,10,4:9,11:15)]
rm(Agegp, Agegp2,cFN, cTN, cTP, cFP, Cutoff, Cutoff2,  Test2)

tab6 <-as.data.frame(t(tab5))

labs <- c("Cutoff","Agegp", "N", "TP","FN", "FP","TN", "Sens", "Spec","Prev", "PPV","NPV","LR.pos", "LR.neg", "OR" )
test_lab <- c("Cutoff, pg/ml", "Age group", "N","TP, n","FN, n", "FP, n", "TN, n", "Sensitivity, % (95% CI)",
              "Specificity, % (95% CI)", "Prevalence, % (95% CI)", "PPV, % (95% CI)","NPV, % (95% CI)",
              "LR+ (95% CI)","LR- (95% CI)", "DOR (95% CI)")

tab6$Test <- rownames(tab6)
tab6$Test <- test_lab[match(tab6$Test, labs)]
rownames(tab6) <- 1:nrow(tab6)
tab6 <- tab6[,c(7,1,3:6,2)]
tab6 <- tab6 %>% rename("Rule-out, <125 pg/ml"="V1",
                        "High risk rule-in >=2000 pg/ml"="V2",
                        "Rule-in >=125 pg/ml, age <50 years only"="V3", 
                        "Rule-in >=250 pg/ml, age 50 to 75 years only"="V4",
                        "Rule-in >=500 pg/ml, age 75 years+ only"="V5", 
                        "Age-adjusted rule-in"="V6")

tab6 <- tab6[c(3:15),]

View(tab6)
# Select output:

write.csv(tab6,paste0("/workspace/test/diagnostic_accuracy_all_",Sys.Date(),".csv"))
# write.csv(tab6,paste0("/workspace/test/diagnostic_accuracy_copd1_",Sys.Date(),".csv"))
# write.csv(tab6,paste0("/workspace/test/diagnostic_accuracy_copd0_",Sys.Date(),".csv"))
# write.csv(tab6,paste0("/workspace/test/diagnostic_accuracy_hyper1_",Sys.Date(),".csv"))
# write.csv(tab6,paste0("/workspace/test/diagnostic_accuracy_hyper0_",Sys.Date(),".csv"))
# write.csv(tab6,paste0("/workspace/test/diagnostic_accuracy_diabetes1_",Sys.Date(),".csv"))
# write.csv(tab6,paste0("/workspace/test/diagnostic_accuracy_diabetesd0_",Sys.Date(),".csv"))
# write.csv(tab6,paste0("/workspace/test/diagnostic_accuracy_dep1_",Sys.Date(),".csv"))
# write.csv(tab6,paste0("/workspace/test/diagnostic_accuracy_dep0_",Sys.Date(),".csv"))
# write.csv(tab6,paste0("/workspace/test/diagnostic_accuracy_obese1_",Sys.Date(),".csv"))
# write.csv(tab6,paste0("/workspace/test/diagnostic_accuracy_obese0_",Sys.Date(),".csv"))


# END OF CODE




