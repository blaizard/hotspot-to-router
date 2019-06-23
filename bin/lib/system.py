#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import subprocess
import sys
import re
import os
import threading
import time
import shlex
try:
	from queue import Queue
except:
	from Queue import Queue

"""
Extract the version number from the output received by a shell command
"""
def getVersion(output):
	for line in output:
		match = re.search(r'(\d+(?:\.\d+)+)', line)
		if match:
			return match.group(1)
	return "unknown"

"""
Split a command string into a list (and handle Windows...)
"""
def shellSplit(commandStr):
	return shlex.split(commandStr, posix="win" not in sys.platform)

"""
Return the path of the executable if available, None otherwise
"""
def which(executable, cwd="."):
	try:
		"""
		Note, Windows will try first to look for the .exe or .cmd
		whithin the drectory requested, hence this code path should
		happen all the time.
		"""
		if sys.platform =='win32':
			pathList = os.environ['PATH'].split(os.pathsep)
			# If the path is a relative path
			if executable.find(os.path.sep):
				pathList.insert(0, path(cwd, os.path.dirname(executable)))
				executable = os.path.basename(executable)
			for root in pathList:
				for ext in [".exe", ".cmd", ""]:
					executablePath = path(root, executable + ext)
					if os.path.isfile(executablePath):
						return executablePath
		else:
			return shell(["which", executable], capture=True)[0]
	except:
		pass
	return None

"""
To store the instance of process started with the non-blocking option
"""
runningProcess = []

"""
Execute a shell command in a specific directory.
If it fails, it will throw.
@param blocking Tells if the process should block the execution. If not it will run in parallel and might block the ending of the caller
                process if it ends.
"""
def shell(command, cwd=".", capture=False, ignoreError=False, queue=None, signal=None, hideStdout=False, hideStderr=False, blocking=True):

	def enqueueOutput(out, queue, signal):
		try:
			for line in iter(out.readline, b''):
				queue.put(line.rstrip().decode('utf-8', 'ignore'))
		except:
			pass
		out.close()
		signal.set()

	stdout = open(os.devnull, 'w') if hideStdout else (subprocess.PIPE if capture or queue else None)
	stderr = open(os.devnull, 'w') if hideStderr else (subprocess.STDOUT if capture or queue else None)

	isReturnStdout = True if capture and not queue else False

	# Workaround on Windows machine, the environment path is not searched to find the executable, hence
	# we need to do this manually.
	if sys.platform =='win32':
		fullPath = which(command[0], cwd=cwd)
		if fullPath:
			command[0] = fullPath

	proc = subprocess.Popen(command, cwd=cwd, shell=False, stdout=stdout, stderr=stderr)

	# If non-blocking returns directly
	if not blocking:
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

"""
Ensure that the processes previously started are destroyed
"""
def destroy():
	isError = False
	# Wait until all non-blocking process previously started are done
	for process in runningProcess:
		isError |= (process.wait() != 0)
	return isError
