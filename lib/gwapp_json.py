#!/usr/bin/env python
# List of JSON requests functions
__author__ = "Shane Nielson"
__maintainer__ = "Shane Nielson"
__email__ = "snielson@projectuminfinitas.com"


def post_createTrustedApp(appName='gwapp'):
	data = {'NMAPEnabled': 'false',
	'archiveServicePort': '0',
	'name': appName,
	'requireSsl': 'false',
	'ipPort': '0',
	'providesRetentionService': 'false',
	'queuingDisabled': 'false',
	'allowArchiveService': 'false'}

	header = {'Content-Type': 'application/json'}
	return data, header

