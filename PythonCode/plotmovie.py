#!/Users/mahmoudshepero/anaconda3/bin/python3


import numpy as np
import random as rnd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as manimation
from matplotlib.colors import Normalize
import ogr
import python as SP


load = np.loadtxt("finalResults.txt", ndmin=2)
plotted = load

# Open Parking layer
InputFileLocation = r'../Data/NewFolder/OSM-epsg3600.shp' # location
shapefile2 = InputFileLocation
parkingDB = ogr.Open(shapefile2)
parkingLayer = parkingDB.GetLayer()

# print the parking layer tags
# print("Amenity Field tags: ", SP.get_field_tags(parkingLayer, "amenity"))
# print("Building Field tags: ", SP.get_field_tags(parkingLayer, "building"))
# Remove None features
parkingLayer.SetAttributeFilter( "NOT OGR_GEOM_WKT LIKE 'None%' AND OGR_GEOM_AREA > 10"
  "AND (amenity IN ('parking', 'parking_space') OR building in ('garage', 'garages'))")
parkingLayer.ResetReading() # reset counting of the filter
# print("Number of parking features: ", parkingLayer.GetFeatureCount())



def norm_cmap(values, cmap, vmin=None, vmax=None):

    mn = np.amin(values)
    mx = np.amax(values)
    norm = Normalize(vmin=mn, vmax=mx)
    n_cmap = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    return(n_cmap)



cmap = norm_cmap(plotted, cmap='jet')
def f(x):
    rgba = cmap.to_rgba(x)
    return(matplotlib.colors.to_hex(rgba))


FFMpegWriter = manimation.writers['ffmpeg']
metadata = dict(title='Movie Test', artist='Matplotlib',
                comment='Movie support!')
writer = FFMpegWriter(fps=30, metadata=metadata, bitrate = 2000)

fig = plt.figure(figsize = (17,10))



with writer.saving(fig, "ResultsDay_final.mp4", 100):
    for i in range(plotted.shape[0]):
        print(i)
        plt.clf()
        j = 0
        for feature in parkingLayer:
            ring = feature.GetGeometryRef()
            coord = ring.GetGeometryRef(0)
            points = coord.GetPoints()
            x, y = zip(*points)
            x = tuple(i/1000.0 for i in x)
            y = tuple(i/1000.0  for i in y)
            plt.fill(x, y, f(plotted[i,j]))
            plt.xlim(641, 657)
            plt.ylim(6630, 6645)
            plt.xlabel("Easting (km)", fontsize=25)
            plt.ylabel("Northing (km)", fontsize=25)
            plt.title(str(int(i/60)).zfill(2)+":"+str(i%60).zfill(2), fontsize=30)
            j += 1
        cmap2 = cmap
        cmap2._A = []
        cbar = plt.colorbar(cmap2)
        cbar.ax.set_ylabel('Power (kW)', fontsize = 25)
        writer.grab_frame()
        parkingLayer.ResetReading()
