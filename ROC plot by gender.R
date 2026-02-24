# ROC plot by gender.R
# KTaylor
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
td12$nt1_result <-sample(c(125,400,2000), nrow(td12), replace=TRUE)


merged <-rbind(td1,td2,td3,td4,td5, td6,td7,td8, td9,td10,td11, td12)
df <-merged
summary(df$bmi)

rm(td1,td2,td3,td4,td5, td6,td7,td8,td9,td10,td11,td12, merged)
# END OF TEMP###########################################

dt1 <-subset(df, sex=="male")
dt2 <-subset(df, sex=="female")
summary(dt1$nt1_result)
hist(dt1$nt1_result)
summary(dt2$nt1_result)
hist(dt2$nt1_result)
rm(dt1,dt2)

#   Sex datasets    
nt1<- subset(df, sex=="male", c("nt1_result","diag"))
nt2 <- subset(df, sex=="female", c("nt1_result","diag")) 

#   Empty table with diagnostic accuracy parameters:

Male <- sort(unique(round(nt1$nt1_result)))
Female <- sort(unique(round(nt2$nt1_result)))

# For a quicker version with similar definition:
# bnp <- sort(c(seq(10,5000,10),35))
# nt <- sort(c(seq(20,10000,20),125))
Cutoff <- c(Male,Female)
Test <- c(rep("nt1_result",length(Male)),
          rep("nt1_result",length(Female)))
#Added
Gengp <- c(rep("male",length(Male)),
           rep("female",length(Female)))

tab <- data.frame(Test, Cutoff,Gengp,
                  #tab <- data.frame(Test, Cutoff,                   
                  TP = NA, FN = NA, FP = NA, TN = NA, 
                  Sens = NA, Sens_lower = NA, Sens_upper = NA, 
                  Spec = NA, Spec_lower = NA, Spec_upper = NA)
tab <- tab[order(tab$Test,tab$Cutoff),]
rownames(tab) <- NULL
rm(nt1,nt2,Cutoff,Test)

#   Fill in the table:
t0 <- Sys.time()
for (i in 1:nrow(tab)){
  te <- tab$Test[i]
  co <- tab$Cutoff[i]
  gen <- tab$Gengp[i]
  dat <- subset(df, is.na(get(te))==FALSE & sex==gen) 
  # dat <- get(te) - Jose's
  #dat <- subset(dta, is.na(get(te))==FALSE)
  y <- factor(dat$diag, levels = c(1,0), labels = c("D+ (HF)","D- (NO HF)"))  
  x <- factor(as.numeric(dat[,te]>=co), levels = c(1,0), labels = paste(c("+ (>=","- (<"),co,")"))
  z <- table(x,y)
  
  tab$TP[i] <- z[1,1]
  tab$FN[i] <- z[2,1]
  tab$FP[i] <- z[1,2]
  tab$TN[i] <- z[2,2]
  
  access <- c("proportion","lower","upper")
  pt <- round(as.numeric(binom.exact(z[1,1],sum(z[,1]))[access]*100),1)
  tab$Sens[i] <- pt[1]
  tab$Sens_lower[i] <- pt[2]
  tab$Sens_upper[i] <- pt[3]
  
  access <- c("proportion","lower","upper")
  pt <- round(as.numeric(binom.exact(z[2,2],sum(z[,2]))[access]*100),1)
  tab$Spec[i] <- pt[1]
  tab$Spec_lower[i] <- pt[2]
  tab$Spec_upper[i] <- pt[3]
  
  rm(i,te,co,dat,y,x,z,access,pt)
}
t1 <- Sys.time()
t1 - t0 # 24 mins
rm(t0,t1)

# Save table to use later
write.csv(tab,paste0("/workspace/test/diagnostic_accuracy_by_sex.csv"), row.names=FALSE)
#rm(tab)
#tab <- read.csv(paste0("/workspace/test/diagnostic_accuracy_by_sex.csv"))


################
#      AUC     #
# HF incidence #
################

nt1 <- subset(df, sex=="male", c("nt1_result","diag"))
dat <- nt1

