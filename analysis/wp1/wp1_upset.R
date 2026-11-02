library(ComplexUpset)
library(ggplot2)
library(tidyverse)

wp1_upset <- wp1_all %>%
  mutate(female = (sex == "female"),
         white = (ethnicity_cat == "White"),
         nonwhite = (ethnicity_cat != "White"),

         male = (sex == "male"),
         most_deprived = (imd_quintile == "1")) %>%
  select(c(ckd, ihd, af, hypertension, copd, t2dm, housebound, substance_abuse, smi,
           female, male, white, black, asian))

wp1_upset[is.na(wp1_upset)] <- FALSE

groups = colnames(wp1_upset)

wp1_upset[groups] = wp1_upset[groups] == TRUE

upset(wp1_upset, groups, name = 'group', width_ratio=.1, keep_empty_groups=TRUE)

test <- wp1_upset %>%
  count(across(all_of(groups))) %>%
  mutate(prevalence = n / sum(n)) %>%
  arrange(desc(prevalence))
  