from osgeo import ogr, osr
import numpy as np
import matplotlib.pyplot as plt
import os
from .parkinglot import ParkingLot
from math import ceil

def list_of_layers(mapFile):
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

def get_layer_fields(layer):
    '''
    returns the fields of a layer
    '''
    fields = []
    layerDefn = layer.GetLayerDefn()

    for n in range(layerDefn.GetFieldCount()):
        featureDefn = layerDefn.GetFieldDefn(n)
        fields.append(featureDefn.name)
    return(fields)

def get_field_tags(layer, tag, unique = True):
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

def plot_features(layer, color):
    '''
    plot the features of a layer
    >>> PlotFeatures(layer, color)
    Note: TODO depth of the geometry.
    '''
    # plotting listing 13.1 in "Geoprocessing with Python" "Geospatial Development By Example with Python "
    # thanks to http://geoinformaticstutorial.blogspot.se/2012/10/

    for feature in layer:
        ring = feature.GetGeometryRef()
        coord = ring.GetGeometryRef(0)
        #coord1 = coord.GetGeometryRef(0)
        points = coord.GetPoints()
        x, y = zip(*points)
        x = list(map(lambda xx: xx/1000, x))
        y = list(map(lambda xx: xx/1000, y))
        plt.fill(x, y, color)

    layer.ResetReading()

def create_buffer_and_projectLayer(inLayer,
                                   inputCoordinateSystem,
                                   outputCoordinateSystem,
                                   outputBufferfn,
                                   bufferDist = 0):
    '''
    Projects layer from the input coordinate to the output corrdinate system,
    and saves the file in outputShapefile. This can be used to buffer a layer
    if the bufferDist > 0.
    >>> ProjectLayer(InputLayer, 3857, 3006, "output.shp", bufferDist = 0)

    Note: this function needs correction since the output shapefile does not have
    a reference system. This should be corrected.
    https://gis.stackexchange.com/questions/61303/python-ogr-transform-coordinates-from-meter-to-decimal-degrees
    https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html#create-a-new-layer-from-the-extent-of-an-existing-layer
    '''

    InputLayerGeomType = inLayer.GetGeomType()

    shpdriver = ogr.GetDriverByName('ESRI Shapefile')

    source = osr.SpatialReference()
    source.ImportFromEPSG(inputCoordinateSystem)

    target = osr.SpatialReference()
    target.ImportFromEPSG(outputCoordinateSystem)

    coordTrans = osr.CoordinateTransformation(source, target)

    fileName = (outputBufferfn+'.shp')

    if os.path.exists(fileName):
        shpdriver.DeleteDataSource(fileName)
    outputBufferds = shpdriver.CreateDataSource(fileName)

    bufferlyr = outputBufferds.CreateLayer(fileName, geom_type=InputLayerGeomType)

    inLayerDefn = inLayer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        bufferlyr.CreateField(fieldDefn)

    bufferlyrDefn = bufferlyr.GetLayerDefn()

    for feature in inLayer:
        ingeom = feature.GetGeometryRef()
        geomBuffer = ingeom.Buffer(bufferDist)
        geomBuffer.Transform(coordTrans)

        outFeature = ogr.Feature(bufferlyrDefn)
        outFeature.SetGeometry(geomBuffer)
        for i in range(0, bufferlyrDefn.GetFieldCount()):
            if type(feature.GetField(i)) is int or type(feature.GetField(i)) is float:
                outFeature.SetField(bufferlyrDefn.GetFieldDefn(i).GetNameRef(), feature.GetField(i))
            elif type(feature.GetField(i)) is str:
                string = feature.GetField(i).encode('utf-8','surrogateescape').decode('ISO-8859-1')
                outFeature.SetField(bufferlyrDefn.GetFieldDefn(i).GetNameRef(), string)
            else:
                outFeature.SetField(bufferlyrDefn.GetFieldDefn(i).GetNameRef(), feature.GetField(i))

        bufferlyr.CreateFeature(outFeature)
        outFeature = None

    target.MorphToESRI()
    file = open((outputBufferfn+'.prj'), 'w')
    file.write(target.ExportToWkt())
    file.close()

    inLayer.ResetReading()
    bufferlyr.ResetReading()
    outputBufferds = None

