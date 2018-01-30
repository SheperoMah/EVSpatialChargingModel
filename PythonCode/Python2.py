#!/Users/mahmoudshepero/anaconda3/bin/python3

from osgeo import ogr, osr
import numpy as np
import sys
import matplotlib.pyplot as plt
import os


def ProjectLayer(inLayer, inputCoordinateSystem, outputCoordinateSystem, outputShapefile):
    '''
    Projects layer from the input coordinate to the output corrdinate system,
    and saves the file in outputShapefile
    >>> ProjectLayer(InputLayer, 3857, 3006, "output.shp")

    Note: this function needs correction since the output shapefile does not have
    a reference system. This should be corrected.
    '''
    # https://gis.stackexchange.com/questions/61303/python-ogr-transform-coordinates-from-meter-to-decimal-degrees

    driver = ogr.GetDriverByName('ESRI Shapefile')

    source = osr.SpatialReference()
    source.ImportFromEPSG(inputCoordinateSystem)

    target = osr.SpatialReference()
    target.ImportFromEPSG(outputCoordinateSystem)

    coordTrans = osr.CoordinateTransformation(source, target)

    if os.path.exists(outputShapefile):
        driver.DeleteDataSource(outputShapefile)

    InputLayerGeomType = inLayer.GetGeomType()
    outDataSet = driver.CreateDataSource(outputShapefile)
    # print("InputLayerType: ", ogr.GeometryTypeToName(InputLayerGeomType))
    outLayer = outDataSet.CreateLayer("OutputLayer", geom_type=ogr.wkbMultiPolygon)
    # print("OutputLayerType: ", ogr.GeometryTypeToName(outLayer.GetGeomType()))
    # print(inLayer.GetSpatialRef())


    inLayerDefn = inLayer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)

    outLayerDefn = outLayer.GetLayerDefn()

    inFeature = inLayer.GetNextFeature()
    while inFeature:
        geom = inFeature.GetGeometryRef()
        geom.Transform(coordTrans)
        outFeature = ogr.Feature(outLayerDefn)
        outFeature.SetGeometry(geom)
        for i in range(0, outLayerDefn.GetFieldCount()):
            if type(inFeature.GetField(i)) is int or type(inFeature.GetField(i)) is float:
                outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i))
            elif type(inFeature.GetField(i)) is str:
                string = inFeature.GetField(i).encode('utf-8','surrogateescape').decode('ISO-8859-1')
                outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), string)
            else:
                outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i))

        outLayer.CreateFeature(outFeature)
        outFeature = None
        inFeature = inLayer.GetNextFeature()
    print(outLayer.GetFeatureCount(), outLayer.GetGeomType())
    inLayer.ResetReading()
    outDataSet = None

