from spatialevcharging.parkinglot import ParkingLot
from math import ceil
from collections import OrderedDict
import numpy as np

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

    """
    columnIndex = [x for x in range(len(stations)) if
                            stations.get(x).state == requiredState]

    copyLoad = np.copy(load)
    requiredLoad = np.copy(copyLoad[:,columnIndex])

    if aggregated:
        return(np.sum(requiredLoad, axis = 1))
    else:
        return(requiredLoad)