def get_floor_areas_of_intersecting_buildings(ParkingLayer, BuildingsLayer):
    '''
    returns the floor area of the intersecting buildings, if the parking lot was
    of type None the returned area will be -1.
    ParkingLayer: a layer with the parking lots as features
    BuildingLayer: a layer with the buildings as features

    >>> get_floor_areas_of_intersecting_buildings(ParkingLayer, workPlacesLayer)
    '''
    UserArea = [0 for i in range(ParkingLayer.GetFeatureCount())]
    index = 0
    count = 0
    for feature in ParkingLayer:
        area  = 0.0
        if feature.GetGeometryRef() != None:
            geom = feature.GetGeometryRef()
            BuildingsLayer.SetSpatialFilter(geom)
            areas = [building.GetGeometryRef().GetArea() for building in \
             BuildingsLayer ]
            BuildingsLayer.ResetReading()
        else:
            area = 0.0
        UserArea[index] = sum(areas)
        index += 1
        count += 1
    ParkingLayer.ResetReading()
    BuildingsLayer.ResetReading()
    return(UserArea)

def get_percentage_of_area_types(parkingLayer, layers):

    area = np.zeros( shape = (parkingLayer.GetFeatureCount(), len(layers)))
    for i in range(len(layers)):
        area[:,i] = get_floor_areas_of_intersecting_buildings(
                                        parkingLayer, layers[i])
    area[np.sum(area, axis = 1) == 0,:] = 1.0/len(layers)
    area = area/(np.sum(area, axis = 1).reshape(parkingLayer.GetFeatureCount(),1))
    return(area)

def get_features_areas(Layer):
    areas = [0 for i in range(Layer.GetFeatureCount())]
    i = 0
    for feature in Layer:
        geom = feature.GetGeometryRef()
        areas[i] = geom.GetArea()
        i += 1
    Layer.ResetReading()
    return(areas)

def create_charging_stations(identitiesArray,
                             areas,
                             percentageOfStates,
                             areaPerCar,
                             charging_status = True,
                             charging_power = 3.7):

    if type(charging_status) is bool:
        charging_status = [charging_status for i in range(len(identitiesArray))]
    if type(charging_power) is int or type(charging_power) is float:
        charging_power = [charging_power for i in range(len(identitiesArray))]
    if type(areaPerCar) is int or type(areaPerCar) is float:
        areaPerCar = [areaPerCar for i in range(len(identitiesArray))]

    ids = list(identitiesArray)
    stations = []
    for st in range(percentageOfStates.shape[1]):

        stations_temp = [ParkingLot(ID = str(ids[i]) + "-" + str(st),
                               state = st,
                               chargingPower = charging_power[i],
                               maximumOccupancy = ceil(
                                   1.0/areaPerCar[i] * percentageOfStates[i,st]
                                   * areas[i]),
                               currentOccupancy = 0,
                               chargingStatus = True,
                               currentLoad = 0.0)
                    for i in range(len(identitiesArray)) if percentageOfStates[i,st] != 0]

        stations.extend(stations_temp)
    return(stations)

def collect_stations_results(ID, results, stations):
    results_temp = np.copy(results)
    lengthOfSimulation = results_temp.shape[0]
    IDs = list(ID)
    stationsIDs = [x.ID for x in stations]
    #list(map(lambda x: x.ID, stations))
    final_results = np.zeros((lengthOfSimulation,len(IDs)))

    for i in enumerate(IDs):
        columns = [idx for idx in range(len(stationsIDs)) if IDs[i[0]] in stationsIDs[idx]]
        temp =  results_temp[:,columns].sum(1).reshape(lengthOfSimulation,1)
        final_results[:,list([i[0]])] = temp
    return(final_results)

def extract_stateLoad(load, requiredState, stations):
    columnIndex = [x for x in stations if x.state == requiredState]
    #list(map(lambda x: x.state == requiredState, stations))
    copyLoad = np.copy(load)
    requiredLoad = np.copy(copyLoad[:,columnIndex])
    return(requiredLoad)
