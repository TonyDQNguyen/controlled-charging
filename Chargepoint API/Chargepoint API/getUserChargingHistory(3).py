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

##class UserChargingHistory has two methods getUserChargingHistory() and getUsers()
class UserChargingHistory:
    USERNAME = '94a8e8abffb20dfc4826221c2b8ba1d058a46c3cd57e11487170620'
    PASSWORD = '0f503938100c2839c2f2fafe0cc6e406'
    wsdl = 'https://webservices.chargepoint.com/cp_api_5.0.wsdl'

    transport = Transport(cache=SqliteCache())
    global client
    client = zeep.Client(wsdl=wsdl, wsse=UsernameToken(USERNAME, PASSWORD))
    global k

##getUserChargingHistory accepts input of a Chargepoint userID and a number
##of previous sessions_amount to output for the userID
    def getUserChargingHistory(userID, sessions_amount):

        chargeHistory = {
                            'userID': userID,
                            'sessions':[],
                            'averageLoad':0.0,
                            'totalLoad': 0.0
                        }
        session_limit = sessions_amount
        i = 0
        totalLoad = 0
        ENDTIME = datetime.utcnow()
        one_day = timedelta(days = 1)
        STARTTIME = ENDTIME - one_day
        print ENDTIME
        print STARTTIME
        time_limit = STARTTIME - timedelta(weeks = 8)
        isLimit = False
        while(i <= session_limit and STARTTIME >= time_limit):
            print 'Still Working'
            charge_sessions = client.service.getChargingSessionData(searchQuery = {'fromTimeStamp':STARTTIME,'toTimeStamp':ENDTIME})
            for j in range(0, len(charge_sessions['ChargingSessionData'])):
                if (charge_sessions['ChargingSessionData'][j]['userID'] == userID):
                    chargeHistory['sessions'].append(charge_sessions['ChargingSessionData'][j])
                    i+=1
                    totalLoad += charge_sessions['ChargingSessionData'][j]['Energy']
                    if i==session_limit:
                        isLimit = True
                        break
            if isLimit == True:
                break
            else:
                ENDTIME = STARTTIME
                STARTTIME = ENDTIME - one_day

        chargeHistory['averageLoad'] = totalLoad/(i+1)
        chargeHistory['totalLoad'] = totalLoad
        return chargeHistory
##getUsers() returns a dictionary with lists of all the users including
##userID, firstName, and lastName
  def getUsers():
        userID = []
        firstName = []
        lastName = []

        user_test = client.service.getUsers(searchQuery = {})
##        print user_test
        for i in range(0,len(user_test['users']['user'])):
            userID.append(user_test['users']['user'][i]['userID'])
            firstName.append(user_test['users']['user'][i]['firstName'])
            lastName.append(user_test['users']['user'][i]['lastName'])
        users = {'userID': userID,
                 'firstName':firstName,
                 'lastName':lastName}
        return users

##main method can be used to run the class UserChargingHistory
##NOTE: The commented section can be used for looping through all the users
##      using getUsers(), and get each user's charging history then save
##      it to an excel spreadsheet called "AHM_User_Charging_History.xlsx"
    
    if __name__ == '__main__':
    ##        users = getUsers()
    ##        users['chargingHistory']=[]
    ##        for k in range(0,9):
    ##            print len(users['userID'])
    ##            print k
    ##            chargingHistory = getUserChargingHistory(users['userID',10][k])
    ##            users['chargingHistory'].append(chargingHistory)
    ##
    ##        excel_data = [users['userID'], users['firstName'], users['lastName'], users['chargingHistory']]        
    ##        workbook = xlsxwriter.Workbook('AHM_User_Charging_History.xlsx')
    ##        worksheet = workbook.add_worksheet()
    ##
    ##        row = 0
    ##
    ##        for col, data in enumerate(excel_data):
    ##            worksheet.write_column(row,col,data)
    ##
    ##        workbook.close()
        print getUserChargingHistory('56373', 10)
