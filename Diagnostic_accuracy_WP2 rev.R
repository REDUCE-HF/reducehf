# Diagnostic_accuracy_WP2rev.R
# Script for diagnostic accuracy of NP testing for WP2 of the REDUCE HF project
# By sex, age group and BMI cat for each core group
# KS Taylor


# Search for TEMP
# Only running for all 

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

# TEMP######################################
# boost dataset and range of NT values to try to get the code working



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
td5$bmi<-42
summary(td5$bmi)

td6 <-df
td6$diag<-1

td7 <-df

td8 <-df
td8$bmi<-16
summary(td8$nt1_result)
td8$nt1_result <- td8$nt1_result*11
summary(td8$nt1_result)

td9 <-df
td9$bmi<-24
summary(td9$nt1_result)
td9$nt1_result <- td9$nt1_result*11
summary(td9$nt1_result)

td10 <-df
td10$bmi<-32
summary(td10$nt1_result)
td10$nt1_result <- td10$nt1_result*11

td11 <-df
td11$bmi<-37
summary(td11$nt1_result)
td11$nt1_result <- td11$nt1_result*11

td12<-df
table(td12$diag)
td12$diag<-1
summary(td12$nt1_result)

merged <-rbind(td1,td2,td3,td4,td5, td6,td7,td8, td9,td10,td11, td12)
df <-merged
summary(df$bmi)

rm(td1,td2,td3,td4,td5, td6,td7,td8,td9,td10,td11,td12, merged)
# END OF TEMP###########################################

all(!is.na(df$nt1_date))
all(!is.na(df$nt1_result))
# All have NT pro test and a test result

# Select dataset 
# QUERY To add MLTCs
# All have NT==1
df <- subset(df, NT==1) 
# df <- subset(df, NT==1 & copd==1)
# df <- subset(df, NT==1 & copd==0)
# df <- subset(df, NT==1 & hypertension==1)
# df <- subset(df, NT==1 & hypertension==0)
# df <- subset(df, NT==1 & diabetes==1)
# df <- subset(df, NT==1 & diabetes==0)
# df <- subset(df, NT==1 & deprived=="Bottom quintile")
# df <- subset(df, NT==1 & deprived=="Not deprived")
# df <- subset(df, NT==1 & obesity==1)
# df <- subset(df, NT==1 & obesity==0)

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


# Count those with HF diagnosis
nrow(subset(df, diag == 1))

# Repeat for age groups
table(df$agecat3)
nrow(subset(df, diag == 1 & age<50))
nrow(subset(df, diag == 1 & age>=50 & age<75))
nrow(subset(df, diag == 1 & age>=75))

# Repeat for WHO BMI categories
nrow(subset(df, diag == 1 & bmi<18.5)) 
nrow(subset(df, diag == 1 & bmi>=18.5 & bmi<25))
nrow(subset(df, diag == 1 & bmi>=25 & bmi<30))
nrow(subset(df, diag == 1 & bmi>=30 & bmi<35))
nrow(subset(df, diag == 1 & bmi>=35 & bmi<40))
nrow(subset(df, diag == 1 & bmi>=40))

# repeat for sex categories
nrow(subset(df, diag == 1 & sex=="female"))
nrow(subset(df, diag == 1 & sex=="male"))

##### Diagnosis of HF
##### Sex subgroup
##### Male

df2<-subset(df, sex=="male")

summary(df2$nt1_result)  
#max =2278

#   Empty table with diagnostic accuracy parameters
Test <- rep(c("nt1_result"), times = 3)
Cutoff <- c(125,400, 2000)
tab1 <- data.frame(Test, Cutoff, N = NA,
                   TP = NA, FN = NA, FP = NA, TN = NA,
                   Sens = NA, Spec = NA,
                   Prev = NA,
                   PPV = NA, NPV = NA,
                   LR.pos = NA, LR.neg = NA, OR = NA)
