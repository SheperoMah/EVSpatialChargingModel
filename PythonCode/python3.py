#!/Users/mahmoudshepero/anaconda3/bin/python3

from osgeo import ogr
from osgeo import osr
import numpy as np
import sys
import matplotlib.pyplot as plt

def main(InputFileLocation):
    shapefile = InputFileLocation
    ds = ogr.Open(shapefile)
    layer = ds.GetLayer(0) # layer 3

    # https://gis.stackexchange.com/questions/61303/python-ogr-transform-coordinates-from-meter-to-decimal-degrees
    # 3857


    def LayerListTags(mapFile):
        '''
        returns the list of layer names in a map file
        >>> LayerListTags(file)
        '''
        # get layer list
        layerList = []
        for i in mapFile:
            daLayer = i.GetName()
            if not daLayer in layerList:
                layerList.append(daLayer)

        return(layerList)

    def getLayerFields(layer):
        '''
        returns the fields of a layer
        '''
        schema = []
        layerDefn = layer.GetLayerDefn()

        for n in range(layerDefn.GetFieldCount()):
            featureDefn = layerDefn.GetFieldDefn(n)
            schema.append(featureDefn.name)
        return(schema)

    def getFieldTags(layer, tag):
        '''
        returns the list of tags in a field of a layer
        >>> getFieldTags(layer, "building")
        '''
        tagsList = []
        for feature in layer:
            tagsList.append( feature.GetField(tag) )
        return(tagsList)

    def getUniqueFieldTags(getFieldTags, layer, tag):
        '''
        returns the list of unique tags in a field of a layer
        >>> getUniqueFieldTags(getFieldTags, layer, "building")
        '''
        tags = getFieldTags(layer, tag)
        uniqueTags = set( tags)
        return( uniqueTags )

    def PlotFeatures(layer, filename, color):
        '''
        plot the features of a layer
        >>> PlotFeatures(layer, filename)
        '''
        fig = plt.figure(figsize = (500,500))
        # plotting listing 13.1 in "Geoprocessing with Python" "Geospatial Development By Example with Python "
        # thanks to http://geoinformaticstutorial.blogspot.se/2012/10/
        for feature in layer:
            ring = feature.GetGeometryRef()
            coord = ring.GetGeometryRef(0)
            # coord1 = coord.GetGeometryRef(0)
            points = coord.GetPoints()
            x, y = zip(*points)
            plt.plot(x, y, color)
        plt.xlabel("lat")
        plt.ylabel("lon")
        plt.axis('equal')
        fig.savefig(filename)


    layer.SetAttributeFilter("amenity = 'parking'")
    PlotFeatures(layer, "plotProjection.pdf", 'k')


if __name__ == "__main__":

    '''
    # example run : $ python3 python3.py <full-path><input-shapefile-name>.osm
    # for help visit http://pcjericks.github.io/py-gdalogr-cookbook/index.html
    '''

    if len( sys.argv ) != 2:
        print("[ ERROR ] you must supply one argument: input-OSM-name.osm")
        sys.exit( 1 )

    InputFileLocation = sys.argv[1]
    main( InputFileLocation )
