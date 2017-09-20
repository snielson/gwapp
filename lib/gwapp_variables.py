#!/usr/bin/env python
# Written by Shane Nielson <snielson@projectuminfinitas.com>
__author__ = "Shane Nielson"
__maintainer__ = "Shane Nielson"
__email__ = "snielson@projectuminfinitas.com"

# GLOBAL VARIABLES
def setGlobalVariables():
	global SCRIPT_NAME
	global gwappDirectory
	global gwappConf
	global gwappLogs
	global gwappTmp
	global gwappLogSettings
	global gwappSettings
	global COMPANY_BU
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


def initLogin():
	global login
	login = []

def initSystem():
	global domainSystem
	global postofficeSystem
	domainSystem = dict()
	postofficeSystem = dict()