import zeep
from zeep.client import Client
from zeep.transports import Transport
from zeep.cache import SqliteCache
from zeep.wsse.username import UsernameToken
import requests
from types import *
from datetime import datetime
from datetime import timedelta

## Use this test program to test various Chargepoint API methods to retrieve data for visualization (i.e. getLoad() for specific stations, groups) 

USERNAME = '94a8e8abffb20dfc4826221c2b8ba1d058a46c3cd57e11487170620'
PASSWORD = '0f503938100c2839c2f2fafe0cc6e406'
wsdl = 'https://webservices.chargepoint.com/cp_api_5.0.wsdl'

transport = Transport(cache=SqliteCache())
client = zeep.Client(wsdl=wsdl, wsse=UsernameToken(USERNAME, PASSWORD))
#response = client.service.getStations(searchQuery = {'stationName':'AHM TORRANCE / 27-28'})
#print response
today = datetime(2017,06,23,19,00,00)

## client.service.getStations(searchQuery = {})
print client.service.getLoad(searchQuery =  {'stationID':'1:115881'})
print client.service.getStations(searchQuery = {'stationID':'1:115791'})
