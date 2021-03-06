#!/usr/bin/env python
# Written by Shane Nielson <snielson@projectuminfinitas.com>
from __future__ import print_function

__author__ = "Shane Nielson"
__maintainer__ = "Shane Nielson"
__email__ = "snielson@projectuminfinitas.com"

import os
import sys
import glob
import select
import subprocess
import getpass
import json
import stat
import traceback
import gwapp_json
import getch
getch = getch._Getch()
import shutil
import logging, logging.config
import ConfigParser
Config = ConfigParser.ConfigParser()

# Import requests as an alternative to urllib
import requests
# Hide requests warning (outdated python with GMS)
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

# GLOBAL VARIABLES
import gwapp_variables
# gwapp_variables.setGlobalVariables()

if sys.stdout.isatty():
	WINDOW_SIZE = rows, columns = os.popen('stty size', 'r').read().split()
else:
	# Default terminal size
	WINDOW_SIZE = [24,80]

# Log Settings
logging.config.fileConfig('%s/logging.cfg' % (gwapp_variables.gwappConf))
logger = logging.getLogger(__name__)
excep_logger = logging.getLogger('exceptions_log')

def my_handler(type, value, tb):
	tmp = traceback.format_exception(type, value, tb)
	logger.error("EXCEPTION: See exception.log")
	excep_logger.error("Uncaught exception:\n%s" % ''.join(tmp).strip())
	print (''.join(tmp).strip())

# Install exception handler
sys.excepthook = my_handler

def clear():
	tmp = subprocess.call('clear',shell=True)

def gwappBanner():
	banner = """
     __ ___      ____ _ _ __  _ __  
    / _` \\ \\ /\\ / / _` | '_ \\| '_ \\ 
   | (_| |\\ V  V / (_| | |_) | |_) |
    \__, | \\_/\\_/ \__,_| .__/| .__/ 
    |___/              |_|   |_|   
	"""
	clear()
	print (banner + "\t\t         v" + gwapp_variables.gwappversion + "\n")

def print_disclaimer(gwappversion):
	gwappBanner()
	prompt = 'Use at your own discretion. gwapp is not supported by Novell.\nSee [gwapp --bug] to report issues.'
	print (prompt)
	r,w,x = select.select([sys.stdin], [], [], 10)
	sys.stdout.flush()

def eContinue():
	if sys.stdout.isatty():
		print("Press Enter to continue ", end='')
		while True:
			enter = getch()
			if ord(enter) == 13:
				break
		print()

def askYesOrNo(question, default=None):

    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    elif default == 'skip':
    	return True
    else:
        raise ValueError("Invalid default answer: '%s'" % default)

    try:
        while True:
            choice = raw_input(question + prompt).lower()
            if default is not None and choice == '':
            	logger.debug('%s: %s' % (question, valid[default]))
            	return valid[default]
            elif choice in valid:
            	logger.debug('%s: %s' % (question, valid[choice]))
            	return valid[choice]
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' "
                                 "(or 'y' or 'n').\n")
    except KeyboardInterrupt:
    	logger.warning("KeyboardInterrupt detected")

def readlines_reverse(filename):
# Credit to Berislav Lopac on Stackoverflow
	with open(filename) as qfile:
		qfile.seek(0, os.SEEK_END)
		position = qfile.tell()
		line = ''
		while position >= 0:
			qfile.seek(position)
			next_char = qfile.read(1)
			if next_char == "\n":
				yield line[::-1]
				line = ''
			else:
				line += next_char
			position -= 1
		yield line[::-1]

def removeAllFiles(path):
	filelist = glob.glob(path +"/*")
	for f in filelist:
		try:
			os.remove(f)
		except OSError:
			if not os.path.isdir(f):
				logger.warning('No such file: %s' % (f))
		logger.debug('Removed: %s' % f)

def removeAllFolders(path):
	folderlist = glob.glob(path + "/*")
	for f in folderlist:
		try:
			shutil.rmtree(f)
		except OSError:
			if not os.path.isfile(f):
				logger.warning('No such directory: %s' % f)
		logger.debug('Removed: %s' % f)

def print_there(x, y, text):
     sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x, y, text))
     sys.stdout.flush()

def getUserID(prompt = "User ID: "):
	userID = raw_input(prompt)
	if not userID:
		while not userID:
			if askYesOrNo("Invalid input, try again"):
				userID = raw_input(prompt)
			else:
				break
				userID = None
	logger.info("User ID = %s" % userID)
	return userID

def util_subprocess(cmd, error=False):
	if not error:
		p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
		p.wait()
		out = p.communicate()
	elif error:
		p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		p.wait()
		out = p.communicate()
	return out

