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
COL1 = "{0:70}"

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
	gw.gwappBanner(gwapp_variables.gwappversion)
	# Get current system list
	gw.getSystemList(gwapp_variables.login)

	with open(healthCheckLog, 'w') as log:
		log.write("##########################################################\n#  General Health Check\n##########################################################\n")
		log.write("Gathered by gwapp v%s on %s\n\n" % (gwapp_variables.gwappversion, datetime.datetime.now().strftime('%c')))
	logger.info("Starting General Health Check..")

	# List of checks to run..
	# Server checks
	check_postSecurity()
	check_poaAgentHttpSSL()
	check_poaAgentMtpSSL()
	check_poaAgentCSSSL()
	check_poaAgentImapSSL()
	check_poaAgentSoapSSL()
	check_poaAgentSSLCert()
	check_poaAgentSSLKey()
	check_mtaAgentHttpSSL()
	check_mtaAgentMtpSSL()
	check_mtaAgentSSLCert()
	check_mtaAgentSSLKey()
	check_mtaAgentSSLKeyPassword()
	check_gwiaAgentHttpSSL()
	check_gwiaAgentMtpSSL()
	check_gwiaAgentImapSSL()
	check_gwiaAgentLdapSSL()
	check_gwiaAgentPopSSL()
	check_gwiaAgentSmtpSSL()
	check_gwiaAgentSSLCert()
	check_gwiaAgentSSLKey()
	check_gwiaAgentSSLKeyPassword()
	check_gwiaAccessControl()
	check_gwiaSendThreads()
	check_gwiaReceiveThreads()
	check_poaThreads()
	check_gwiaimapSettings()
	check_dvaConfigured()

	# Server checks
	check_gwhaFile()

	gwapp_variables.restDATA.clear()
	print();print() # Adds spacing after all checks


def check_postSecurity():
	_util_NewHeader("Checking [System] Post Office Security..")
	problem = 'passed'
	# security = gw.getPostSecurity(healthCheck=True)
	security = gw.getPostSetting('securitySettings', 'Post Offices have been found with low security', debug=True, healthCheck=True)
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
	poahttpssl = gw.getPoaSettings('httpUsesSsl', 'Post Offices have been found with HTTP SSL security DISABLED')
	with open(healthCheckLog, 'a') as log:
		for key in poahttpssl:
			if 'DISABLED' == poahttpssl[key]:
				problem = 'warning'
			log.write("%s has HTTP SSL set to: %s \n" % (key, poahttpssl[key]))

	if problem == 'warning':
		msg = "\nPost Offices have been found with HTTP SSL security Disabled\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)
	# https://151.155.214.174:9710/gwadmin-service/domains/pkldom/postoffices/pklpo/poas

