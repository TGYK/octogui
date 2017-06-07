import sys
import configparser
import urllib.request
import json
from urllib.parse import urlencode

def getConfig(index):
	config = configparser.ConfigParser()
	try:
		config.read("config")
	except:
		print("Caught exception trying to read config file!")
		return None
	if index == "key":
		if "Connection" not in config.sections():
			print("No [Connection] section found within config!")
			return None
		else:
			try:
				key = config.get("Connection", "apikey")
			except:
				print("Exception caught trying to read API key from config")
				key = None
		return key
	elif index == "address":
		if "Connection" not in config.sections():
			print("No [Connection] section found within config!")
			return
		else:
			try:
				address = config.get("Connection", "address")
			except:
				print("Exception caught trying to read server address from config")
				address = None
		return address
	if index == "numheads":
		if "Toolheads" not in config.sections():
			print("No [Toolheads] section found within config!")
			return None
		else:
			try:
				numheads = config.get("Toolheads", "numheads")
			except:
				print("Exception caught trying to read number of heads from config")
				numheads = "1"
		return numheads
	if index == "mixing":
		if "Toolheads" not in config.sections():
			print("No [Toolheads] section found within config!")
			return None
		else:
			try:
				mix = config.get("Toolheads", "mixing")
			except:
				print("Exception caught trying to mixing head from config")
				mix = "False"
		mix = json.loads(mix)
		return mix
	else:
		print("Unrecognized getConfig command!")
		return None

def writeConfig(api, server):
	config = configparser.ConfigParser()
	cfgfile = open("config",'w')
	config.add_section('Connection')
	config.set('Connection', 'apiKey', api)
	config.set('Connection', 'address', server)
	config.write(cfgfile)
	cfgfile.close()

def getRequest(api, server, url):
	data = None
	response = None
	req_headers = {
		'X-Api-Key' : api,
		'User-Agent': 'Mozilla/5.0'}
	try:
		request = urllib.request.Request(url, headers = req_headers)
		opener = urllib.request.build_opener()
		response = opener.open(request).read().decode('utf-8')
	except urllib.error.HTTPError as e:
		#print(e.code)
		#print(e.msg)
		if e.code == 409:
			print("Error collecting data from server! Probably due to server-printer connection error.")
			data = None
		else:
			print("General HTTP error!")
	if response is not None:
		try:
			data = json.loads(response)
		except urllib.error.HTTPError as e:
			#print(e.code)
			#print(e.msg)
			if e.code == 409:
				print("Error collecting data from server! Probably due to server-printer connection error.")
				data = None
			else:
				print("General HTTP error!")
				data = None	
	return data

def postRequest(api, server, url, post_fields):
	data = None
	dump = json.dumps(post_fields)
	bytes = dump.encode('utf-8')
	req_headers = {
		'X-Api-Key' : api,
		'Content-Type' : 'application/json',
		'User-Agent': 'Mozilla/5.0'}	
	try:
		request = urllib.request.Request(url, headers = req_headers)
		request.add_header('Content-Length', len(bytes))
		opener = urllib.request.build_opener()
		response = opener.open(request, bytes).read()
	except urllib.error.HTTPError as e:
		print(e.code)
		#print(e.msg)
		#print(e.headers)
		#print(e.fp.read())
	return

def deleteRequest(api, server, url, req_headers):
	try:
		request = urllib.request.Request(url, headers = req_headers)
		request.get_method = lambda: 'DELETE'
		opener = urllib.request.build_opener()
		response = opener.open(request).read()
	except urllib.error.HTTPError as e:
		print(e.code)
		print(e.msg)
		print(e.headers)
		print(e.fp.read())
	return

def connectTest(api, server):
	state = False
	url = "http://"+server+"/api/version"
	data = getRequest(api, server, url)
	if data is not None:
		#print("Connection successful, server version is " + data['server'] + ", API version is " + data['api'])	
		state = True
	return state

def getJobData(api, server):
	data = None
	url = "http://"+server+"/api/job"
	data = getRequest(api, server, url)
	return data

def getPrinterData(api, server):
	data = None
	url = "http://"+server+"/api/printer"
	data = getRequest(api, server, url)
	if data == None:
		print("No data received!")
		return
	return data

def getProgress(data):
	progress = 0
	if data['progress']['completion'] == None:
		progress = 0
	else:
		progress = float(data['progress']['completion'])
	return progress


def getJob(data):
	jobName = ""
	if data['job']['file']['name'] == None:
		jobName = "No Job Printing"
	else:
		jobName = data['job']['file']['name']
	return jobName