def getServerInfo():
	server = None
	port = None
	url = None

	print ("GroupWise Administration Information")
	logger.info("GroupWise Administration Information")

	server = raw_input("Server IP/DNS: ")
	port = raw_input("Port: ")
	logger.debug("[Server: %s][Port: %s]" % (server,port))
	if not server or not port:
		print ("Invalid server or port input")
		logger.info("Invalid server or port input")
	else:
		url = "https://%s:%s" % (server,port)

	logger.info("URL = https://%s:%s" % (server,port))
	return url

def getPassWD(debug=False):
	if not debug:
		p1 = None
		p2 = None
		p1 = getpass.getpass("Enter password: ")
		p2 = getpass.getpass("Re-Enter password: ")
		if p1 == p2:
			logger.info("Passwords match")
			return p1
		else:
			print ("Passwords do not match")
			logger.error("Passwords do not match")
			return None
	else:
		return 'novell'

def getGWLogin(debug=False):
	loginInfo = dict()
	loginInfo['url'] = getServerInfo()
	loginInfo['admin'] = getUserID("Admin user: ")
	if not debug:
		loginInfo['pass'] = getPassWD()
	else:
		loginInfo['pass'] = 'novell'
	return loginInfo

def checkDictKeys(list):
	result = True
	for key in list:
		# Check value in key
		if list[key] is None:
			result = False
	return result

def saveServerSettings(reconfig=False, debug=False):
	gwappBanner()
	Config.read(gwapp_variables.gwappSettings)
	if Config.get('Login', 'url') == 'None' or Config.get('Login','admin') == 'None' or reconfig:
		login = getGWLogin(debug)
		if checkDictKeys(login):
			if askYesOrNo("\nStore login information"):
				with open(gwapp_variables.gwappSettings, 'wb') as cfgfile:
					Config.set('Login', 'url', login['url'])
					Config.set('Login', 'admin', login['admin'])
					logger.debug("Writing: [Login] url = %s" % login['url'])
					logger.debug("Writing: [Login] admin = %s" % login['admin'])
					Config.write(cfgfile)
		else:
			print ("Missing login information")
			logger.error("Missing login information")
			sys.exit(1)
	else:
		logger.info("Found url login information")
		print ("GroupWise Administration password")
		passwd = getPassWD(debug)
		if passwd is None:
			sys.exit(1)
		login = {'url':Config.get('Login', 'url'), 'admin':Config.get('Login', 'admin'), 'pass': passwd}
		logger.debug("Login settings: {'url': %s, 'admin': %s}" % (login['url'],login['admin']))
	return login

def checkLoginInfo(login):
	r = None
	try:
		r = requests.get(login['url'] + '/gwadmin-service/list/domain', auth=(login['admin'],login['pass']), verify=False)
	except:
		pass
	if r is None:
		print ("Connection refused")
		logger.error("Connection refused")
		return False

	logger.info("Status code: %s" % r.status_code)
	if r.status_code != 200:
		print ("Unable to authenticate with login information")
		logger.error("Unable to authenticate with login information")
		return False
	return True

def restGetRequest(login, urlPath, healthCheck=False):
	r = None
	if healthCheck:
		if urlPath not in gwapp_variables.restDATA:
			r = requests.get(login['url'] + urlPath, auth=(login['admin'],login['pass']), verify=False, headers={"Accept":"application/json"})
			logger.debug("GET request URL: %s" % login['url'] + urlPath)
			logger.info("Status code: %s" % r.status_code)
			logger.debug("Adding new key [%s]" % urlPath)
			gwapp_variables.restDATA[urlPath] = r
		else:
			logger.debug("Key [%s] found, returning JSON" % urlPath)
		return gwapp_variables.restDATA[urlPath]
	else:
		try:
			r = requests.get(login['url'] + urlPath, auth=(login['admin'],login['pass']), verify=False, headers={"Accept":"application/json"})
			logger.debug("GET request URL: %s" % login['url'] + urlPath)
			logger.info("Status code: %s" % r.status_code)
		except:
			pass
		return r

def restPostRequest(login, urlPath, data, header):
	r = None
	try:
		r = requests.post(login['url'] + urlPath, auth=(login['admin'], login['pass']), verify=False, data=json.dumps(data), headers=header)
		logger.debug("POST request URL: %s" % login['url'] + urlPath)
		logger.info("Status code: %s" % r.status_code)
	except:
		pass

	if r.status_code == 200 or r.status_code == 201:
		logger.info("Successfully posted data")
		logger.debug("data = %s" % data)
	return r

def restDeleteRequest(login, urlPath):
	r = None
	try:
		r = requests.delete(login['url'] + urlPath, auth=(login['admin'],login['pass']), verify=False)
		logger.debug("DELETE request URL: %s" % login['url'] + urlPath)
		logger.info("Status code: %s" % r.status_code)
	except:
		pass

	if r.status_code == 200:
		logger.info("Successfully deleted %s" % login['url'] + urlPath)
	return r

