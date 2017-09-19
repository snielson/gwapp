#!/usr/bin/env python
# Written by Shane Nielson <snielson@projectuminfinitas.com>
from __future__ import print_function

__author__ = "Shane Nielson"
__maintainer__ = "Shane Nielson"
__email__ = "snielson@projectuminfinitas.com"

import os
import sys
import select
import subprocess
import logging, logging.config
import ConfigParser
Config = ConfigParser.ConfigParser()

# Import requests as an alternative to urllib
import requests
# Hide requests warning (outdated python with GMS)
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

# GLOBAL VARIABLES
from gwapp_variables import *

# Log Settings
logging.config.fileConfig('%s/logging.cfg' % (gwappConf))
logger = logging.getLogger(__name__)
excep_logger = logging.getLogger('exceptions_log')

def my_handler(type, value, tb):
	tmp = traceback.format_exception(type, value, tb)
	logger.error("EXCEPTION: See exception.log")
	excep_logger.error("Uncaught exception:\n%s" % ''.join(tmp).strip())
	print (''.join(tmp).strip())

# Install exception handler
sys.excepthook = my_handler


name_space = {
'SOAP-ENV': 'http://schemas.xmlsoap.org/soap/envelope/',
'gwm': 'http://schemas.novell.com/2005/01/GroupWise/methods',
'gwt': 'http://schemas.novell.com/2005/01/GroupWise/types',
'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
}

HTTPS_STRING = "https://"
HTTP_STRING = "http://"
SOAP_STRING = "/soap"
CONTENT_TYPE = "Content-Type"
TEXT_XML = "text/xml"

logoutRequest = """<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:ns0="http://schemas.novell.com/2005/01/GroupWise/types" xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns2="http://schemas.novell.com/2005/01/GroupWise/methods" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
	<SOAP-ENV:Header/>
		<ns1:Body>
			<ns2:logoutRequest>
				<session xmlns="http://schemas.novell.com/2005/01/GroupWise/methods">%s</session>
			</ns2:logoutRequest>
		</ns1:Body>
	</SOAP-ENV:Envelope>
"""

loginRequest = """<?xml version="1.0" encoding="UTF-8"?>
	<SOAP-ENV:Envelope xmlns:ns0="http://schemas.novell.com/2005/01/GroupWise/types" xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns2="http://schemas.novell.com/2005/01/GroupWise/methods" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
		<SOAP-ENV:Header/>
		<SOAP-ENV:Body>
			<ns1:loginRequest>
				<auth xmlns="http://schemas.novell.com/2005/01/GroupWise/methods" xsi:type="ns0:TrustedApplication">
					<ns0:username>%s</ns0:username>
					<ns0:name>%s</ns0:name>
					<ns0:key>%s</ns0:key>
				</auth>
				<language xmlns="http://schemas.novell.com/2005/01/GroupWise/methods">en</language>
				<version xmlns="http://schemas.novell.com/2005/01/GroupWise/methods">1.05</version>
				<application xmlns="http://schemas.novell.com/2005/01/GroupWise/methods">gwapp_service</application>
				<userid xmlns="http://schemas.novell.com/2005/01/GroupWise/methods">true</userid>
			</ns1:loginRequest>
		</SOAP-ENV:Body>
	</SOAP-ENV:Envelope>
"""

getFolderListRequest = """<?xml version="1.0" encoding="UTF-8"?>
	<SOAP-ENV:Envelope xmlns:ns0="http://schemas.novell.com/2005/01/GroupWise/types" xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns2="http://schemas.novell.com/2005/01/GroupWise/methods" xmlns:tns="http://schemas.novell.com/2005/01/GroupWise/types" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
		<SOAP-ENV:Header>
			<tns:session>%s</tns:session>
		</SOAP-ENV:Header>
		<SOAP-ENV:Body>
			<ns0:getFolderListRequest>
				<parent xmlns="http://schemas.novell.com/2005/01/GroupWise/methods">folders</parent>
				<view xmlns="http://schemas.novell.com/2005/01/GroupWise/methods">default nodisplay pabName</view>
				<recurse xmlns="http://schemas.novell.com/2005/01/GroupWise/methods">true</recurse>
				<imap xmlns="http://schemas.novell.com/2005/01/GroupWise/methods">true</imap>
				<nntp xmlns="http://schemas.novell.com/2005/01/GroupWise/methods">true</nntp>
			</ns0:getFolderListRequest>
		</SOAP-ENV:Body>
	</SOAP-ENV:Envelope>
"""

