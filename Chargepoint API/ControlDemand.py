import zeep # Zeep is the module used for calling the methods in Chargepoint's API under the SOAP API standard 
from zeep.client import Client
from zeep.transports import Transport
from zeep.cache import SqliteCache
from zeep.wsse.username import UsernameToken
from types import * # this module defines the different Python types, used for typechecking
from datetime import datetime # this modules have methods for working with dates and times
from datetime import timedelta # check the datetime module docs for usage
import xlsxwriter # module used to read and write to Excel files from Python
import time as time # this module allows for system clock manipulation such as adding delays
import sys # this module allows the user to manipulate system processes such as interrupts
from decimal import Decimal #this module allows user to work with decimal type numericals

## Version 1.0 ##
## Note: This version is the crude, barebones implementation of Demand Response (DR) features ##
## Control Demand Checks site load based every pre-determined interval
## then shed all actively charging stations according to user input demand cap

## NOTE: Needs to be tested and debugged in practical usage which would require
## either software simulation of the charging station hardware for the algorithm
## to perform demand response control on or actual EVSEs site and hardware
## manipulation if given permission 

## Future updates: Implement DR based on each user's charging history ##

# The controlDemand class implements DR functionalities to the Chargepoint EVSE
# network via API data query and adjustments

class ControlDemand: #contains all methods developed to aid in demand response functionality 
   
    #Chargepoint API network access credentials
    USERNAME = '94a8e8abffb20dfc4826221c2b8ba1d058a46c3cd57e11487170620' # Provided by Chargepoint to access API
    PASSWORD = '0f503938100c2839c2f2fafe0cc6e406' # Provided by Chargepoint to access API
    wsdl = 'https://webservices.chargepoint.com/cp_api_5.0.wsdl' # This variable is assigned a URL to Chargepoint XML-based database with the API's callable methods

    transport = Transport(cache=SqliteCache()) # Enable Zeep to initialize its caching feature to improve performance
    global client # declare client as a globally accesible variable

    # initialize client and authenticate USERNAME and PASSWORD
    # to access API for calling methods
    client = zeep.Client(wsdl=wsdl, wsse=UsernameToken(USERNAME, PASSWORD))  

    # getUserChargingHistory returns a list of
    # last "sessions_amount" sessions for analysis for a given "userID"
    # NOTE: This method was planned for the next level of DR to set shed states adaptively to each user's charging history 
    def getUserChargingHistory(userID, sessions_amount):

        #Initialize dictionary displaying the specified user's last charging sessions
        chargeHistory = {
                            'userID': userID,
                            'sessions':[], #list or array of charging session data objects queried from Chargepoint API servers
                            'averageLoad':0.0, # kW
                            'totalLoad': 0.0 #kW
                        }
        session_limit = sessions_amount #number of charging sessions to query and stop loop
        
        ENDTIME = datetime.utcnow() # datetime.utcnow() to get current date and time to initialize and assign to ENDTIME 
        one_day = timedelta(days = 1) # declares a timedelta object or time difference of one day
        STARTTIME = ENDTIME - one_day # Assign STARTTIME to be one day before ENDTIME (datetime objects can be arithmetically combined with timedelta objects)
        print ENDTIME # print out times just for checking, this can be removed
        print STARTTIME

         # set time_limit for loop time iteration since some users might not charge frequently, and loop can run on forever 
        time_limit = STARTTIME - timedelta(weeks = 24) #The number of weeks can be manipulated depending on how far back should the loop iterates 
        
        i = 0 # initialize iterating variable for loop
        totalLoad = 0 # initialize variable to store totalLoad of all charging sessions

        while(i < session_limit and STARTTIME > time_limit): #end loop if session limit is reached and STARTTIME has not goes
            charge_sessions = client.service.getChargingSessionData(searchQuery = {'fromTimeStamp':STARTTIME,'toTimeStamp':ENDTIME}) #return list of charging sessions in one day 
            for j in range(0, len(charge_sessions['ChargingSessionData'])): # loop over list of charge sessions in one day
                if (charge_sessions['ChargingSessionData'][j]['userID'] == userID): # if the desired userID has completed a charging session
                    chargeHistory['sessions'].append(charge_sessions['ChargingSessionData'][j]) # add that session to the 'sessions' list in the chargeHistory dict
                    totalLoad += charge_sessions['ChargingSessionData'][j]['Energy'] # increment the energy used in that session to the totalLoad
                    i+=1 # increment interator                    
                    if i == session_limit: #detect if i has reached desired session limit
                        break # stop loop from iterating to end of charge_sessions list to save time and performance
            ENDTIME = STARTTIME # set ENDTIME one day back
            STARTTIME = ENDTIME - one_day # set STARTTIME one day back

            #repeat loop with previous day
            # NOTE: This loop takes a long time to iterate through especially with users who don't frequenly charge,
            # Try coming up with a more optimized algorithm for getting charging history if possible


        chargeHistory['averageLoad'] = totalLoad/(i+1) #calculate averageLoad
        chargeHistory['totalLoad'] = totalLoad #save totalLoad to chargeHistory dictionary
        return chargeHistory

    # getUsers return a dictionary of all the EVSE users under management
    def getUsers():
        userID = [] #initialize list of userID
        firstName = [] #initialize list of users' first names
        lastName = [] #initialize list of users' last names

        user_test = client.service.getUsers(searchQuery = {}) #getUsers method with empty search argument returns a dict of all EVSE users registered under company domain

        for i in range(0,len(user_test['users']['user'])): #Iterate over each user until all users are iterated over
            userID.append(user_test['users']['user'][i]['userID']) # add the user's ID to userID list
            firstName.append(user_test['users']['user'][i]['firstName']) # add the user's first name to list of first names
            lastName.append(user_test['users']['user'][i]['lastName']) # add user's last name to list of last names
        users = {'userID': userID,
                 'firstName':firstName,
                 'lastName':lastName}
        return users

    # getSiteLoad returns the site load of all EVSEs
    # within station groups "sgIDs" in kW
    def getSiteLoad(sgIDs):
        siteLoad = 0 #kW
        for i in range(0,len(sgIDs)): #iterate over all station groups (sgIDs)
            load = client.service.getLoad(searchQuery = {'sgID':sgIDs[i]}) #this method with sgID search parameter returns the load of the station group
            siteLoad += float(load['sgLoad']) #add station group load to total site load
        return siteLoad # return current total site load

    # Main executes the demand control algorithm by checking the site load per user defined frequency
    # and adjust load shedding for active stations based on demand conditions
    if __name__ == '__main__':
        try:
            demandCap = float(raw_input('Please Enter a Demand Cap in kW: ')) #This input prompt allows user to set a desired site load limit for DR functionality 
        except TypeError as e: # catch error or exception if user types in wrong type of value
            traceback.print_exc()
            sys.exit(1)
        sgIDs = [61001, 61195, 61005, 78673, 61727, 61003] #list of all station group IDs for AHM
        with open('stations.txt','r') as stations: #open the text file containing a list of all station IDs
            stationIDs = stations.readlines() # return a list of station IDs after reading the text file
            
        try:
            while True: #continuously run the loop without any terminating condition
                siteLoad = getSiteLoad(sgIDs) # get the current site load
                
                # The following conditionals, using the current site load as a benchmark, trigger the respective demand response actions
                
                # Condition 1: If total current site load is a significant margin from desired demand cap, clear all stations' shed states and allow peak charge capacity
                if siteLoad < (demandCap - Decimal(16.6)): #16.6 kW difference margin was set as a hard test value, but should be changed based on actual testing on the site
                    print "Current site load is: " + str(siteLoad) + " kW"
                    print "Clearing shed states"
                    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61195'}})
                    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61005'}})
                    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61003'}})
                    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61001'}})
                    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'78673'}})
                    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61727'}})
                
                # Condition 2: If total site load is still moderately far from demand cap, increase charging power by 1.25 times to allow faster EV charging for employees
                elif siteLoad < (demandCap - 10): #again, 10 kW margin was set as a hard test value, perform practical testing to certify a good value for this condition
                    print "Current site load is: " + str(siteLoad) + " kW"
                    print "Increasing load to reach demand cap"
                    
                    # Iterate over each station
                    for i in range(0, len(stationIDs)):
                        s = client.service.getLoad(searchQuery = {'stationID':stationIDs[i]}) #return a dict of the station load data
                        stationLoad = s['stationData'][0]['stationLoad'] # Retrieve the station total load and assign to variable
                        port1Load = s['stationData'][0]['Port'][0]['portLoad'] # Retrieve station port 1's load and assign to variable
                        port2Load = s['stationData'][0]['Port'][1]['portLoad'] # Retrieve station port 2's load and assign to variable
    
                        if stationLoad == 0.0: # if the station is not charging or is inactive
                            continue # iterate to next station
                        else:
                            if port1Load != 0.0 and port1Load <= Decimal(2.5): # if port 1's load is charging and load is less 2.5 kW
                                # increase port 1's load by 1.25 times
                                client.service.shedLoad(shedQuery = {'shedStation':{'stationID':stationIDs[i],'Ports':{'Port':{'portNumber':1,'allowedLoadPerPort':str(port1Load * Decimal(1.25))}}},'timeInterval':0})
                            if port2Load != 0.0 and port2Load <= Decimal(2.5): # if port 2's load is charging and load is less 2.5 kW
                                # increase port 2's load by 1.25 times
                                client.service.shedLoad(shedQuery = {'shedStation':{'stationID':stationIDs[i],'Ports':{'Port':{'portNumber':2,'allowedLoadPerPort':str(port2Load * Decimal(1.25))}}},'timeInterval':0})
                
                # Condition 3: If site load is below the demand cap by an acceptable margin, make no change
                elif siteLoad < (demandCap - Decimal(6.6)): # 6.6 kW is a hard test value, should be changed based on practical testing
                    print "Current site load is: " + str(siteLoad) + " kW"
                    print "Continue operations"
                    time.sleep(60) # delay 1 minute
                    continue # continue loop

                # Condition 4: If site load is approaching close to the demand cap, begin load shedding
                elif siteLoad >= (demandCap - Decimal(6.6)):
                    print "Current site load is: " + str(siteLoad) + " kW"
                    print "Applying additional load shedding"
                    for i in range(0, len(stationIDs)): #for loop iterates through each station to query and save each station's load along with its ports' load values
                        s = client.service.getLoad(searchQuery = {'stationID':stationIDs[i]})
                        stationLoad = s['stationData'][0]['stationLoad']
                        port1Load = s['stationData'][0]['Port'][0]['portLoad']
                        port2Load = s['stationData'][0]['Port'][1]['portLoad']
                        if stationLoad == 0.0: # if station not charging
                            continue # iterate to next station
                        else:
                            if port1Load != 0.0 or port1Load > Decimal(2.5): #if port 1 is charging higher than 2.5 kW
                                #shed port charging load to 75%
                                client.service.shedLoad(shedQuery = {'shedStation':{'stationID':stationIDs[i],'Ports':{'Port':{'portNumber':1,'allowedLoadPerPort':str(port1Load * Decimal(0.75))}}},'timeInterval':0})
                            if port2Load != 0.0 or port2Load > Decimal(2.5): #if port 2 is charging higher than 2.5 kW
                                #shed port charging load to 75%
                                client.service.shedLoad(shedQuery = {'shedStation':{'stationID':stationIDs[i],'Ports':{'Port':{'portNumber':2,'allowedLoadPerPort':str(port2Load * Decimal(0.75))}}},'timeInterval':0})
                time.sleep(120) # delay next site load check by 2 minutes, interval can be manually set
        except KeyboardInterrupt: #allow loop and program to stop executing using CONTROL+C
            print "Program Ended"