def getDomains(login):
	# Gets domains in JSON. Loop through data, and pull names into list
	domains = []
	r = restGetRequest(login, '/gwadmin-service/domains')
	logger.info("Building list of domains..")
	for objects in r.json()['object']:
		domains.append(objects['name'])
		logger.debug("Appending domain to list: %s" % objects['name'])
	return domains

def getPostOffices(login, domain):
	# Gets postoffices in JSON. Loop through data, and pull names into list
	postoffices = []
	url = "/gwadmin-service/domains/%s/postoffices" % domain
	logger.info("Building list of post offices..")
	r = restGetRequest(login, url)
	try:
		for objects in r.json()['object']:
			postoffices.append(objects['name'])
			logger.debug("Appending post office to list: %s" % objects['name'])
	except KeyError: # KeyError if domain has no post office
		pass
	return postoffices

def getGWIAs(login, domain):
	# Gets gwia in JSON. Loop through data, and pull names into list
	gwias = []
	url = "/gwadmin-service/domains/%s/gwias" % domain
	logger.info("Building list of gwias..")
	r = restGetRequest(login, url)
	try:
		for objects in r.json()['object']:
			gwias.append(objects['name'])
			logger.debug("Appending gwia to list: %s" % objects['name'])
	except KeyError: # KeyError if domain has no gwia
		pass
	return gwias

def getPOAs(login, domain, postoffice):
	# Gets POAs in JSON. Loop through data, and pull names into list
	poas = []
	url = "/gwadmin-service/domains/%s/postoffices/%s/poas" % (domain, postoffice)
	logger.info("Building list of post office agents..")
	r = restGetRequest(login, url)
	try:
		for objects in r.json()['object']:
			poas.append(objects['name'])
			logger.debug("Appending post office agent to list: %s" % objects['name'])
	except KeyError: # KeyError if domain has no POA
		pass
	return poas

def getSystemList(login):
	gwapp_variables.initSystem()
	domains = getDomains(login)
	logger.info("Creating global domain and post office links")
	for domain in domains:
		postoffices = getPostOffices(login, domain)
		gwapp_variables.domainSystem[domain] = postoffices
		logger.debug("Creating domainSystem key: %s" % domain)
		logger.debug("Adding value: %s" % postoffices)

		for postoffice in postoffices: # Create postoffice dictionary
			gwapp_variables.postofficeSystem[postoffice] = domain
			logger.debug("Creating postofficeSystem key: %s" % postoffices)
			logger.debug("Adding value: %s" % domain)
			# Create POA dictonary
			poas = getPOAs(login, domain, postoffice)
			gwapp_variables.POASystem[postoffice] = poas
			logger.debug("Creating POASystem key: %s" % postoffice)
			logger.debug("Adding value: %s" % poas)

		# Create GWIAs dictonary
		gwias = getGWIAs(login, domain)
		gwapp_variables.gwiaSystem[domain] = gwias
		logger.debug("Creating gwiaSystem key: %s" % domain)
		logger.debug("Adding value: %s" % gwias)

def createTrustedApp(login, appName='gwapp', delete=False):
	if not checkTrustedApp(login, appName, delete=delete):
		if askYesOrNo("Create and store a trusted application"):
			data, header = gwapp_json.post_createTrustedApp()
			r = restPostRequest(login, '/gwadmin-service/system/trustedapps', data, header)
			if r.status_code == 201:
				print ("Successfully created trusted application '%s'" % appName)
				logger.info("Successfully created trusted application '%s'" % appName)
				with open(gwapp_variables.gwappSettings, 'wb') as cfgfile:
					Config.set('Settings', 'trustedName', appName)
					Config.set('Settings', 'trustedKey', r.text)
					Config.write(cfgfile)
			else:
				print ("Problem creating trusted application")
				logger.error("Problem creating trusted application")
	else:
		logger.warning("Trusted application already exists")

def checkTrustedApp(login, appName, delete=False):
	if delete:
		restDeleteRequest(login, '/gwadmin-service/system/trustedapps/%s' % appName)

	logger.info("Checking if trusted application '%s' exists.." % appName)
	r = restGetRequest(login, '/gwadmin-service/system/trustedapps/%s' % appName)
	try:
		if r.status_code != 200:
			logger.info("No trusted application")
			return False
	except AttributeError:
		logger.error("Unable to connect to address")
		return False

	Config.read(gwapp_variables.gwappSettings)
	if Config.get('Settings', 'trustedName') == 'None' or Config.get('Settings', 'trustedKey') == 'None':
		print ("\nTrusted application config missing. See '%s --help' to recreate" % gwapp_variables.SCRIPT_NAME)
		logger.error("setting.cfg missing trusted application information")
		sys.exit(1)

	logger.info("Trusted application found")
	return True

