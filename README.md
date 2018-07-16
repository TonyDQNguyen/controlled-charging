# controlled-charging
Algorithm that takes in data from Chargepoint API and SolarCity PowerGuide API to determine charging stations settings based on data obtained

# Technical Description
The various scripts retrieve data, perform control functions and execute algorithms using methods defined by The Chargepoint API and SolarCity Powerguide API in Python 2.7. Make sure to install Python 2.7 as well as any dependencies and modules using Python's pip tool. Refer to official Python 2.7 Documentations for more information.

The Chargepoint API utilizes the Simple Object Access Protocol (SOAP) web service protocol to govern its methods. The author has decided to utilize the Python SOAP client Zeep to interface with the SOAP-based Chargepoint API.  

The SolarCity PowerGuide API utilizes the Representational State Transfer (REST) web service protocol to govern its methods which is primarily based on HTML queries. Python's
standard library's *requests* module to interface with the RESTful SolarCity PowerGuide API.

Refer to the Documentations section for official docs, usage appications, and examples on each API as well as the Python module used to interact with them

# Documentations
## Chargepoint API

**Chargepoint Developer Notes v4.1:** https://na.chargepoint.com/UI/downloads/en/ChargePoint_Web_Services_API_Guide_Ver4.1_Rev4.pdf
**Zeep Python SOAP Client Docs:** http://docs.python-zeep.org/en/master/

## SolarCity Powerguide API

**SolarCity Powerguide API Official Site:** https://api.solarcity.com/powerguide/
**Zeep Python SOAP Client Docs:** http://docs.python-requests.org/en/master/

## Python 2.7

**Official Documentations:** https://docs.python.org/2.7/

# Important Scripts and Files
 1) ControlDemand.py: Contains the first algorithmic implementation of Demand Response functionalities which require testing and further development

 2) write-load.py: Contains a function that continouously outputs a station's current load at each port and writes to a text file for real time testing and data acquisition

 3) stations-excel-writer.py: Script that queries all AHM's stations information and save to an Excel spreadsheet at AHM_EVSEs_Index.xlsx

 4) getAHMStations.py: Script that queries and returns a dict of all AHM stations along with their respective load and port statuses

