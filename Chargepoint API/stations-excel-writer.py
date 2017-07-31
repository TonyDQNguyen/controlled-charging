import zeep
from zeep.client import Client
from zeep.transports import Transport
from zeep.cache import SqliteCache
from zeep.wsse.username import UsernameToken
import requests
import openpyxl
import xlsxwriter
from types import *


USERNAME = '94a8e8abffb20dfc4826221c2b8ba1d058a46c3cd57e11487170620'
PASSWORD = '0f503938100c2839c2f2fafe0cc6e406'
wsdl = 'https://webservices.chargepoint.com/cp_api_5.0.wsdl'


transport = Transport(cache=SqliteCache())
client = zeep.Client(wsdl=wsdl, wsse=UsernameToken(USERNAME, PASSWORD))
client.options(raw_response = False)
response = client.service.getStations(searchQuery = {'City':'Torrance'})
station_names = []
stationIDs = []
sgIDs = []
mac_addresses = []
last_iteration = len(response['stationData'])
for i in range(0,last_iteration):
    station_names.append(response['stationData'][i]['Port'][0]['stationName'])
    stationIDs.append(response['stationData'][i]['stationID'])
    sgIDs.append(response['stationData'][i]['sgID'].split(",")[0])
    mac_addresses.append(response['stationData'][i]['stationMacAddr'])
excel_data = [station_names, stationIDs, sgIDs, mac_addresses]        
workbook = xlsxwriter.Workbook('AHM_EVSEs_Index.xlsx')
worksheet = workbook.add_worksheet()

row = 0

for col, data in enumerate(excel_data):
    worksheet.write_column(row,col,data)

workbook.close()



