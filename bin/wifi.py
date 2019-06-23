#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
from lib import system

import sys
import re
import json
import argparse

"""
Rescan and list all available wifi connections
"""
def actionList():
	if system.which("nmcli"):
		#system.shell(["nmcli", "dev", "wifi", "rescan"])
		output = system.shell(["nmcli", "dev", "wifi", "list"], capture=True)

		ssidPos = re.search(r'(SSID\s*)', output[0]).span()
		signalPos = re.search(r'(SIGNAL\s*)', output[0]).span()
		securityPos = re.search(r'(SECURITY\s*)', output[0]).span()
		inUsePos = re.search(r'(IN-USE\s*)', output[0]).span()

		data = []
		for line in output[1:]:
			ssid = line[ssidPos[0]:ssidPos[1]].strip()
			signal = line[signalPos[0]:signalPos[1]].strip()
			security = line[securityPos[0]:securityPos[1]].strip()
			inUse = line[inUsePos[0]:inUsePos[1]].strip()
			data.append({
				"inUse": bool(inUse),
				"ssid": ssid,
				"signal": int(signal),
				"security": str(security).lower()
			})

		return data

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description = "Wifi command line.")
	subparsers = parser.add_subparsers(dest="command", help="Available commands.")
	parserRun = subparsers.add_parser("list", help="List all available Wifi.")
	args = parser.parse_args()

	# Excecute the action
	if args.command == "list":
		data = actionList()

	print(json.dumps(data))

	# Clean-up the library
	if system.destroy():
		sys.exit(1)
	sys.exit(0)
