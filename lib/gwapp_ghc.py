#!/usr/bin/env python
from __future__ import print_function
import sys
import traceback
import datetime
import json
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
COL1 = "{0:62}"

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
	check_poaAgentHttpSSL()
	check_poaAgentMtpSSL()
	check_poaAgentCSSSL()
	check_poaAgentImapSSL()
	check_poaAgentSoapSSL()
	check_poaAgentSSLCert()
	check_poaAgentSSLKey()

	print();print() # Adds spacing after all checks



def check_postSecurity():
	_util_NewHeader("Checking [System] POA Security..")
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

def check_poaAgentHttpSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] POA HTTP SSL Security settings..")
	problem = 'passed'
	poahttpssl = gw.getPoaSettings('httpUsesSsl', 'Post Offices have been found with HTTP SSL security DISABLED.')
	with open(healthCheckLog, 'a') as log:
		for key in poahttpssl:
			if 'DISABLED' == poahttpssl[key]:
				problem = 'warning'
			log.write("%s.%s has HTTP SSL set to: %s \n" % (key, gwapp_variables.postofficeSystem[key], poahttpssl[key]))

	if problem == 'warning':
		msg = "\nPost Offices have been found with HTTP SSL security Disabled\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)
	# https://151.155.214.174:9710/gwadmin-service/domains/pkldom/postoffices/pklpo/poas

