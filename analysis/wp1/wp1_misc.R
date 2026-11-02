


wp1_ethnicity <- wp1_all %>%
  group_by(year, age_group, ethnicity_cat) %>%
  summarise(hf_emerg = sum(hf_diagnosis_emerg == TRUE, na.rm = TRUE ),
            hf_primary = sum(hf_diagnosis_primary == TRUE, na.rm = TRUE),
            hf_any = sum(hf_diagnosis_any == TRUE, na.rm = TRUE),
            hf_ae = sum(hf_diagnosis_ec == TRUE, na.rm = TRUE),
            hf_death = sum(hf_death == TRUE, na.rm = TRUE),
            pop = n()) %>%
  ungroup() %>%
  select(c(year, hf_emerg, hf_primary, hf_any, age_group, ethnicity_cat, pop)) %>%
  mutate(hf_emerg_rate = hf_emerg / pop * 100000,
         hf_primary_rate = hf_primary / pop * 100000)

a <- ggplot(wp1_ethnicity) +
  geom_line(aes(x = year, y = hf_emerg_rate, colour = age_group)) +
  facet_wrap(~ethnicity_cat) +
  scale_colour_viridis_d() +
  scale_y_continuous(limits = c(0, 35000)) +
  xlab("Year") + ylab("Rate per 100,000") +
  labs(title="Emergency diagnosis") +
  theme_bw() +
  theme(strip.background = element_blank(),
        strip.text= element_text(hjust = 0),
        legend.title = element_blank())

b <- ggplot(wp1_ethnicity) +
  geom_line(aes(x = year, y = hf_primary_rate, colour = age_group)) +
  facet_wrap(~ethnicity_cat) +
  scale_colour_viridis_d() +
  scale_y_continuous(limits = c(0, 10000)) +
  xlab("Year") + ylab("Rate per 100,000") +
  labs(title = "Community diagnosis") +
  theme_bw() +
  theme(strip.background = element_blank(),
        strip.text= element_text(hjust = 0),
        legend.title = element_blank())


ggarrange(a, b, nrow = 2)





wp1_age <- wp1_all %>%
  group_by(year, age_group) %>%
  summarise(hf_emerg = sum(hf_diagnosis_emerg == TRUE, na.rm = TRUE ),
            hf_primary = sum(hf_diagnosis_primary == TRUE, na.rm = TRUE),
            hf_any = sum(hf_diagnosis_any == TRUE, na.rm = TRUE),
            hf_ae = sum(hf_diagnosis_ec == TRUE, na.rm = TRUE),
            hf_death = sum(hf_death == TRUE, na.rm = TRUE),
            pop = n(), 
            ptime = sum(end_date - patient_index_date)) %>%
  ungroup() %>%
  select(c(year, hf_emerg, hf_primary, hf_any, hf_death, hf_ae, age_group, pop)) %>%
  mutate(hf_emerg_rate = hf_emerg / pop * 100000,
         hf_primary_rate = hf_primary / pop * 100000, 
         hf_ae_rate = hf_ae / pop * 100000,
         hf_death_rate = hf_death / pop * 100000,
         hf_any_rate = hf_any/pop * 100000
  )



wp1_agesex <- wp1_all %>%
  group_by(year, age_group, sex) %>%
  summarise(hf_emerg = sum(hf_diagnosis_emerg == TRUE, na.rm = TRUE ),
            hf_primary = sum(hf_diagnosis_primary == TRUE, na.rm = TRUE),
            hf_any = sum(hf_diagnosis_any == TRUE, na.rm = TRUE),
            hf_ae = sum(hf_diagnosis_ec == TRUE, na.rm = TRUE),
            hf_death = sum(hf_death == TRUE, na.rm = TRUE),
            pop = n()) %>%
  ungroup() %>%
  select(c(year, hf_emerg, hf_primary, hf_any, hf_death, hf_ae, age_group, sex, pop)) %>%
  mutate(hf_emerg_rate = hf_emerg / pop * 100000,
         hf_primary_rate = hf_primary / pop * 100000, 
         hf_ae_rate = hf_ae / pop * 100000,
         hf_death_rate = hf_death / pop * 100000,
         hf_any_rate = hf_any/pop * 100000
  )

