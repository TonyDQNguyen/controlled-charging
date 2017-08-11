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
from decimal import Decimal


## getAHMStations() returns a list of objects(dictionaries) that compiles the current status and
## loads of all station and their ports at AHM Torrance
def getAHMStations():
    USERNAME = '94a8e8abffb20dfc4826221c2b8ba1d058a46c3cd57e11487170620'
    PASSWORD = '0f503938100c2839c2f2fafe0cc6e406'
    wsdl = 'https://webservices.chargepoint.com/cp_api_5.0.wsdl'

    AHM_stations = []
    transport = Transport(cache=SqliteCache())
    client = zeep.Client(wsdl=wsdl, wsse=UsernameToken(USERNAME, PASSWORD))
    response = client.service.getStations(searchQuery = {'City':'Torrance'})
    for i in range(0,len(response['stationData'])):
        station_data = {
                    'stationName':'',
                    'stationID':'',
                    'stationLoad':Decimal(0.0),
                    'port1Status':'',
                    'port1UserID': '',
                    'port1Load':Decimal(0.0),
                    'port2Status':'',
                    'port2UserID': '',
                    'port2Load':Decimal(0.0)
                    }
        stationID = response['stationData'][i]['stationID']
        station_status = client.service.getLoad(searchQuery = {'stationID':stationID})
        station_data['stationName'] = station_status['stationData'][0]['stationName']
        station_data['stationID'] = stationID
        station_data['stationLoad'] = station_status['stationData'][0]['stationLoad']
        if len(station_status['stationData'][0]['Port']) == 1:
            if station_status['stationData'][0]['Port'][0]['userID'] is None:
                station_data['port1Status'] = 'AVAILABLE'
                station_data['port1UserID'] = None
            elif not(station_status['stationData'][0]['Port'][0]['userID'] is None):
                station_data['port1UserID'] = station_status['stationData'][0]['Port'][0]['userID']
                if station_status['stationData'][0]['Port'][0]['portLoad'] == Decimal(0.0):
                    station_data['port1Status'] = 'NOT CHARGING'
                else:
                    station_data['port1Status'] = 'CHARGING'
                    station_data['port1Load'] = station_status['stationData'][0]['Port'][0]['portLoad']
            station_data['port2Status'] = None
            station_data['port2UserID'] = None
            station_data['port2Load'] = None
        else:
            if station_status['stationData'][0]['Port'][0]['userID'] is None:
                station_data['port1Status'] = 'AVAILABLE'
                station_data['port1UserID'] = None
            elif not(station_status['stationData'][0]['Port'][0]['userID'] is None):
                station_data['port1UserID'] = station_status['stationData'][0]['Port'][0]['userID']
                if station_status['stationData'][0]['Port'][0]['portLoad'] == Decimal(0.0):
                    station_data['port1Status'] = 'NOT CHARGING'
                else:
                    station_data['port1Status'] = 'CHARGING'
                    station_data['port1Load'] = station_status['stationData'][0]['Port'][0]['portLoad']
                    
            if station_status['stationData'][0]['Port'][1]['userID'] is None:
                station_data['port2Status'] = 'AVAILABLE'
                station_data['port2UserID'] = None
            elif not(station_status['stationData'][0]['Port'][1]['userID'] is None):
                station_data['port2UserID'] = station_status['stationData'][0]['Port'][1]['userID']
                if station_status['stationData'][0]['Port'][1]['portLoad'] == Decimal(0.0):
                    station_data['port2Status'] = 'NOT CHARGING'
                else:
                    station_data['port2Status'] = 'CHARGING'
                    station_data['port2Load'] = station_status['stationData'][0]['Port'][1]['portLoad']
                
        AHM_stations.append(station_data)
    return AHM_stations
       
##calling getAHMStations() to get current stations status then save it to a csv file
## called "AHM_stations_status.csv"
AHM_stations=getAHMStations()
pprint.pprint(AHM_stations)
keys = ['stationName','stationID','stationLoad','port1Status','port1UserID','port1Load','port2Status','port2UserID','port2Load']
with open('AHM_stations_status.csv', 'wb') as outfile:
    fp = csv.DictWriter(outfile, fieldnames = keys)
    fp.writeheader()
    fp.writerows(AHM_stations)