y <- dat$diag
x <- dat$nt1_result
curve <- pROC::roc(y ~ x)
# x1 <- curve$specificities
# y1 <- curve$sensitivities
auc <- as.numeric(ci.auc(curve))
auc <- round(auc,3)
for (i in 1:3){
  a <- auc[i]
  a <- ifelse(nchar(a) < 5, paste0(a,"0"), a)
  a -> auc[i]
  rm(i,a)
}
auc1 <- paste0("AUC: ",auc[2]," (",auc[1]," to ",auc[3],")")
#curve.bnp.hf.inc <- curve
curve.M1.hf.inc <- curve
rm(dat,y,x,curve,auc)


nt2 <- subset(df, sex=="female", c("nt1_result","diag")) 

dat <- nt2
y <- dat$diag
x <- dat$nt1_result
curve <- pROC::roc(y ~ x)
# x2 <- curve$specificities
# y2 <- curve$sensitivities
auc <- as.numeric(ci.auc(curve))
auc <- round(auc,3)
for (i in 1:3){
  a <- auc[i]
  a <- ifelse(nchar(a) < 5, paste0(a,"0"), a)
  a -> auc[i]
  rm(i,a)
}
auc2 <- paste0("AUC: ",auc[2]," (",auc[1]," to ",auc[3],")")
#curve.nt.hf.inc <- curve
curve.M0.hf.inc <- curve

rm(dat,y,x,curve,auc)

# compare (unpaired) AUC/ROC curves
#pROC::roc.test(roc1 = curve.bnp.hf.inc,
#              roc2 = curve.nt.hf.inc,
#             paired = FALSE)

pROC::roc.test(roc1 = curve.M1.hf.inc,
               roc2 = curve.M0.hf.inc,
               paired = FALSE)

# local agreement/disagreement
# p.nt <- auc(curve.nt.hf.inc, partial.auc = c(0.75, 0), partial.auc.focus = "sp")
# p.nt1 <- ci.auc(p.nt, method = "bootstrap", boot.n = 1000)
# 
# p.bnp <- auc(curve.bnp.hf.inc, partial.auc = c(0.75, 0), partial.auc.focus = "sp")
# p.bnp1 <- ci.auc(p.bnp, method = "bootstrap", boot.n = 1000)
#   
# p.nt1; p.bnp1 # no difference
# rm(p.nt, p.bnp)

p.M0 <- auc(curve.M0.hf.inc, partial.auc = c(0.75, 0), partial.auc.focus = "sp")
p.M01 <- ci.auc(p.M0, method = "bootstrap", boot.n = 1000)

p.M1 <- auc(curve.M1.hf.inc, partial.auc = c(0.75, 0), partial.auc.focus = "sp")
p.M11 <- ci.auc(p.M1, method = "bootstrap", boot.n = 1000)

p.M01; p.M11 # no difference
rm(p.M0, p.M1)


# p.nt <- auc(curve.nt.hf.inc, partial.auc = c(1, 0.75), partial.auc.focus = "sp")
# p.nt2 <- ci.auc(p.nt, method = "bootstrap", boot.n = 1000)
# 
# p.bnp <- auc(curve.bnp.hf.inc, partial.auc = c(1, 0.75), partial.auc.focus = "sp")
# p.bnp2 <- ci.auc(p.bnp, method = "bootstrap", boot.n = 1000)
# 
# p.nt2; p.bnp2 # no difference
# 
# rm(p.nt1,p.nt2,p.bnp1,p.bnp2)
# rm(curve.bnp.hf.inc,curve.nt.hf.inc)

p.M0 <- auc(curve.M0.hf.inc, partial.auc = c(1, 0.75), partial.auc.focus = "sp")
p.M02 <- ci.auc(p.M0, method = "bootstrap", boot.n = 1000)

p.M1 <- auc(curve.M1.hf.inc, partial.auc = c(1, 0.75), partial.auc.focus = "sp")
p.M12 <- ci.auc(p.M1, method = "bootstrap", boot.n = 1000)

p.M02; p.M12 # no difference

rm(p.M01,p.M02,p.M11,p.M12)
rm(curve.M1.hf.inc,curve.M0.hf.inc)

