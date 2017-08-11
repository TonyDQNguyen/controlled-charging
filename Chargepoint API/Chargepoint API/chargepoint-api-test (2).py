import zeep
from zeep.client import Client
from zeep.transports import Transport
from zeep.cache import SqliteCache
from zeep.wsse.username import UsernameToken
import requests
from types import *
from datetime import datetime
from datetime import timedelta

## NOTE: This module is used for general API call testing
## USE: Comment out any code you don't want run, and run the calls not commented

USERNAME = '94a8e8abffb20dfc4826221c2b8ba1d058a46c3cd57e11487170620'
PASSWORD = '0f503938100c2839c2f2fafe0cc6e406'
wsdl = 'https://webservices.chargepoint.com/cp_api_5.0.wsdl'

transport = Transport(cache=SqliteCache())
client = zeep.Client(wsdl=wsdl, wsse=UsernameToken(USERNAME, PASSWORD))

##response = client.service.getStations(searchQuery = {'City': 'Torrance'})
##print response

##charge_sessions = client.service.getStationStatus(searchQuery = {'City':'Torrance','Status':2,'portDetails':True})
##print charge_sessions

##station_groups = client.service.getStationGroups(orgID='1:NA002323')
##print station_groups

##station_group_details = client.service.getStationGroupDetails(sgID = 61005)
##print station_group_details

##print client.service.getStationRightsProfile(sgID = 61005)

##print client.service.getAlarms(searchQuery = {})
##print client.service.clearAlarms(searchQuery = {'stationID':'1:115821'})

##client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61195'}})
##client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61005'}})
##client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61003'}})
##client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61001'}})

print client.service.getLoad(searchQuery = {'stationID':'1:115821'})

##print client.service.clearShedState(shedQuery = {'shedStation':{'stationID':'1:115821','Ports':{'Port':{'portNumber':2}}}})

##shed_load = client.service.shedLoad(shedQuery = {'shedStation':{'stationID':'1:115821','allowedLoadPerStation':'2.0'},'timeInterval':0})
####'Ports':{'Port':{'portNumber':2,'allowedLoadPerPort':'2.5'}}},'timeInterval':0})
##print shed_load

##feed = client.service.registerFeeds(Events = {'feedEventName':['station_usage_status_change', 'station_charging_session_start']}, searchQuery = {'stationID':'1:115821'})
##print client.service.updateFeed(subscriptionID = 125522L, Refresh = 0)
##print feed
## subscription ID = 125522L

##print client.service.updateFeed(hi =  0)
##print client.service.getTransactionData(searchQuery = {'stationID':'1:115821'})