def check_poaAgentMtpSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] POA MTP SSL Security settings..")
	problem = 'passed'
	poamtpssl = gw.getPoaSettings('mtpUsesSsl', 'Post Offices have been found with MTP SSL security DISABLED.')
	with open(healthCheckLog, 'a') as log:
		for key in poamtpssl:
			if 'DISABLED' == poamtpssl[key]:
				problem = 'warning'
			log.write("%s.%s has MTP SSL set to: %s \n" % (key, gwapp_variables.postofficeSystem[key], poamtpssl[key]))

	if problem == 'warning':
		msg = "\nPost Offices have been found with MTP SSL security Disabled\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_poaAgentCSSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] POA Client/Server SSL Security settings..")
	problem = 'passed'
	poacsssl = gw.getPoaSettings('clientServerUsesSsl', 'Post Offices have been found with Client/Server SSL security DISABLED.')
	with open(healthCheckLog, 'a') as log:
		for key in poacsssl:
			if 'DISABLED' == poacsssl[key]:
				problem = 'warning'
			log.write("%s.%s has Client/Server SSL set to: %s \n" % (key, gwapp_variables.postofficeSystem[key], poacsssl[key]))

	if problem == 'warning':
		msg = "\nPost Offices have been found with Client/Server SSL security Disabled\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_poaAgentImapSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] POA IMAP SSL Security settings..")
	problem = 'passed'
	poaimapssl = gw.getPoaSettings('imapUsesSsl', 'Post Offices have been found with IMAP SSL security DISABLED.')
	with open(healthCheckLog, 'a') as log:
		for key in poaimapssl:
			if 'DISABLED' == poaimapssl[key]:
				problem = 'warning'
			log.write("%s.%s has IMAP SSL set to: %s \n" % (key, gwapp_variables.postofficeSystem[key], poaimapssl[key]))

	if problem == 'warning':
		msg = "\nPost Offices have been found with IMAP SSL security Disabled\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_poaAgentSoapSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] POA SOAP SSL Security settings..")
	problem = 'passed'
	poasoapssl = gw.getPoaSettings('soapUsesSsl', 'Post Offices have been found with SOAP SSL security DISABLED.')
	with open(healthCheckLog, 'a') as log:
		for key in poasoapssl:
			if 'DISABLED' == poasoapssl[key]:
				problem = 'warning'
			log.write("%s.%s has SOAP SSL set to: %s \n" % (key, gwapp_variables.postofficeSystem[key], poasoapssl[key]))

	if problem == 'warning':
		msg = "\nPost Offices have been found with SOAP SSL security Disabled\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_poaAgentSSLCert(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] POA SSL Certificate file settings..")
	problem = 'passed'
	poasslcert = gw.getPoaSettings('sslCertificateFile', 'Post Offices have been found without a SSL Certificate.')
	with open(healthCheckLog, 'a') as log:
		for key in poasslcert:
			if None == poasslcert[key]:
				problem = 'warning'
			log.write("%s.%s has SSL Certificate set to: %s \n" % (key, gwapp_variables.postofficeSystem[key], poasslcert[key]))

	if problem == 'warning':
		msg = "\nPost Offices have been found without a SSL Certificate\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_poaAgentSSLKey(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] POA SSL Certificate key settings..")
	problem = 'passed'
	poasslkey = gw.getPoaSettings('sslKeyFile', 'Post Offices have been found without a SSL key.')
	with open(healthCheckLog, 'a') as log:
		for key in poasslkey:
			if None == poasslkey[key]:
				problem = 'warning'
			log.write("%s.%s has a SSL key set to: %s \n" % (key, gwapp_variables.postofficeSystem[key], poasslkey[key]))

	if problem == 'warning':
		msg = "\nPost Offices have been found without a SSL key\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_mtaAgentHttpSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] MTA SSL Security settings..")
	problem = 'passed'
	mtahttpssl = gw.getMtaHttpSSL()
	with open(healthCheckLog, 'a') as log:
		for key in mtahttpssl:
			if 'disabled' in (' '.join(mtahttpssl[key])).lower():
				problem = 'warning'
			log.write("%s has HTTP SSL %s \n" % (key, gwapp_variables.postofficeSystem[key], ' '.join(mtahttpssl[key])))

	if problem == 'warning':
		msg = "\nMTAs have been found with HTTP SSL security Disabled\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_mtaAgentMtpSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] MTA SSL Security settings..")
	problem = 'passed'
	mtamtpssl = gw.getMtaMtpSSL()
	with open(healthCheckLog, 'a') as log:
		for key in mtamtpssl:
			if 'disabled' in (' '.join(mtamtpssl[key])).lower():
				problem = 'warning'
			log.write("%s has MTP SSL %s \n" % (key, gwapp_variables.postofficeSystem[key], ' '.join(mtamtpssl[key])))

	if problem == 'warning':
		msg = "\nMTAs have been found with MTP SSL security Disabled\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_mtaAgentSSLCert(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] MTA SSL Certificate settings..")
	problem = 'passed'
	mtasslcert = gw.getMtaSSLCert()
	with open(healthCheckLog, 'a') as log:
		for key in mtasslcert:
			if 'Unable to find security setting' in (' '.join(mtasslcert[key])).lower():
				problem = 'warning'
			log.write("%s has MTP SSL Certificate: %s \n" % (key, gwapp_variables.postofficeSystem[key], ' '.join(mtasslcert[key])))

	if problem == 'warning':
		msg = "\nMTAs have been found without SSL certificates\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_mtaAgentSSLKey(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] MTA SSL Certificate settings..")
	problem = 'passed'
	mtasslkey = gw.getMtaSSLKey()
	with open(healthCheckLog, 'a') as log:
		for key in mtasslkey:
			if 'Unable to find security setting' in (' '.join(mtasslkey[key])).lower():
				problem = 'warning'
			log.write("%s has MTP a SSL key: %s \n" % (key, gwapp_variables.postofficeSystem[key], ' '.join(mtasslkey[key])))

	if problem == 'warning':
		msg = "\nMTAs have been found without an SSL key\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_mtaAgentSSLKeyPassword(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] MTA SSL Certificate settings..")
	problem = 'passed'
	mtasslkeypassword = gw.getMtaSSLKeyPassword()
	with open(healthCheckLog, 'a') as log:
		for key in mtasslkeypassword:
			if 'Unable to find security setting' in (' '.join(mtasslkeypassword[key])).lower():
				problem = 'warning'
			log.write("%s has MTP a SSL key password set: %s \n" % (key, gwapp_variables.postofficeSystem[key], ' '.join(mtasslkeypassword[key])))

	if problem == 'warning':
		msg = "\nMTAs have been found without a SSL key password set\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_gwiaAgentHttpSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] GWIA SSL Security settings..")
	problem = 'passed'
	gwiahttpssl = gw.getGwiaHttpSSL()
	with open(healthCheckLog, 'a') as log:
		for key in gwiahttpssl:
			if 'disabled' in (' '.join(gwiahttpssl[key])).lower():
				problem = 'warning'
			log.write("%s has HTTP SSL %s \n" % (key, gwapp_variables.postofficeSystem[key], ' '.join(gwiahttpssl[key])))

	if problem == 'warning':
		msg = "\nMTAs have been found with HTTP SSL security Disabled\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_gwiaAgentMtpSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] GWIA SSL Security settings..")
	problem = 'passed'
	gwiamtpssl = gw.getGwiaMtpSSL()
	with open(healthCheckLog, 'a') as log:
		for key in gwiamtpssl:
			if 'disabled' in (' '.join(gwiamtpssl[key])).lower():
				problem = 'warning'
			log.write("%s has MTP SSL %s \n" % (key, gwapp_variables.postofficeSystem[key], ' '.join(gwiamtpssl[key])))

	if problem == 'warning':
		msg = "\nMTAs have been found with MTP SSL security Disabled\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_gwiaAgentImapSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] GWIA SSL Security settings..")
	problem = 'passed'
	gwiaimapssl = gw.getGwiaImapSSL()
	with open(healthCheckLog, 'a') as log:
		for key in gwiaimapssl:
			if 'disabled' in (' '.join(gwiaimapssl[key])).lower():
				problem = 'warning'
			log.write("%s has IMAP SSL %s \n" % (key, gwapp_variables.postofficeSystem[key], ' '.join(gwiaimapssl[key])))

	if problem == 'warning':
		msg = "\nMTAs have been found with IMAP SSL security Disabled\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_gwiaAgentLdapSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] GWIA SSL Security settings..")
	problem = 'passed'
	gwialdapssl = gw.getGwiaLdapSSL()
	with open(healthCheckLog, 'a') as log:
		for key in gwialdapssl:
			if 'disabled' in (' '.join(gwialdapssl[key])).lower():
				problem = 'warning'
			log.write("%s has LDAP SSL %s \n" % (key, gwapp_variables.postofficeSystem[key], ' '.join(gwialdapssl[key])))

	if problem == 'warning':
		msg = "\nMTAs have been found with LDAP SSL security Disabled\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_gwiaAgentPopSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] GWIA SSL Security settings..")
	problem = 'passed'
	gwiapopssl = gw.getGwiaPopSSL()
	with open(healthCheckLog, 'a') as log:
		for key in gwiapopssl:
			if 'disabled' in (' '.join(gwiapopssl[key])).lower():
				problem = 'warning'
			log.write("%s has POP3 SSL %s \n" % (key, gwapp_variables.postofficeSystem[key], ' '.join(gwiapopssl[key])))

	if problem == 'warning':
		msg = "\nMTAs have been found with POP3 SSL security Disabled\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_gwiaAgentSmtpSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] GWIA SSL Security settings..")
	problem = 'passed'
	gwiasmtpssl = gw.getGwiaSmtpSSL()
	with open(healthCheckLog, 'a') as log:
		for key in gwiasmtpssl:
			if 'disabled' in (' '.join(gwiasmtpssl[key])).lower():
				problem = 'warning'
			log.write("%s has SMTP SSL %s \n" % (key, gwapp_variables.postofficeSystem[key], ' '.join(gwiasmtpssl[key])))

	if problem == 'warning':
		msg = "\nMTAs have been found with SMTP SSL security Disabled\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_gwiaAgentSSLCert(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] GWIA SSL Certificate settings..")
	problem = 'passed'
	gwiasslcert = gw.getGwiaSSLCert()
	with open(healthCheckLog, 'a') as log:
		for key in gwiasslcert:
			if 'Unable to find security setting' in (' '.join(gwiasslcert[key])).lower():
				problem = 'warning'
			log.write("%s.%s has SSL Certificate set to: %s \n" % (key, gwapp_variables.postofficeSystem[key], ' '.join(gwiasslcert[key])))

	if problem == 'warning':
		msg = "\nGWIAs have been found without a SSL Certificate\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_gwiaAgentSSLKey(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] GWIA SSL Certificate settings..")
	problem = 'passed'
	gwiasslkey = gw.getGwiaSSLKey()
	with open(healthCheckLog, 'a') as log:
		for key in gwiasslkey:
			if 'Unable to find security setting' in (' '.join(gwiasslkey[key])).lower():
				problem = 'warning'
			log.write("%s.%s has SSL key set to: %s \n" % (key, gwapp_variables.postofficeSystem[key], ' '.join(gwiasslkey[key])))

	if problem == 'warning':
		msg = "\nGWIAs have been found without a SSL key\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_gwiaAgentSSLKeyPassword(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] GWIA SSL Certificate settings..")
	problem = 'passed'
	gwiasslkeypassword = gw.getGwiaSSLKeyPassword()
	with open(healthCheckLog, 'a') as log:
		for key in gwiasslkeypassword:
			if 'Unable to find security setting' in (' '.join(gwiasslkeypassword[key])).lower():
				problem = 'warning'
			log.write("%s.%s has MTP a SSL key password set: %s \n" % (key, gwapp_variables.postofficeSystem[key], ' '.join(gwiasslkeypassword[key])))

	if problem == 'warning':
		msg = "\nGWIAs have been found without a SSL key password set\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_webaccHttpCert(): # Make sure the http cert for webaccess is used
	pass

def check_agentOwner(): # Run agents as user other than root
	pass

def check_gwiaAccessControl(): # GWIA Access Control (No relay)
	_util_NewHeader("Checking [System] GWIA relay settings..")
	problem = 'passed'
	gwiarelay = gw.getGwiaRelay()
	with open(healthCheckLog, 'a') as log:
		for key in gwiarelay:
			if 'allow' in (' '.join(gwiarelay[key])).lower():
				problem = 'warning'
			log.write("%s.%s has SMTP relaying set to: %s \n" % (key, gwapp_variables.postofficeSystem[key], ' '.join(gwiarelay[key])))

	if problem == 'warning':
		msg = "\nGWIAs have been found to have SMTP relaying allowed.\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)


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
	_util_NewHeader("Checking [System] Post Office DVA..")
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
	_util_NewHeader("Checking [Server] GWHA duplicates..")
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
