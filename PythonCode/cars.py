#!/Users/mahmoudshepero/anaconda3/bin/python3

import random as rn
import numpy as np
import itertools as iter


class EV:
    '''Class representing electric vehicles

        Attributes:
            currentLocation (-): location of the electric vehicle.
            currentState (-): the current Markov state of the electric vehicle.
            batteryCharge (float): the charge in the battery of the electric vehicle (kWh).
            batteryCapacity (float): the battery capacity of the electric vehicle (kWh).

    '''
    def __init__(self,
                 currentLocation,
                 currentState,
                 mpg = 0.2, # kWh/km
                 batteryCharge = 0.0,
                 batteryCapacity = 0.0,
                 trips = 0,
                 initialDistance = 0):

        self.batteryCapacity = batteryCapacity
        self.currentLocation = currentLocation
        self.batteryCharge = batteryCharge
        self.currentState = currentState
        self.trips = trips
        self.distance = initialDistance
        self.mpg = mpg

    def find_free_stations(self, stations):
        freeStations = [ x for x in stations
                        if x.state == self.currentState and
                        x.currentOccupancy < x.maximumOccupancy]
        # list(iter.filterfalse(lambda x:
        #                             not(x.state == self.currentState
        #                             and x.currentOccupancy < x.maximumOccupancy)
        #                             , stations))
        return(freeStations)


    def inital_conditions(self, stations, initalState):

        self.currentState = initalState
        freeStations = self.find_free_stations(stations)
        initialStation = rn.choice(freeStations)
        self.currentLocation = initialStation.ID
        initialStation.occupy_station()
        return(True)

    def charge_EV(self, duration, stations):
        ''' Charges an EV.

            Arguments:
                power (float): the power in the charging station in (kW).
                duration (float): the charging duration in (h).

            Returns:
                (float): update to the batteryCharge

        '''
        if (self.batteryCharge < 0.0 and
            self.find_station(stations).chargingStatus == True):
            self.batteryCharge += self.find_station(stations).chargingPower * duration
            self.find_station(stations).charge_EV()
            return(True)
        else:
            return(False)

    def drive_EV(self, distance):
        ''' Disharges an EV.

            Arguments:
                distance (float): the distance driven by the electric vehicle in (km).
                mpg (float): the consumption of the the electric vehicle for
                every unit of distance in (kWh/km).

            Returns:
                (float): update to the batteryCharge

        '''
        self.batteryCharge -= distance * self.mpg
        self.distance += distance
        return(True)

    def find_state(self, chain, time_step, stations, distances):
        futureState = chain.next_state(self.currentState, time_step)
        if (futureState != self.currentState):
            distancesList = distances[str(self.currentState)+str(futureState)]
            distance = rn.choice(distancesList)
            self.currentState = futureState
            self.change_location(stations)
            self.trips += 1
            self.drive_EV(distance)
            return(True)
        else:
            return(False)

    def change_location(self, stations):
        previousStation = self.find_station(stations)
        previousStation.leave_station()
        freeStations = self.find_free_stations(stations)
        newStation= rn.choice(freeStations)
        self.currentLocation  = newStation.ID
        newStation.occupy_station()

    def find_station(self, stations):
        station = [ x for x in stations if x.ID == self.currentLocation]
        # list(iter.filterfalse(lambda x:
        #                             not (x.ID == self.currentLocation)
        #                             , stations))
        return(station[0])

class Markov:
    ''' Extracts the transition probability from the current state

        Attributes:
            chain (np.array(floats)): the transition matrix as 3-d array.
            Square matrix in both the x and y axis, where the row represents the
            current state, and the coulumn represents the following state. The
            z-axis represents the inhomogenous factor, which is the dependancy on
            on the transition time.
    '''
    def __init__(self, chain):
        self.chain = chain
        # assert (self.chain.sum(0) == np.ones((self.chain.shape[0],1)) ), "the sum \
        # of each row in the transition matrix should  be one"
        assert (self.chain.shape[0] == self.chain.shape[1]), "the transition \
            matrix should be square in the first two dimensions"


    def extract_transition_probability(self, currentState, time_step = None):
        ''' Extracts the transition probability from the current state.

            Arguments:
                currentState (int): the current state of the Markov chain.
                time_step (int): the time step of the inhomegenous Markov chain.

            Returns:
                np.array(float): the row of the tranistion probabilty matrix for
                the current state and time
        '''
        if time_step is None:
            return( self.chain[currentState, :] )
        else:
            return( self.chain[currentState, :, time_step] )

    def next_state(self, currentState, time_step = None):
        ''' Estimates the future state of the Markov chain.

            Arguments:
                currentState (int): the current state of the Markov chain.
                time_step (int): the time step of the inhomegenous Markov chain.

            Returns:
                (int): the future state of the Markov chain.

        '''

        transitionProb = self.extract_transition_probability(currentState, time_step)
        cumulativeSum = transitionProb.cumsum(0)
        rndNumber = np.random.random_sample()
        nextState = np.where(cumulativeSum >= rndNumber)[0][0]
        return(nextState)

class ParkingLot:

    def __init__(self,
                 ID,
                 state,
                 chargingPower,
                 maximumOccupancy,
                 currentOccupancy,
                 chargingStatus = True,
                 currentLoad = 0.0):
        self.ID = ID
        self.state = state
        self.chargingStatus = chargingStatus
        self.chargingPower = chargingPower
        self.currentLoad = currentLoad
        self.maximumOccupancy = maximumOccupancy
        self.currentOccupancy = currentOccupancy

    def occupy_station(self):
        self.currentOccupancy += 1
        return( True )

    def leave_station(self):
        self.currentOccupancy -= 1

    def charge_EV(self):

        # current load is in unit of power * unit of time, in other words, it is
        # energy. For example, if we work with kW for power and time in minutes,
        # then the current load will be in kWmin/min, thus to aggregate to one hour
        # you need to average the values which results in kWh/h.

        self.currentLoad += self.chargingPower

class Simulation:

    def __init__(self,
                 stations,
                 cars,
                 chain,
                 distancesDictionary,
                 resolution = 1/60):
        self.stations = stations
        self.cars = cars
        self.chain = chain
        self.resolution = resolution
        self.distancesDictionary = distancesDictionary

    def model_function(self, timestep):
        def reset_load_new_timestep(x):
            x.currentLoad = 0.0
            return(x)

        #list(map(reset_load_new_timestep, self.stations))
        [reset_load_new_timestep(x) for x in self.stations]

        def do_on_car(self, x, timestep):
            x.find_state(self.chain,
                         timestep,
                         self.stations,
                         self.distancesDictionary)

            x.charge_EV(self.resolution, self.stations)

        #list(map(lambda x: do_on_car(self, x, timestep), self.cars))
        [do_on_car(self, x, timestep) for x in self.cars]

        #return(list(map(lambda x: x.currentLoad, self.stations)))
        return([x.currentLoad for x in self.stations])

    def simulate_model(self, simulationLength):
        # results = list(
        #                iter.accumulate(range(-1, simulationLength),
        #                                lambda x, y: self.model_function(y % 1440)))
        resultsMatrix = np.zeros((simulationLength, len(self.stations)))

        for time in range(simulationLength):
            resultsMatrix[time,::] = self.model_function(time % 1440)

        return(resultsMatrix)
