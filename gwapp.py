#!/usr/bin/env python
# gwapp created by Shane Nielson to help with SOAP and REST commands on GroupWise 2014 +
__author__ = "Shane Nielson"
__maintainer__ = "Shane Nielson"
__email__ = "snielson@projectuminfinitas.com"

gwappversion='1'

import os
import sys
import traceback
import atexit
import logging, logging.config
import ConfigParser
Config = ConfigParser.ConfigParser()

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/lib')

##################################################################################################
#	Start up check
##################################################################################################

# Make sure user is root
if (os.getuid() != 0):
	print ("Root user required to run this script")
	sys.exit(1)

##################################################################################################
#	Global Variables
##################################################################################################

# Global Variables
from gwapp_variables import *
WSDL = 'file://%s/wsdl/GW2012/groupwise.wsdl' % (os.path.dirname(os.path.realpath(__file__)) + '/lib')

# Create gwapp folder stucture
gwapp_folders = [gwappDirectory, gwappConf, gwappLogs, gwappTmp]
for folder in gwapp_folders:
	if not os.path.exists(folder):
		os.makedirs(folder)

# Create setting.cfg if not found
if not os.path.isfile(gwappSettings):
	with open(gwappSettings, 'w') as cfgfile:
		Config.add_section('Misc')
		Config.add_section('Login')
		Config.add_section('Settings')
		Config.set('Misc', 'gwapp.version', gwappversion)
		Config.set('Login', 'url', None)
		Config.set('Login', 'admin', None)
		Config.set('Settings', 'trustedName', None)
		Config.set('Settings', 'trustedKey', None)
		Config.write(cfgfile)

##################################################################################################
#	Log Settings
##################################################################################################

# Log Settings
logging.config.fileConfig(gwappLogSettings)
excep_logger = logging.getLogger('exceptions_log')
logger = logging.getLogger(__name__)
logger.info('------------- Starting gwapp v%s -------------' % gwappversion)
if not sys.stdout.isatty():
	logger.info('Running in CRON')

##################################################################################################
#	Setup local definitions
##################################################################################################
import gwapp_definitions as gw

def exit_cleanup():
	logger.debug("Running exit cleanup..")

	# Clear gwapp/tmp
	gw.removeAllFolders(gwappTmp)
	gw.removeAllFiles(gwappTmp)

	# Reset terminal (for blank text bug on Ctrl + C)
	os.system('stty sane')
	
	logger.info('------------- Exiting gwapp v%s -------------' % gwappversion)

def signal_handler_SIGINT(signal, frame):
	# Clean up gwapp
	exit_cleanup()
	sys.exit(0)

def my_handler(type, value, tb):
	tmp = traceback.format_exception(type, value, tb)
	logger.error("EXCEPTION: See exception.log")
	excep_logger.error("Uncaught exception:\n%s" % ''.join(tmp).strip())
	print (''.join(tmp).strip())

# Install exception handler
sys.excepthook = my_handler

##################################################################################################
#	Set up script
##################################################################################################

# Register exit_cleanup with atexit
atexit.register(exit_cleanup)

# Get Console Size
if sys.stdout.isatty():
	windowSize = rows, columns = os.popen('stty size', 'r').read().split()
	if int(windowSize[0]) < int(24) or int(windowSize[1]) < int(80):
		print ("Terminal window does not meet size requirements\nCurrent Size: [%s x %s]\nPlease resize window to [80 x 24] or greater\n" % (windowSize[1],windowSize[0]))
		sys.exit(1)

##################################################################################################
#	Check Switches
##################################################################################################
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--version', action='version', version='%(prog)s (version {version})'.format(version=gwappversion))
parser.add_argument('--setlog', dest='loglevel', choices=['debug','info','warning'], help='Set the logging level')
parser.add_argument('-c', '--config', action='store_true', dest='config', help='Prompt to store new server settings')
parser.add_argument('-t', '--trusted', action='store_true', dest='newApp', help='Recreate the default trusted application')
args = parser.parse_args()
logger.debug("Switches: %s" % args)

# Set logs if loglevel switch passed in
if args.loglevel:
	logger.info("Running switch: setlog")
	Config.read(gwappLogSettings)
	Config.set('logger___main__', 'level', args.loglevel.upper())
	Config.set('logger_gwapp_definitions', 'level', args.loglevel.upper())
	with open(gwappLogSettings, 'wb') as logFile:
		Config.write(logFile)
	print "gwapp logs set to %s" % args.loglevel.upper()
	logger.info("gwapp logs set to %s" % args.loglevel.upper())
	sys.exit(0)

# Get or set login info
login = gw.saveServerSettings(args.config)
gw.createTrustedApp(login, delete=args.newApp)

##################################################################################################
#	DEBUG
##################################################################################################

DEBUG_ENABLED = False
if DEBUG_ENABLED:

	gw.eContinue()
	sys.exit(0)

##################################################################################################
#	Main
##################################################################################################

# Check login info before loading the script
if not gw.checkLoginInfo(login):
	sys.exit(1)

import gwapp_menu as menu
menu.main_menu()

sys.exit(0)