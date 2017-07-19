#!/usr/bin/env python

# most of the code here was based on the following example on splunk custom alert actions
# http://docs.splunk.com/Documentation/Splunk/6.5.3/AdvancedDev/ModAlertsAdvancedExample

import os
import sys
import json
import gzip
import csv
import requests
import uuid
from requests.auth import HTTPBasicAuth

def create_alert(config, row):
	print >> sys.stderr, "DEBUG Creating alert with config %s" % config

	url = config.get('url') # Get TheHive URL from Splunk configuration
	username = config.get('username') # Get TheHive username from Splunk configuration
	password = config.get('password') # Get TheHive password from Splunk configuration
	auth = requests.auth.HTTPBasicAuth(username=username,password=password)
	sourceRef = str(uuid.uuid4())[0:6] # Generate unique identifier for alert

	# Filter empty multivalue fields
	row = {key: value for key, value in row.iteritems() if not key.startswith("__mv_")}

	# Take KV pairs and make a list-type of dicts
	artifacts = []
	for key, value in row.iteritems():
		artifacts.append(dict(
			dataType = key,
			data = value,
			message = "%s observed in this alert" % key
		))

	# Get the payload for the alert from the config, use defaults if they are not specified
	payload = json.dumps(dict(
		title = config.get('title'),
		description = config.get('description', "No description provided."),
		tags = [] if config.get('tags') is None else config.get('tags').split(","), # capable of continuing if Tags is empty and avoids split failing on empty list
		severity = int(config.get('severity', 2)),
		tlp = int(config.get('tlp', -1)),
		type = config.get('type', "alert"),
		artifacts = artifacts,
		source = config.get('source', "splunk"),
		caseTemplate = config.get('caseTemplate', "default"),
		sourceRef = sourceRef
	))
	# actually send the request to create the alert; fail gracefully
	try:
		print >> sys.stderr, 'INFO Calling url="%s" with payload=%s' % (url, payload)
		# set proper headers
		headers = {'Content-type': 'application/json'}
		# post alert
		response = requests.post(url, headers=headers, data=payload, auth=auth, verify=False)
		print >> sys.stderr, "INFO TheHive server responded with HTTP status %s" % response.status_code
		# check if status is anything other than 200; throw an exception if it is
		response.raise_for_status()
		# response is 200 by this point or we would have thrown an exception
		print >> sys.stderr, "INFO theHive server response: %s" % response.json()
	# somehow we got a bad response code from thehive
	except requests.exceptions.HTTPError as e:
		print >> sys.stderr, "ERROR theHive server returned following error: %s" % e
	# some other request error occurred
	except requests.exceptions.RequestException as e:
		print >> sys.stderr, "ERROR Error creating alert: %s" % e


if __name__ == "__main__":
	# make sure we have the right number of arguments - more than 1; and first argument is "--execute"
	if len(sys.argv) > 1 and sys.argv[1] == "--execute":
		# read the payload from stdin as a json string
	   	payload = json.loads(sys.stdin.read())
		# extract the file path and alert config from the payload
		config = payload.get('configuration')
		filepath = payload.get('results_file')
		# test if the results file exists - this should basically never fail unless we are parsing configuration incorrectly
		# example path this variable should hold: '/opt/splunk/var/run/splunk/12938718293123.121/results.csv.gz'
		if os.path.exists(filepath):
			# file exists - try to open it; fail gracefully
			try:
				# open the file with gzip lib, start making alerts
				# can with statements fail gracefully??
				with gzip.open(filepath) as file:
					# DictReader lets us grab the first row as a header row and other lines will read as a dict mapping the header to the value
					# instead of reading the first line with a regular csv reader and zipping the dict manually later
					# at least, in theory
					reader = csv.DictReader(file)
					# iterate through each row, creating a alert for each and then adding the observables from that row to the alert that was created
					for row in reader:
						# make the alert with predefined function; fail gracefully
						create_alert(config, row)
				# by this point - all alerts should have been created with all necessary observables attached to each one
				# we can gracefully exit now
				sys.exit(0)
			# something went wrong with opening the results file
			except IOError as e:
				print >> sys.stderr, "FATAL Results file exists but could not be opened/read"
				sys.exit(3)
		# somehow the results file does not exist
		else:
			print >> sys.stderr, "FATAL Results file does not exist"
			sys.exit(2)
	# somehow we received the wrong number of arguments
	else:
		print >> sys.stderr, "FATAL Unsupported execution mode (expected --execute flag)"
		sys.exit(1)
