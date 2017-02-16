
import sys
import os
import traceback
import gwapp_definitions as gw
import gwapp_soap as gwsoap
import logging, logging.config
import ConfigParser
Config = ConfigParser.ConfigParser()
import getch
getch = getch._Getch()

COMPANY_BU = 'Micro Focus'
DISCLAIMER = "%s accepts no liability for the consequences of any actions taken\n     by the use of this application. Use at your own discretion" % COMPANY_BU

# Folders
gwappDirectory = "/opt/gwapp"
gwappConf = gwappDirectory + "/conf"
gwappSettings = gwappConf + "/setting.cfg"
gwappLogs = gwappDirectory + "/logs"
gwappTmp = gwappDirectory + "/tmp"
gwappLogSettings = gwappConf + "/logging.cfg"

# Log Settings
logging.config.fileConfig('%s/logging.cfg' % (gwappConf))
logger = logging.getLogger('__main__')
excep_logger = logging.getLogger('exceptions_log')

def my_handler(type, value, tb):
	tmp = traceback.format_exception(type, value, tb)
	logger.error("EXCEPTION: See exception.log")
	excep_logger.error("Uncaught exception:\n%s" % ''.join(tmp).strip())
	print ''.join(tmp).strip()

# Install exception handler
sys.excepthook = my_handler

# Read Config
Config.read(gwappSettings)
gwappversion = Config.get('Misc', 'gwapp.version')

def show_menu(menu_call):
	gw.gwappBanner(gwappversion)
	logger.debug("Showing menu options: %s" % menu_call)

	for i in xrange(len(menu_call)):
		print "     %s" % menu_call[i]

def get_choice(available, special=None):
	print "\n     Selection: ",
	while True:
		choice = getch()
		if special is not None and choice == special:
			print
			logger.debug("Selected option: %s" % choice)
			return special
		elif choice in available or choice == 'q' or choice == 'Q':
			if choice == '0' or choice == 'q' or choice == 'Q':
				print
				logger.debug("Selected option: 0")
				return '0'
			else:
				print
				logger.debug("Selected option: %s" % choice)
				return choice

def build_avaialbe(menu):
	available = []
	for i in range(len(menu)):
		available.append('%s' % i)
	return available

##################################################################################################
#	Menus
##################################################################################################

def main_menu():
	menu = ['1. Test', '\n     0. Quit']
	sub_menus = {'1': menu_1}
	
	available = build_avaialbe(menu)
	show_menu(menu)

	# Print disclaimer
	gw.print_there(23,6, DISCLAIMER)
	
	choice = get_choice(available)
	if choice == '0':
		loop = False
		gw.clear()
		return
	else:
		sub_menus[choice]()


## Sub menus ##

def menu_1():
	menu = ['1. Test 1', '\n     0. Back']
	
	available = build_avaialbe(menu)
	loop = True
	while loop:
		show_menu(menu)
		choice = get_choice(available)
		if choice == '1':
			pass
		elif choice == '0':
			loop = False
			main_menu()