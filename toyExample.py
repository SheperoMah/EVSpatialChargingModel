
import math
import random as rnd
rnd.seed(10) # for reproducibility
from collections import OrderedDict

import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import numpy as np
np.random.seed(1) # for reproducibility
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from spatialModelPkg.ev import EV
from spatialModelPkg.markov import Markov
from spatialModelPkg.simulation import Simulation
from spatialModelPkg.parkinglot import ParkingLot
from spatialModelPkg.extractDistances import extractDistances
from spatialModelPkg.extractFiles import readMatrixfiles


def main(numberOfEVs, numberOfparkingloc):


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
                           maximumOccupancy = numberOfEVs,
                           currentOccupancy = 0,
                           chargingStatus = False)) for i in range(3)]
    stations = OrderedDict(stationsList)


    # create cars
    EVs = [EV(currentLocation = None,
              currentState = None,
              mpg = 0.2)
           for i in range (numberOfEVs)]

    # distribute the cars on the stations with state zero
    [x.inital_conditions(stations,0) for x in EVs]

    # load the weekday distances filter >200km
    weekdayDistances = extractDistances("./distanceData/*day*.txt", 200)

    # load the weekend distances filter >200km
    weekendDistances = extractDistances("./distanceData/*end*.txt", 200)

    # Create a distance Dictionary, if the key is true, use weekday distances,
    # else use weekend distances.
    dist = {True: weekdayDistances,
            False: weekendDistances}

    # WEEKDAY
    weekdayChain = readMatrixfiles("./TransitionMatrix/*weekday*.txt")
    # define the tranistion Matrix
    weekday = Markov(weekdayChain)
    # WEEKEND
    weekdendChain = readMatrixfiles("./TransitionMatrix/*weekend*.txt")
    # define the tranistion Matrix
    weekend = Markov(weekdendChain)

    # Create a Markov chain Dictionary, if the key is true, use weekday Markov chain,
    # else use weekend Markov chain.
    chain = {True: weekday,
             False: weekend}

    # simulate one week
    minutes = pd.date_range('2020-03-28', '2020-04-05', freq="min", tz="CET")[:-1]
    numberOfDays = (minutes[-1] - minutes[0]).days


    load = np.zeros(shape = (minutes.shape[0],
    len([v for (k,v) in stations.items() if v.chargingStatus == True])))

    # Setup the simulation Model
    simulationCase = Simulation(stations,
                                EVs,
                                chain,
                                dist,
                                minutes)

    # Estimate the electric load
    load = simulationCase.simulate_model()


    print("Average number of trips/car/day :",
          np.mean(np.asarray([x.trips for x in EVs]))/numberOfDays)
    print("Average distance traveled per car per day (km/day/car):",
          np.mean(np.asarray([x.distance  for x in EVs]))/numberOfDays)

    fig = plt.figure(figsize = (10,10))
    plt.plot(minutes, np.sum(load,1))
    plt.xticks(rotation = 'vertical')
    # xfrmt = mdates.DateFormatter('%d %H:%M')
    # plt.gca().xaxis.set_major_formatter(xfrmt)
    plt.xlabel("Date")
    plt.ylabel("Power (kWh/h)")
    plt.rcParams.update({'font.size': 35})
    fig.savefig("resultLoad.pdf")



if __name__ == "__main__":

        numberOfEVs = 1000
        numberOfparkingloc = 10
        main(numberOfEVs, numberOfparkingloc)
