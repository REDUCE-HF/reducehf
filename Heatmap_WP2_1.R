# Heatmap_WP2_1.R

# Need one line per region
# TEMP
# count number male


rm(v)
rm(list=ls()) 

library(feather)
library(sf)
library(leaflet)
library(sf)
library(ggplot2)
library(dplyr)
library(viridis)


# Boundary datafile
# Strategic Health Authorities 
# East of England,SE, EM, SW, London, WM, NE, Y&H, NW (n=9)
# Source: Open Geography portal
# Website: https://geoportal.statistics.gov.uk/
# Search Terms: "Regions (December 2021) Boundaries" (selected  "EN BUC", downloaded geojson format)
# To display: Office for National Statistics licensed under the Open Government Licence v.3.0
regions <- st_read(here::here("test", "Regions_December_2021_EN_BUC_2022_5473375263085398332.geojson"))
names(regions)[names(regions)=="RGN21NM"] <- "region"
table(regions$region)
str(regions$region)
#Character

# Import files
# General datafile
df <- read_feather(here::here("test", "file4analysisWP2_1_COVID.feather"))
# Only for post-COVID WP2_1. 
any(grepl("region",names(df)))
grep("region",names(df), value=TRUE)
table(df$region)
str(df$region)
#Character

# Standardise region names
df$region[df$region=="East"] <- "East of England"

# Heat variable
# Obtain counts of  in each region
# TEMP heat variable
# should be count with (df$near_np)

table(df$sex, df$region)

df2 <- data.frame(table(df$sex, df$region))
df2 <- df2[df2$Var1=="male",]
names(df2)[names(df2)=="Var2"] <-"reg"
str(df2$reg)
#Factor 

df2$region<-as.character(df2$reg)

df2$region <-ifelse(df2$region=="1","East Midlands",df2$region)
df2$region <-ifelse(df2$region=="2","East of England",df2$region)
df2$region <-ifelse(df2$region=="3","London",df2$region)
df2$region <-ifelse(df2$region=="4","North East",df2$region)
df2$region <-ifelse(df2$region=="5","North West",df2$region)
df2$region <-ifelse(df2$region=="6","South East",df2$region)
df2$region <-ifelse(df2$region=="7","South West",df2$region)
df2$region <-ifelse(df2$region=="8","West Midlands",df2$region)
df2$region <-ifelse(df2$region=="9","Yorkshire and The Humber",df2$region)
str(df2$region)

# Merge data

merged<- regions %>%
  left_join(df2, by="region")


# 2) Create demo data - one row per English region
#set.seed(42)
#regions$demo_value <- runif(nrow(regions), min = 0, max = 100)


# 4) Plot choropleth with ggplot2
ggplot(merged) +
  geom_sf(aes(fill =Freq), size = 0.15, color = "white") +
  scale_fill_viridis(option = "magma", name = "Value", na.value = "grey80") +
  theme_minimal() +
  labs(title = "Choropleth of England by region (males)",
       caption = "Data:dummy data") +
  theme(axis.text = element_blank(), axis.ticks = element_blank())

