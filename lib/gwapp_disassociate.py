#!/usr/bin/env python
# Written by Shane Nielson <snielson@projectuminfinitas.com>
from __future__ import print_function

__author__ = "Shane Nielson"
__maintainer__ = "Shane Nielson"
__email__ = "snielson@projectuminfinitas.com"

import sys
import signal
import traceback
import logging, logging.config
import gwapp_variables
import gwapp_definitions as gw

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

	def printList(self):
		for item in self.urlList:
			print (item)

	def getListCount(self):
		return len(self.urlList)

	def disassociate(self, url):
		r = gw.restDeleteRequest(gwapp_variables.login, url)
		if r.status_code == 204:
			print ("Successfully disassociated %s" % url)
			logger.info("Successfully disassociated %s" % url)
		else:
			print ("Failed to disassociated %s" % url)
			logger.info("Failed to disassociated %s" % url)

	def disassociateList(self):
		if self.getListCount() == 0:
			print ("Nothing to disassociate")
			logger.info("Nothing to disassociate")
		else:
			for url in self.urlList:
				self.disassociate(url)
			self.urlList = [] # Clear list after trying to disassociate it

	def buildList(self, scope, types=[], id=None): 
		"""
		scope can be the following [system, dom, post, name, directory]
		type can be a list of the following [user, group, resource]
		id should be the name of the user, group, resource, post office, or domain
		"""
		urls = []
		scopeList = {'system':"", 'dom':'domainName=', 'post':'postOfficeName=', 'name':'name=', 'directory':'directoryID='}

		for type in types:
			if id != None:
				url = "/gwadmin-service/list/%s?%s%s&attrs=domain,postoffice,name" % (type, scopeList[scope], id)
				logger.debug("URL: %s" % url)
				urls.append(url)
			else:
				url = "/gwadmin-service/list/%s?attrs=domain,postoffice,name" % type
				logger.debug("URL: %s" % url)
				urls.append(url)

		for url in urls:
			r = gw.restGetRequest(gwapp_variables.login, url)
			try:
				for item in r.json()['object']:
					self.urlList.append(item['@url'] +"/directorylink")
			except KeyError:
				pass



