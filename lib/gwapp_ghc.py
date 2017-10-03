#!/usr/bin/env python
import gwapp_definitions as gw
import gwapp_variables
import commands
gw.gwappBanner(gwapp_variables.gwappversion)
#gw.getSystemList(gwapp_variables.login)
def getpoSec():
    postofficeSecurity = dict()
    gw.getSystemList(gwapp_variables.login)
    for dom in gwapp_variables.domainSystem:
        for PO in gwapp_variables.domainSystem[dom]:
            url = "/gwadmin-service/domains/%s/postoffices/%s" % (dom, PO)
            r = gw.restGetRequest(gwapp_variables.login, url)
            try:
                postofficeSecurity[PO] = (r.json()['securitySettings'])
            except:
                pass
    return postofficeSecurity

def AgentCrtChk():
	pass
#Check of Agent Certs
def AgentSslChk():
	pass
#https://151.155.214.174:9710/gwadmin-service/domains/pkldom/postoffices/pklpo/poas
#Set all Agents to Require SSL
def WebaccHttpCrt():
	pass
#Make sure the http cert for webaccess is used
def AgentOwners():
	pass
#Run agents as user other than root
def GwiaAccCon():
	pass
#GWIA Access Control (No relay)

#End Security section

def DiskSpdSrv():
	pass
#Disk Speed on Post Office Servers

def DiskSpcSrv():
	commands.getoutput("df -h")
#Disk Space on Post Office Servers
##Need to figure out how to read in where the data is located for pass/fail.

def ErrChkLogs():
	gw.getSystemList(gwapp_variables.login)
	for dom in gwapp_variables.domainSystem:
		for PO in gwapp_variables.domainSystem[dom]:
			logpath = gw.getPOLogPath(dom, PO)
			if logpath[PO] != None:
				log = "%s/poa.currentlog" % logpath[PO][0]
			else:
				log = "/var/log/novell/groupwise/%s.poa/poa.currentlog" % (PO)	
			#commands.getoutput("less /var/log/novell/groupwise/%s.poa/poa.currentlog | grep -i "error"") % (dom, PO)
			with open(log, "r") as poacurrentlog:
			#with open("/GWAPP/gwapp/1028poa.00c", "r") as poacurrentlog:
				for line in poacurrentlog:
					if "error" in line.lower():
						#print (dom, PO)
						print (line)
#Error Check on All Logs

def WebaccConn():
	pass
#Webaccess suggested settings for connections

def WebaccMemTom():
	pass
#Webaccess suggested memory settings for Tomcat

def GwiaThreads():
	pass
#Thread Settings for GWIA send/receive

def POAThreads():
	pass
#POA Thread Settings C/S Message Handler

def IMAPsettings():
	pass
#IMAP Settings for max messages per folder / Read First

def ChkRetention():
	pass
#Retention Plan and Software