def check_poaAgentMtpSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] POA MTP SSL Security settings..")
	problem = 'passed'
	poamtpssl = gw.getPoaSettings('mtpUsesSsl', 'Post Offices have been found with MTP SSL security DISABLED', healthCheck=True)
	with open(healthCheckLog, 'a') as log:
		for key in poamtpssl:
			if 'DISABLED' == poamtpssl[key]:
				problem = 'warning'
			log.write("%s has MTP SSL set to: %s \n" % (key, poamtpssl[key]))

	if problem == 'warning':
		msg = "\nPost Offices have been found with MTP SSL security Disabled\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_poaAgentCSSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] POA Client/Server SSL Security settings..")
	problem = 'passed'
	poacsssl = gw.getPoaSettings('clientServerUsesSsl', 'Post Offices have been found with Client/Server SSL security DISABLED', healthCheck=True)
	with open(healthCheckLog, 'a') as log:
		for key in poacsssl:
			if 'DISABLED' == poacsssl[key]:
				problem = 'warning'
			log.write("%s has Client/Server SSL set to: %s \n" % (key, poacsssl[key]))

	if problem == 'warning':
		msg = "\nPost Offices have been found with Client/Server SSL security Disabled\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_poaAgentImapSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] POA IMAP SSL Security settings..")
	problem = 'passed'
	poaimapssl = gw.getPoaSettings('imapUsesSsl', 'Post Offices have been found with IMAP SSL security DISABLED', healthCheck=True)
	with open(healthCheckLog, 'a') as log:
		for key in poaimapssl:
			if 'DISABLED' == poaimapssl[key]:
				problem = 'warning'
			log.write("%s has IMAP SSL set to: %s \n" % (key, poaimapssl[key]))

	if problem == 'warning':
		msg = "\nPost Offices have been found with IMAP SSL security Disabled\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_poaAgentSoapSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] POA SOAP SSL Security settings..")
	problem = 'passed'
	poasoapssl = gw.getPoaSettings('soapUsesSsl', 'Post Offices have been found with SOAP SSL security DISABLED', healthCheck=True)
	with open(healthCheckLog, 'a') as log:
		for key in poasoapssl:
			if 'DISABLED' == poasoapssl[key]:
				problem = 'warning'
			log.write("%s has SOAP SSL set to: %s \n" % (key, poasoapssl[key]))

	if problem == 'warning':
		msg = "\nPost Offices have been found with SOAP SSL security Disabled\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_poaAgentSSLCert(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] POA SSL Certificate file settings..")
	problem = 'passed'
	poasslcert = gw.getPoaSettings('sslCertificateFile', 'Post Offices have been found without a SSL Certificate', healthCheck=True)
	with open(healthCheckLog, 'a') as log:
		for key in poasslcert:
			if None == poasslcert[key]:
				problem = 'warning'
			log.write("%s has SSL Certificate set to: %s \n" % (key, poasslcert[key]))

	if problem == 'warning':
		msg = "\nPost Offices have been found without a SSL Certificate\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_poaAgentSSLKey(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] POA SSL Certificate key settings..")
	problem = 'passed'
	poasslkey = gw.getPoaSettings('sslKeyFile', 'Post Offices have been found without a SSL key', healthCheck=True)
	with open(healthCheckLog, 'a') as log:
		for key in poasslkey:
			if None == poasslkey[key]:
				problem = 'warning'
			log.write("%s has a SSL key set to: %s \n" % (key, poasslkey[key]))

	if problem == 'warning':
		msg = "\nPost Offices have been found without a SSL key\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_mtaAgentHttpSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] MTA HTTP SSL Security settings..")
	problem = 'passed'
	mtahttpssl = gw.getMtaSettings('httpUsesSsl', 'Message Transfer Agents have been found with HTTP SSL security DISABLED')
	with open(healthCheckLog, 'a') as log:
		for key in mtahttpssl:
			if 'DISABLED' == mtahttpssl[key]:
				problem = 'warning'
			log.write("%s has HTTP SSL set to: %s \n" % (key, mtahttpssl[key]))

	if problem == 'warning':
		msg = "\nMessage Transfer Agents have been found with HTTP SSL security DISABLED\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_mtaAgentMtpSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] MTA SSL Security settings..")
	problem = 'passed'
	mtamtpssl = gw.getMtaSettings('mtpUsesSsl', 'Message Transfer Agents have been found with MTP SSL security DISABLED')
	with open(healthCheckLog, 'a') as log:
		for key in mtamtpssl:
			if 'DISABLED' == mtamtpssl[key]:
				problem = 'warning'
			log.write("%s has MTP SSL set to: %s \n" % (key, mtamtpssl[key]))

	if problem == 'warning':
		msg = "\nMessage Transfer Agents have been found with MTP SSL security DISABLED\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_mtaAgentSSLCert(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] MTA SSL Certificate file settings..")
	problem = 'passed'
	mtasslcert = gw.getMtaSettings('sslCertificateFile', 'Message Transfer Agents have been found without a SSL Certificate', healthCheck=True)
	with open(healthCheckLog, 'a') as log:
		for key in mtasslcert:
			if None == mtasslcert[key]:
				problem = 'warning'
			log.write("%s has SSL Certificate set to: %s \n" % (key, mtasslcert[key]))

	if problem == 'warning':
		msg = "\nMessage Transfer Agents have been found without a SSL Certificate\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_mtaAgentSSLKey(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] MTA SSL Certificate key password settings..")
	problem = 'passed'
	mtasslkey = gw.getMtaSettings('sslKeyFile','Message Transfer Agents have been found without a SSL Key')
	with open(healthCheckLog, 'a') as log:
		for key in mtasslkey:
			if None == mtasslkey[key]:
				problem = 'warning'
			log.write("%s has SSL Certificate set to: %s \n" % (key, mtasslkey[key]))

	if problem == 'warning':
		msg = "\nMessage Transfer Agents have been found without a SSL Key\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_mtaAgentSSLKeyPassword(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] MTA SSL Certificate key settings..")
	problem = 'passed'
	mtasslkeypassword = gw.getMtaSettings('hasSslKeyPassword','Message Transfer Agents have been found without a SSL Key Password')
	with open(healthCheckLog, 'a') as log:
		for key in mtasslkeypassword:
			if not mtasslkeypassword[key]:
				problem = 'warning'
			log.write("%s has SSL Certificate Key Password set to: %s \n" % (key, mtasslkeypassword[key]))

	if problem == 'warning':
		msg = "\nMessage Transfer Agents have been found without a SSL Key Password\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_gwiaAgentHttpSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] GWIA HTTP SSL Security settings..")
	problem = 'passed'
	gwiahttpssl = gw.getGwiaSettings('httpUsesSsl','GWIAs have been found with HTTP SSL security DISABLED')
	with open(healthCheckLog, 'a') as log:
		for key in gwiahttpssl:
			if 'DISABLED' == gwiahttpssl[key]:
				problem = 'warning'
			log.write("%s has HTTP SSL set to: %s \n" % (key, gwiahttpssl[key]))

	if problem == 'warning':
		msg = "\nGWIAs have been found with HTTP SSL security DISABLED\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_gwiaAgentMtpSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] GWIA MTP SSL Security settings..")
	problem = 'passed'
	gwiamtpssl = gw.getGwiaSettings('mtpUsesSsl','MTAs have been found with MTP SSL security Disabled')
	with open(healthCheckLog, 'a') as log:
		for key in gwiamtpssl:
			if 'DISABLED' == gwiamtpssl[key]:
				problem = 'warning'
			log.write("%s has MTP SSL set to: %s \n" % (key, gwiamtpssl[key]))

	if problem == 'warning':
		msg = "\nMTAs have been found with MTP SSL security Disabled\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_gwiaAgentImapSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] GWIA IMAP SSL Security settings..")
	problem = 'passed'
	gwiaimapssl = gw.getGwiaSettings('imapUsesSsl','MTAs have been found with IMAP SSL security Disabled')
	with open(healthCheckLog, 'a') as log:
		for key in gwiaimapssl:
			if 'DISABLED' == gwiaimapssl[key]:
				problem = 'warning'
			log.write("%s has IMAP SSL set to: %s \n" % (key, gwiaimapssl[key]))

	if problem == 'warning':
		msg = "\nMTAs have been found with IMAP SSL security Disabled\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_gwiaAgentLdapSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] GWIA LDAP SSL Security settings..")
	problem = 'passed'
	gwialdapssl = gw.getGwiaSettings('ldapUsesSsl','MTAs have been found with LDAP SSL security Disabled')
	with open(healthCheckLog, 'a') as log:
		for key in gwialdapssl:
			if 'DISABLED' == gwialdapssl[key]:
				problem = 'warning'
			log.write("%s has LDAP SSL set to: %s \n" % (key, gwialdapssl[key]))

	if problem == 'warning':
		msg = "\nMTAs have been found with LDAP SSL security Disabled\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_gwiaAgentPopSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] GWIA POP3 SSL Security settings..")
	problem = 'passed'
	gwiapopssl = gw.getGwiaSettings('popUsesSsl','MTAs have been found with POP3 SSL security Disabled')
	with open(healthCheckLog, 'a') as log:
		for key in gwiapopssl:
			if 'DISABLED' == gwiapopssl[key]:
				problem = 'warning'
			log.write("%s has POP3 SSL set to: %s \n" % (key, gwiapopssl[key]))

	if problem == 'warning':
		msg = "\nMTAs have been found with POP3 SSL security Disabled\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_gwiaAgentSmtpSSL(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] GWIA SSL Security settings..")
	problem = 'passed'
	gwiasmtpssl = gw.getGwiaSettings('smtpUsesSsl','MTAs have been found with smtp SSL security Disabled')
	with open(healthCheckLog, 'a') as log:
		for key in gwiasmtpssl:
			if 'DISABLED' == gwiasmtpssl[key]:
				problem = 'warning'
			log.write("%s has POP3 SSL set to: %s \n" % (key, gwiasmtpssl[key]))

	if problem == 'warning':
		msg = "\nMTAs have been found with SMTP SSL security Disabled\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_gwiaAgentSSLCert(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] GWIA SSL Certificate file settings..")
	problem = 'passed'
	gwiasslcert = gw.getGwiaSettings('sslCertificateFile', 'GWIAs have been found without a SSL Certificate', healthCheck=True)
	with open(healthCheckLog, 'a') as log:
		for key in gwiasslcert:
			if None == gwiasslcert[key]:
				problem = 'warning'
			log.write("%s has SSL Certificate set to: %s \n" % (key, gwiasslcert[key]))

	if problem == 'warning':
		msg = "\nGWIAs have been found without a SSL Certificate\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_gwiaAgentSSLKey(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] GWIA SSL Certificate Key file settings..")
	problem = 'passed'
	gwiasslkey = gw.getGwiaSettings('sslKeyFile', 'GWIAs have been found without a SSL Certificate Key', healthCheck=True)
	with open(healthCheckLog, 'a') as log:
		for key in gwiasslkey:
			if None == gwiasslkey[key]:
				problem = 'warning'
			log.write("%s has a SSL certificate key file set to: %s \n" % (key, gwiasslkey[key]))

	if problem == 'warning':
		msg = "\nGWIAs have been found without a SSL key\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_gwiaAgentSSLKeyPassword(): # Set all Agents to Require SSL
	_util_NewHeader("Checking [System] GWIA SSL Certificate Key password settings..")
	problem = 'passed'
	gwiasslkeypassword = gw.getGwiaSettings('hasSslKeyPassword','GWIAs have been found without a SSL Certificate Key', healthCheck=True)
	with open(healthCheckLog, 'a') as log:
		for key in gwiasslkeypassword:
			if None == gwiasslkeypassword[key]:
				problem = 'warning'
			log.write("%s has a SSL certificate key password set to: %s \n" % (key, gwiasslkeypassword[key]))

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
	gwiarelay = gw.getGwiaSettings('smtpMessageRelayAllow','GWIAs have been found to have SMTP relaying set to ALLOWED')
	with open(healthCheckLog, 'a') as log:
		for key in gwiarelay:
			if 'ALLOW' == gwiarelay[key]:
				problem = 'warning'
			log.write("%s has relaying set to: %s \n" % (key, gwiarelay[key]))

	if problem == 'warning':
		msg = "\nGWIAs have been found to have SMTP relaying set to ALLOWED\n"
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
			logpath = gw.getPOLogPath(dom, post, healthCheck=True) # TODO: Switch this over to use gw.getPoaSettings()
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

