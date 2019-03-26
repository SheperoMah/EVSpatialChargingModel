from osgeo import ogr, osr
import numpy as np
import matplotlib.pyplot as plt
import os
from parkinglot import ParkingLot
from math import ceil
from collections import OrderedDict

def list_of_layers(mapFile):
    """Lists the layers in a geographical information systems (GIS) file.

    Parameters
    ----------
    mapFile : ogr opened file
        A spatial opened file. Use ogr.open() function.

    Returns
    -------
    list(Unique Layers)
        A list containing the names of the layers in the GIS file.
    """
    # get layer list
    layerList = []
    for i in mapFile:
        daLayer = i.GetName()
        if not daLayer in layerList:
            layerList.append(daLayer)
    return(layerList)

def get_layer_fields(layer):
    """Returns the fields of features in a vector layer.
    A vector file contains layers and each layer have fields of information.

    Parameters
    ----------
    layer :  an ogr layer
        A layer from a spaital file. Use ogr.open().GetLayer().

    Returns
    -------
    list(fields)
        A list of the fields available for a layer.
    """
    fields = []
    layerDefn = layer.GetLayerDefn()

    for n in range(layerDefn.GetFieldCount()):
        featureDefn = layerDefn.GetFieldDefn(n)
        fields.append(featureDefn.name)
    return(fields)

def get_field_tags(layer, field, unique = True):
    '''Returns the list of tags in a field of a vector layer
    A vector layer contains fields and each field have tags. For example, in
    OpenStreetMaps you might find fields like "building". This field might
    have tags such as "hospital".

    Parameters
    ----------
    layer : an ogr layer
        A layer from a spaital file. Use ogr.open().GetLayer().

    field : string
        A field in the vector layer. Usually fields are stored as strings.

    unique : bool, optional
        Returns only unique tags if True, else it returns the tag of
        every feature in the layer.(the default is True)

    Returns
    -------
    list(string)
        A list of tags for the tags stored for this layer.

    '''
    tagsList = []
    for feature in layer:# and feature is not None:
        tagsList.append( feature.GetField(field) )
    layer.ResetReading()
    return {
        True : set(tagsList),
        False: tagsList,
    }.get(unique)

def plot_features(layer, color, scale = 1/1000):
    """Plot the features of a layer
    This is an auxiliary function. Users are encouraged to use their own plotting
    funtions. The reason is that every GIS data provider stores the feature
    coordinates at differnt depths. This makes this function non-generalizable.
    Use this function as inspiration instead.

    Note: TODO depth of the geometry.

    Plotting listing 13.1 in "Geoprocessing with Python" "Geospatial Development By Example with Python "
    thanks to http://geoinformaticstutorial.blogspot.se/2012/10/

    Parameters
    ----------
    layer :  ogr layer
        A vector layer of spatial file. Use ogr.open().GetLayer().
    color :  matplotlib.color
        A valid color in matplotlib module.
    scale : float
        A scale to use for the plot. Default 1:1000, i.e., converts meters to
        kms in the x and y axes.

    Returns
    -------
    None
        This function returns a plot.

    """


    for feature in layer:
        ring = feature.GetGeometryRef()
        coord = ring.GetGeometryRef(0)
        #coord1 = coord.GetGeometryRef(0)
        points = coord.GetPoints()
        x, y = zip(*points)
        x = [i * scale for i in x]
        y = [i * scale for i in y]
        plt.fill(x, y, color)

    layer.ResetReading()

