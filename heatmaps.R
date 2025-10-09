# heatmaps.R

# ChatGPT search - how can I plot a heatmap  of England using R

# Where to get real boundaries / data
# England administrative boundaries: ONS Geography (UK), GADM, or rnaturalearth::ne_states(country="United Kingdom") for coarse subnational units.
# Smaller units (counties, LSOA, MSOA): download from the ONS Open Geography portal (shapefiles / GeoJSON).
# Raster sources: population density rasters (e.g., WorldPop, ONS), or generate from point observations.

# install.packages(c("sf","ggplot2","rnaturalearth","rnaturalearthdata","dplyr","viridis"))
install.packages("rnaturalearthhires")
install.packages("rnaturalearth")
install.packages("devtools")
install.packages ("rnaturalearthdata") 
devtools::install_github("ropensci/rnaturalearthhires")

library(sf)
library(ggplot2)
library(rnaturalearth)
library(rnaturalearthdata)
library(dplyr)
library(viridis)

# 1) get subnational units (states/provinces) for United Kingdom
uk_states <- rnaturalearth::ne_states(country = "United Kingdom", returnclass = "sf")

# 2) filter to England only
england <- uk_states %>% filter(geonunit == "England")

# Quick check
print(st_geometry_type(england))
plot(st_geometry(england))

# 3) create demo data — one row per administrative area inside England
# (if you have a value per county, replace this with your real data and join by name/ID)
set.seed(42)
england$demo_value <- runif(nrow(england), min = 0, max = 100)

# 4) plot choropleth with ggplot2
ggplot(england) +
  geom_sf(aes(fill = demo_value), size = 0.15, color = "white") +
  scale_fill_viridis(option = "magma", name = "Value", na.value = "grey80") +
  theme_minimal() +
  labs(title = "Choropleth of England (demo values)",
       caption = "Data: demo random values") +
  theme(axis.text = element_blank(), axis.ticks = element_blank())