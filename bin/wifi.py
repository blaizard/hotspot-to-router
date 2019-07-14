#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
import sys
import os
import re
import json
import argparse

## git-lego dep "https://github.com/blaizard/git-lego.git" "loader.py" "[branch=master]" "[namespace=gitlego]" [checksum=4269232004]
import imp
gitlego = imp.new_module("gitlego")
gitlego.__dict__["__file__"] = __file__
exec("""#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import imp, os, subprocess, sys
def loader(command = None):
	if len(sys.argv) < 2 or sys.argv[1] != "git-lego": return
	gitLegoPath = os.path.join(os.path.realpath(os.path.expanduser("~") if os.path.expanduser("~") else os.path.dirname(__file__)), ".git-lego")
	if not os.path.isdir(gitLegoPath): os.mkdir(gitLegoPath)
	gitLegoDepPath = os.path.join(gitLegoPath, "https.github.com.blaizard.git.lego.git")
	if not os.path.isdir(gitLegoDepPath): subprocess.call(["git", "clone", "https://github.com/blaizard/git-lego.git", gitLegoDepPath])
	lib = imp.load_module("lib", None, os.path.join(gitLegoDepPath, "lib"), ('', '', imp.PKG_DIRECTORY))
	gitlego = lib.interface.Interface(__file__, cwd=gitLegoPath)
	sys.exit(gitlego.run(command) if command else gitlego.run(sys.argv[2:]))
""", gitlego.__dict__)
## git-lego end

## git-lego dep "https://github.com/blaizard/python.git" "system/which.py" "[branch=master]" "[namespace=system]" [checksum=2354402845]
import imp
system = imp.new_module("system")
system.__dict__["__file__"] = __file__
exec("""#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import os
import sys
import subprocess

\"""
Return the path of the executable if available, None otherwise
\"""
def which(executable, cwd="."):
	try:
		\"""
		Note, Windows will try first to look for the .exe or .cmd
		whithin the drectory requested, hence this code path should
		happen all the time.
		\"""
		if sys.platform == "win32":
			pathList = os.environ["PATH"].split(os.pathsep)
			# If the path is a relative path
			if executable.find(os.path.sep):
				pathList.insert(0, path(cwd, os.path.dirname(executable)))
				executable = os.path.basename(executable)
			for root in pathList:
				for ext in [".exe", ".cmd", ""]:
					executablePath = os.path.join(root, "%s%s" % (executable, ext)).replace("/" if os.sep == "\\\\" else "\\\\", os.sep)
					if os.path.isfile(executablePath):
						return executablePath
		else:
			output = subprocess.check_output(["which", executable]).strip()
			return output if len(output) else None
	except:
		pass
	return None
""", system.__dict__)
## git-lego end

## git-lego dep "https://github.com/blaizard/python.git" "system/shell.py" "[branch=master]" "[namespace=system]" [checksum=1726439287]
import imp
exec("""#!/usr/bin/python
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
""", system.__dict__)
## git-lego end

"""
Rescan and list all available wifi connections
"""
def actionListNetworks(interface):
	networks = []

	if interface == None:
		pass

	elif system.which("nmcli") :
		# Might fail if 2 scans are done in a minimum interval
		system.shell(["nmcli", "dev", "wifi", "rescan", "ifname", interface], ignoreError=True)
		output = system.shell(["nmcli", "-t", "-f", "ssid,active,signal,security", "dev", "wifi", "list", "ifname", interface], capture=True)

		for line in output:
			items = line.split(":")
			networks.append({
				"inUse": bool(items[1].lower() == "yes"),
				"ssid": items[0],
				"signal": int(items[2]),
				"security": True if len(items[3]) > 0 else False
			})

	elif system.which("iwlist") and system.which("iwgetid"):

		output = system.shell(["iwlist", interface, "scan"], capture=True)
		output = re.compile("^\s*Cell [0-9]+", re.MULTILINE | re.IGNORECASE).split("\n".join(output))

		ssidRegexpr = re.compile("^\s*ESSID:\s*[\"']?(.*?)\s*[\"']?\s*$", re.MULTILINE | re.IGNORECASE)
		signalRegexpr = re.compile("^\s*Quality=([0-9]+)/?([0-9]+)*", re.MULTILINE | re.IGNORECASE)
		securityRegexpr = re.compile("^\s*Encryption\s+key:\s*on", re.MULTILINE | re.IGNORECASE)

		current = system.shell(["iwgetid", "-r", interface], capture=True)

		for item in output:
			match = ssidRegexpr.search(item)
			if match:
				ssid = match.group(1)
				signalMatch = signalRegexpr.search(item)
				signal = int(float(signalMatch.group(1)) / float(signalMatch.group(2)) * 100)
				security = True if securityRegexpr.search(item) else False

				networks.append({
					"inUse": bool(ssid == current[0]),
					"ssid": ssid,
					"signal": int(signal),
					"security": security
				})
	else:
		raise Exception("No interface supported")

	return filter(lambda x: len(x["ssid"]), networks)

"""
Rescan and list all available wifi connections
"""
def actionListInterfaces():
	interfaceList = []

	# Should work on most linux distros
	# Note: /proc/net/wireless only works if the interface is connected
	if os.path.isdir("/sys/class/net"):
		for interface in [f for f in os.listdir("/sys/class/net")]:
			if os.path.isdir(os.path.join("/sys/class/net", interface, "wireless")):
				interfaceList.append(interface)
	else:
		raise Exception("No interface supported")

	return interfaceList

"""
Connect to a Wifi network
"""
def actionConnect(interface, ssid, password = None):
	if interface == None:
		pass

	elif system.which("nmcli"):
		command = ["nmcli", "dev", "wifi", "connect", ssid, "ifname", interface]
		if password:
			command += ["password", password]
		output = system.shell(command, capture=True)
		if not re.search(r'successfully', output[0]):
			raise Exception(output[0])

	elif system.which("iwconfig"):
		command = ["sudo", "iwconfig", interface, "essid", ssid]
		if password:
			command += ["key", password]
		system.shell(command, capture=True)

	else:
		raise Exception("No interface supported")

if __name__ == "__main__":

	gitlego.loader()

	parser = argparse.ArgumentParser(description = "Wifi command line.")
	parser.add_argument("-i", "--interface", default=None, help="The interface to be used, if none is set it uses the default. Also default is a valid value for this argument.")
	subparsers = parser.add_subparsers(dest="command", help="Available commands.")
	subparsers.add_parser("list", help="List all available wifi networks.")
	subparsers.add_parser("interfaces", help="List all available interfaces.")
	parserConnect = subparsers.add_parser("connect", help="Connect to a wifi.")
	parserConnect.add_argument("ssid", help="The SSID to connect")
	parserConnect.add_argument("password", nargs="?", default=None, help="A password to connect to the SSID")
	args = parser.parse_args()

	# Excecute the action
	try:

		# Compute the default interface if needed
		interface = args.interface
		if args.interface == None or args.interface == "default":
			interfaceList = actionListInterfaces()
			interface = interfaceList[0] if len(interfaceList) else None

		data = None
		if args.command == "list":
			data = actionListNetworks(interface)
		elif args.command == "interfaces":
			data = actionListInterfaces() 
		elif args.command == "connect":
			actionConnect(interface, args.ssid, args.password)

		if data != None:
			print(json.dumps(data))

	except Exception as e:
		print(e)
		sys.exit(1)

	# Clean-up the library
	sys.exit(0)
