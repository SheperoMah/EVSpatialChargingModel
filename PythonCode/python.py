#!/Users/mahmoudshepero/anaconda3/bin/python3

from osgeo import ogr, osr
import numpy as np
import sys
import matplotlib.pyplot as plt
import os


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
    >>> getLayerFields(layer)
    '''
    schema = []
    layerDefn = layer.GetLayerDefn()

    for n in range(layerDefn.GetFieldCount()):
        featureDefn = layerDefn.GetFieldDefn(n)
        schema.append(featureDefn.name)

    return(schema)

def getFieldTags(layer, tag, unique = True):
    '''
    returns the list of tags in a field of a layer
    >>> getFieldTags(layer, "building")
    >>> getFieldTags(layer, "building", False)
    '''
    tagsList = []
    for feature in layer:
        tagsList.append( feature.GetField(tag) )
    return {
        True : set(tagsList),
        False: tagsList,
    }.get(unique)

def PlotFeatures(layer, filename, color):
    '''
    plot the features of a layer
    >>> PlotFeatures(layer, filename)
    '''
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize = (500,500))
    # plotting listing 13.1 in "Geoprocessing with Python" "Geospatial Development By Example with Python "
    # thanks to http://geoinformaticstutorial.blogspot.se/2012/10/
    for feature in layer:
        ring = feature.GetGeometryRef()
        coord = ring.GetGeometryRef(0)
        coord1 = coord.GetGeometryRef(0)
        coord1.Transform(transform)
        points = coord1.GetPoints()
        x, y = zip(*points)
        plt.plot(x, y, color)
    plt.xlabel("lat")
    plt.ylabel("lon")
    plt.axis('equal')
    fig.savefig(filename)

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