getAddressBookListRequest = """<?xml version="1.0" encoding="UTF-8"?>
	<SOAP-ENV:Envelope xmlns:ns0="http://schemas.novell.com/2005/01/GroupWise/types" xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns2="http://schemas.novell.com/2005/01/GroupWise/methods" xmlns:tns="http://schemas.novell.com/2005/01/GroupWise/types" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
		<SOAP-ENV:Header>
			<tns:session>%s</tns:session>
		</SOAP-ENV:Header>
		<SOAP-ENV:Body>
			<ns0:getAddressBookListRequest>
				<view xmlns="http://schemas.novell.com/2005/01/GroupWise/methods">shared fullid</view>
			</ns0:getAddressBookListRequest>
		</SOAP-ENV:Body>
	</SOAP-ENV:Envelope>
"""

modifyItemRequest = """<?xml version="1.0" encoding="UTF-8"?>
	<SOAP-ENV:Envelope xmlns:ns0="http://schemas.novell.com/2005/01/GroupWise/types" xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns2="http://schemas.novell.com/2005/01/GroupWise/methods" xmlns:tns="http://schemas.novell.com/2005/01/GroupWise/types" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
		<SOAP-ENV:Header>
			<tns:session>%s</tns:session>
		</SOAP-ENV:Header>
		<SOAP-ENV:Body>
			<ns0:modifyItemRequest>
				<id xmlns="http://schemas.novell.com/2005/01/GroupWise/methods">%s</id>
				<updates xmlns="http://schemas.novell.com/2005/01/GroupWise/methods">
					<update xmlns="http://schemas.novell.com/2005/01/GroupWise/methods">
						<parent xmlns="http://schemas.novell.com/2005/01/GroupWise/methods">%s</parent>
						<sequence xmlns="http://schemas.novell.com/2005/01/GroupWise/methods">0</sequence>
					</update>
				</updates>
			</ns0:modifyItemRequest>
		</SOAP-ENV:Body>
	</SOAP-ENV:Envelope>
"""

modifyItemRequest_Calendar = """<?xml version="1.0" encoding="UTF-8"?>
	<SOAP-ENV:Envelope xmlns:ns0="http://schemas.novell.com/2005/01/GroupWise/types" xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns2="http://schemas.novell.com/2005/01/GroupWise/methods" xmlns:tns="http://schemas.novell.com/2005/01/GroupWise/types" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
		<SOAP-ENV:Header>
			<tns:session>%s</tns:session>
		</SOAP-ENV:Header>
		<SOAP-ENV:Body>
			<ns0:modifyItemRequest>
				<id xmlns="http://schemas.novell.com/2005/01/GroupWise/methods">%s</id>
				<updates xmlns="http://schemas.novell.com/2005/01/GroupWise/methods">
					<update xmlns="http://schemas.novell.com/2005/01/GroupWise/methods">
						<parent xmlns="http://schemas.novell.com/2005/01/GroupWise/methods">%s</parent>
						<sequence xmlns="http://schemas.novell.com/2005/01/GroupWise/methods">0</sequence>
						<calSequence xmlns="http://schemas.novell.com/2005/01/GroupWise/methods">0</calSequence>
					</update>
				</updates>
			</ns0:modifyItemRequest>
		</SOAP-ENV:Body>
	</SOAP-ENV:Envelope>
"""