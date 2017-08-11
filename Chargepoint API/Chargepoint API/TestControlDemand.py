import zeep
from zeep.client import Client
from zeep.transports import Transport
from zeep.cache import SqliteCache
from zeep.wsse.username import UsernameToken
import requests
from types import *
from datetime import datetime
from datetime import timedelta
import xlsxwriter
import time as time
import sys
from decimal import Decimal

##NOTE: This script is modified to test ControlDemand functionalities on one
##station only

## Version 1.0 ##
## Note: This version is the crude, barebones implementation of DR features ##
## Future updates: Implement DR based on users ##

# The controlDemand class implements DR functionalities to the Chargepoint EVSE
# network via API data query and adjustments

class ControlDemand:
    #Chargepoint API network access credentials
    USERNAME = '94a8e8abffb20dfc4826221c2b8ba1d058a46c3cd57e11487170620'
    PASSWORD = '0f503938100c2839c2f2fafe0cc6e406'
    wsdl = 'https://webservices.chargepoint.com/cp_api_5.0.wsdl'

    transport = Transport(cache=SqliteCache())
    global client
    client = zeep.Client(wsdl=wsdl, wsse=UsernameToken(USERNAME, PASSWORD))  

    # getUserChargingHistory returns a list of EVSE user (userID)
    # last "sessions_amount" sessions for analysis
    def getUserChargingHistory(userID, sessions_amount):

        chargeHistory = {
                            'userID': userID,
                            'sessions':[],
                            'averageLoad':0.0,
                            'totalLoad': 0.0
                        }
        session_limit = sessions_amount
        i = 0
        totalLoad = 0
        ENDTIME = datetime.utcnow()
        one_day = timedelta(days = 1)
        STARTTIME = ENDTIME - one_day
        print ENDTIME
        print STARTTIME
        time_limit = STARTTIME - timedelta(weeks = 24)
        while(i < session_limit and STARTTIME > time_limit):
            charge_sessions = client.service.getChargingSessionData(searchQuery = {'fromTimeStamp':STARTTIME,'toTimeStamp':ENDTIME})
            for j in range(0, len(charge_sessions['ChargingSessionData'])):
                if (charge_sessions['ChargingSessionData'][j]['userID'] == userID):
                    chargeHistory['sessions'].append(charge_sessions['ChargingSessionData'][j])
                    i+=1
                    totalLoad += charge_sessions['ChargingSessionData'][j]['Energy']
                    if i==10:
                        break
            ENDTIME = STARTTIME
            STARTTIME = ENDTIME - one_day

        chargeHistory['averageLoad'] = totalLoad/(i+1)
        chargeHistory['totalLoad'] = totalLoad
        return chargeHistory

    # getUsers return a dictionary of all the EVSE user under management
    def getUsers():
        userID = []
        firstName = []
        lastName = []

        user_test = client.service.getUsers(searchQuery = {})

        for i in range(0,len(user_test['users']['user'])):
            userID.append(user_test['users']['user'][i]['userID'])
            firstName.append(user_test['users']['user'][i]['firstName'])
            lastName.append(user_test['users']['user'][i]['lastName'])
        users = {'userID': userID,
                 'firstName':firstName,
                 'lastName':lastName}
        return users

    # getSiteLoad returns the site load of all EVSEs in kW
    def getSiteLoad():
       l = client.service.getLoad(searchQuery = {'stationID':'1:115821'})
       return l['stationData'][0]['stationLoad']
    
    # main part executes the demand control algorithm by checking the site load
    # and adjust per necessity
    if __name__ == '__main__':
        try:
            demandCap = float(raw_input('Please Enter a Demand Cap in kW: '))
        except TypeError as e:
            traceback.print_exc()
            sys.exit(1)
            
        try:
            sgIDs = [61001, 61195, 61005, 78673, 61727, 61003]
            # read in one stationID under realm management
            # from a txt file called "stations.txt" to
            # iterate through for demand control implementation  
            with open('teststation.txt','r') as stations:
                stationIDs = stations.readlines()
            while True:
                siteLoad = getSiteLoad()
                if siteLoad < (demandCap - 0.75):
                    print "Current site load is: " + str(siteLoad) + " kW"
                    print "Clearing shed states on all stations"
                    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61195'}})
                    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61005'}})
                    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61003'}})
                    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61001'}})
                    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'78673'}})
                    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61727'}})
                elif siteLoad < (demandCap - 0.25):
                    print "Current site load is: " + str(siteLoad) + " kW"
                    print "Continue operations"
                    continue
                elif siteLoad >= (demandCap - 0.25):
                    print "Current site load is: " + str(siteLoad) + " kW"
                    print "Applying additional load shedding"
                    for i in range(0, len(stationIDs)):
                        s = client.service.getLoad(searchQuery = {'stationID':stationIDs[i]})
                        stationLoad = s['stationData'][0]['stationLoad']
                        port1Load = s['stationData'][0]['Port'][0]['portLoad']
                        port2Load = s['stationData'][0]['Port'][1]['portLoad']
                        if stationLoad == 0.0:
                            continue
                        else:
                            if port1Load != 0.0 or port1Load > Decimal(1.5):
                                port1Shed = s['stationData'][0]['Port'][0]['allowedLoad']
                                client.service.shedLoad(shedQuery = {'shedStation':{'stationID':stationIDs[i],'Ports':{'Port':{'portNumber':1,'allowedLoadPerPort':str(port1Load - Decimal(0.5))}}},'timeInterval':0})
                            if port2Load != 0.0 or port2Load > Decimal(1.5):
                                port2Shed = s['stationData'][0]['Port'][1]['allowedLoad']
                                print port2Load
                                print port2Shed  
                                client.service.shedLoad(shedQuery = {'shedStation':{'stationID':stationIDs[i],'Ports':{'Port':{'portNumber':2,'allowedLoadPerPort':str(port2Load - Decimal(0.5))}}},'timeInterval':0})
                time.sleep(120)
        except KeyboardInterrupt:
            print "Program Ended"
