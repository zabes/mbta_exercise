# Main entry point for application
# handles user input
import mbtaAPI

print("Welcome")

# Instantiate the mbta data object
mbta = mbtaAPI.mbtaData()

while True:
    usrInput = input("Valid Input commands: Get Subway Lines, Get Subway Stops, Plan a Trip, Quit\n")
    # Remove leading and trailing whitespace from the user input and convert to lowercase
    usrInput = usrInput.strip()
    usrInput = usrInput.lower()
    if usrInput == "get subway lines":
        print("\nRetrieving subway lines for user:")
        subwayMaxStops = [0,0]
        subwayMinStops = [-1, -1]
        for subway in mbta.mbtaLines:
            print(subway)
            #if subway != 'Red Line':
            for route in mbta.getAvailableRoutes(subway):
                stops = mbta.getNumStopsOnRoute(subway, route)
                if stops is not None:
                    if subwayMaxStops[1] == 0:
                            subwayMaxStops.clear()
                            subwayMaxStops.append(subway)
                            subwayMaxStops.append(stops)
                    else:
                        if subwayMaxStops[1] < stops:
                            subwayMaxStops.clear()
                            subwayMaxStops.append(subway)
                            subwayMaxStops.append(stops)
                    if subwayMinStops[1] == -1:
                            subwayMinStops.clear()
                            subwayMinStops.append(subway)
                            subwayMinStops.append(stops)
                    else:
                        if subwayMinStops[1] > stops:
                            subwayMinStops.clear()
                            subwayMinStops.append(subway)
                            subwayMinStops.append(stops)
                                
        # Print The Subway Line with Most Number of Stops
        print("\nSubway Line with Highest Number of stops: ", subwayMaxStops[0] )
        print("Number of stops: ", subwayMaxStops[1])
        # Print The Subway Line with Least Number of Stops
        print("\nSubway Line with Lowest Number of stops: ",  subwayMinStops[0])
        print("Number of stops: ", subwayMinStops[1])
        print()
        
        for subway in mbta.mbtaLines:
            print(subway)
    elif usrInput == "get subway stops":
        while True:
            print("Here is a List of Connecting Stops: (Station Name - Connecting Lines)")
            for station in mbta.mbtaConnections:
                tmpstr = ''
                for route in mbta.mbtaConnections[station]:
                    tmpstr = tmpstr + ', ' + route
                print(station + ' - ' + tmpstr)
            
            print("Please enter a valid subway line. Enter Return to go back to main menu\n")
            print("Valid Subway Line Names:");
            for subway in mbta.mbtaLines:
                print(subway)
            print()
            subwayLineInput = input()
            subwayLineInput = subwayLineInput.strip()
            subwayLineInput = subwayLineInput.lower()
            subwayLineInput = subwayLineInput.title()
            print()
            
            if subwayLineInput in mbta.mbtaLines:
                mbta.printStops(subwayLineInput)
                break
            elif subwayLineInput == 'Return':
                break
            elif subwayLineInput == 'Quit':
                print("Exiting.....")
                quit()
            else:
                print('invalid entry')
    elif usrInput == "plan a trip":
        startStopInput = input("Please enter a valid subway stop for the start of your trip\n")
        startStopInput = startStopInput.strip()
        startStopInput = startStopInput.lower()
        startStopInput = startStopInput.title()
        print()
        endStopInput = input("Please enter a valid subway stop for the end of your trip\n")
        endStopInput = endStopInput.strip()
        endStopInput = endStopInput.lower()
        endStopInput = endStopInput.title()
        print()

        # Determine if both inputs are valid stops
        mbta.planTrip(startStopInput, endStopInput)
    elif usrInput == "quit":
        print("Exiting.....")
        quit()
    else:
        print("Invalid command entered")
