#!/usr/bin/env python
from __future__ import print_function
import sys
import traceback
import datetime
import logging, logging.config
import gwapp_definitions as gw
import gwapp_variables
# import commands


# Global variables
healthCheckLog = gwapp_variables.gwappLogs + '/healthCheck.log'

# Log Settings
logging.config.fileConfig('%s/logging.cfg' % (gwapp_variables.gwappConf))
logger = logging.getLogger('gwapp_definitions')
excep_logger = logging.getLogger('exceptions_log')

def my_handler(type, value, tb):
	tmp = traceback.format_exception(type, value, tb)
	logger.error("EXCEPTION: See exception.log")
	excep_logger.error("Uncaught exception:\n%s" % ''.join(tmp).strip())
	print (''.join(tmp).strip())

# Install exception handler
sys.excepthook = my_handler

# Text color formats
colorGREEN = "\033[01;32m{0}\033[00m"
colorRED = "\033[01;31m{0}\033[00m"
colorYELLOW = "\033[01;33m{0}\033[00m"
colorBLUE = "\033[01;34m{0}\033[00m"

# Printing Columns
COL1 = "{0:40}"

###  Utility definitions for General Health Checks ###
def _util_NewHeader(header):
	print (COL1.format("\n%s  " % header), end='')
	sys.stdout.flush()
	logger.info("[GHC] %s" % header)
	with open(healthCheckLog, 'a') as log:
		log.write("==========================================================\n%s\n==========================================================\n" % header)

def _util_passFail(result, msg=None): # Prints to screen Passed,Failed, Warning, or Skipped with proper format
	with open(healthCheckLog, 'a') as log:
		if msg is not None:
			log.write(msg)

		if result == 'failed':
			print (colorRED.format("Failed"), end='')
	 		log.write("\nFailed\n\n")
	 	elif result == 'warning':
	 		print (colorYELLOW.format("Warning"), end='')
	 		log.write("\nWarning\n\n")
	 	elif result == 'skipped':
	 		print (colorBLUE.format("Skipped"), end='')
			log.write("\nSkipped\n\n")
	 	elif result == 'passed':
	 		print (colorGREEN.format("Passed"), end='')
			log.write("\nPassed\n\n")



def mainCheck(): # Main function to run all health checks

	# TODO: clear screen, or use banner?
	# gw.clear()
	gw.gwappBanner(gwapp_variables.gwappversion)

	with open(healthCheckLog, 'w') as log:
		log.write("##########################################################\n#  General Health Check\n##########################################################\n")
		log.write("Gathered by gwapp v%s on %s\n\n" % (gwapp_variables.gwappversion, datetime.datetime.now().strftime('%c')))
	logger.info("Starting General Health Check..")

	# Get current system list
	gw.getSystemList(gwapp_variables.login)
	# List of checks to run..
	check_postSecurity()
	check_dvaConfigured()
	check_gwhaFile()

	print();print() # Adds spacing after all checks



def check_postSecurity():
	_util_NewHeader("Checking [all] Post Office Security..")
	problem = 'passed'
	security = gw.getPostSecurity()
	with open(healthCheckLog, 'a') as log:
		for key in security:
			if 'low' in (' '.join(security[key])).lower():
				problem = 'warning'
			log.write("%s.%s has %s security\n" % (key, gwapp_variables.postofficeSystem[key], ' '.join(security[key])))

	if problem == 'warning':
		msg = "\nPost Offices have been found with LOW security\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_agentCert(): # Check of Agent Certs
	pass

def check_agentSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking Agents for SSL set to Required..")
	problem = 'passed'
	SSLsecurity = gw.getSSLsettings()
	with open(healthCheckLog, 'a') as log:
		for key in SSLsecurity:
			if 'ENABLED' or 'DISABLED' in (' '.join(SSLsecurity[key])).lower():
				problem = 'warning'
			log.write("%s.%s has %s security\n" % (key, gwapp_variables.postofficeSystem[key], ' '.join(SSLsecurity[key])))

	if problem == 'warning':
		msg = "\nPost Offices have been found with LOW security\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)
	# https://151.155.214.174:9710/gwadmin-service/domains/pkldom/postoffices/pklpo/poas

def check_webaccHttpCert(): # Make sure the http cert for webaccess is used
	pass

def check_agentOwner(): # Run agents as user other than root
	pass

def check_gwiaAccessControl(): # GWIA Access Control (No relay)
	pass


### End Security section ###

def check_diskSpeed(): # Disk Speed on Post Office Servers
	pass

def check_diskSpace(): # Disk Space on Post Office Servers
	pass # TODO: Need to figure out how to read in where the data is located for pass/fail.

def check_poaErrorLog(): # Error Check on all POA logs
	for dom in gwapp_variables.domainSystem:
		for post in gwapp_variables.domainSystem[dom]:
			logpath = gw.getPOLogPath(dom, post)
			if logpath[post] != None:
				log = "%s/poa.currentlog" % logpath[post].rstrip('/')
			else:
				log = "/var/log/novell/groupwise/%s.poa/poa.currentlog" % (post)	

			logger.info("Checking log: %s" % log)
			with open(log, "r") as poa_currentLog:
				for line in poa_currentLog:
					if "error" in line.lower():
						print (line)

def check_webaccConnection(): #Webaccess suggested settings for connections
	pass

def check_webaccMemoryHeap(): # Webaccess suggested memory settings for Tomcat
	pass

def check_gwiaThreads(): # Thread Settings for GWIA send/receive
	pass

def check_poaThreads(): # POA Thread Settings C/S Message Handler
	pass

def check_imapSettings(): # IMAP Settings for max messages per folder / Read First
	pass

def check_Retention(): # Retention Plan and Software
	pass

def check_dvaConfigured():
	_util_NewHeader("Checking [all] Post Office DVA..")
	problem = 'passed'
	
	with open(healthCheckLog, 'a') as log:
		# Check post office for DVA
		for post in gwapp_variables.postofficeSystem:
			DVA = None
			url = "/gwadmin-service/domains/%s/postoffices/%s/poas" % (gwapp_variables.postofficeSystem[post], post)
			r = gw.restGetRequest(gwapp_variables.login, url)
			try:
				DVA = (r.json()['object'][0]['dvaName1'])
			except:
				pass

			if DVA is None:
				log.write("%s.%s has no DVA configured\n" % (post, gwapp_variables.postofficeSystem[post]))
				problem = 'failed'

	if problem == 'failed':
		_util_passFail(problem)
	else:
		msg = "Every Post Office has DVA configured\n"
		_util_passFail(problem, msg)

def check_gwhaFile(): # Look for any duplicates in the gwha.conf file
	_util_NewHeader("Checking [local] GWHA duplicates..")
	problem = 'passed'
	agent = []
	with open(gwapp_variables.gwhaFile, 'r') as gwha:
		for line in gwha:
			if ';' not in line:
				if ('startup=' in line) or ('[' in line and ']' in line):
					agent.append(line)

	if len(agent) != len(set(agent)):
		problem = 'failed'

	if problem == 'failed':
		msg = "\nDuplicate lines found in gwha.conf\n"
		_util_passFail(problem, msg)
	else:
		msg = "No duplicates found in gwha.conf\n"
		_util_passFail(problem, msg)
