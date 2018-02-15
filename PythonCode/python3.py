#!/Users/mahmoudshepero/anaconda3/bin/python3

import python as SP
from osgeo import ogr, osr
import matplotlib.pyplot as plt
import os
import numpy as np
import matplotlib.patches as mpatches

# load the buildings layer "LänmaterietLayer"
InputFileLocation = r'../Data/NewFolder/buildings-epsg3006.shp' # location
shapefile1 = InputFileLocation
buildingDS1 = ogr.Open(shapefile1)
buildingDS2 = ogr.Open(shapefile1)
buildingDS3 = ogr.Open(shapefile1)


# print the number of layers
print("Layer names:", SP.list_of_layers(buildingDS1))


# load the first layer
buildingsLayer = buildingDS1.GetLayer()

# check that the spatial reference is a metric spatial reference
print("spatial reference system: ",buildingsLayer.GetSpatialRef().ExportToWkt())

# filter to remove buildings with area less than 10m2
buildingsLayer.SetAttributeFilter("OGR_GEOM_WKT LIKE 'POLYGON%' AND OGR_GEOM_AREA > 10")
buildingsLayer.ResetReading() # reset counting of the filter

# print the layer fields
print("Layer Fields:", SP.get_layer_fields(buildingsLayer))

# print the tags from the interesting fieldDefn
print("Field tags: ", SP.get_field_tags(buildingsLayer, "ANDAMAL_1"))


## RESIDENTIAL LAYER
# load the layer to residential
ResbuildingsLayer = buildingDS1.GetLayer()
# we are interested in the layer residential codes 133 and 135, 199
ResbuildingsLayer.SetAttributeFilter( "OGR_GEOM_WKT LIKE 'POLYGON%' AND OGR_GEOM_AREA > 10"
"AND ANDAMAL_1 IN (133, 135, 199, 130, 131, 132, 133, 135)"
)
ResbuildingsLayer.ResetReading() # reset counting of the filter
print("Number of residential features: ", ResbuildingsLayer.GetFeatureCount())


## WORKPLACE LAYER
# load the layer to workplace
workplacesLayer = buildingDS2.GetLayer()
# workplaces are 240:299, 302, 304, 307, 311, 319, 322, 499
workplacesLayer.SetAttributeFilter( "OGR_GEOM_WKT LIKE 'POLYGON%' AND OGR_GEOM_AREA > 10"
"AND ANDAMAL_1 IN (240, 242, 243, 247, 248, 249, 252, 253, 299, "
"302, 304, 307, 311, 319, 322, 499)"
)
workplacesLayer.ResetReading() # reset counting of the filter
print("Number of workplace features: ", workplacesLayer.GetFeatureCount())


## OTHERS LAYER
# load the layer to other
otherLayer = buildingDS3.GetLayer()
# Otherplaces (leisure and shopping) are 301, 309, 313, 316, 317, 320, 399, 799
otherLayer.SetAttributeFilter( "OGR_GEOM_WKT LIKE 'POLYGON%' AND OGR_GEOM_AREA > 10"
"AND ANDAMAL_1 IN (301, 309, 313, 316, 317, 320, 399, 799)"
)
otherLayer.ResetReading() # reset counting of the filter
print("Number of other features: ", otherLayer.GetFeatureCount())





# Save the layers
# SP.create_buffer_and_projectLayer(ResbuildingsLayer, 3006, 3006, "residentialLayer", bufferDist = 0)
# SP.create_buffer_and_projectLayer(workplacesLayer, 3006, 3006, "workLayer", bufferDist = 0)
# SP.create_buffer_and_projectLayer(otherLayer, 3006, 3006, "otherLayer", bufferDist = 0)



# Open Buffered layers
InputFileLocation = r'../Data/NewFolder/OSM-epsg3600.shp' # location
shapefile2 = InputFileLocation
parkingDB = ogr.Open(shapefile2)
parkingLayer = parkingDB.GetLayer()

# print the parking layer tags
print("Field tags: ", SP.get_field_tags(parkingLayer, "amenity"))
print("Field tags: ", SP.get_field_tags(parkingLayer, "building"))
# Remove None features
parkingLayer.SetAttributeFilter( "NOT OGR_GEOM_WKT LIKE 'None%' AND OGR_GEOM_AREA > 10"
  "AND (amenity IN ('parking', 'parking_space') OR building in ('garage', 'garages'))")
parkingLayer.ResetReading() # reset counting of the filter
print("Number of parking features: ", parkingLayer.GetFeatureCount())


#
# InputFileLocation = r'UppsalaParkingBuffer100meter3006.shp' # location
# shapefile3 = InputFileLocation
# parkingBuffer = ogr.Open(shapefile3)
# parkingBufferLayer = parkingBuffer.GetLayer()
#
# # Calculate intersection of the buffered parking lot layer with the buidlings layers
# areaPercentage = SP.get_percentage_of_area_types(parkingBufferLayer,
#                 [ResbuildingsLayer, workplacesLayer, otherLayer])
# np.savetxt("areaPercentage.txt", areaPercentage)
#
#


fig = plt.figure(figsize = (50,50))
SP.plot_features(parkingLayer, "parkingPlot.pdf", 'k')#'#555577')
SP.plot_features(otherLayer, "parkingPlot.pdf", '#208778')#'#118877')
SP.plot_features(workplacesLayer, "parkingPlot.pdf", '#992266')
SP.plot_features(ResbuildingsLayer, "parkingPlot.pdf", '#1779b2')#'#228811')
parking_patch = mpatches.Patch(color='k', label='Parking lots')
work_patch = mpatches.Patch(color='#992266', label='Workplaces buildings')
other_patch = mpatches.Patch(color='#208778', label='Other buildings')
residential_patch = mpatches.Patch(color='#1779b2', label='Residential buildings')
fntsize= 40
plt.legend(handles= [parking_patch, work_patch, other_patch, residential_patch],
            fontsize = fntsize)
plt.xlim(641, 657)
plt.ylim(6630, 6645)
plt.xlabel("Easting (km)", fontsize = fntsize+20)
plt.ylabel("Northing (km)", fontsize = fntsize+20)
plt.xticks(fontsize = fntsize)
plt.yticks(fontsize = fntsize)
fig.savefig("parkingPlot2.pdf")
