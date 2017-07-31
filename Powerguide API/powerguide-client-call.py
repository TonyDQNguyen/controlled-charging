import base64
import requests
import pprint
import datetime
from threading import Timer,Thread,Event
import time
import matplotlib.pyplot as plt
import matplotlib.lines as line
import numpy as numpy
import matplotlib.animation as animation
from matplotlib import style

def powerguide_client_call():
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
    pprint.pprint(r.json())

    # Request Customer detail for first customer record
    guid = r.json()['Data'][2]['GUID']
    customer_detail = requests.get('https://api.solarcity.com/powerguide/v1.0/customers/'+guid, 
          headers=headers, 
          params = {'IsDetailed':'true'})

##    print 'CUSTOMER'
    pprint.pprint(customer_detail.json())

    # Request Installation Detail
    installation_guid = customer_detail.json()['Installations'][0]['GUID']
    installation_detail = requests.get('https://api.solarcity.com/powerguide/v1.0/installations/'+installation_guid, 
          headers=headers, 
          params = {'IncludeDevices':'true'})

##    print 'INSTALLATION DETAIL'
    pprint.pprint(installation_detail.json())

    # Request Time Series Generation data by 15 minute interval
    from datetime import datetime
    from datetime import timedelta
    now = datetime.now()
    StartTime = now.replace(hour = 0, minute = 0, second = 0)
    now = now.isoformat()
    StartTime = StartTime.isoformat()
    r = requests.get('https://api.solarcity.com/powerguide/v1.0/measurements/'+installation_guid, 
          headers=headers, 
          params = {'StartTime': StartTime, 
          'EndTime': now,
          'Period': 'QuarterHour',
          'IsByDevice': 'false',
          'IncludeCurrent': 'true'})
##    print '15 Minute MEASUREMENTS'
    pprint.pprint(r.json())
    latest_index = len(r.json()['Measurements'])-1
    measurements = []
    timestamps_temp = []
    timestamps=[]
    for i in range(0,latest_index+1):
        measurements.append(r.json()['Measurements'][i]['EnergyInIntervalkWh'])
        timestamps_temp.append(r.json()['Measurements'][i]['Timestamp'])
        timestamps.append(datetime.strptime(timestamps_temp[i],"%Y-%m-%dT%H:%M:%S"))
    newest_timestamp = timestamps[latest_index]
    newest_measurement = measurements[latest_index]
    return [timestamps, measurements, newest_timestamp, newest_measurement]
    


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

def metrics(electricity_in_kWh):
    carbon_offset = (0.000703*1000)*electricity_in_kWh # kg CO2
    trees_saved = (1.0/0.039*0.000703)*electricity_in_kWh #trees seedling in 10 years
    return carbon_offset, trees_saved

def update_line(i):
    timestamps, measurements, newest_timestamp, newest_measurement = powerguide_client_call()
    global total_trees_saved
    global total_carbon_offset
    global n
    if n != len(measurements):
        total_carbon_offset += trees_saved(newest_measuremeent).carbon_offset
        total_trees_saved += trees_saved(newest_measurement).trees_saved
        n+=1
    timestamps_hour = []
    for i in range(0, len(timestamps)):
        timestamps_hour.append(float(timestamps[i].hour)+(timestamps[i].minute*1.0/60.0))
    line.set_data(timestamps_hour, measurements)
    ax.clear()
    ax.plot(timestamps_hour,measurements)
    text_box = 'Total CO2 Offset: ' + str(round(total_carbon_offset)) + ' kg CO2 \nTotal Trees Saved: ' + str(round(total_trees_saved,2)) + ' trees'
    ax.text(0.95,0.8, text_box, style='normal', color = 'white', 
            verticalalignment='top', horizontalalignment='right', bbox={'facecolor':'green', 'alpha':0.5, 'pad':10}, transform=ax.transAxes)
    rects = ax.bar(timestamps_hour,measurements,  color = 'green', width = 0.15)
    plt.title('Solar-Generated Energy as of ' + newest_timestamp.isoformat())
    plt.xlabel('Time in hour')
    plt.ylabel('Solar-generated energy in kWh')
    plt.xlim(0,24)
    plt.xticks(numpy.arange(0,24, 1.0))
    
##    plt.ylim(0,250)


def autolabel(rects):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                '%d' % int(height),
                ha='center', va='bottom')

if __name__ == "__main__":
    try:
        style.use('fivethirtyeight')
        timestamps, measurements, newest_timestamp, newest_measurement = powerguide_client_call()
        global timestamps_hour
        global total_carbon_offset
        global total_trees_saved
        global n
        timestamps_hour = []
        total_carbon_offset, total_trees_saved = metrics(sum(list(measurements)))
        n = len(measurements)
        for i in range(0, len(timestamps)):
            timestamps_hour.append(float(timestamps[i].hour)+(timestamps[i].minute*1.0/60.0))
        fig1 = plt.figure()
        ax = fig1.add_subplot(1,1,1)
        plt.title('Solar-Generated Energy as of ' + newest_timestamp.isoformat())
        line, = ax.plot(timestamps_hour,measurements)
        rects = ax.bar(timestamps_hour,measurements, color = 'green', width = 0.15)
        line_ani = animation.FuncAnimation(fig1, update_line, interval = 3000000)
        plt.xlabel('Time in hour')
        plt.ylabel('Solar-generated energy in kWh')
        plt.xlim(0,24)
        plt.xticks(numpy.arange(0,24 , 1.0))
        text_box = 'Total CO2 Offset: ' + str(round(total_carbon_offset)) + ' kg CO2 \nTotal Trees Saved: ' + str(round(total_trees_saved,2)) + ' trees'
        ax.text(0.95,0.8, text_box, style='normal', color = 'white', 
                verticalalignment='top', horizontalalignment='right', bbox={'facecolor':'green', 'alpha':0.5, 'pad':10}, transform=ax.transAxes)
        plt.grid()
        plt.show()
    except requests.exceptions.ConnectionError as e:
        print e
        
  



