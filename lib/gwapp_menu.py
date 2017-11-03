
import sys
import os
import traceback
import gwapp_definitions as gw
import gwapp_soap as gwsoap
import logging, logging.config
import ConfigParser
import pydoc
Config = ConfigParser.ConfigParser()
import getch
getch = getch._Getch()
import gwapp_ghc as ghc
import gwapp_disassociate as dis

# GLOBAL VARIABLES
import gwapp_variables

# Log Settings
logging.config.fileConfig('%s/logging.cfg' % (gwapp_variables.gwappConf))
logger = logging.getLogger('__main__')
excep_logger = logging.getLogger('exceptions_log')

def my_handler(type, value, tb):
	tmp = traceback.format_exception(type, value, tb)
	logger.error("EXCEPTION: See exception.log")
	excep_logger.error("Uncaught exception:\n%s" % ''.join(tmp).strip())
	print ''.join(tmp).strip()

# Install exception handler
sys.excepthook = my_handler

def show_menu(menu_call):
	gw.gwappBanner()
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
	menu = ['1. Checks..', '2. Disassociate..', '\n     0. Quit']
	sub_menus = {'1': check_menu, '2': disassociate_menu}
	
	available = build_avaialbe(menu)
	show_menu(menu)

	# Print disclaimer
	# gw.print_there(23,6, gwapp_variables.DISCLAIMER) ## TODO: Enable this?
	
	choice = get_choice(available)
	if choice == '0':
		loop = False
		gw.clear()
		return
	else:
		sub_menus[choice]()


## Sub menus ##

def check_menu():
	menu = ['1. Health Check', '\n     0. Back']
	
	available = build_avaialbe(menu)
	loop = True
	while loop:
		show_menu(menu)
		choice = get_choice(available)
		if choice == '1':
			ghc.mainCheck()
			gw.eContinue()
		elif choice == '0':
			loop = False
			main_menu()

def disassociate_menu():
	disList = dis.dissassociate()
	
	menu = ['1. GroupWise Menu', '2. Users Menu', '3. Group Menu', '4. Resources Menu', '\n     5. Show List', '6. Clear List', '7. Disassociate List', '\n     0. Back']
	
	available = build_avaialbe(menu)
	loop = True
	while loop:
		show_menu(menu)
		choice = get_choice(available)
		if choice == '1':
			sub_disassociate_GroupWise(disList)
		elif choice == '2':
			sub_disassociate_select(disList,'Users')
		elif choice == '3':
			sub_disassociate_select(disList,'Groups')
		elif choice == '4':
			sub_disassociate_select(disList,'Resources')
		elif choice == '5':
			if disList.getListCount() > 0:
				pydoc.pager(disList.getList())
			else:
				gw.gwappBanner()
				print ("Disassociate list is empty")
				logger.info("Disassociate list is empty")
				gw.eContinue()
		elif choice == '6':
			gw.gwappBanner()
			if disList.getListCount() > 0:
				disList.clearList()
				print ("List has been cleared")
				logger.info("List has been cleared")
			else:
				print ("Nothing to clear")
				logger.info(("Nothing to clear"))
			gw.eContinue()
		elif choice == '7':
			gw.gwappBanner()
			if disList.getListCount() > 0:
				print ("This will remove the directory association for all URls in the disassociate list")
				if gw.askYesOrNo("Do you want to continue"):
					disList.disassociateList()
					gw.eContinue()
			else:
				print ("Nothing to disassociate")
				logger.info("Nothing to disassociate")
				gw.eContinue()
			
		elif choice == '0':
			loop = False
			main_menu()

# Sub menus for disassociate
def sub_disassociate_GroupWise(disList):
	menu = ['1. List GroupWise System', '2. List by Directory ID', '3. List by Domain', '4. List by Post Office','5. List by Ojbect Name' , '\n     0. Back']
	
	available = build_avaialbe(menu)
	loop = True
	while loop:
		show_menu(menu)
		choice = get_choice(available)
		if choice == '1':
			gw.gwappBanner()
			disList.buildList('system', ['user', 'group','resource'])
			print ("URLs have been added to the disassociate list")
			logger.info("URLs have been added to the disassociate list")
			gw.eContinue()
		elif choice == '2':
			gw.gwappBanner()
			userInput = raw_input("LDAP Directory ID: ")
			disList.buildList('system', ['user', 'group','resource'], "directoryID=" + userInput)
			print ("URLs have been added to the disassociate list")
			logger.info("URLs have been added to the disassociate list")
			gw.eContinue()
		elif choice == '3':
			gw.gwappBanner()
			userInput = raw_input("Domain: ")
			disList.buildList('system', ['user', 'group','resource'], "domainName=" + userInput)
			print ("URLs have been added to the disassociate list")
			logger.info("URLs have been added to the disassociate list")
			gw.eContinue()
		elif choice == '4':
			gw.gwappBanner()
			userInput = raw_input("Post Office: ")
			disList.buildList('system', ['user', 'group','resource'], "postOfficeName=" + userInput)
			print ("URLs have been added to the disassociate list")
			logger.info("URLs have been added to the disassociate list")
			gw.eContinue()
		elif choice == '5':
			gw.gwappBanner()
			userInput = raw_input("Object Name: ")
			disList.buildList('system', ['user', 'group','resource'], "name=" + userInput)
			print ("URLs have been added to the disassociate list")
			logger.info("URLs have been added to the disassociate list")
			gw.eContinue()
		elif choice == '0':
			loop = False
			return

def sub_disassociate_select(disList, disType):
	menu = ['1. List All %s' % disType, '2. List %s by Directory ID' % disType, '3. List %s by Domain' % disType, '4. List %s by Post Office' % disType,'5. List %s by Ojbect Name' % disType, '\n     0. Back']
	selectType = {'Users': 'user', 'Groups': 'group', 'Resources': 'resource'}
	available = build_avaialbe(menu)
	loop = True
	while loop:
		show_menu(menu)
		choice = get_choice(available)
		if choice == '1':
			gw.gwappBanner()
			disList.buildList('system', [selectType[disType]])
			print ("URLs have been added to the disassociate list")
			logger.info("URLs have been added to the disassociate list")
			gw.eContinue()
		elif choice == '2':
			gw.gwappBanner()
			userInput = raw_input("LDAP Directory ID: ")
			disList.buildList('system', [selectType[disType]], "directoryID=" + userInput)
			print ("URLs have been added to the disassociate list")
			logger.info("URLs have been added to the disassociate list")
			gw.eContinue()
		elif choice == '3':
			gw.gwappBanner()
			userInput = raw_input("Domain: ")
			disList.buildList('system', [selectType[disType]], "domainName=" + userInput)
			print ("URLs have been added to the disassociate list")
			logger.info("URLs have been added to the disassociate list")
			gw.eContinue()
		elif choice == '4':
			gw.gwappBanner()
			userInput = raw_input("Post Office: ")
			disList.buildList('system', [selectType[disType]], "postOfficeName=" + userInput)
			print ("URLs have been added to the disassociate list")
			logger.info("URLs have been added to the disassociate list")
			gw.eContinue()
		elif choice == '5':
			gw.gwappBanner()
			userInput = raw_input("Object Name: ")
			disList.buildList('system', [selectType[disType]], "name=" + userInput)
			print ("URLs have been added to the disassociate list")
			logger.info("URLs have been added to the disassociate list")
			gw.eContinue()
		elif choice == '0':
			loop = False
			return