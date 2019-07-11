#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import os
import sys
import json
import argparse

def actionGet():
    temperature = 0
    # Should work on most linux distros
    if os.path.isdir("/sys/class/thermal"):
        for file in [f for f in os.listdir("/sys/class/thermal")]:
            if file.startswith("thermal_zone"):
                try:
                    with open(os.path.join("/sys/class/thermal", file, "temp")) as f:
                        temperature = max(temperature, int(f.readline()))
                except:
                    pass
        temperature /= 1000
    return temperature

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description = "Temperature command line.")
	subparsers = parser.add_subparsers(dest="command", help="Available commands.")
	parserRun = subparsers.add_parser("get", help="Get the current temperature.")
	args = parser.parse_args()

	# Excecute the action
	if args.command == "get":
		data = actionGet()

	print(json.dumps(data))

	sys.exit(0)
