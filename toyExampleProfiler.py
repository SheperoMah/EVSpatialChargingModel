


def main(numberOfEVs, numberOfparkingloc):
    import numpy as np
    from collections import OrderedDict
    np.random.seed(1) # for reproducibility
    import random as rnd
    rnd.seed(1) # for reproducibility
    import math
    import datetime
    from spatialevcharging.ev import EV
    from spatialevcharging.markov import Markov
    from spatialevcharging.simulation import Simulation
    from spatialevcharging.parkinglot import ParkingLot
    from spatialevcharging.auxiliary.extractdistances import extract_distances
    from spatialevcharging.auxiliary.extractfiles import read_matrix_files


    stationTypes = rnd.choices(range(3), k = numberOfparkingloc)
    stationsList = [(i, ParkingLot(ID = i,
                           state = stationTypes[i],
                           chargingPower = 3.7,
                           maximumOccupancy = numberOfEVs,
                           currentOccupancy = 0))
                for i in range(numberOfparkingloc)]

    # add stations with no charging
    stationsList += [(str(i*1000), ParkingLot(ID = str(i*1000),
                           state = i,
                           chargingPower = 0.0,
                           maximumOccupancy = 10,
                           currentOccupancy = 0,
                           chargingStatus = False))
                            for i in range(3)]
    stations = OrderedDict(stationsList)

    # create cars
    EVs = [EV(currentLocation = None,
              currentState = None,
              mpg = 0.2)
           for i in range (numberOfEVs)]

    # distribute the cars on the stations with state zero
    [x.inital_conditions(stations,0) for x in EVs]

    # load the weekday distances filter >100km
    weekdayDistances = extract_distances("./distanceData/*day*.txt", 200)

    # load the weekend distances filter >100km
    weekendDistances = extract_distances("./distanceData/*end*.txt", 200)


    # WEEKDAY
    weekdayChain = read_matrix_files("./TransitionMatrix/*weekday*.txt")
    # define the tranistion Matrix
    weekday = Markov(weekdayChain)
    # WEEKEND
    weekdendChain = read_matrix_files("./TransitionMatrix/*weekend*.txt")
    # define the tranistion Matrix
    weekend = Markov(weekdendChain)

    # simulate one weekday
    daysArray = np.arange('2018-01-01', '2018-01-08', dtype='datetime64[D]')
    lengthOfDaySimulation = 1440 # 1440 timestep a day

    load = np.zeros(shape = (len(daysArray)*lengthOfDaySimulation,
    len([v for (k,v) in stations.items() if v.chargingStatus == True])))

    for day in range(len(daysArray)):

        if np.is_busday(daysArray[day]):
            chain = weekday
            dist = weekdayDistances
        else:
            chain = weekend
            dist = weekendDistances

        # Setup the simulation Model
        simulationCase = Simulation(stations,
                                EVs,
                                chain,
                                dist,
                                lengthOfDaySimulation)

        # Estimate the electric load
        temp_load = simulationCase.simulate_model()

        initialIdx = day*1440
        finalIdx = initialIdx +1440
        load[initialIdx:finalIdx, ::] = temp_load




if __name__ == "__main__":

        numberOfEVs = 1000
        numberOfparkingloc = 3000
        main(numberOfEVs, numberOfparkingloc)
