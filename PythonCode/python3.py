#!/Users/mahmoudshepero/anaconda3/bin/python3

from osgeo import ogr
from osgeo import osr
import numpy as np
import sys
import matplotlib.pyplot as plt
import python as SP


InputFileLocation = r'../Data/NewFolder/buildings-epsg3857.shp'
shapefile1 = InputFileLocation
ds1 = ogr.Open(shapefile1)
layer1 = ds1.GetLayer()
print(SP.ListOfLayers(ds1))