def create_buffer_and_projectLayer(inLayer,
                                   inputCoordinateSystem,
                                   outputCoordinateSystem,
                                   outputBufferfn,
                                   bufferDist = 0):
    """Projects layer from the input coordinate to the output corrdinate system,
    and saves the file in outputShapefile. This can be used to buffer a layer
    if the bufferDist > 0.

    Parameters
    ----------
    inLayer :  ogr layer
        A vector layer of spatial file. Use ogr.open().GetLayer().
    inputCoordinateSystem : int
        An EPSG coordinate system (projection) of the vector layer.
        Check the https://epsg.io.
    outputCoordinateSystem : int
        An EPSG coordinate system (projection) of the vector layer.
        Check the https://epsg.io.
    outputBufferfn : string
        Filename used to store the output layer.
    bufferDist :  int, optional
        The buffer distance in the same units as the original projection, i.e.,
        the inputCoordinateSystem. (the default is 0)

    Note: this function needs correction since the output shapefile does not have
    a reference system. This should be corrected.
    https://gis.stackexchange.com/questions/61303/python-ogr-transform-coordinates-from-meter-to-decimal-degrees
    https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html#create-a-new-layer-from-the-extent-of-an-existing-layer

    Returns
    -------
    None
        This function saves the buffered layer into a file

    """

    InputLayerGeomType = inLayer.GetGeomType()

    shpdriver = ogr.GetDriverByName('ESRI Shapefile')

    source = osr.SpatialReference()
    source.ImportFromEPSG(inputCoordinateSystem)

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

    create_projection_file(outputBufferfn, outputCoordinateSystem)

    inLayer.ResetReading()
    bufferlyr.ResetReading()
    outputBufferds = None

def get_floor_areas_of_intersecting_buildings(ParkingLayer, BuildingsLayer):
    """Returns the floor area of the intersecting buildings.
    If the parking lot was of type None the returned area will be 0.

    Parameters
    ----------
    ParkingLayer :  ogr layer
        A layer with the parking lots (buffered) as features
    BuildingLayer : ogr layer
        A layer with the buildings as features

    Returns
    -------
    list(float)
        A list containg the sum of intersecting areas for each feature

    """
    UserArea = [0 for i in range(ParkingLayer.GetFeatureCount())]
    index = 0
    count = 0
    for feature in ParkingLayer:
        areas  = [0.0]
        if feature.GetGeometryRef() != None:
            geom = feature.GetGeometryRef()
            BuildingsLayer.SetSpatialFilter(geom)
            for building in BuildingsLayer:
                areas.append(building.GetGeometryRef().GetArea())# for building in \BuildingsLayer ]
            BuildingsLayer.ResetReading()
        else:
            areas = [0.0]
        UserArea[index] = sum(areas)
        index += 1
        count += 1
    ParkingLayer.ResetReading()
    BuildingsLayer.SetSpatialFilter(None)
    BuildingsLayer.ResetReading()
    return(UserArea)

def get_percentage_of_area_types(parkingLayer, layers):
    """Returns the percentage of area intersecting each layer in layers.

    Parameters
    ----------
    parkingLayer : ogr layer
        A layer with with the parking lots (buffered) as features
    layers : list(ogr layer)
        A list of layers that we want to estimate the precentage of intersections

    Returns
    -------
    numpy.array(float)
        An array containg the percentage of areas for each layer. This array is
        of length equals the number of parking features and of width equals the
        number of layers.
    """

    area = np.zeros( shape = (parkingLayer.GetFeatureCount(), len(layers)))
    for i in range(len(layers)):
        area[:,i] = get_floor_areas_of_intersecting_buildings(
                                        parkingLayer, layers[i])
    sumRows = area.sum(axis=1)
    sumRows[sumRows == 0] = 1.0 # do not divide by zero
    area /= sumRows.reshape(-1,1)
    return(area)

def get_features_areas(Layer):
    """Returns a list of feature areas.

    Parameters
    ----------
    Layer : ogr layer
        A layer that we want to find the areas of it's features

    Returns
    -------
    list(float)
        A list containing the area of features inside the layer

    """
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
    """Creates and returns a list of stations
    This function is used to create a list of stations. The idea is every
    charging station is divided into several charging stations based on the
    percentages of areas. Each subset charging station is then considered to have
    a unique state.

    Parameters
    ----------
    identitiesArray : list(-)
        A list of unique names (IDs) for each station. It is used to name the
        stations and their subsets.
    areas : list(float)
        A list containing the areas of each charging station.
    percentageOfStates : numpy.array(float)
        A numpy array containing the percentage of areas of each feature dedicated
        to each state. In other words, each charging station will be divided into
        several states, what is the percentage of division.
    areaPerCar : float
        A float encoding the ground area needed to fit a car in a parking lot.
        This area should take into account the manuevering area and landscaping
        area.
    charging_status : list(bool), optional
        Which stations will only be considered parking lots and no charging will
        be enabled in. Default True.
    charging_power : float, optional
        The charging power of the stations. Default 3.7 kW.

    Returns
    -------
    OrderedDict(ParkingLot)
        An orderedDict of parking lots representing charging stations and or parking lots
        without charging.

    """
    if type(charging_status) is bool:
        charging_status = [charging_status for i in range(len(identitiesArray))]
    if type(charging_power) is int or type(charging_power) is float:
        charging_power = [charging_power for i in range(len(identitiesArray))]
    if type(areaPerCar) is int or type(areaPerCar) is float:
        areaPerCar = [areaPerCar for i in range(len(identitiesArray))]

    ids = list(identitiesArray)
    stations = []
    for st in range(percentageOfStates.shape[1]):

        stations_temp = [(str(ids[i]) + "-" + str(st), ParkingLot(
                               ID = str(ids[i]) + "-" + str(st),
                               state = st,
                               chargingPower = charging_power[i],
                               maximumOccupancy = ceil(
                                   1.0/areaPerCar[i] * percentageOfStates[i,st]
                                   * areas[i]),
                               currentOccupancy = 0,
                               chargingStatus = True,
                               currentLoad = 0.0))
                    for i in range(len(identitiesArray)) if
                    percentageOfStates[i,st] != 0
                    ]

        stations.extend(stations_temp)
    stationsDict = OrderedDict(stations)
    return(stationsDict)