def getSize(data):
	size = ""
	if data['job']['file']['size'] == None:
		size = "0 MB"
	else:
		size = data['job']['file']['size']
		if abs(size) < 1024.0:
			size = str("{0:.2f}".format(size))+"B"
		elif size / 1024.0 < 1024.0:
			size /= 1024.0
			size = str("{0:.2f}".format(size))+"KB"
		else:
			size /= 1048576.0
			size = str("{0:.2f}".format(size))+"MB"
	return size

def getTimeLeft(data):
	timeLeft = 0
	if data['progress']['printTimeLeft'] == None:
		timeLeft = 0
	else:
		timeLeft = data['progress']['printTimeLeft']
	return timeLeft

def getTimeSpent(data):
	timeSpent = 0
	if data['progress']['printTime'] == None:
		timeSpent = 0
	else:
		timeSpent = data['progress']['printTime']
	return timeSpent

def getFiles(api, server):
	data = None
	url = "http://"+server+"/api/files"
	data = getRequest(api, server, url)
	return data

def getState(api, server):
	state = ""
	url = "http://"+server+"/api/connection"
	data = getRequest(api, server, url)
	if data is not None:
		if data['current']['state'] == None:
			state = "Unknown"
		else:
			state = data['current']['state']
	return state

def getHeadTemp(data, tool="tool0"):
	if data['temperature'][tool]['actual'] == None:
		temp = 0
	else:
		temp = data['temperature'][tool]['actual']
	return temp

def getHeadTarget(data, tool='tool0'):
	temp = 0
	if data['temperature'][tool]['target'] == None:
		temp = 0
	else:
		temp = data['temperature'][tool]['target']
	return temp

def getBedTemp(data):
	temp = 0
	if data['temperature']['bed']['actual'] == None:
		temp = 0
	else:
		temp = data['temperature']['bed']['actual']
	return temp

def getBedTarget(data):
	temp = 0
	if data['temperature']['bed']['target'] == None:
		temp = 0
	else:
		temp = data['temperature']['bed']['target']
	return temp

def isDir(api, server, path, name):
	dirstate = False
	url = "http://"+server+"/api/files/"+path+"/"+name
	data = getRequest(api, server, url)
	if data['type'] == "folder":
		dirstate = True
	return dirstate

def postSelect(api, server, name, data):
	for file in data['files']:
		if name == file['name']:
			origin = file['origin']
			path = file['path']
			break
	url = "http://"+server+"/api/files/"+origin+"/"+path
	post_fields = {
		'command' : 'select',
		'print' : 'false'}
	response = postRequest(api, server, url, post_fields)
	return

def postDelete(api, server, name, data):
	for file in data['files']:
		if name == file['name']:
			origin = file['origin']
			path = file['path']
			break
	url = "http://"+server+"/api/files/"+origin+"/"+path
	response = deleteRequest(api, server, url)
	return

def postPrint(api, server, name, data):
	for file in data['files']:
		if name == file['name']:
			origin = file['origin']
			path = file['path']
			break
	url = "http://"+server+"/api/files/"+origin+"/"+path
	post_fields = {
		'command' : 'select',
		'print' : 'true'}
	response = postRequest(api, server, url, post_fields)

def postJog(api, server, axis, dist):
	url = "http://"+server+"/api/printer/printhead"
	post_fields = {
		'command' : 'jog',
		axis : dist}
	response = postRequest(api, server, url, post_fields)

def postHome(api, server, axis):
	url = "http://"+server+"/api/printer/printhead"
	post_fields = {
		'command' : 'home',
		'axes' : axis}
	response = postRequest(api, server, url, post_fields)

def postCommand(api, server, command):
	url = "http://"+server+"/api/printer/command"
	post_fields = {
		'command' : command}
	response = postRequest(api, server, url, post_fields)

def postConnect(api, server):
	url = "http://"+server+"/api/connection"
	post_fields = {
		'command' : 'connect'}
	response = postRequest(api, server, url, post_fields)

def postStop(api, server):
	url = "http://"+server+"/api/job"
	post_fields = {
		'command' : 'cancel'}
	response = postRequest(api, server, url, post_fields)

def postTogglePause(api, server):
	url = "http://"+server+"/api/job"
	post_fields = {
		'command' : 'pause',
		'action' : 'toggle'}
	response = postRequest(api, server, url, post_fields)

def postFeedRate(api, server, rate):
	url = "http://"+server+"/api/printer/printhead"
	post_fields = {
		'command' : 'feedrate',
		'factor' : rate}
	response = postRequest(api, server, url, post_fields)

def postHeadTemp(api, server, temp, tool='tool0'):
	url = "http://"+server+"/api/printer/tool"
	post_fields = {
		'command' : 'target',
		'targets' : {
			tool : temp}}
	response = postRequest(api, server, url, post_fields)

def postBedTemp(api, server, temp):
	url = "http://"+server+"/api/printer/bed"
	post_fields = {
		'command' : 'target',
		'target' : temp}
	response = postRequest(api, server, url, post_fields)