def check_gwiaSendThreads(): # Thread Settings for GWIA send/receive
	_util_NewHeader("Checking [System] GWIA SMTP send threads..")
	problem = 'passed'
	gwiaoutboundthreads = gw.getGwiaSettings('smtpSendThreads','GWIA SMTP send threads are outside of the normal threshold', healthCheck=True)
	with open(healthCheckLog, 'a') as log:
		for key in gwiaoutboundthreads:
			if not 5 <= gwiaoutboundthreads[key] <= 25:
				problem = 'warning'
			log.write("%s SMTP send threads set to: %s \n" % (key, gwiaoutboundthreads[key]))

	if problem == 'warning':
		msg = "\nGWIA SMTP send threads are outside of the normal threshold\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_gwiaReceiveThreads(): # Thread Settings for GWIA send/receive
	_util_NewHeader("Checking [System] GWIA SMTP receive threads..")
	problem = 'passed'
	gwiainboundthreads = gw.getGwiaSettings('smtpReceiveThreads','GWIA SMTP receive threads are outside of the normal threshold', healthCheck=True)
	with open(healthCheckLog, 'a') as log:
		for key in gwiainboundthreads:
			if not 5 <= gwiainboundthreads[key] <= 25:
				problem = 'warning'
			log.write("%s SMTP receive threads set to: %s \n" % (key, gwiainboundthreads[key]))

	if problem == 'warning':
		msg = "\nGWIA SMTP receive threads are outside of the normal threshold\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_poaThreads(): # POA Thread Settings C/S Message Handler
	_util_NewHeader("Checking [System] POA Client/Server threads..")
	problem = 'passed'
	poaclientserverthreads = gw.getPoaSettings('clientServerThreads','POA Client/Server threads are outside of the normal threshold', healthCheck=True)
	with open(healthCheckLog, 'a') as log:
		for key in poaclientserverthreads:
			if not 6 <= poaclientserverthreads[key] <= 20:
				problem = 'warning'
			log.write("%s Client/Server threads set to: %s \n" % (key, poaclientserverthreads[key]))

	if problem == 'warning':
		msg = "\nPOA Client/Server threads are outside of the normal threshold\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_gwiaimapSettings(): # GWIA IMAP Settings for max messages per folder / Read First
	_util_NewHeader("Checking [System] GWIA IMAP read limit..")
	problem = 'passed'
	gwiaimapreadlimit = gw.getGwiaSettings('imapReadLimit','IMAP read limit set to more than 10,000 items', healthCheck=True)
	with open(healthCheckLog, 'a') as log:
		for key in gwiaimapreadlimit:
			if gwiaimapreadlimit[key] >= 10:
				problem = 'warning'
			log.write("%s IMAP read limit set to: %s \n" % (key, gwiaimapreadlimit[key]))

	if problem == 'warning':
		msg = "\nIMAP read limit set to more than 10,000 items\n"
		_util_passFail(problem, msg)
	else:
		_util_passFail(problem)

