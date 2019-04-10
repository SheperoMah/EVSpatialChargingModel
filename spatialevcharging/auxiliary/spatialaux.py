from osgeo import ogr, osr
import numpy as np

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
            areas = [building.GetGeometryRef().GetArea() for building in \
             BuildingsLayer ]
            BuildingsLayer.ResetReading()
        else:
            areas = [0.0]
        UserArea[index] = sum(areas)
        index += 1
        count += 1
    ParkingLayer.ResetReading()
    BuildingsLayer.ResetReading()
    return(UserArea)

def get_percentage_of_area_types(parkingLayer, layers):
    """Returns the percentage of area intersecting each layer in layers
       If a feature does not intersect any layer it's percentage was equally
       divided between the layers.

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
    sumRowsAreas = np.sum(area, axis=1).reshape(-1,1)
    sumRowsAreas[sumRowsAreas == 0.0] = 1.0
    area = area / sumRowsAreas
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
        The name of the output file without .shp.
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
