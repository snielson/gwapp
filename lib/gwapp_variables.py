#!/usr/bin/env python
# Written by Shane Nielson <snielson@projectuminfinitas.com>
__author__ = "Shane Nielson"
__maintainer__ = "Shane Nielson"
__email__ = "snielson@projectuminfinitas.com"

def initVersion():
	global gwappversion
	gwappversion = '0.1.6'

def setGlobalVariables(): # GLOBAL VARIABLES
	global SCRIPT_NAME
	global gwappDirectory
	global gwappConf
	global gwappLogs
	global gwappTmp
	global gwappLogSettings
	global gwappSettings
	global COMPANY_BU
	global DISCLAIMER
	global ERROR_MSG
	SCRIPT_NAME = 'gwapp'
	gwappDirectory = "/opt/gwapp"
	gwappConf = gwappDirectory + "/conf"
	gwappLogs = gwappDirectory + "/logs"
	gwappTmp = gwappDirectory + "/tmp"
	gwappLogSettings = gwappConf + "/logging.cfg"
	gwappSettings = gwappConf + "/setting.cfg"
	COMPANY_BU = 'Micro Focus'
	ERROR_MSG = "\ndgwapp has encountered an error. See gwapp.log for more details"
	DISCLAIMER = "%s accepts no liability for the consequences of any actions taken\n     by the use of this application. Use at your own discretion" % COMPANY_BU

def initLogin():
	global login
	login = []

def initSystem():
	global gwiaSystem
	global domainSystem
	global postofficeSystem
	global POASystem
	gwiaSystem = dict()
	domainSystem = dict()
	postofficeSystem = dict()
	POASystem = dict()

def setOSFiles():
	global gwhaFile
	gwhaFile = "/etc/opt/novell/groupwise/gwha.conf"

def initRESTData():
	global restDATA
	restDATA = dict()
