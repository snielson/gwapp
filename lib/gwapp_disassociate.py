#!/usr/bin/env python
# Written by Shane Nielson <snielson@projectuminfinitas.com>
from __future__ import print_function

__author__ = "Shane Nielson"
__maintainer__ = "Shane Nielson"
__email__ = "snielson@projectuminfinitas.com"

import os
import sys
import re
import shutil
import signal
import traceback
import logging, logging.config
import gwapp_variables
import gwapp_definitions as gw

# Import requests as an alternative to urllib
import requests
# Hide requests warning (outdated python with GMS)
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

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

class dissassociate:
	def __init__(self):
		self.urlList = []

	def getURL(self, dom, post, type, id):
		url = "/gwadmin-service/domains/%s/postoffices/%s/%s/%s/directorylink" % (dom, post, type, id)
		return url

	def printList(self):
		for item in self.urlList:
			print (item)

	def getListCount(self):
		return len(self.urlList)

	def disassociate(self, url):
		r = gw.restDeleteRequest(gwapp_variables.login, url)
		if r.status_code == '200':
			print ("Successfully disassociated %s" % url)
			logger.info("Successfully disassociated %s" % url)
		else:
			print ("Failed to disassociated %s" % url)
			logger.info("Failed to disassociated %s" % url)

	def disassociateList(self, urlList):
		failedList = []
		for url in urlList:
			self.disassociate(url)
		self.urlList = [] # Clear list after trying to disassociate it


	# TODO : Get URLs based on [system, domain, post office, name] for [system, user, group, resource]
