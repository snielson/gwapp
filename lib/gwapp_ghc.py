#!/usr/bin/env python
import gwapp_definitions as gw
import gwapp_variables
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