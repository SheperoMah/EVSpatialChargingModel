import random as rnd


class EV:
    '''Electric vehicle class.

    This class represents electric vehicles.

    Attributes
    ----------
    currentLocation : -
        Location of the electric vehicle.
    currentState : -
        The current Markov state of the electric vehicle.
    mpg : float
        The MPG of the vehicle in unit of energy per distance, e.g.,
        kWh/km.
    batteryCharge : float
        The charge in the battery of the electric vehicle in units of
        energy,  kWh. The battery charge in this model is assumed to
        be 0.0 if the electric vehicle is fully charged, else negative if
        the battery is depleted.
    batteryCapacity : float
        The battery capacity of the electric vehicle (kWh).
        NOT FULLY TESTED. NOW IT IS ALWAYS ZERO WHICH MEANS THAT THE
        ELECTRIC VEHICLE HAS INFINTIE RANGE, AND THAT THE ENERGY DEPLETION WAS
        WAS MEASURED.
    trips : int
        The number of trips perfromed by the electric vehilce.
        initaldistance (int): Distance driven by the vehicle.
    distance : float
        The distance traveled by the vehicle.
    rnd : float
        Random number used to sample for the next Markov state of the vehicle.

    '''
    def __init__(self,
                 currentLocation,
                 currentState,
                 mpg = 0.2, # kWh/km
                 batteryCharge = 0.0,
                 batteryCapacity = 0.0,
                 trips = 0,
                 distance = 0,
                 rnd = 0.0):

        self.batteryCapacity = batteryCapacity
        self.currentLocation = currentLocation
        self.batteryCharge = batteryCharge
        self.currentState = currentState
        self.trips = trips
        self.distance = distance
        self.mpg = mpg
        self.rnd = rnd

    def find_free_stations(self, stations):
        """Finds the vacant ParkingLots which the electric vehicle can occupy.

        Parameters
        ----------
        stations : list(ParkingLot)
            A list of ParkingLot objects.

        Returns
        -------
        list(ParkingLot)
            A list of vacant ParkingLots matching the current state of the vehicle.

        """
        freeStations = [x for x in stations
                        if x.state == self.currentState and
                        x.currentOccupancy < x.maximumOccupancy]
        return(freeStations)

    def inital_conditions(self, stations, initalState):
        """Finds the vacant ParkingLots which the electric vehicle can occupy.

        Parameters
        ----------
        stations : list(ParkingLot)
            A list of ParkingLot objects.

        Returns
        -------
        list(ParkingLot)
            A list of vacant ParkingLots matching the current state of the vehicle.

        """
        self.currentState = initalState
        freeStations = self.find_free_stations(stations)
        initialStation = rnd.choice(freeStations)
        self.currentLocation = initialStation.ID
        initialStation.occupy_station()
        return(True)

    def charge_EV(self, duration, stations):
        '''Charges an EV.

        Parameters
        ----------
        power : float
            The power in the charging station in  units of power ex. (kW).
        duration : (float)
        The charging duration in units of time for example (h).

        Returns
        -------
        float
            update to the batteryCharge by the charging energy which equals the
            power * duration.

        '''
        if (self.batteryCharge < self.batteryCapacity and
            self.find_station(stations).chargingStatus == True):
            maxPower = self.find_station(stations).chargingPower
            chargeAfterChargingMaxPower = self.batteryCharge + \
                                            maxPower * duration
            if (chargeAfterChargingMaxPower <= self.batteryCapacity):
                self.batteryCharge = chargeAfterChargingMaxPower
                self.find_station(stations).charge_EV(maxPower)
            else:
                effectivePower = (self.batteryCapacity - self.batteryCharge)/duration
                self.batteryCharge = self.batteryCapacity
                self.find_station(stations).charge_EV(effectivePower)
            return(True)
        else:
            return(False)

    def drive_EV(self, distance):
        '''Disharges the EV.

        Parameters
        ----------
        distance : float
            The distance which was traveled by the electric vehicle.

        Returns
        -------
        float
            update to the batteryCharge to evaluate the depleted energy for
            driving which equals distance * mpg.

        '''
        self.batteryCharge -= distance * self.mpg
        self.distance += distance
        return(True)

    def find_state(self, chain, time_step, stations, distances):
        '''Estimates the state of the electric vehicle updates the state, changes the location, occupies the new location.

        Parameters
        ----------
        chain : Markov
            The Markov chain class which contains the transition matrix and
            the remaining methods.
        time_step : int
            The time in which the tranistion is taking place. The time is needed
            to calculate the tranistion probabiltiy from the non-homogenous Markov
            chain.
        stations : list(ParkingLot)
            A list of the parking lots.
        distances : dictionary
            A dictionary with keys representing the state transitions and values
            containing  a list of distances.
            ex. distance = {'01': [9.3, 20.0, 13.5]} means that the distances
            from state 0 to state 1 are in the list [9.3, 20.0, 13.5]. This
            dictionary is used to sample driving distances from.

        Returns
        -------
        bool
            True if a change in the state occurs.

        '''
        futureState = chain.next_state(self.currentState, self.rnd, time_step)
        if (futureState != self.currentState):
            distancesList = distances[str(self.currentState)+str(futureState)]
            distance = rnd.choice(distancesList)
            self.currentState = futureState
            self.change_location(stations)
            self.trips += 1
            self.drive_EV(distance)
            return(True)
        else:
            return(False)

    def change_location(self, stations):
        '''Changes the location.

        Parameters
        ----------
        stations : list(ParkingLot)
            A list of the parking lots.

        Returns
        -------
        None
            nothing is returned
        '''
        previousStation = self.find_station(stations)
        previousStation.leave_station()
        freeStations = self.find_free_stations(stations)
        newStation= rnd.choice(freeStations)
        self.currentLocation  = newStation.ID
        newStation.occupy_station()

    def find_station(self, stations):
        '''Returns the current location of the electric vehicle.

        Parameters
        ----------
        stations : list(ParkingLot)
            A list of the parkinglots.

        Returns
        -------
        ParkingLot
            The parking lot in which the electric vehicle is parked.

        '''
        station = [x for x in stations if x.ID == self.currentLocation]
        return(station[0])
