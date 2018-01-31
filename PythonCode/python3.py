#!/Users/mahmoudshepero/anaconda3/bin/python3

import python as SP
from osgeo import ogr, osr
import matplotlib.pyplot as plt
import os


# load the buildings layer "LänmaterietLayer"
InputFileLocation = r'../Data/NewFolder/buildings-epsg3006.shp' # location
shapefile1 = InputFileLocation
buildingDS = ogr.Open(shapefile1)

# print the number of layers
print("Layer names:", SP.ListOfLayers(buildingDS))


# load the first layer
buildingsLayer = buildingDS.GetLayer()

# check that the spatial reference is a metric spatial reference
print("spatial reference system: ",buildingsLayer.GetSpatialRef().ExportToWkt())

# filter to remove buildings with area less than 10m2
buildingsLayer.SetAttributeFilter("OGR_GEOM_WKT LIKE 'POLYGON%' AND OGR_GEOM_AREA > 10")
buildingsLayer.ResetReading() # reset counting of the filter

# print the layer fields
print("Layer Fields:", SP.getLayerFields(buildingsLayer))

# print the tags from the interesting fieldDefn
print("Field tags: ", SP.getFieldTags(buildingsLayer, "ANDAMAL_1"))


## RESIDENTIAL LAYER
# load the layer to residential
ResbuildingsLayer = buildingDS.GetLayer()
# we are interested in the layer residential codes 133 and 135, 199
ResbuildingsLayer.SetAttributeFilter( "OGR_GEOM_WKT LIKE 'POLYGON%' AND OGR_GEOM_AREA > 10"
"AND ANDAMAL_1 IN (133, 135, 199)"
)
ResbuildingsLayer.ResetReading() # reset counting of the filter
print("Number of residential features: ", ResbuildingsLayer.GetFeatureCount())


## WORKPLACE LAYER
# load the layer to workplace
workplacesLayer = buildingDS.GetLayer()
# workplaces are 240:299, 302, 304, 307, 311, 319, 322, 499
workplacesLayer.SetAttributeFilter( "OGR_GEOM_WKT LIKE 'POLYGON%' AND OGR_GEOM_AREA > 10"
"AND ANDAMAL_1 IN (240, 242, 243, 247, 248, 249, 252, 253, 299, "
"302, 304, 307, 311, 319, 322, 499)"
)
workplacesLayer.ResetReading() # reset counting of the filter
print("Number of workplace features: ", workplacesLayer.GetFeatureCount())


## OTHERS LAYER
# load the layer to other
otherLayer = buildingDS.GetLayer()
# Otherplaces (leisure and shopping) are 301, 309, 313, 316, 317, 320, 399, 799
otherLayer.SetAttributeFilter( "OGR_GEOM_WKT LIKE 'POLYGON%' AND OGR_GEOM_AREA > 10"
"AND ANDAMAL_1 IN (301, 309, 313, 316, 317, 320, 399, 799)"
)
otherLayer.ResetReading() # reset counting of the filter
print("Number of other features: ", otherLayer.GetFeatureCount())
