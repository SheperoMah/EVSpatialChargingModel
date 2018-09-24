import numpy as np
import os
from .parkinglot import ParkingLot
from math import ceil


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
    final_results = np.zeros((lengthOfSimulation,len(IDs)))

    for i in enumerate(IDs):
        columns = [idx for idx in range(len(stationsIDs)) if IDs[i[0]] in stationsIDs[idx]]
        temp =  results_temp[:,columns].sum(1).reshape(lengthOfSimulation,1)
        final_results[:,list([i[0]])] = temp
    return(final_results)

def extract_stateLoad(load, requiredState, stations):
    columnIndex = [x for x in stations if x.state == requiredState]
    copyLoad = np.copy(load)
    requiredLoad = np.copy(copyLoad[:,columnIndex])
    return(requiredLoad)
