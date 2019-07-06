#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
from lib import system

import sys
import re
import json
import argparse

## git-lego dep "https://github.com/blaizard/git-lego.git" "loader.py" "master" "gitlego" 3762600802
_gitlego121 = """#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import os
import subprocess
import sys
import imp
def gitLegoLoader(command = None):
	if len(sys.argv) < 2 or sys.argv[1] != "git-lego": return
	gitLegoPath = os.path.join(os.path.realpath(os.path.expanduser("~") if os.path.expanduser("~") else os.path.dirname(__file__)), ".git-lego")
	if not os.path.isdir(gitLegoPath): os.mkdir(gitLegoPath)
	gitLegoDepPath = os.path.join(gitLegoPath, "https.github.com.blaizard.git.lego.git")
	if not os.path.isdir(gitLegoDepPath): subprocess.call(["git", "clone", "https://github.com/blaizard/git-lego.git", gitLegoDepPath])
	lib = imp.load_module("lib", None, os.path.join(gitLegoDepPath, "lib"), ('', '', imp.PKG_DIRECTORY))
	gitlego = lib.interface.Interface(__file__, cwd=gitLegoPath)
	sys.exit(gitlego.run(command) if command else gitlego.run(sys.argv[2:]))
"""
import imp
gitlego = imp.new_module("gitlego")
gitlego.__dict__["__file__"] = __file__
exec(_gitlego121, gitlego.__dict__)
## git-lego end




## git-lego dep "https://github.com/blaizard/python.git" "system/shell.py" "master" "shell" 1504378792
_gitlego1211 = """#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import subprocess
import sys
import threading
import time
try:
	from queue import Queue
except:
	from Queue import Queue

\"""
To store the instance of process started with the non-blocking option
\"""
global runningProcess
runningProcess = []

\"""
Execute a shell command in a specific directory.
If it fails, it will throw.
@param blocking Tells if the process should block the execution. If not it will run in parallel and might block the ending of the caller
                process if it ends.
\"""
def shell(command, cwd=".", capture=False, ignoreError=False, queue=None, signal=None, hideStdout=False, hideStderr=False, blocking=True):

	def enqueueOutput(out, queue, signal):
		try:
			for line in iter(out.readline, b''):
				queue.put(line.rstrip().decode('utf-8', 'ignore'))
		except:
			pass
		out.close()
		signal.set()

	stdout = open(os.devnull, "w") if hideStdout else (subprocess.PIPE if capture or queue else None)
	stderr = open(os.devnull, "w") if hideStderr else (subprocess.STDOUT if capture or queue else None)

	isReturnStdout = True if capture and not queue else False

	# Workaround on Windows machine, the environment path is not searched to find the executable, hence
	# we need to do this manually.
	if sys.platform == "win32":
		fullPath = which(command[0], cwd=cwd)
		if fullPath:
			command[0] = fullPath

	proc = subprocess.Popen(command, cwd=cwd, shell=False, stdout=stdout, stderr=stderr)

	# If non-blocking returns directly
	if not blocking:
		global runningProcess
		runningProcess.append(proc)
		return

	if not queue:
		queue = Queue()

	if not signal:
		signal = threading.Event()

	# Wait until a signal is raised or until the the process is terminated
	if capture:
		outputThread = threading.Thread(target=enqueueOutput, args=(proc.stdout, queue, signal))
		outputThread.start()
		signal.wait()
	else:
		while proc.poll() is None:
			time.sleep(0.1)
			if signal.is_set():
				break

	errorMsgList = []

	# Kill the process (max 5s)
	stoppedBySignal = True if proc.poll() is None else False
	if stoppedBySignal:
		def processTerminateTimeout():
			proc.kill()
			errorMsgList.append("stalled")
		timer = threading.Timer(5, processTerminateTimeout)
		try:
			timer.start()
			proc.terminate()
			proc.wait()
		finally:
			timer.cancel()

	if proc.returncode != 0:
		errorMsgList.append("return.code=%s" % (str(proc.returncode)))

	if len(errorMsgList):
		if not ignoreError:
			message = "Failed to execute '%s' in '%s': %s" % (" ".join(command), str(cwd), ", ".join(errorMsgList))
			raise Exception(message)

	# Build the output list
	return list(queue.queue) if isReturnStdout else []

\"""
Ensure that the processes previously started are destroyed
\"""
def destroy():
	isError = False
	# Wait until all non-blocking process previously started are done
	global runningProcess
	for process in runningProcess:
		isError |= (process.wait() != 0)
	return isError
"""
import imp
shell = imp.new_module("shell")
shell.__dict__["__file__"] = __file__exec(_gitlego1211, shell.__dict__)
## git-lego end





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

	gitlego.gitLegoLoader()

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