#   Fill in the table:
for (i in 1:nrow(tab1)){
  # i <- 3
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

##### Female

df2<-subset(df, sex=="female")

summary(df2$nt1_result)  
#max =2311  

#   Empty table with diagnostic accuracy parameters
Test <- rep(c("nt1_result"), times = 3)
Cutoff <- c(125,400, 2000)
tab2 <- data.frame(Test, Cutoff, N = NA,
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
  rm(i,te,co,dat,y,x,z,lr.pos,lr.neg,or,access,pt)
}

View(tab2)

tab3 <- bind_rows(tab1,tab2)
View(tab3)

# Tidy up and format table
tab3$Cutoff <- as.character(tab3$Cutoff)
tab3$Test <- NULL
tab3 <- tab3[,c(1:2,9,3:8,10:14)]
rm(Cutoff,Test)

tab4 <-as.data.frame(t(tab3))

labs <- c("Cutoff","N", "TP","FN", "FP","TN", "Sens", "Spec","Prev", "PPV","NPV","LR.pos", "LR.neg", "OR" )
test_lab <- c("Cutoff, pg/ml","N","TP, n","FN, n", "FP, n", "TN, n", "Sensitivity, % (95% CI)",
              "Specificity, % (95% CI)", "Prevalence, % (95% CI)", "PPV, % (95% CI)","NPV, % (95% CI)",
              "LR+ (95% CI)","LR- (95% CI)", "DOR (95% CI)")

tab4$Test <- rownames(tab4)
tab4$Test <- test_lab[match(tab4$Test, labs)]
rownames(tab4) <- 1:nrow(tab4)
tab4 <- tab4[,c(7,1:6)]
tab4 <- tab4 %>% rename("Cutoff >=125 pg/ml, male"="V1", 
                        "Cutoff >=400 pg/ml, male"="V2",
                        "Cutoff >=2000 pg/ml, male"="V3", 
                        "Cutoff >=125 pg/ml, female"="V4", 
                        "Cutoff >=400 pg/ml, female"="V5",
                        "Cutoff >=2000 pg/ml, female"="V6")

tab4 <- tab4[c(2:14),]
rm(labs, test_lab)  
View(tab4)
#   Save the table:
write.csv(tab4,paste0("/workspace/test/diagnostic_accuracy_by_sex_",btable,Sys.Date(),".csv"), row.names=FALSE)
rm(tab1,tab2,tab3,tab4)


# ##### BMI categories (WHO classification)

##### WHO class underweight

df2 <- subset(df, bmi<18.5)
summary(df2$nt1_result)  
# debug

d1 <-subset(df2,nt1_result>=2000 & diag==1)
d2 <-subset(df2,nt1_result>=2000 & diag==0)
d3 <-subset(df2,nt1_result<2000 & diag==1)
d4 <-subset(df2,nt1_result<2000 & diag==0)

nrow(d1)
nrow(d2)
nrow(d3)
nrow(d4)

#   Empty table with diagnostic accuracy parameters
Test <- rep(c("nt1_result"), times = 3)
Cutoff <- c(125,400,2000)
tab1 <- data.frame(Test, Cutoff, N = NA,
                   TP = NA, FN = NA, FP = NA, TN = NA,
                   Sens = NA, Spec = NA,
                   Prev = NA,
                   PPV = NA, NPV = NA,
                   LR.pos = NA, LR.neg = NA, OR = NA)
#   Fill in the table:
for (i in 1:nrow(tab1)){
  # i <- 3
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

# Tidy up and format table
tab1$Cutoff <- as.character(tab1$Cutoff)
tab1$Test <- NULL
tab1 <- tab1[,c(1:2,9,3:8,10:14)]
rm(Cutoff,Test)

tab2 <-as.data.frame(t(tab1))

labs <- c("Cutoff","N", "TP","FN", "FP","TN", "Sens", "Spec","Prev", "PPV","NPV","LR.pos", "LR.neg", "OR" )
test_lab <- c("Cutoff, pg/ml","N","TP, n","FN, n", "FP, n", "TN, n", "Sensitivity, % (95% CI)",
              "Specificity, % (95% CI)", "Prevalence, % (95% CI)", "PPV, % (95% CI)","NPV, % (95% CI)",
              "LR+ (95% CI)","LR- (95% CI)", "DOR (95% CI)")

tab2$Test <- rownames(tab2)
tab2$Test <- test_lab[match(tab2$Test, labs)]
rownames(tab2) <- 1:nrow(tab2)
tab2 <- tab2[,c(4,1:3)]
tab2 <- tab2 %>% rename("Cutoff >=125 pg/ml"="V1", 
                        "Cutoff >=400 pg/ml"="V2",
                        "Cutoff >=2000 pg/ml"="V3")

rm(labs, test_lab)  
View(tab2)
#   Save the table:
write.csv(tab2,paste0("/workspace/test/diagnostic_accuracy_underwt_",btable,Sys.Date(),".csv"), row.names=FALSE)
rm(tab1,tab2)


##### WHO class normal weight

df2 <- subset(df, bmi>=18.5 & bmi<25)
summary(df2$nt1_result)  


#   Empty table with diagnostic accuracy parameters
Test <- rep(c("nt1_result"), times = 3)
Cutoff <- c(125,400,2000)
tab1 <- data.frame(Test, Cutoff, N = NA,
                   TP = NA, FN = NA, FP = NA, TN = NA,
                   Sens = NA, Spec = NA,
                   Prev = NA,
                   PPV = NA, NPV = NA,
                   LR.pos = NA, LR.neg = NA, OR = NA)
#   Fill in the table:
for (i in 1:nrow(tab1)){
  # i <- 3
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

# Tidy up and format table
tab1$Cutoff <- as.character(tab1$Cutoff)
tab1$Test <- NULL
tab1 <- tab1[,c(1:2,9,3:8,10:14)]
rm(Cutoff,Test)

tab2 <-as.data.frame(t(tab1))

labs <- c("Cutoff","N", "TP","FN", "FP","TN", "Sens", "Spec","Prev", "PPV","NPV","LR.pos", "LR.neg", "OR" )
test_lab <- c("Cutoff, pg/ml","N","TP, n","FN, n", "FP, n", "TN, n", "Sensitivity, % (95% CI)",
              "Specificity, % (95% CI)", "Prevalence, % (95% CI)", "PPV, % (95% CI)","NPV, % (95% CI)",
              "LR+ (95% CI)","LR- (95% CI)", "DOR (95% CI)")

tab2$Test <- rownames(tab2)
tab2$Test <- test_lab[match(tab2$Test, labs)]
rownames(tab2) <- 1:nrow(tab2)
tab2 <- tab2[,c(4,1:3)]
tab2 <- tab2 %>% rename("Cutoff >=125 pg/ml"="V1", 
                        "Cutoff >=400 pg/ml"="V2",
                        "Cutoff >=2000 pg/ml"="V3")

rm(labs, test_lab)  
View(tab2)
#   Save the table:
write.csv(tab2,paste0("/workspace/test/diagnostic_accuracy_normalwt_",btable,Sys.Date(),".csv"), row.names=FALSE)
rm(tab1,tab2)

##### WHO class overweight

df2 <- subset(df, bmi>=25 & bmi<30)
summary(df2$nt1_result)  


#   Empty table with diagnostic accuracy parameters
Test <- rep(c("nt1_result"), times = 3)
# TEMP 
#Cutoff <- c(125,400,2000)
Cutoff <- c(125,400,700)
tab1 <- data.frame(Test, Cutoff, N = NA,
                   TP = NA, FN = NA, FP = NA, TN = NA,
                   Sens = NA, Spec = NA,
                   Prev = NA,
                   PPV = NA, NPV = NA,
                   LR.pos = NA, LR.neg = NA, OR = NA)
#   Fill in the table:
for (i in 1:nrow(tab1)){
  # i <- 3
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

# Tidy up and format table
tab1$Cutoff <- as.character(tab1$Cutoff)
tab1$Test <- NULL
tab1 <- tab1[,c(1:2,9,3:8,10:14)]
rm(Cutoff,Test)

tab2 <-as.data.frame(t(tab1))

labs <- c("Cutoff","N", "TP","FN", "FP","TN", "Sens", "Spec","Prev", "PPV","NPV","LR.pos", "LR.neg", "OR" )
test_lab <- c("Cutoff, pg/ml","N","TP, n","FN, n", "FP, n", "TN, n", "Sensitivity, % (95% CI)",
              "Specificity, % (95% CI)", "Prevalence, % (95% CI)", "PPV, % (95% CI)","NPV, % (95% CI)",
              "LR+ (95% CI)","LR- (95% CI)", "DOR (95% CI)")

tab2$Test <- rownames(tab2)
tab2$Test <- test_lab[match(tab2$Test, labs)]
rownames(tab2) <- 1:nrow(tab2)
tab2 <- tab2[,c(4,1:3)]
tab2 <- tab2 %>% rename("Cutoff >=125 pg/ml"="V1", 
                        "Cutoff >=400 pg/ml"="V2",
                        "Cutoff >=2000 pg/ml"="V3")

rm(labs, test_lab)  
View(tab2)
#   Save the table:
write.csv(tab2,paste0("/workspace/test/diagnostic_accuracy_overwt_",btable,Sys.Date(),".csv"), row.names=FALSE)
rm(tab1,tab2)

##### WHO class obesity I

df2 <- subset(df, bmi>=30 & bmi<35)
summary(df2$nt1_result)  
# debug

d1 <-subset(df2,nt1_result>=2000 & diag==1)
d2 <-subset(df2,nt1_result>=2000 & diag==0)
d3 <-subset(df2,nt1_result<2000 & diag==1)
d4 <-subset(df2,nt1_result<2000 & diag==0)

nrow(d1)
nrow(d2)
nrow(d3)
nrow(d4)

#   Empty table with diagnostic accuracy parameters
Test <- rep(c("nt1_result"), times = 3)
# TEMP 
#Cutoff <- c(125,400,2000)
Cutoff <- c(125,400,700)
tab1 <- data.frame(Test, Cutoff, N = NA,
                   TP = NA, FN = NA, FP = NA, TN = NA,
                   Sens = NA, Spec = NA,
                   Prev = NA,
                   PPV = NA, NPV = NA,
                   LR.pos = NA, LR.neg = NA, OR = NA)
#   Fill in the table:
for (i in 1:nrow(tab1)){
  # i <- 3
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

# Tidy up and format table
tab1$Cutoff <- as.character(tab1$Cutoff)
tab1$Test <- NULL
tab1 <- tab1[,c(1:2,9,3:8,10:14)]
rm(Cutoff,Test)

tab2 <-as.data.frame(t(tab1))

labs <- c("Cutoff","N", "TP","FN", "FP","TN", "Sens", "Spec","Prev", "PPV","NPV","LR.pos", "LR.neg", "OR" )
test_lab <- c("Cutoff, pg/ml","N","TP, n","FN, n", "FP, n", "TN, n", "Sensitivity, % (95% CI)",
              "Specificity, % (95% CI)", "Prevalence, % (95% CI)", "PPV, % (95% CI)","NPV, % (95% CI)",
              "LR+ (95% CI)","LR- (95% CI)", "DOR (95% CI)")

tab2$Test <- rownames(tab2)
tab2$Test <- test_lab[match(tab2$Test, labs)]
rownames(tab2) <- 1:nrow(tab2)
tab2 <- tab2[,c(4,1:3)]
tab2 <- tab2 %>% rename("Cutoff >=125 pg/ml"="V1", 
                        "Cutoff >=400 pg/ml"="V2",
                        "Cutoff >=2000 pg/ml"="V3")

rm(labs, test_lab)  
View(tab2)
#   Save the table:
write.csv(tab2,paste0("/workspace/test/diagnostic_accuracy_obesityI_",btable,Sys.Date(),".csv"), row.names=FALSE)
rm(tab1,tab2)

##### WHO class obesity II

df2 <- subset(df, bmi>=35 & bmi<40)
summary(df2$nt1_result)  

# debug
 
d1 <-subset(df2,nt1_result>=1500 & diag==1)
d2 <-subset(df2,nt1_result>=1500 & diag==0)
d3 <-subset(df2,nt1_result<1500 & diag==1)
d4 <-subset(df2,nt1_result<1500 & diag==0)
d5 <-subset(df2, diag==1)
d6 <-subset(df2, diag==0)

nrow(d1)
nrow(d2)
nrow(d3)
nrow(d4)
nrow(d5)
summary(d5$nt1_result)
summary(d6$nt1_result)



#   Empty table with diagnostic accuracy parameters
Test <- rep(c("nt1_result"), times = 3)
# TEMP replacing 2000 with 400
#Cutoff <- c(125,400,2000)
Cutoff <- c(1500,1500,1500)
tab1 <- data.frame(Test, Cutoff, N = NA,
                   TP = NA, FN = NA, FP = NA, TN = NA,
                   Sens = NA, Spec = NA,
                   Prev = NA,
                   PPV = NA, NPV = NA,
                   LR.pos = NA, LR.neg = NA, OR = NA)
#   Fill in the table:
for (i in 1:nrow(tab1)){
  # i <- 3
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

# Tidy up and format table
tab1$Cutoff <- as.character(tab1$Cutoff)
tab1$Test <- NULL
tab1 <- tab1[,c(1:2,9,3:8,10:14)]
rm(Cutoff,Test)

tab2 <-as.data.frame(t(tab1))

labs <- c("Cutoff","N", "TP","FN", "FP","TN", "Sens", "Spec","Prev", "PPV","NPV","LR.pos", "LR.neg", "OR" )
test_lab <- c("Cutoff, pg/ml","N","TP, n","FN, n", "FP, n", "TN, n", "Sensitivity, % (95% CI)",
              "Specificity, % (95% CI)", "Prevalence, % (95% CI)", "PPV, % (95% CI)","NPV, % (95% CI)",
              "LR+ (95% CI)","LR- (95% CI)", "DOR (95% CI)")

tab2$Test <- rownames(tab2)
tab2$Test <- test_lab[match(tab2$Test, labs)]
rownames(tab2) <- 1:nrow(tab2)
tab2 <- tab2[,c(4,1:3)]
tab2 <- tab2 %>% rename("Cutoff >=125 pg/ml"="V1", 
                        "Cutoff >=400 pg/ml"="V2",
                        "Cutoff >=2000 pg/ml"="V3")

rm(labs, test_lab)  
View(tab2)
#   Save the table:
write.csv(tab2,paste0("/workspace/test/diagnostic_accuracy_obesityII_",btable,Sys.Date(),".csv"), row.names=FALSE)
rm(tab1,tab2)

##### WHO class obesity III

df2 <- subset(df, bmi>40)
summary(df2$nt1_result)  

# debug

d1 <-subset(df2,nt1_result>=400 & diag==1)
d2 <-subset(df2,nt1_result>=400 & diag==0)
d3 <-subset(df2,nt1_result<400 & diag==1)
d4 <-subset(df2,nt1_result<400 & diag==0)
d5 <-subset(df2, diag==1)
d6 <-subset(df2, diag==0)

nrow(d1)
nrow(d2)
nrow(d3)
nrow(d4)
nrow(d5)
summary(d5$nt1_result)
summary(d6$nt1_result)



#   Empty table with diagnostic accuracy parameters
Test <- rep(c("nt1_result"), times = 3)
# TEMP 
#Cutoff <- c(125,400,2000)
Cutoff <- c(125,125,125)
tab1 <- data.frame(Test, Cutoff, N = NA,
                   TP = NA, FN = NA, FP = NA, TN = NA,
                   Sens = NA, Spec = NA,
                   Prev = NA,
                   PPV = NA, NPV = NA,
                   LR.pos = NA, LR.neg = NA, OR = NA)
#   Fill in the table:
for (i in 1:nrow(tab1)){
  # i <- 3
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

# Tidy up and format table
tab1$Cutoff <- as.character(tab1$Cutoff)
tab1$Test <- NULL
tab1 <- tab1[,c(1:2,9,3:8,10:14)]
rm(Cutoff,Test)

tab2 <-as.data.frame(t(tab1))

labs <- c("Cutoff","N", "TP","FN", "FP","TN", "Sens", "Spec","Prev", "PPV","NPV","LR.pos", "LR.neg", "OR" )
test_lab <- c("Cutoff, pg/ml","N","TP, n","FN, n", "FP, n", "TN, n", "Sensitivity, % (95% CI)",
              "Specificity, % (95% CI)", "Prevalence, % (95% CI)", "PPV, % (95% CI)","NPV, % (95% CI)",
              "LR+ (95% CI)","LR- (95% CI)", "DOR (95% CI)")

tab2$Test <- rownames(tab2)
tab2$Test <- test_lab[match(tab2$Test, labs)]
rownames(tab2) <- 1:nrow(tab2)
tab2 <- tab2[,c(4,1:3)]
tab2 <- tab2 %>% rename("Cutoff >=125 pg/ml"="V1", 
                        "Cutoff >=400 pg/ml"="V2",
                        "Cutoff >=2000 pg/ml"="V3")

rm(labs, test_lab)  
View(tab2)
#   Save the table:
write.csv(tab2,paste0("/workspace/test/diagnostic_accuracy_obesityIII_",btable,Sys.Date(),".csv"), row.names=FALSE)
rm(tab1,tab2)


# END OF CODE