def getPOLogPath(dom, post):
	logFilePath = dict()
	url = "/gwadmin-service/domains/%s/postoffices/%s/poas" % (dom, post)
	r = restGetRequest(gwapp_variables.login, url)
	try:
		logFilePath[post] = (r.json()['object'][0]['logFilePath'])
	except:
		logFilePath[post] = None
	return logFilePath

def getLocalAgents():
	agents = []
	agent = dict()
	services = "/opt/novell/groupwise/admin/gwadminutil services -l"
	out = util_subprocess(services)
	for line in out[0].splitlines():
		if "Service" in line:
			agent['service'] = line.split(' ')[1]
		if "Executable" in line:
			agent['executable'] = line.split(' ')[1]
		if "Startup" in line:
			agent['startup'] = line.split(' ')[1]
		if not line and len(agent) >= 1:
			agents.append(agent)
			agent = dict()
	return agents

def getFilePermission(file):
	return stat.S_IMODE(os.stat(file).st_mode)

def getPostSetting(value, warning, debug=False, healthCheck=False):
    postSettings = dict()
    if not healthCheck:
	    getSystemList(gwapp_variables.login)
    for dom in gwapp_variables.domainSystem:
        for post in gwapp_variables.domainSystem[dom]:
            url = "/gwadmin-service/domains/%s/postoffices/%s" % (dom, post)
            r = restGetRequest(gwapp_variables.login, url, healthCheck)
            try:
                postSettings[post] = (r.json()[value])
                if debug:
	                logger.debug("Post Office [%s.%s] %s set to %s" % (post, dom, value, r.json()[value]))
            except:
                logger.warning(warning)
    return postSettings

def getDomainSetting(value, warning, debug=False, healthCheck=False):
    domSettings = dict()
    if not healthCheck:
	    getSystemList(gwapp_variables.login)
    for dom in gwapp_variables.domainSystem:
        url = "/gwadmin-service/domains/%s" % dom
        r = restGetRequest(gwapp_variables.login, url, healthCheck)
        try:
            domSettings[dom] = (r.json()[value])
            if debug:
                logger.debug("Domain [%s] %s set to %s" % (dom, value, r.json()[value]))
        except:
            logger.warning(warning)
    return domSettings

def getPoaSettings(value, warning, debug=False, healthCheck=False):
	PoaSettings = dict()
	if not healthCheck:
		getSystemList(gwapp_variables.login)
	for dom in gwapp_variables.domainSystem:
		for post in gwapp_variables.domainSystem[dom]:
			for poa in gwapp_variables.POASystem[post]:
				url = "/gwadmin-service/domains/%s/postoffices/%s/poas/%s" % (dom, post, poa)
				r = restGetRequest(gwapp_variables.login, url, healthCheck)
				try:
					PoaSettings["%s.%s.%s" % (poa,post,dom)] = (r.json()[value])
					if debug:
						logger.debug("POA [%s.%s.%s] %s set to %s" % (poa, post, dom, value, r.json()[value]))
				except:
					PoaSettings["%s.%s.%s" % (poa,post,dom)] = None 
					logger.warning(warning)
	return PoaSettings

def getMtaSettings(value, warning, debug=False, healthCheck=False):
	MtaSettings = dict()
	if not healthCheck:
		getSystemList(gwapp_variables.login)
	for dom in gwapp_variables.domainSystem:
		url = "/gwadmin-service/domains/%s/mta" % (dom)
		r = restGetRequest(gwapp_variables.login, url, healthCheck)
		try:
			MtaSettings[dom] = (r.json()[value])
		except:
			MtaSettings[dom] = None 
			logger.warning(warning)
	return MtaSettings

def getGwiaSettings(value, warning, debug=False, healthCheck=False):
	GwiaSettings = dict()
	if not healthCheck:
		getSystemList(gwapp_variables.login)
	for dom in gwapp_variables.domainSystem:
		try:
			for gwia in gwapp_variables.gwiaSystem[dom]:
				url = "/gwadmin-service/domains/%s/gwias/%s" % (dom, gwia)
				r = restGetRequest(gwapp_variables.login, url, healthCheck)
				try:
					GwiaSettings[gwia] = (r.json()[value])
				except:
					GwiaSettings[gwia] = None 
					logger.warning(warning)
		except KeyError:
			pass
	return GwiaSettings

def getLocalAgentHome(gwhaList):
	# Uses gwha settings for startup paths. Reads --home from startup files
	for agent in gwhaList:
		with open(agent['startup'], 'r') as startup:
			for line in startup:
				if '--home' in line and ';' not in line:
					try:
						agent['path'] = line.split(' ')[1].split('\n')[0]
						logger.info("Home path set to [%s] for %s" % (agent['path'], agent['service']))
					except IndexError:
						logger.error("Unable to find home path for %s" % agent['service'])
	return gwhaList
