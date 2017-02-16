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
SCRIPT_NAME = 'gwapp'
gwappDirectory = "/opt/gwapp"
gwappConf = gwappDirectory + "/conf"
gwappLogs = gwappDirectory + "/logs"
gwappLogSettings = gwappConf + "/logging.cfg"
gwappSettings = gwappConf + "/setting.cfg"
COMPANY_BU = 'Micro Focus'
ERROR_MSG = "\ndgwapp has encountered an error. See gwapp.log for more details"

if sys.stdout.isatty():
	WINDOW_SIZE = rows, columns = os.popen('stty size', 'r').read().split()
else:
	# Default terminal size
	WINDOW_SIZE = [24,80]


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

# Read Config
Config.read(gwappSettings)
gwappversion = Config.get('Misc', 'gwapp.version')

def clear():
	tmp = subprocess.call('clear',shell=True)

def gwappBanner(gwappversion):
	banner = """
     __ ___      ____ _ _ __  _ __  
    / _` \\ \\ /\\ / / _` | '_ \\| '_ \\ 
   | (_| |\\ V  V / (_| | |_) | |_) |
    \__, | \\_/\\_/ \__,_| .__/| .__/ 
    |___/              |_|   |_|   
	"""
	clear()
	print (banner + "\t\t         v" + gwappversion + "\n")

def print_disclaimer(gwappversion):
	gwappBanner(gwappversion)
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

def getPassWD():
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

def getGWLogin():
	loginInfo = dict()
	loginInfo['url'] = getServerInfo()
	loginInfo['admin'] = getUserID("Admin user: ")
	loginInfo['pass'] = getPassWD()
	return loginInfo

def checkDictKeys(list):
	result = True
	for key in list:
		# Check value in key
		if list[key] is None:
			result = False
	return result

def saveServerSettings(reconfig=False):
	gwappBanner(gwappversion)
	Config.read(gwappSettings)
	if Config.get('Login', 'url') == 'None' or Config.get('Login','admin') == 'None' or reconfig:
		login = getGWLogin()
		if checkDictKeys(login):
			if askYesOrNo("\nStore login information"):
				with open(gwappSettings, 'wb') as cfgfile:
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
		passwd = getPassWD()
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

def restGetRequest(login, urlPath):
	r = None
	try:
		r = requests.get(login['url'] + urlPath, auth=(login['admin'],login['pass']), verify=False)
		logger.info("Status code: %s" % r.status_code)
	except:
		pass
	return r

def restPostRequest(login, urlPath, data, header):
	r = None
	try:
		r = requests.post(login['url'] + urlPath, auth=(login['admin'], login['pass']), verify=False, data=json.dumps(data), headers=header)
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
		logger.info("Status code: %s" % r.status_code)
	except:
		pass

	if r.status_code == 200:
		logger.info("Successfully deleted %s" % login['url'] + urlPath)

	return r

def createTrustedApp(login, appName='gwapp', delete=False):
	if not checkTrustedApp(login, appName, delete=delete):
		if askYesOrNo("Create and store a trusted application"):
			data, header = gwapp_json.post_createTrustedApp()
			r = restPostRequest(login, '/gwadmin-service/system/trustedapps', data, header)
			if r.status_code == 201:
				print ("Successfully created trusted application '%s'" % appName)
				logger.info("Successfully created trusted application '%s'" % appName)
				with open(gwappSettings, 'wb') as cfgfile:
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
	if r.status_code != 200:
		logger.info("No trusted application")
		return False

	Config.read(gwappSettings)
	if Config.get('Settings', 'trustedName') == 'None' or Config.get('Settings', 'trustedKey') == 'None':
		print ("\nTrusted application config missing. See '%s --help' to recreate" % SCRIPT_NAME)
		logger.error("setting.cfg missing trusted application information")
		sys.exit(1)

	logger.info("Trusted application found")
	return True