a <- ggplot(wp1_agesex) +
  geom_line(aes(x = year, y = hf_emerg_rate, colour = age_group)) +
  facet_wrap(~sex) +
  scale_colour_viridis_d() +
  scale_y_continuous(limits = c(0, 22000)) +
  xlab("Year") + ylab("Rate per 100,000") +
  labs(title="Emergency diagnosis") +
  theme_bw() +
  theme(strip.background = element_blank(),
        strip.text= element_text(hjust = 0),
        legend.title = element_blank())

b <- ggplot(wp1_agesex) +
  geom_line(aes(x = year, y = hf_primary_rate, colour = age_group)) +
  facet_wrap(~sex) +
  scale_colour_viridis_d() +
  scale_y_continuous(limits = c(0, 2000)) +
  xlab("Year") + ylab("Rate per 100,000") +
  labs(title = "Community diagnosis") +
  theme_bw() +
  theme(strip.background = element_blank(),
        strip.text= element_text(hjust = 0),
        legend.title = element_blank())

ggarrange(a, b, nrow = 2)


primary <- wp1_agesex %>%
  select(c(year, hf_primary_rate, age_group, sex)) %>%
  mutate(location = "Community") %>%
  rename(rate = hf_primary_rate)

emerg <- wp1_agesex %>%
  select(c(year, hf_emerg_rate, age_group, sex)) %>%
  mutate(location = "Emergency") %>%
  rename(rate = hf_emerg_rate)

both <- rbind(primary, emerg) 

ggplot(both) +
  geom_bar(aes(y= rate, x = year, group=location, fill = location), stat="identity", position = position_dodge()) +
  facet_wrap(~age_group) +
  scale_fill_viridis_d() +
  xlab("Year") + ylab("Rate per 100,000") +
  theme_bw() +
  theme(strip.background = element_blank(),
        strip.text= element_text(hjust = 0),
        legend.title = element_blank())

ggplot(subset(both, sex == "Female")) +
  geom_line(aes(y= rate, x = year, group=location, colour = location)) +
  facet_wrap(~age_group ) +
  scale_colour_viridis_d() +
  xlab("Year") + ylab("Rate per 100,000") +
  theme_bw() +
  theme(strip.background = element_blank(),
        strip.text= element_text(hjust = 0),
        legend.title = element_blank())




#######


clean2.fn <- function(df){
  df %>%
    mutate(hf_diagnosis_primary_3yrs = (hf_diagnosis_primary_date >= patient_index_date) & 
             (hf_diagnosis_primary_date < patient_index_date + years(3)),
           hf_diagnosis_apc_3yrs = (hf_diagnosis_apc_date >= patient_index_date) & 
             (hf_diagnosis_apc_date < patient_index_date + years(3)),
           hf_diagnosis_ec_3yrs = (hf_diagnosis_ec_date >= patient_index_date) & 
             (hf_diagnosis_ec_date < patient_index_date + years(3)),
           hf_death_3yrs = (hf_death_date >= patient_index_date) & 
             (hf_death_date < patient_index_date + years(3)),
           hf_diagnosis_emerg = (hf_diagnosis_emerg_date >= patient_index_date) & 
             (hf_diagnosis_emerg_date < patient_index_date + years(3)),
           hf_diagnosis_any = (hf_diagnosis_emerg | hf_diagnosis_primary ))
}


wp1_covid <- wp1_2020 %>%
  clean2.fn()

mutate()





#write.csv(wp1_common, "C:/Users/aschaffer/OneDrive - Nexus365/Documents/GitHub/reducehf/output/dataset_wp1_common.csv")