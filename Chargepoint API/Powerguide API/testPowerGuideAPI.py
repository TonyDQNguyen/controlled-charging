import base64
import requests
import pprint


def powerguideClientCall():
    # Put your username and password here
    USERNAME = 'ryan_harty@ahm.honda.com'
    PASSWORD = 'Solar421'

    # OAuth2 settings
    CLIENT_ID = 'powerguide_api_dev'
    CLIENT_SECRET = 'm+OxOfSw9E3daSXsl5Qt7yCI4TAxjRPAJcDa5BUbiJA='
    SCOPE = 'https://api.solarcity.com/solarguard/'

    auth_data = {'grant_type': 'password', 
          'username':USERNAME,
          'password':PASSWORD,
          'scope':SCOPE}

    headers = {'Authorization':'Basic '+ base64.b64encode(CLIENT_ID+':'+CLIENT_SECRET)}

    r = requests.post('https://login.solarcity.com/issue/oauth2/token', headers=headers, data=auth_data)
##    print r.json()
    access_token = r.json()['access_token']
##    print 'Obtained Access Token'

    headers = {'Authorization': 'Bearer '+access_token}

    # Request list of Customers records
    r = requests.get('https://api.solarcity.com/powerguide/v1.0/customers', 
          headers=headers, 
          params = {'Size':10,'Page':1})
##    pprint.pprint(r.json())

    # Request Customer detail for first customer record
    guid = r.json()['Data'][1]['GUID']
    customer_detail = requests.get('https://api.solarcity.com/powerguide/v1.0/customers/'+guid, 
          headers=headers, 
          params = {'IsDetailed':'true'})

##    print 'CUSTOMER'
##    pprint.pprint(customer_detail.json())

    # Request Installation Detail
    installation_guid = customer_detail.json()['Installations'][0]['GUID']
    installation_detail = requests.get('https://api.solarcity.com/powerguide/v1.0/installations/'+installation_guid, 
          headers=headers, 
          params = {'IncludeDevices':'true'})

##    print 'INSTALLATION DETAIL'
##  pprint.pprint(installation_detail.json())

    # Request Time Series Generation data by 15 minute interval 
    r = requests.get('https://api.solarcity.com/powerguide/v1.0/measurements/'+installation_guid, 
          headers=headers, 
          params = {'StartTime': '2017-6-14T06:00:00', 
          'EndTime': '2017-6-14T14:30:00',
          'Period': 'QuarterHour',
          'IsByDevice': 'false',
          'IncludeCurrent': 'true'})
    print '15 Minute MEASUREMENTS'
    latest_index = len(r.json()['Measurements'])-1
    newest_measurement = r.json()['Measurements'][latest_index]['EnergyInIntervalkWh']
    return newest_measurement
##    pprint.pprint(r.json())

    # Request Time Series Generation data by daily interval
##    r = requests.get('https://api.solarcity.com/powerguide/v1.0/measurements/'+installation_guid, 
##          headers=headers, 
##          params = {'StartTime': '2017-6-1', 
##          'EndTime': '2017-6-14',
##          'Period': 'Day',
##          'IsByDevice': 'true'})
##    print 'Daily MEASUREMENTS'
##
##    for i in range(0,len(r.json()['Devices'])):
##        latest_index = len(r.json()['Devices'][i]['Measurements'])-1
##        print r.json()['Devices'][i]['Measurements'][latest_indexs]['EnergyInIntervalkWh']
##        
##    #pprint.pprint(r.json())
##
##    # Request Time Series Consumption data by hourly interval
##    r = requests.get('https://api.solarcity.com/powerguide/v1.0/consumption/'+installation_guid,
##        headers=headers,
##        params = {'Period': 'Hour',
##                  'StartTime': '2017-6-14T06:00:00',
##                  'EndTime': '2017-6-14T15:00:00',
##                  'IncludeCurrent': 'true'})
##    print 'Hourly Consumption 06/14/2017'
##    pprint.pprint(r.json())