def check_Retention(): # Retention Plan and Software
	pass

def check_dvaConfigured():
	_util_NewHeader("Checking [System] POA configured for DVAs..")
	problem = 'passed'
	results = gw.getPoaSettings('dvaName1', 'POA has not been DVA configured', debug=True, healthCheck=True)
	with open(healthCheckLog, 'a') as log:
		for key in results:
			if None == results[key]:
				problem = 'failed'
				log.write("%s has no DVA configured\n" % key)

	if problem == 'failed':
		_util_passFail(problem)
	else:
		msg = "Every Post Office has DVA configured\n"
		_util_passFail(problem, msg)


	# _util_NewHeader("Checking [System] Post Office DVA..")
	# problem = 'passed'
	
	# with open(healthCheckLog, 'a') as log:
	# 	# Check post office for DVA
	# 	for post in gwapp_variables.postofficeSystem:
	# 		DVA = None
	# 		url = "/gwadmin-service/domains/%s/postoffices/%s/poas" % (gwapp_variables.postofficeSystem[post], post)
	# 		r = gw.restGetRequest(gwapp_variables.login, url)
	# 		try:
	# 			DVA = (r.json()['object'][0]['dvaName1'])
	# 		except:
	# 			pass

	# 		if DVA is None:
	# 			log.write("%s.%s has no DVA configured\n" % (post, gwapp_variables.postofficeSystem[post]))
	# 			problem = 'failed'

	# if problem == 'failed':
	# 	_util_passFail(problem)
	# else:
	# 	msg = "Every Post Office has DVA configured\n"
	# 	_util_passFail(problem, msg)

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
