# Heatmap_WP2_1.R

rm(v)
rm(list=ls()) 

df <- read_feather(here::here("test", "file4analysisWP2_1_COVID.feather"))
# Only for post-COVID. Using COVID file for script development

any(grepl("region",names(df)))
grep("region",names(df), value=TRUE)
table(df$region)
# Has 9 SHAs
# East, South East, East Midlands, South West, London, West Midlands, North East, Yorkshire and the Humber, North West
# The source below has 10 SHAs
# East, South East Coast, South Central,East Midlands, South West, London, West Midlands, North East, Yorkshire and the Humber, North West

# Heat variable
table(df$near_np)
# The following code only runs outside Github. I don't know how to import the map.
# Messaged SLACK on Tues 10/12/25 but they are away all week for a conference. 
# someone replied saying they probably won't know. Messaged Andrea and Olivia as Marwa has python scripts for heat maps
# I can't read them.
# The heat variable is sha$demo_value

# Strategic Health Authority regional data (n=10)
# Source: University of Edinburgh Datashare
# Website: https://datashare.ed.ac.uk/
# Search Term: Strategic Health Authority (SHA) Boundaries (2006)
# Citation: McGarva, Guy. (2017). Strategic Health Authority (SHA) Boundaries (2006), [Dataset]. University of Edinburgh. https://doi.org/10.7488/ds/1725.
# Extracted .shp file from zipped directory

# 1) Get subnational units 
sha_shp_path <- "C:/Users/ktaylor/OneDrive - Nexus365/Emily & Clare REDUCE HF/SHA/SHA.shp"
# Read data
sha <- st_read(sha_shp_path, quiet = TRUE)

#Inspect data
print(names(sha))
print(head(sha))

# Write to GeoJSON
st_write(sha, "SHA_2006.geojson", driver = "GeoJSON",append=FALSE)

# 2) Create demo data - one row per English region
set.seed(42)
sha$demo_value <- runif(nrow(sha), min = 0, max = 100)

# 3) Plot choropleth with ggplot2
ggplot(sha) +
  geom_sf(aes(fill = demo_value), size = 0.15, color = "white") +
  scale_fill_viridis(option = "magma", name = "Value", na.value = "grey80") +
  theme_minimal() +
  labs(title = "Choropleth of England by SHA  region (demo values)",
       caption = "Data: demo random values") +
  theme(axis.text = element_blank(), axis.ticks = element_blank())
