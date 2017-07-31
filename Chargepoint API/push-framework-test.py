import zeep
from zeep.client import Client
from zeep.transports import Transport
from zeep.cache import SqliteCache
from zeep.wsse.username import UsernameToken
import requests
from types import *
from datetime import datetime
from datetime import timedelta
import sleekxmpp
import sys
import logging
import getpass
from optparse import OptionParser
from pprint import pprint
import ssl

USERNAME = '94a8e8abffb20dfc4826221c2b8ba1d058a46c3cd57e11487170620'
PASSWORD = '0f503938100c2839c2f2fafe0cc6e406'
wsdl = 'https://webservices.chargepoint.com/cp_api_5.0.wsdl'

transport = Transport(cache=SqliteCache())
client = zeep.Client(wsdl=wsdl, wsse=UsernameToken(USERNAME, PASSWORD))


##feed = client.service.registerFeeds(Events = {'feedEventName':['station_usage_status_change', 'station_charging_session_start']}, searchQuery = {'City':'Torrance'})
##print feed
## subscription ID = 125546L


"""
    SleekXMPP: The Sleek XMPP Library
    Copyright (C) 2010  Nathanael C. Fritz
    This file is part of SleekXMPP.

    See the file LICENSE for copying permission.
"""

import sys
import logging
import getpass
from optparse import OptionParser

import sleekxmpp

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input


class EchoBot(sleekxmpp.ClientXMPP):

    """
    A simple SleekXMPP bot that will echo messages it
    receives, along with a short thank you message.
    """

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

        # The message event is triggered whenever a message
        # stanza is received. Be aware that that includes
        # MUC messages and error messages.
        self.add_event_handler("message", self.message)

    def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        try:
            self.get_roster()
        except IqError as err:
            logging.error('There was an error getting the roster')
            logging.error(err.iq['error']['condition'])
            self.disconnect()
        except IqTimeout:
            logging.error('Server is taking too long to respond')
            self.disconnect()

    def message(self, msg):
        print "recievd xml \n"
        print "Message from:" + msg['from'] +"\n"
        if msg['subject']: print "Subject: " + msg['subject']+"\n"
        print "\n%(body)s" % msg
        print "\nfinish"
        ##pprint(msg)

if __name__ == '__main__':

    # Setup the EchoBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = EchoBot(USERNAME, PASSWORD)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0199') # XMPP Ping
    xmpp.ssl_version = ssl.PROTOCOL_SSLv3
    logging.basicConfig(level=logging.DEBUG,format='%(levelname)-8s %(message)s')
    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect(('https://webservice.chargepointportal.net',5223)):
        xmpp.process(block=True)
        print("Done")
        
    else:
        print("Unable to connect.")
