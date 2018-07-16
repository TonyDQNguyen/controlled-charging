## Abort.py clears all settings applied on the station using the region id ("sgID" tags)
## to return all EVSEs to their nominal peak charging state. Refer to Chargepoint API Docs for Usage
## and list of callable methods

## IMPORTANT: abort.py should be executed after any demand respone (DR) testing is conducted and/or at end of day (especially Friday)
## to ensure entire site charging returns to normal without any shed states if any testing or settings is done during the workday

import zeep # Zeep is the package used for calling the methods in Chargepoint's API under the SOAP API standard 
from zeep.client import Client # To learn more about installing and using Zeep, go to http://docs.python-zeep.org/en/master/
from zeep.transports import Transport
from zeep.cache import SqliteCache
from zeep.wsse.username import UsernameToken

def abort():
    USERNAME = '94a8e8abffb20dfc4826221c2b8ba1d058a46c3cd57e11487170620' # Provided by Chargepoint to access API
    PASSWORD = '0f503938100c2839c2f2fafe0cc6e406' # Provided by Chargepoint to access API
    wsdl = 'https://webservices.chargepoint.com/cp_api_5.0.wsdl' # This variable is assigned a URL to Chargepoint XML-based database with the API's callable methods 

    transport = Transport(cache=SqliteCache()) # Enable Zeep to initialize its caching feature to improve performance
    global client # declare client as a globally accesible variable

    # initialize client and authenticate USERNAME and PASSWORD
    # to access API for calling methods
    client = zeep.Client(wsdl=wsdl, wsse=UsernameToken(USERNAME, PASSWORD)) 

    # method clearShedState removes all shedStates on the target specified in the argument
    # NOTE: Chargepoint API Method Calling Format:
    # client.service.API_METHOD_HERE(QUERY_TYPE_HERE = {
    #   'TARGETED_PARAMETER':'SPECIFIER'
    # }) 
    #   QUERY_TYPE_HERE can be either shedQuery or searchQuery depends on method called
    #   for clearShedState, use shedQuery
    #   the TARGETED_PARAMETER is shedGroup which declares the method will set the shed state on a group specified by
    #   the SPEFICIER which is the {'sgID':'GROUP_ID'} within shedGroup
    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61195'}}) 
    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61005'}}) 
    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61003'}})
    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61001'}})
    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'78673'}})
    client.service.clearShedState(shedQuery = {'shedGroup':{'sgID':'61727'}})


if __name__ == "__main__": #comparable to the main method in other languages, used to execute functions
    abort() #execute abort()
