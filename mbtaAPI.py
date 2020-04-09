# MBTA API Module
# Handles all calls to the mbta api
import requests
import json

class mbtaData:
    # Class initialization
    def __init__(self):
        try:
            self.requestHeaders = {'x-api-key': '5ba55cb81f0c4738afa9077f1ea1d3ad'}
            self.requestRoutesURL = 'https://api-v3.mbta.com/routes'
            self.requestStopsURL = 'https://api-v3.mbta.com/stops?filter%5Broute_type%5D=0,1'
            self.requestShapesURLBase = 'https://api-v3.mbta.com/shapes?include=stops&filter%5Broute%5D='
            self.mbtaDataRoutesRecieved = requests.get(self.requestRoutesURL, headers=self.requestHeaders)
            self.mbtaDataStopsRecieved = requests.get(self.requestStopsURL, headers=self.requestHeaders)
        except:
            print("Could not retrieve data")
            print("Exiting....")
            quit()
        # Retrieve Heavy and Light Rail Names from mbta api and store them
        self.setupRailLines()

        # Retrieve Rail Stops for each Rail Line from mbta api and store them
        self.setupRailStops()

        # Populate Connecting stops dictionary
        self.setupConnectionStops()
        
    # Retrieves and stores the Light and Heavy Rail Lines with their corresponding id
    def setupRailLines(self):
        if self.mbtaDataRoutesRecieved.status_code == 200:
            self.mbtaDataRoutesRecieved = self.mbtaDataRoutesRecieved.json()
            self.mbtaRawRoutesDataList = self.mbtaDataRoutesRecieved.get('data')
            # Build a dictionary of all available lines using their long names as key with id as value
            self.mbtaLines = dict()
            for item in self.mbtaRawRoutesDataList:
                itemAttributes = item.get('attributes')
                itemID = item.get('id')
                # determine if it is light or heavy rail
                if (itemAttributes.get('type') == 0 or itemAttributes.get('type') == 1):
                    # Light or Heavy Rail, add as those are the ones of the type we care about
                    self.mbtaLines[itemAttributes.get('long_name')] = []
                    if itemID == 'Red':
                        itemDestinations = itemAttributes.get('direction_destinations')
                        temp = itemDestinations[0].partition('/')
                        temp1 = temp[0]
                        temp2 = temp[2]
                        temp3 = itemDestinations[1]
                        line1 = temp1 + ' -> ' + temp3
                        line2 = temp3 + ' -> ' + temp1
                        line3 = temp2 + ' -> ' + temp3
                        line4 = temp3 + ' -> ' + temp2
                        lines = [line1, line2, line3, line4]
                    else:
                        itemDestinations = itemAttributes.get('direction_destinations')
                        temp1 = itemDestinations[0]
                        temp2 = itemDestinations[1]
                        line1 = temp1 + ' -> ' + temp2
                        line2 = temp2 + ' -> ' + temp1
                        lines = [line1, line2]
                    self.mbtaLines[itemAttributes.get('long_name')].append(itemID)
                    self.mbtaLines[itemAttributes.get('long_name')].append(lines)
                else:
                    pass
        else:
            print(self.mbtaDataRoutesRecieved.status_code)
            print("Did not recieve 200 OK from request. Exiting....")
            quit()

    # Data population for associating a subway rail route with the stops on it
    def setupRailStops(self):
        self.mbtaLineStops = dict()
        for line in self.mbtaLines:
            temp = self.requestShapesURLBase + self.mbtaLines[line][0]
            try:
                self.mbtaShapesDataRecieved = requests.get(temp, headers = self.requestHeaders)
            except:
                print("Could not retrieve data")
                print("Exiting....")
                quit()
            if self.mbtaShapesDataRecieved.status_code == 200:
                self.mbtaShapesDataRecieved = self.mbtaShapesDataRecieved.json()
                self.mbtaRawShapesDataList = self.mbtaShapesDataRecieved.get('data')
                self.mbtaRawShapesIncludesList = self.mbtaShapesDataRecieved.get('included')
            else:
                print(self.mbtaShapesDataRecieved.status_code)
                print("Did not recieve 200 OK from request. Exiting....")
                quit()

            self.mbtaLineStops[line] = []
            # Each line has 2 directions, each direction will have a list of stops
            if line == 'Red Line':
                # Need to do additional setup here for the multiple endpoints on red line
                temp0 = self.mbtaLines[line][1][0]
                temp1 = self.mbtaLines[line][1][1]
                temp2 = self.mbtaLines[line][1][2]
                temp3 = self.mbtaLines[line][1][3]

                tempdict = dict()
                tempdict[temp0] = []
                tempdict[temp1] = []
                tempdict[temp2] = []
                tempdict[temp3] = []

                for item in self.mbtaRawShapesDataList:
                    itemAttributes = item.get('attributes')
                    itemDirection = itemAttributes.get('direction_id')
                    itemName = itemAttributes.get('name')
                    relationships = item.get('relationships')
                    stops = relationships.get('stops')
                    stops = stops.get('data')
                    for stop in stops:
                        stopID = stop.get('id')
                        for station in self.mbtaRawShapesIncludesList:
                            stnID = station.get('id')
                            stnAttributes = station.get('attributes')
                            stnName = stnAttributes.get('name')
                            if stopID == stnID:
                                # Found matching station, insert and exit loop
                                if (itemDirection == 0) and (itemName == 'Ashmont'):
                                    if stnName in tempdict[temp0]:
                                        # Station is already present in the list, no need to add
                                        pass
                                    else:
                                        # Add the station since it's not present
                                        tempdict[temp0].append(stnName)
                                    pass
                                elif (itemDirection == 0) and (itemName == 'Braintree'):
                                    if stnName in tempdict[temp2]:
                                        # Station is already present in the list, no need to add
                                        pass
                                    else:
                                        # Add the station since it's not present
                                        tempdict[temp2].append(stnName)
                                    pass
                                elif (itemDirection == 1) and (itemName == 'Ashmont'):
                                    if stnName in tempdict[temp1]:
                                        # Station is already present in the list, no need to add
                                        pass
                                    else:
                                        # Add the station since it's not present
                                        tempdict[temp1].append(stnName)
                                    pass
                                elif (itemDirection == 1) and (itemName == 'Braintree'):
                                    if stnName in tempdict[temp3]:
                                        # Station is already present in the list, no need to add
                                        pass
                                    else:
                                        # Add the station since it's not present
                                        tempdict[temp3].append(stnName)
                                    pass
                                break
                
                tempdict[temp0].reverse()
                tempdict[temp1].reverse()
                tempdict[temp2].reverse()
                tempdict[temp3].reverse()
                self.mbtaLineStops[line].append(tempdict)
            else:
                # Create an empty list to add to for each line
                temp0 = self.mbtaLines[line][1][0]
                temp1 = self.mbtaLines[line][1][1]
                tempdict = dict()
                tempdict[temp0] = []
                tempdict[temp1] = []
                for item in self.mbtaRawShapesDataList:
                    itemAttributes = item.get('attributes')
                    itemDirection = itemAttributes.get('direction_id')
                    relationships = item.get('relationships')
                    stops = relationships.get('stops')
                    stops = stops.get('data')
                    for stop in stops:
                        stopID = stop.get('id')
                        for station in self.mbtaRawShapesIncludesList:
                            stnID = station.get('id')
                            stnAttributes = station.get('attributes')
                            stnName = stnAttributes.get('name')
                            if stopID == stnID:
                                # Found matching station, insert and exit loop
                                if itemDirection == 0:
                                    if stnName in tempdict[temp0]:
                                        # Station is already present in the list, no need to add
                                        pass
                                    else:
                                        # Add the station since it's not present
                                        tempdict[temp0].append(stnName)
                                    pass
                                else:
                                    if stnName in tempdict[temp1]:
                                        # Station is already present in the list, no need to add
                                        pass
                                    else:
                                        # Add the station since it's not present
                                        tempdict[temp1].append(stnName)
                                    pass
                                break
                tempdict[temp0].reverse()
                tempdict[temp1].reverse()
                self.mbtaLineStops[line].append(tempdict)
                
    # Prints all stops for a route in either direction to terminal
    def printStops(self, subwayLine):
        for lines in self.mbtaLineStops[subwayLine]:
            for direction in lines:
                print()
                print(direction)
                stopsList = lines.get(direction)
                for stop in stopsList:
                    print(stop)

    # Returns a list of the available routes for a subway line
    def getAvailableRoutes(self, subwayLine):
        output = []
        for lines in self.mbtaLineStops[subwayLine]:
            for direction in lines:
                output.append(direction)
        if len(output) > 0:
            return output

    # Returns the number of stops on a specific subway line route
    def getNumStopsOnRoute(self, subwayLine, subwayRoute):
        for lines in self.mbtaLineStops[subwayLine]:
            stopsList = lines.get(subwayRoute)
        return len(stopsList)

    # Data Contruction for returning Connecting Stops
    def setupConnectionStops(self):
        self.mbtaConnections = dict()
        connections = dict()
        for subway in self.mbtaLines:
            for lines in self.mbtaLineStops[subway]:
                for direction in lines:
                    stopsList = lines.get(direction)
                    for stop in stopsList:
                        if stop not in connections:
                            # Stop Does Not Exist. Add it
                            connections[stop] = set()
                        connections[stop].add(subway)
        for stop in connections:
            if len(connections[stop]) > 1:
                temp = connections[stop]
                self.mbtaConnections[stop]= temp

    # Determines what line(s) a stop is on. Returns subway lines or False of nothing found
    def getStopSubwayLine(self, usrStop):
        retval = set()
        for subway in self.mbtaLines:
            for lines in self.mbtaLineStops[subway]:
                for direction in lines:
                    stopsList = lines.get(direction)
                    for stop in stopsList:
                        if usrStop == stop:
                            # Valid Station, return true
                            retval.add(subway)
        return retval

    # Determines travel direction between two stops. returns value if determined
    def getDirection(self, subway, startPoint, endPoint):
        startFound = False
        endFound = False
        travelDirection = ''
        for lines in self.mbtaLineStops[subway]:
            for direction in lines:
                stopsList = lines.get(direction)
                for stop in stopsList:
                    if stop == startPoint:
                        startFound = True
                    elif (stop == endPoint) and (startFound == True):
                        endFound = True
                        travelDirection = direction
                        break
                if (startFound == True) and (endFound == True):
                    break
            if (startFound == True) and (endFound == True):
                break
        if (startFound == True) and (endFound == True):
            return travelDirection

    def planTrip(self, starting, ending):
        print('Planning Trip')
        # Determine if the start is a valid station
        # Determine which subway line the stations are on
        startLine = self.getStopSubwayLine(starting)
        endLine = self.getStopSubwayLine(ending)
        startSubways = []
        endSubways = []
        if len(startLine) > 0:
            if len(endLine) > 0:

                if starting == ending:
                    print('Same station selected for start and end of trip')
                else:
                    tstr = False
                    for e in startLine:
                        startSubways.append(e)
                    for e in endLine:
                        endSubways.append(e)

                    for i in startSubways:
                        if endSubways.count(i) > 0:
                            subway = i
                            tstr = True
                            break
                    # Determine if they are on the same subway line
                    if tstr is True:
                        print('Stations are on same subway Line')
                        print('Determining direction')
                        travelDirection = self.getDirection(subway, starting, ending)
                        if travelDirection != None:
                            # Figured out direction on rail to go
                            # print out directions to user
                            print('Trip Planned\n')
                            print('Take the ' + subway + ' Train: ' + travelDirection)
                            print('From ' + starting + ' to ' + ending)
                    else:
                        print('Stations are not on same subway line')
                        print('Determining route to take')

                        # determine which connections are on this subway line
                        connectionComplete = False
                        searchDepth = 0
                        connectingStops = []
                        for stop1 in self.mbtaConnections:
                            tmpset = self.mbtaConnections.get(stop1)
                            # convert set to a list
                            tmplst = []
                            for i in tmpset:
                                tmplst.append(i)
                                
                            for i in startSubways:
                                if tmplst.count(i) > 0:
                                    # set search depth to 1. Limiting depth to 2 layers
                                    searchDepth = 1
                                    # Connection is on this subway line
                                    # determine if the connection is on the endpoint line
                                    for j in endSubways:
                                        if tmplst.count(j) > 0:
                                            # Connection is also on the endpoint subway
                                            connectingStops.append(stop)
                                            travelStartSubway = i
                                            travelEndSubway = j
                                            conectionComplete = True
                                            break
                                        else:
                                            # Endpoint is not reachable via this connection
                                            # now iterate through this connections subway lines for connections and check them for endpoint reachability
                                            for line1 in tmplst:
                                                # determine what connections are available on this line
                                                for stop2 in self.mbtaConnections:
                                                    if stop2 != stop1:
                                                        # Make sure we're not checking the same stop
                                                        stop2Lines = self.getStopSubwayLine(stop2)
                                                        # See if this is connected to the first stop
                                                        if line1 in stop2Lines:
                                                            for line2 in stop2Lines:
                                                                if line1 == line2:
                                                                    # Connecting Subway Line
                                                                    travelConnectSubway = line2
                                                                if line2 in endSubways:
                                                                    for line3 in endSubways:
                                                                        if line2 == line3:
                                                                            travelStartSubway = line1
                                                                            travelConnectSubway = line2
                                                                            travelEndSubway = line3
                                                                            connectingStops.append(stop1)
                                                                            connectingStops.append(stop2)
                                                                            connectionComplete = True
                                                                            break
                                                                if connectionComplete == True:
                                                                    break
                                                    if connectionComplete == True:
                                                        break
                                                if connectionComplete == True:
                                                    break
                            if connectionComplete == True:
                                break
                                
                        print(connectingStops)
                        # Take first connection available
                        if (connectionComplete == True) and (len(connectingStops) < 2):
                            connectingStop = connectingStops.pop(0)
                            travelStartDirection = self.getDirection(travelStartSubway, starting, connectingStop)
                            travelEndDirection = self.getDirection(travelEndSubway, connectingStop, ending)
                            # print out directions to user
                            print('Trip Planned\n')
                            print('Take the ' + travelStartSubway + ' Train: ' + travelStartDirection)
                            print('From ' + starting + ' to ' + connectingStop)
                            print('Take the ' + travelEndSubway + ' Train: ' + travelEndDirection)
                            print('From ' + connectingStop + ' to ' + ending + '\n')
                        elif (connectionComplete == True) and (len(connectingStops) == 2):
                            pass
                            # Requires 2 connections
                            connectingStop1 = connectingStops.pop(0)
                            connectingStop2 = connectingStops.pop(0)
                            travelStartDirection = self.getDirection(travelStartSubway, starting, connectingStop1)
                            travelStartDirection = str(travelStartDirection)
                            travelConnectingDirections = self.getDirection(travelConnectSubway, connectingStop1, connectingStop2)
                            travelConnectingDirections = str(travelConnectingDirections)
                            travelEndDirection = self.getDirection(travelEndSubway, connectingStop2, ending)
                            travelEndDirection = str(travelEndDirection)
                            print('Trip Planned\n')
                            print('Take the ' + travelStartSubway + ' Train: ' + travelStartDirection)
                            print('From ' + starting + ' to ' + connectingStop1)
                            print('From ' + connectingStop1 + ', take the ' + travelConnectSubway + ' Train: ' + travelConnectingDirections)
                            print('to ' + connectingStop2)
                            print('From ' + connectingStop2 + ', take the ' + travelEndSubway + ' Train: ' + travelEndDirection)
                            print('to ' + ending + '\n')
        else:
            print('Invalid Stations Entered. Please enter a valid station')
