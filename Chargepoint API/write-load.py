import zeep
from zeep.client import Client
from zeep.transports import Transport
from zeep.cache import SqliteCache
from zeep.wsse.username import UsernameToken
import requests
from types import *
from datetime import datetime
from datetime import timedelta
import time as time

# write_load() continously print and write a the inputted station's load at each port on the console and to a text file 'station_loads.txt' respectively
def write_load(stationID):
    
    USERNAME = '94a8e8abffb20dfc4826221c2b8ba1d058a46c3cd57e11487170620'
    PASSWORD = '0f503938100c2839c2f2fafe0cc6e406'
    wsdl = 'https://webservices.chargepoint.com/cp_api_5.0.wsdl'

    transport = Transport(cache=SqliteCache())
    client = zeep.Client(wsdl=wsdl, wsse=UsernameToken(USERNAME, PASSWORD))
    
    with open('station_loads.txt','w') as text_file:
        n = 0
        text = ''
        try:
            while(True):
                get_load = client.service.getLoad(searchQuery = {'stationID':stationID})
                if len(get_load['stationData'][0]['Port'])==2:
                    text = '\n('+str(n)+')' + '\n'+'Station Load:'+str(get_load['stationData'][0]['stationLoad'])+ ' kW\n\n Port 1'   + '\n Port 1 Load: '+str(get_load['stationData'][0]['Port'][0]['portLoad'])+ ' kW \n Port 1 Allowed Load: '+str(get_load['stationData'][0]['Port'][0]['allowedLoad'])+ ' kW\n\n Port 2'  + '\n Port 2 Load: '+str(get_load['stationData'][0]['Port'][1]['portLoad'])+ ' kW\n Port 2 Allowed Load: '+str(get_load['stationData'][0]['Port'][1]['allowedLoad'])+' kW\n'
                    print text
                    text_file.write(text)
                elif len(get_load['stationData'][0]['Port'])==1:
                    text = '\n('+str(n)+')' + '\n'+'Station Load:'+str(get_load['stationData'][0]['stationLoad'])+ ' kW\n\n Port 1'   + '\n Port 1 Load: '+str(get_load['stationData'][0]['Port'][0]['portLoad'])+ ' kW \n Port 1 Allowed Load: '+str(get_load['stationData'][0]['Port'][0]['allowedLoad'])+ ' kW\n'
                    print text
                    text_file.write(text)
                n+=1
                time.sleep(15)
        except KeyboardInterrupt: # Terminate station load console output and file writing with CONTROL + C
            pass
                
