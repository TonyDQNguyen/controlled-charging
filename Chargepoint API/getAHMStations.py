import zeep
from zeep.client import Client
from zeep.transports import Transport
from zeep.cache import SqliteCache
from zeep.wsse.username import UsernameToken
import requests
from types import *
from datetime import datetime
from datetime import timedelta
import pprint as pprint
import csv

def getAHMStations():
    USERNAME = '94a8e8abffb20dfc4826221c2b8ba1d058a46c3cd57e11487170620'
    PASSWORD = '0f503938100c2839c2f2fafe0cc6e406'
    wsdl = 'https://webservices.chargepoint.com/cp_api_5.0.wsdl'

    AHM_stations = []
    transport = Transport(cache=SqliteCache())
    client = zeep.Client(wsdl=wsdl, wsse=UsernameToken(USERNAME, PASSWORD))
    response = client.service.getStations(searchQuery = {'City':'Torrance'})
    station_status = client.service.getLoad(searchQuery = {'stationID':'1:145107'})
    for i in range(0,len(response['stationData'])):
        station_data = {
                    'stationName':'',
                    'stationID':'',
                    'stationLoad':0,
                    'Port':[]
                    }
        stationID = response['stationData'][i]['stationID']
        station_status = client.service.getLoad(searchQuery = {'stationID':stationID})
        station_data['stationName'] = station_status['stationData'][0]['stationName']
        station_data['Port'] = station_status['stationData'][0]['Port']
        station_data['stationID'] = stationID
        station_data['stationLoad'] = station_status['stationData'][0]['stationLoad']
        AHM_stations.append(station_data)
    return AHM_stations
       

AHM_stations=getAHMStations()
pprint.pprint(AHM_stations)
keys = AHM_stations[0].keys()

with open('output.csv', 'wb') as output:
##    fieldnames = ['stationID', 'stationLoad', 'Port','stationName']
##    writer = csv.DictWriter(output, fieldnames=fieldnames)
##    writer.writeheader()
##    writer = csv.writer(output)
####    writer.writerow(AHM_stations)
##    for each in AHM_stations:
##        temp_list = []
##        for value in each.iteritems():
##            value = list(value)
##            temp_list.append(value[1])
##
##        writer.writerow(temp_list)
    pprint(getAHMStations())
