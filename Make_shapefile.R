library(plyr)
library(sf)
library(sp)
library(tidyverse)
# read in shapefiles
county_data <- st_read(
  "C:\\Users\\bckol\\Downloads\\PA_CoTr\\County42.shp")
VTD_data <- st_read(
  "C:\\Users\\bckol\\Downloads\\PA_VTD\\PA_VTD.shp")
# set quantile (50% default) and filter counties
# TOTPOP could be substituted with BVAP, etc. 
names(VTD_data)[names(VTD_data)=="TOT_POP"] <- "TOTPOP"
qnt = quantile(county_data$TOTPOP,.60)
#pnt = quantile(county_data$TOTPOP,.40)
#rnt = quantile(county_data$TOTPOP,.55)
county <- county_data %>% filter(TOTPOP < qnt) #& TOTPOP < pnt & TOTPOP > rnt)
# remove all counties from BG that are already represented by county
VTD <- VTD_data %>% filter(!(COUNTYFP10 %in% county$COUNTYFP10))
# Not sure how to deal with projections
crs <- st_crs(county)
VTD <- st_transform(VTD,crs)
#st_crs(VTD) <- crs
# This join could be improved
cv <- intersect(names(VTD), names(county))
x <- VTD[,c(cv)]
y <- county[,c(cv)]
z <- rbind(x,y)
# clear
rm(x,y,cv,VTD,county,qnt)
# write .shp
st_write(z,"PA_60_adj.shp")