def ListOfLayers(mapFile):
    '''
    returns the list of layer names in a map file
    >>> ListOfLayers(file)
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
    fields = []
    layerDefn = layer.GetLayerDefn()

    for n in range(layerDefn.GetFieldCount()):
        featureDefn = layerDefn.GetFieldDefn(n)
        fields.append(featureDefn.name)
    return(fields)

def getFieldTags(layer, tag, unique = True):
    '''
    returns the list of tags in a field of a layer
    >>> getFieldTags(layer, "building")
    >>> getFieldTags(layer, "building", False)
    '''
    tagsList = []
    for feature in layer:# and feature is not None:
        tagsList.append( feature.GetField(tag) )
    layer.ResetReading()
    return {
        True : set(tagsList),
        False: tagsList,
    }.get(unique)

def PlotFeatures(layer, filename, color):
    '''
    plot the features of a layer
    >>> PlotFeatures(layer, filename)
    Note:TODO depth of the geometry.
    '''
    fig = plt.figure(figsize = (500,500))
    # plotting listing 13.1 in "Geoprocessing with Python" "Geospatial Development By Example with Python "
    # thanks to http://geoinformaticstutorial.blogspot.se/2012/10/

    for feature in layer:
        ring = feature.GetGeometryRef()
        coord = ring.GetGeometryRef(0)
        #coord1 = coord.GetGeometryRef(0)
        points = coord.GetPoints()
        x, y = zip(*points)
        plt.plot(x, y, color)

    plt.xlabel("Easting (m)")
    plt.ylabel("Northing (m)")
    plt.axis('equal')
    layer.ResetReading()
    fig.savefig(filename)

def createBuffer(inputfn, outputBufferfn, bufferDist = 100):
    '''
    https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html#create-a-new-layer-from-the-extent-of-an-existing-layer
    '''
    inputds = ogr.Open(inputfn)
    inputlyr = inputds.GetLayer()

    shpdriver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists(outputBufferfn):
        shpdriver.DeleteDataSource(outputBufferfn)
    outputBufferds = shpdriver.CreateDataSource(outputBufferfn)
    bufferlyr = outputBufferds.CreateLayer(outputBufferfn, geom_type=ogr.wkbPolygon)
    featureDefn = bufferlyr.GetLayerDefn()

    for feature in inputlyr:
        ingeom = feature.GetGeometryRef()
        geomBuffer = ingeom.Buffer(bufferDist)

        outFeature = ogr.Feature(featureDefn)
        outFeature.SetGeometry(geomBuffer)
        bufferlyr.CreateFeature(outFeature)
        outFeature = None

    inputlyr.ResetReading()

def GetFloorAreasOfNearBuildings(ParkingLayer, BuildingsLayer, distance = 100):
    '''
    returns the floor area of the near buildings within a specified distance
    ParkingLayer: a layer with the parking lots as features
    BuildingLayer: a layer with the buildings as features
    distance: the distance in meters. The parking lot is used by the building if the
        nearest distance between them is less than the distance.
    >>> (ParkingLayer, workPlacesLayer, distance = 200)
    '''
    UserArea = [0 for i in range(ParkingLayer.GetFeatureCount()) ]
    index = 0
    count = 0
    for feature in ParkingLayer:
        area  = 0.0
        if feature.GetGeometryRef() != None:
            geom = feature.GetGeometryRef()
            geomBuffered = geom.Buffer(distance)
            coord = geom.GetGeometryRef(0)
            coordBuffer = geomBuffered.GetGeometryRef(0)
            buildingNumber = 0
            for building in BuildingsLayer:
                if building.GetGeometryRef().Distance(feature.GetGeometryRef()) <= distance:
                    area += building.GetGeometryRef().GetArea()
            BuildingsLayer.ResetReading()
        else:
            area = -1
        UserArea[index] = area
        print(UserArea[index])
        index += 1
        count += 1
    ParkingLayer.ResetReading()

if __name__ == "__main__":
    '''
    # example run : $ python3 python3.py <full-path><input-shapefile-name>.osm <full-path><input-shapefile-name>.osm
    # for help visit http://pcjericks.github.io/py-gdalogr-cookbook/index.html
    '''
    if len( sys.argv ) != 3:
        print("[ ERROR ] you must supply two arguments, for example: input-OSM-name.osm")
        sys.exit( 1 )

    InputFileLocation = sys.argv[1]
    SecondInputFileLocation = sys.argv[2]


    shapefile1 = InputFileLocation
    ds1 = ogr.Open(shapefile1)
    layer1 = ds1.GetLayer()

    shapefile2 = SecondInputFileLocation
    ds2 = ogr.Open(shapefile2)
    layer2 = ds2.GetLayer()


    layer1.SetAttributeFilter("OGR_GEOM_WKT LIKE 'POLYGON%' AND OGR_GEOM_AREA > 10")
    layer1.ResetReading()

    layer2.SetAttributeFilter(
    "(building IN ('garage', 'garages') OR amenity IN ('parking_space', 'parking')) \
    AND OGR_GEOM_AREA > 10"
    )
    print("Tags of 'building': ",getFieldTags(layer2, 'building', unique = True))
    print("Tags of 'amenity': ", getFieldTags(layer2, 'amenity', unique = True))
    print("Number of filtered features (public parking places): ", layer2.GetFeatureCount())

    # layer1.SetAttributeFilter(
    # ""
    # )
    #
    # print(GetFloorAreasOfNearBuildings(layer2, layer1, 100))
    GetFloorAreasOfNearBuildings(layer2, layer1, 100)

    # list of layers reset layer count
    # layer fields reset field counts
