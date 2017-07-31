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

def abort():
    USERNAME = '94a8e8abffb20dfc4826221c2b8ba1d058a46c3cd57e11487170620'
    PASSWORD = '0f503938100c2839c2f2fafe0cc6e406'
    wsdl = 'https://webservices.chargepoint.com/cp_api_5.0.wsdl'

    transport = Transport(cache=SqliteCache())
    global client
    client = zeep.Client(wsdl=wsdl, wsse=UsernameToken(USERNAME, PASSWORD)) 

    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61195'}})
    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61005'}})
    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61003'}})
    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61001'}})
    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'78673'}})
    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61727'}})


if __name__ == "__main__":
    abort()
