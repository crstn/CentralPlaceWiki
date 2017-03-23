library(spatstat)
library(rgdal)
library(maptools)

setwd("~/Dropbox/Code/CentralPlaceWiki/R_Analysis")

# load data
declared  <- readOGR("Shapefiles","Declared_proj")
extracted <- readOGR("Shapefiles","Extracted_proj")

#germany <- readShapePoly('de_states.shp', proj4string=CRS("+proj=utm +zone=32 +ellps=GRS80 +units=m +no_defs"))

germany <- readOGR("Shapefiles", "de-states")

#change germany polygon to owin type, so that we can use it as the boundary for our point pattern analysis
germany.window <- as.owin(germany)
class(germany.window)

# change the point layers to spatstat point patterns and set the window to the border of germany
declared.ppp  <- as.ppp(coordinates(declared),  germany.window)
extracted.ppp <- as.ppp(coordinates(extracted), germany.window)

# class(declared.ppp)
# class(extracted.ppp)

# summary(declared.ppp)
# summary(extracted.ppp)

# plot.ppp(declared.ppp)
# plot.ppp(extracted.ppp)


# these take quite long to run, 

# k_ex <- Kest(extracted.ppp)
# k_ex
# k_dec <- Kest(declared.ppp)
# k_dec

# plot(k_ex)
# plot(k_dec)

# plot(envelope(extracted.ppp,Kest))
# plot(envelope(declared.ppp,Kest))

#duplicated(declared.ppp,extracted.ppp)

# compute nearest neighbors between the two point patterns
nn <- nncross(declared.ppp,extracted.ppp)

neighbors = nn$which # indicies of nearest neighbors
distances = nn$dist  # distances

table(distances)

plot(superimpose(declared.ppp=declared.ppp,extracted.ppp=extracted.ppp), main="nncross", cols=c("red","blue"))
arrows(declared.ppp$x, declared.ppp$y, extracted.ppp[neighbors]$x, extracted.ppp[neighbors]$y, length=0.15)

boxplot (distances/1000)
summary(distances/1000)

hist(distances/1000)