def collect_stations_results(ID, results, stations):
    """Collects the results of subsets of charging stations into one station.
    Previously charging stations were divided into subset of charging stations
    each representing a unique state.

    Parameters
    ----------
    ID : list(-)
        list of unique IDs of charging stations. The same list used in the
        create_charging_stations() function.
    results : numpy.array(float)
        A numpy array containg the results of the simulation, where each column
        represents a charging station in the stations list.
    stations : OrderedDict(ParkingLot)
        An OrderedDict of stations; the one created in the create_charging_stations()
        function.

    Returns
    -------
    numpy.array(float)
        A numpy array where each column represents a parking lot from the ID list.

    """
    results_temp = np.copy(results)
    lengthOfSimulation = results_temp.shape[0]
    IDs = list(ID)
    stationsIDs = [v.ID for (k,v) in stations.items()]
    final_results = np.zeros((lengthOfSimulation,len(IDs)))

    for i in range(len(IDs)):
        columns = [idx for idx in range(len(stationsIDs)) if IDs[i] in stationsIDs[idx]]
        temp =  results_temp[:,columns].sum(1)
        final_results[:, i] = temp
    return(final_results)

def extract_state_load(load, requiredState, stations, aggregated = False):
    """Returns the load of all the stations that belong to a certain state.

    Parameters
    ----------
    load : numpy.array(float)
        A numpy array where each column represnts the load of a single station
        or subset thereof.
    requiredState : int
        An integer representing the code of the required state.
    stations : OrderedDict(ParkingLot)
        An OrderedDict of stations; the one created in the create_charging_stations()
        function.
    aggregated : bool, optional
            False (default) if we want to return the load of every station, else
            the function sums the load of all stations and returns the aggregate
            load.

    Returns
    -------
    numpy.array(float)
        The load of every/the aggregate load of stations belonging to the
        specified state.

    TODO correct to make it suitable with orderedDict. The code will not work.
    """
    columnIndex = [x for x in range(len(stations)) if
                            stations.get(x).state == requiredState]

    copyLoad = np.copy(load)
    requiredLoad = np.copy(copyLoad[:,columnIndex])

    if aggregated:
        return(np.sum(requiredLoad, axis = 1))
    else:
        return(requiredLoad)

def create_rectangle(x, dx, y, dy):
    """Returns a list containing the coordinates of a rectangle vertices.

    Parameters
    ----------
    x : float, int
        The x-coordinate of a vertix.
    dx : float, int
        The width of the rectangle-along the x-axis.
    y : float, int
        The y-coordinate of a vertix.
    dy : float, int
        The height of the rectangle-along the y-axis.

    """
    return([(x,y), (x+dx, y), (x+dx,y+dy), (x, y+dy), (x,y)])

