import numpy as np
import pandas as pd

class Simulation:
    """A class representing the simulation model.

    In this class, the simulation data is inputed in addition the model is ran
    and the results are returned.

    Attributes
    ----------
    stations : OrderedDict(ParkingLot)
        An OrderedDict of the available parking lots in the city. Make sure that there
        are enough parking lots to fit the cars.
    cars : list(EV)
        A list of EVs which will be simulated.
    numCars : int
        The number of cars simualted
    chain : Markov
        A Markov class which contains the markov chain.
    distancesDictionary : dict
        A dictionray containing the distances of trips between states, See help
        of Markov class for more details.
    simulationLength : int
        The number of time steps with which the simulation is run, i.e. the
        length of the simulation. The time step is determined by the unit of the
        battery charge and battery capacity for the EV class.
    resolution : float
        The resolution of the timestep. Used to charge the EV class. (the
        default is 1/60). OTHER VALUES ARE YET NOT FULLY TESTED YET.


    """

    def __init__(self,
                 stations,
                 cars,
                 chain,
                 distancesDictionary,
                 timeSteps,
                 resolution = 1/60):
        self.stations = stations
        self.cars = cars
        self.numCars = len(self.cars)
        self.chain = chain
        self.resolution = resolution
        self.distancesDictionary = distancesDictionary
        self.timeSteps = timeSteps

    def model_function(self, timestep, isWeekday):
        def reset_load_new_timestep(x):
            x.currentLoad = 0.0
            return(x)

        [reset_load_new_timestep(v) for (k,v) in self.stations.items()]

        def do_on_car(self, x, timestep, isWeekday):
            x.find_state(self.chain[isWeekday],
                         timestep,
                         self.stations,
                         self.distancesDictionary[isWeekday])

            x.charge_EV(self.resolution, self.stations)

        [do_on_car(self, x, timestep, isWeekday) for x in self.cars]

        rndmNums = np.random.random(self.numCars)
        for i in range(self.numCars):
            self.cars[i].rnd = rndmNums[i]

        chargingStationsFiltered = [v for (k,v) in self.stations.items() if
                                    v.chargingStatus == True]
        return([x.currentLoad for x in chargingStationsFiltered])

    def simulate_model(self):

        resultsMatrix = np.zeros((self.timeSteps.shape[0],
        len([k for (k,v) in self.stations.items() if v.chargingStatus == True])))

        for i, time in enumerate(self.timeSteps):
            weekday = True if time.weekday() < 5 else False
            minute = time.minute + 60 * time.hour
            resultsMatrix[i,::] = self.model_function(minute, weekday)

        return(resultsMatrix)