# plot(x1,y1,type = "l",xlim = c(1,0), xlab = "Specificity", ylab = "Sensitivity", col = "red")
# lines(x2,y2, col = "blue")
# rm(x1,y1,x2,y2)

# rm(bnp_pg_ml,nt_pro_bnp_pg_ml)
rm(nt1,nt2)


##############
#  Figure 2  #
#  ROC plot  #
##############

#   Create the plot:
{
  # save as tiff
 tiff(filename = paste0("/workspace/test/ROC plot HF incidence by gender.tiff"),
      width = 480/72*600, height = 480/72*600, 
      res = 72/72*600, compression = "lzw")
  # Series
  
  
  NT1 <- tab$Gengp=="male"
  NT2 <- tab$Gengp=="female"
  
  
  # Plot:
  plot(x = tab$Spec, 
       y = tab$Sens, 
       type = "n",
       xlim = c(100,0),
       ylim = c(0,100),
       axes = FALSE,
       xlab = "",
       ylab = "",
       pch = 20,
       col = "black",
       cex = 1)
  
  # lines
  lines(x = tab$Spec[NT1], 
        y = tab$Sens[NT1],
        col = "#ED0000FF")
  lines(x = tab$Spec[NT2], 
        y = tab$Sens[NT2],
        col = "#00468BFF")
  
  # NICE and ESC thresholds
 c1 <- tab$Cutoff %in% c(125,400,2000) & NT1
 c2 <- tab$Cutoff %in% c(125,400,2000) & NT2
 # Don't need c2 but keeping it for flexibility

 points(x = tab$Spec[c1], y = tab$Sens[c1], col = "#ED0000FF", pch = 20)
 points(x = tab$Spec[c2], y = tab$Sens[c2], col = "#00468BFF", pch = 20)

 # label points
 text(x = tab$Spec[c1] + c(0,0,-2.5),
      y = tab$Sens[c1] + c(-2.5,-2.5,0),
      labels = c(125,400,2000),
      col = "#ED0000FF",
      cex = 0.50)
 text(x = tab$Spec[c2] + c(0,0,2.5),
      y = tab$Sens[c2] + c(2.5,2.5,2.5),
      labels = c(125,400,2000),
      col = "#00468BFF",
      cex = 0.50)
  
  # title
  title(main = "", cex.main = 1)
  
  # x axis and label
  axis(1, at = c(100,75,50,25,0), labels = c(100,75,50,25,0), lwd.ticks = 1, pos = 0, cex.axis = 1)
  #axis(1, at = c(100,90,80,70,60,50,40,30,20,10,0), labels = c(100,90,80,70,60,50,40,30,20,10,0), lwd.ticks = 1, pos = 0, cex.axis = 1)
  mtext(side = 1, line = 2, "Specificity (%)", font = 2, cex = 1)
  
  # y axis
  axis(2, at = seq(0,100,25), labels = seq(0,100,25), pos = 100, las = 2, cex.axis = 1)
  #axis(2, at = seq(0,100,10), labels = seq(0,100,10), pos = 100, las = 2, cex.axis = 1)
  mtext(side = 2, line = 2, "Sensitivity (%)", font = 2, cex = 1)
  
  # build box
  lines(x = c(0,0), y = c(0,100))
  lines(x = c(100,0), y = c(100,100))
  
  # legend text
  text(x = c(20), y = c(20), labels = "male", col = "#ED0000FF", adj = 1)
  text(x = c(20), y = c(35), labels = "female", col = "#00468BFF", adj = 1)
  
  # legend lines
  lines(x = c(15,10), y = c(20,20), col = "#ED0000FF")
  lines(x = c(15,10), y = c(35,35), col = "#00468BFF")
  
  # AUC values
  text(x = 30, y = 15, labels = auc1, col = "#ED0000FF")
  text(x = 30, y = 30, labels = auc2, col = "#00468BFF")
  
  # reference line
  lines(x = c(100,0), y = c(0,100), col = "black", lty = 2)
  
  # remove unnecessary objects
  #rm(NT1, NT2, c1, c2)
  
  # close plotting device
 dev.off()
}
# rm(tab,auc1,auc2)




### END OF CODE ###