def create_spatial_grid(initialXCoord,
                      initialYCoord,
                      spacingX,
                      spacingY,
                      numberOfXGridCells,
                      numberOfYGridCells):
    """Returns a grid of squares.

    Parameters
    ----------
    initialXCoord : int
        The starting x coordinate of the grid.
    initialYCoord : int
        The starting y coordinate of the grid.
    spacingX : int
        The width of the grid-along the x axis.
    spacingY : int
        The height of the grid-along the y axis.
    numberOfXGridCells : int
        The number of horizontal grid cells-along the x axis.
    numberOfYGridCells : int
        The number of vertical grid cells-along the y axis.

    Returns
    -------
    list(list(int, int))
        A list containing a list of the coordinates of the vertices of each
        grid cell.

    """
    endX = initialXCoord + spacingX * numberOfXGridCells
    xs = range(initialXCoord, endX, spacingX)

    endY = initialYCoord + spacingY * numberOfYGridCells
    ys = range(initialYCoord, endY, spacingY)

    connPoints = [create_rectangle(x, spacingX, y, spacingY) for x in xs for y in ys]

    return(connPoints)

def create_polygon(coordinates):
    """Creates a ogr polygon from a set of coordinates.

    Parameters
    ----------
    coordinates : list((float, float))
        A list of points representing the coordinates of the vertices of the polygon.
        Note, ensure to close the polygon by repeating the first point in the end.

    Returns
    -------
    ogr.polygon
        A polygon

    """
    ring = ogr.Geometry(ogr.wkbLinearRing)
    [ring.AddPoint(i[0], i[1]) for i in coordinates]
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    return(poly)

def save_grid_into_layer(fileName,
                      polygons,
                      outputCoordinateSystem = None):
    """Saves a set of polygons into a shapefile.

    Parameters
    ----------
    fileName : str
        The name of the output file without .shp.
    polygons : list(ogr.polygon)
        A list of ogr polygons.
    outputCoordinateSystem : int, optional
        An EPSG coordinate system (projection) of the vector layer.
        Check the https://epsg.io. Default is None, where no projection is saved.

    Returns
    -------
    None
        Saves a file.
    TODO test this I think there is a problem with fileName with and without extenstions.
    """
    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    fileNameWithExt = fileName
    if os.path.exists(fileNameWithExt):
        outDriver.DeleteDataSource(fileNameWithExt)
    outSource = outDriver.CreateDataSource(fileNameWithExt)
    outLayer = outSource.CreateLayer(fileName, geom_type=ogr.wkbPolygon)
    featureDef = outLayer.GetLayerDefn()

    for i in polygons:
        outFeature = ogr.Feature(featureDef)
        outFeature.SetGeometry(i)
        outLayer.CreateFeature(outFeature)
        outFeature = None

    outSource = None

    if outputCoordinateSystem:
        create_projection_file(fileName+"/"+fileName, outputCoordinateSystem)


def create_projection_file(fileName,
                         outputCoordinateSystem):
    """Saves a the projectionfile of a specific reference system.

    Parameters
    ----------
    fileName : str
        The name of the output file without .prj.
    outputCoordinateSystem : int
        An EPSG coordinate system (projection) of the vector layer.
        Check the https://epsg.io.

    Returns
    -------
    None
        Saves a file.

    """
    coordSys = osr.SpatialReference()
    coordSys.ImportFromEPSG(outputCoordinateSystem)
    coordSys.MorphToESRI()
    file = open((fileName+'.prj'), 'w')
    file.write(coordSys.ExportToWkt())
    file.close()

def aggregate_time_series(ts, timeStep, aggrFunc):
	""" Aggregates a time series by applying a function to the values within timeSteps.

	Paramters
	---------
	ts : numpy 1D array
		time series that needs to be aggregated. This time series has high
        resolution and length has to be mutliple of timeStep.
	timeStep : int
		The time step used to apply the function to.
	aggrFunc : function
		The aggregation function to apply to a numpy row. For example,
        lambda x: np.sum(x, axis=1) to sum over the values.
        Alternatively, np.mean can be used.

	Returns
	-------
	numpy 1D array
		A new time series with the function applied to every timeStep elements.

	Examples
	--------
	>>> x = np.arange(10)
	>>> aggregate_time_series(x, 2, lambda x: np.sum(x, axis=1))
	array([ 1,  5,  9, 13, 17])

	"""
	assert ts.shape[0] % timeStep == 0, "The length of the time series must" + \
    "be divisable by the timeStep."

	reshapedTs = ts.reshape(-1, timeStep)
	return(aggrFunc(reshapedTs))
