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

## Version 1.5 ##
## Note: On top of shedding every station to below the demand cap, this version
## dynamically compiles and observes three lists:
##      1. List of users charging
##      2. List of users finished charging
##      3. Total users charging and finished
##  This user lists analysis is then implemented in addition to the base level
##  load shedding to accomplish first stage user-oriented demand control

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
        time_limit = STARTTIME - timedelta(weeks = 8)
        isLimit = False
        while(i <= session_limit and STARTTIME >= time_limit):
            print 'Still Working'
            charge_sessions = client.service.getChargingSessionData(searchQuery = {'fromTimeStamp':STARTTIME,'toTimeStamp':ENDTIME})
            for j in range(0, len(charge_sessions['ChargingSessionData'])):
                if (charge_sessions['ChargingSessionData'][j]['userID'] == userID):
                    chargeHistory['sessions'].append(charge_sessions['ChargingSessionData'][j])
                    i+=1
                    totalLoad += charge_sessions['ChargingSessionData'][j]['Energy']
                    if i==session_limit:
                        isLimit = True
                        break
            if isLimit == True:
                break
            else:
                ENDTIME = STARTTIME
                STARTTIME = ENDTIME - one_day

        chargeHistory['averageLoad'] = totalLoad/(i+1)
        chargeHistory['totalLoad'] = totalLoad
        return chargeHistory

    # getUsers return a dictionary of all the EVSE users under management
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

    # getSiteLoad returns the site load of all EVSEs
    # within station groups "sgIDs" in kW
    def getSiteLoad(sgIDs):
        siteLoad = 0 #kW
        users = 0
        for i in range(0,len(sgIDs)):
            load = client.service.getLoad(searchQuery = {'sgID':sgIDs[i]})
            siteLoad += float(load['sgLoad'])
            for j in range(0, len(load['stationData'])):
                for k in range(0,len(load['stationData'][j]['Port']):
                    if not(load['stationData'][j]['Port'][k]['userID'] is None):
                        users += 1
        return siteLoad, users

    # Main executes the demand control algorithm by checking the site load
    # and adjust load shedding for active stations per necessity
    if __name__ == '__main__':
        try:
            demandCap = float(raw_input('Please Enter a Demand Cap in kW: '))
        except TypeError as e:
            traceback.print_exc()
            sys.exit(1)
        sgIDs = [61001, 61195, 61005, 78673, 61727, 61003]
        with open('stations.txt','r') as stations:
            stationIDs = stations.readlines()
        try:
            users = 0
            while True:              
                siteLoad, tempUsers = getSiteLoad(sgIDs)
                if tempUsers <= users:
                    users = tempUsers
                    if siteLoad < (demandCap - 10):
                        print "Current site load is: " + str(siteLoad) + " kW"
                        print "Clearing shed states on all stations"
                        client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61195'}})
                        client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61005'}})
                        client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61003'}})
                        client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61001'}})
                        client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'78673'}})
                        client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61727'}})
                    elif siteLoad < (demandCap - 6.6):
                        print "Current site load is: " + str(siteLoad) + " kW"
                        print "Continue operations"
                        time.sleep(60)
                        continue
                    elif siteLoad >= (demandCap - 6.6):
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
                                    client.service.shedLoad(shedQuery = {'shedStation':{'stationID':stationIDs[i],'Ports':{'Port':{'portNumber':1,'allowedLoadPerPort':str(port1Load*0.75)}}},'timeInterval':0})
                                if port2Load != 0.0 or port2Load > Decimal(1.5):
                                    client.service.shedLoad(shedQuery = {'shedStation':{'stationID':stationIDs[i],'Ports':{'Port':{'portNumber':2,'allowedLoadPerPort':str(port2Load*0.75)}}},'timeInterval':0})
                elif tempUsers > users:
                    users = tempUsers
                    if siteLoad < (demandCap - 10):
                        print "Current site load is: " + str(siteLoad) + " kW"
                        print "Clearing shed states on all stations"
                        client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61195'}})
                        client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61005'}})
                        client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61003'}})
                        client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61001'}})
                        client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'78673'}})
                        client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61727'}})
                    elif siteLoad < (demandCap - 6.6):
                        print "Current site load is: " + str(siteLoad) + " kW"
                        print "Continue operations"
                        time.sleep(60)
                        continue
                    elif siteLoad >= (demandCap - 6.6):
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
                                    client.service.shedLoad(shedQuery = {'shedStation':{'stationID':stationIDs[i],'Ports':{'Port':{'portNumber':1,'allowedLoadPerPort':str(port1Load*0.75)}}},'timeInterval':0})
                                if port2Load != 0.0 or port2Load > Decimal(1.5):
                                    client.service.shedLoad(shedQuery = {'shedStation':{'stationID':stationIDs[i],'Ports':{'Port':{'portNumber':2,'allowedLoadPerPort':str(port2Load*0.75)}}},'timeInterval':0})
           
                time.sleep(120)
        except KeyboardInterrupt:
            print "Program Ended"
