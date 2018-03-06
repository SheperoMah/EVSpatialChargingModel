


def main(numberOfEVs, numberOfparkingloc):
    import numpy as np
    np.random.seed(1) # for reproducibility
    import random as rnd
    rnd.seed(1) # for reproducibility
    import math
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import datetime
    from pkg.ev import EV
    from pkg.markov import Markov
    from pkg.simulation import Simulation
    from pkg.parkinglot import ParkingLot
    from pkg.extractDistances import extractDistances
    from pkg.extractFiles import readMatrixfiles


    stationTypes = rnd.sample(range(3), k = numberOfparkingloc)
    stations = [ParkingLot(ID = i,
                           state = stationTypes[i],
                           chargingPower = 3.7,
                           maximumOccupancy = numberOfEVs,
                           currentOccupancy = 0)
                for i in range(numberOfparkingloc)]

    # add stations with no charging
    stations += [ParkingLot(ID = str(i*1000),
                           state = i,
                           chargingPower = 0.0,
                           maximumOccupancy = 10,
                           currentOccupancy = 0,
                           chargingStatus = False) for i in range(3)]


    # create cars
    EVs = [EV(currentLocation = None,
              currentState = None,
              mpg = 0.2)
           for i in range (numberOfEVs)]

    # distribute the cars on the stations with state zero
    [x.inital_conditions(stations,0) for x in EVs]

    # load the weekday distances filter >100km
    weekdayDistances = extractDistances("./distanceData/*day*.txt", 200)

    # load the weekend distances filter >100km
    weekendDistances = extractDistances("./distanceData/*end*.txt", 200)


    # WEEKDAY
    weekdayChain = readMatrixfiles("./TransitionMatrix/*weekday*.txt")
    # define the tranistion Matrix
    weekday = Markov(weekdayChain)
    # WEEKEND
    weekdendChain = readMatrixfiles("./TransitionMatrix/*weekend*.txt")
    # define the tranistion Matrix
    weekend = Markov(weekdendChain)

    # simulate one weekday
    daysArray = np.arange('2018-01-01', '2018-01-08', dtype='datetime64[D]')
    lengthOfDaySimulation = 1440 # 1440 timestep a day

    load = np.zeros(shape = (len(daysArray)*lengthOfDaySimulation,
    len([x for x in stations if x.chargingStatus == True])))

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

    print("Average number of trips:", np.mean(np.asarray([x.trips for x in EVs])))
    print("Average distance traveled by car (km):",
            np.mean(np.asarray([x.distance  for x in EVs])))

    fig = plt.figure(figsize = (10,10))
    minutes = np.arange('2018-01-01', '2018-01-08', dtype='datetime64[m]').astype(datetime.datetime)
    plt.plot(minutes, np.sum(load,1))
    plt.xticks(rotation = 'vertical')
    # xfrmt = mdates.DateFormatter('%d %H:%M')
    # plt.gca().xaxis.set_major_formatter(xfrmt)
    plt.xlabel("Date")
    plt.ylabel("Power (kWh/h)")
    plt.rcParams.update({'font.size': 35})
    fig.savefig("resultLoad.pdf")



if __name__ == "__main__":

        numberOfEVs = 10
        numberOfparkingloc = 3
        main(numberOfEVs, numberOfparkingloc)
