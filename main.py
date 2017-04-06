#~~~OctoGUI by TGYK~~~
#Version 0.1
#Description:
#-Provides a basic graphical user interface for an octoprint
#-for use on a raspberry pi with a 2.8" tft LCD screen.
#-Assumes that you've already installed and configured your
#-pitft screen to work properly as the default screen.
#Depends:
#-python3
#-qt5
#-pyqt5
#Install using:
#-'sudo apt-get install python3 qt5'
#-'sudo apt-get install pyqt5'
###TODO###
#*Handle directories
#*Impliment move operation
#*Impliment mkdir operation
#*Add extruder move sub-menu to control menu
#*Move progress bar to Monitor page
#*Come up with method to start on login
#*Possibly add on-screen keyboard for config page - to not require an ssh login to edit config file/keyboard to type parameters.
#*Add extruder count and heated bed options to config page
#**Modify print page UI based on config options for extruder count, heated bed
#*Add labels to print page UI
#Known bugs:
#*



import sys
import PyQt5
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
import mainwindow_auto
from backend import *

class MainWindow(QMainWindow, mainwindow_auto.Ui_MainWindow):
	#Handle button hooks
	def handleCommand(self, command):
		#Define global variables which are updated on button press
		global apiKey
		global serverAddr
		global jogDist
		global feedRate
		global headTarget
		global bedTarget
		global fileList
		global printerData
		#Button hook command switch
		if command == 'home':
			#Switch to Home view, restart timed updates
			self.pageSwitcher.setCurrentWidget(self.homePage)
			self.start()
		elif command == 'control':
			#Switch to control view, stop timed updates (Unused in this view or interferes with user input)
			self.pageSwitcher.setCurrentWidget(self.controlPage)
			self.stop()
		elif command == 'configure':
			#Switch to configure view, stop timed updates (Unused in this view or interferes with user input)
			self.pageSwitcher.setCurrentWidget(self.configurePage)
			self.stop()
		elif command == 'file':
			#Switch to control view, stop timed updates (Unused in this view or interferes with user input)
			#Check for changes in file list since last update, if so, clear list and re-populate
			self.pageSwitcher.setCurrentWidget(self.filePage)
			fileListOld = fileListDir
			if apiKey is not None and serverAddr is not None:
				fileListNew = self.updateFileList(apiKey, serverAddr)
				if fileListOld != fileListNew:
					self.listFile.clear()
					for file in fileListNew['files']:
						self.listFile.addItem(file['name'])
			self.stop()
		elif command == 'monitor':
			#Switch to monitor page
			self.pageSwitcher.setCurrentWidget(self.monitorPage)
		elif command == 'print':
			#Switch to print page, update values, update GUI to reflect these values
			self.pageSwitcher.setCurrentWidget(self.printPage)
			if apiKey is not None and serverAddr is not None:
				printerData = getPrinterData(apiKey, serverAddr)
				headTarget = getHeadTarget(printerData)
				bedTarget = getBedTarget(printerData)
			self.tempHead.setValue(headTarget)
			self.tempBed.setValue(bedTarget)
		elif command == 'deleteselected':
			#Delete selected file
			if apiKey is not None and serverAddr is not None:
				postDelete(apiKey, serverAddr, selectedFile, fileListNoDir)
		elif command == 'postconnect':
			#Connect server-printer
			if apiKey is not None and serverAddr is not None:
				postConnect(apiKey, serverAddr)
		elif command == 'printstop':
			#Stop current print
			if apiKey is not None and serverAddr is not None:
				postStop(apiKey, serverAddr)
		elif command == 'printpause':
			#Toggle pause on current print
			if apiKey is not None and serverAddr is not None:
				postTogglePause(apiKey, serverAddr)
		elif command == 'hundred':
			#Set jog distance to 100mm
			jogDist = 100
		elif command == 'ten':
			#Set jog distance to 10mm
			jogDist = 10
		elif command == 'one':
			#Set jog distance to 1mm
			jogDist = 1
		elif command == 'pointone':
			#Set jog distance to 0.1mm
			jogDist = 0.1
		elif command == 'printselected':
			#Print selected file
			if apiKey is not None and serverAddr is not None:
				postPrint(apiKey, serverAddr, selectedFile, fileListNoDir)
		elif command == 'setTemp':
			#Set head and bed temps, as well as feedrate from current UI values
			feedRate = self.moveFeed.value()
			newHeadTemp = self.tempHead.value()
			newBedTemp = self.tempBed.value()
			self.setFeedRate(feedRate)
			self.setHeadTemp(newHeadTemp)
			self.setBedTemp(newBedTemp)
		elif command == 'close':
			#Exit app
			print("Close app")
			self.stop()
			self.closeApp()
		elif command == 'connect':
			#Connect GUI-server using UI values (Set during init from config or changed by user)
			#Alert if UI is blank or error connecting
			apiKey = self.textAPIKey.text()
			serverAddr = self.textServerAddr.text()
			if apiKey is not None and apiKey is not '':
				print("API key is "+apiKey)
			if serverAddr is not None and serverAddr is not '':
				print("Server Address is "+serverAddr)
			if apiKey == '' or apiKey == None:
				QMessageBox.information(None,"Error!","Please enter a key!")
			elif serverAddr == '' or serverAddr == None:
				QMessageBox.information(None,"Error!", "Please enter an address!")
			else:
				response = connectTest(apiKey, serverAddr)
				if not response:
					QMessageBox.information(None, "Error!", "Error connecting to server")
				else:
					cfgfile = open("config",'w')
					writeConfig(apiKey, serverAddr)
					cfgfile.close()
		else:
			#Unhandled button press
			print("Unrecognized command")

	def closeApp(self):
		#Close app
		self.close()

	def updateFileList(self, apiKey, serverAddr):
		#Declare global variables
		global fileListDir
		global fileListNoDir
		#Try to update file lists, add "/" to directories
		fileList = getFiles(apiKey, serverAddr)
		fileListNoDir = fileList
		if fileList is not None:
			for file in fileList['files']:
				dirState = isDir(apiKey, serverAddr, file['origin'], file['name'])
				if dirState:
					file['name'] = file['name']+"/"
		fileListDir = fileList
		return fileList

	def selectFile(self, index):
		#Declare global variables
		global selectedFile
		#Select file from file list without the appended "/" for directories to prevent breaking any backend calls
		name = str(index.text())
		for file in fileListNoDir['files']:
			if file['name'] in name:
				postSelect(apiKey, serverAddr, file['name'], fileListNoDir)
				selectedFile = file['name']

	def jogHead(self, axis, direction):
		#Move head/bed using value determined from button press or default value (1)
		if direction == 'neg':
			dist = -jogDist
		else:
			dist = jogDist
		postJog(apiKey, serverAddr, axis, dist)

	def homeHead(self, axis):
		#Issue home command for either X/Y or Z
		postHome(apiKey, serverAddr, axis)

	def issueCommand(self, command):
		#Issue arbitrary command to printer (Only ever used for G29 currently)
		postCommand(apiKey, serverAddr, command)

	def convMinSecStr(self, seconds):
		#Convert from seconds to minutes/seconds for print screen info
		minutes, seconds= divmod(seconds, 60)
		hours, minutes= divmod(minutes, 60)
		minSecStr = str(hours) + ":" + str(minutes) + ":" + str(seconds)
		return minSecStr

	def setFeedRate(self, rate):
		#Set feed rate
		postFeedRate(apiKey, serverAddr, rate)

	def setHeadTemp(self, temp):
		#Set tool0 temp
		postHeadTemp(apiKey, serverAddr, temp)

	def setBedTemp(self, temp):
		#Set bed temp
		postBedTemp(apiKey, serverAddr, temp)

	def __init__(self):
		#Declare global variables
		global apiKey
		global serverAddr
		global jogDist
		global job
		global size
		global timeLeft
		global timeSpent
		global sizePrinted
		global state
		global headTemp
		global headTarget
		global bedTemp
		global bedTarget
		global feedRate
		global jobData
		global printerData
		#Init stuff for UI
		super(self.__class__, self).__init__()
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.setupUi(self)
		#Initialize variables which are not updated.
		fileListNoDir = None
		fileListDir = None
		fileList = None
		jobData = None
		printerData = None
		state = None
		jogDist = 1
		feedRate = 100
		response = False
		#Get API key from config - update GUI with current figures if found
		apiKey = getConfig("key")
		serverAddr = getConfig("address")
		if apiKey == None:
			print("No API key found in config")
			apiKey = None
		else:
			print("Found API key in config")
			self.textAPIKey.setText(apiKey)
		#Get server address from config - update GUI with current figures if found
		if serverAddr == None:
			print("No server address found in config")
			serverAddr = None
		else:
			print("Found server address in config")
			self.textServerAddr.setText(serverAddr)
		if apiKey is None and serverAddr is None:
			print("Config file must not exist... Creating")
			cfgfile = open("config",'w+')
			cfgfile.close()
		#If both api key or server address are None, create config and update with values from UI
			
		#Test connection to OctoPrint server with gathered API key and address
		#If failed, alert to check config
		if apiKey is not None and serverAddr is not None:
			response = connectTest(apiKey, serverAddr)
		if not response:
			QMessageBox.information(None,"Error!","Error connecting, see config")
		#Try to get /api/job json data
		#If not None, update global variables, update GUI to reflect relevant values
		if apiKey is not None and serverAddr is not None:
			jobData = getJobData(apiKey, serverAddr)
		if jobData is not None:
			timeLeft = getTimeLeft(jobData)
			timeSpent = getTimeSpent(jobData)
			size = getSize(jobData)
			job = getJob(jobData)
			progress = getProgress(jobData)
			self.labelJob.setText(job)
			self.labelSize.setText(size)
			self.labelTimeLeft.setText(self.convMinSecStr(timeLeft))
			self.labelPrintTime.setText(self.convMinSecStr(timeSpent))
			self.printBar.setValue(progress)
		#Try to get /api/printer json data
		#If not None, update global variables, update GUI to reflect relevant values
		if apiKey is not None and serverAddr is not None and response is not None:
			printerData = getPrinterData(apiKey, serverAddr)
		if printerData is not None:
			headTemp = getHeadTemp(printerData)
			headTarget = getHeadTarget(printerData)
			bedTemp = getHeadTemp(printerData)
			bedTarget = getBedTarget(printerData)
			self.tempHead.setValue(headTarget)
			self.tempBed.setValue(bedTarget)
		#Try to get server-printer connection state
		#If not None, update global variables, update GUI to reflect relevant values
		if apiKey is not None and serverAddr is not None:
			teststate = connectTest(apiKey, serverAddr)
			if connectTest is not None:
				state = getState(apiKey, serverAddr)
			else:
				state = "Closed"
		if state is not None:
			self.labelState.setText(state)
			if "Closed" not in state and "Error" not in state:
				self.btnPostConnect.setEnabled(False)
				self.btnConnect.setEnabled(False)
				if "Printing"not in state:
					self.btnControl.setEnabled(True)
					self.btnPrint.setEnabled(True)
					self.btnFile.setEnabled(True)
					self.btnPrintSelected.setEnabled(True)
				else:
					self.btnControl.setEnabled(False)
					self.btnPrintSelected.setEnabled(False)
					self.btnPrint.setEnabled(True)
			else:
				self.btnPostConnect.setEnabled(True)
				self.btnControl.setEnabled(False)
				self.btnPrint.setEnabled(False)
				self.btnFile.setEnabled(False)
		else:
			self.labelState.setText("Error")
		#Get default feedrate (100%) from GUI
		self.moveFeed.setValue(feedRate)
		#Tell the server about our default feedrate
		if apiKey is not None and serverAddr is not None:
			self.setFeedRate(feedRate)
		#Try to get /api/files json data
		#If not None, update global variables, update GUI to reflect relevant values
		if apiKey is not None and serverAddr is not None:
			fileList = self.updateFileList(apiKey, serverAddr)
		if fileList is not None:
			for file in fileList['files']:
				#Add each file to the list
				self.listFile.addItem(file['name'])
			
			for file in fileList['files']:
				if file['name'] is not None:
					#Global variable for selectedFile is the first file in the list (Prevents breaking from hitting delete or print)
					selectedFile = file['name']
					break
		# button hooks
		self.btnHome.clicked.connect(lambda: self.handleCommand("home"))
		self.btnHome2.clicked.connect(lambda: self.handleCommand("home"))
		self.btnHome3.clicked.connect(lambda: self.handleCommand("home"))
		self.btnHome4.clicked.connect(lambda: self.handleCommand("home"))
		self.btnHome5.clicked.connect(lambda: self.handleCommand("home"))
		self.btnControl.clicked.connect(lambda: self.handleCommand("control"))
		self.btnConfigure.clicked.connect(lambda: self.handleCommand("configure"))
		self.btnFile.clicked.connect(lambda: self.handleCommand("file"))
		self.btnMonitor.clicked.connect(lambda: self.handleCommand("monitor"))
		self.btnPrint.clicked.connect(lambda: self.handleCommand("print"))
		self.btnPrintSelected.clicked.connect(lambda: self.handleCommand("printselected"))
		self.btnConnect.clicked.connect(lambda: self.handleCommand("connect"))
		self.btnExit.clicked.connect(lambda: self.handleCommand("close"))
		self.btnDelete.clicked.connect(lambda: self.handleCommand("deleteselected"))
		self.btnYPlus.clicked.connect(lambda: self.jogHead("y", "pos"))
		self.btnYMinus.clicked.connect(lambda: self.jogHead("y", "neg"))
		self.btnXPlus.clicked.connect(lambda: self.jogHead("x", "pos"))
		self.btnXMinus.clicked.connect(lambda: self.jogHead("x", "neg"))
		self.btnZPlus.clicked.connect(lambda: self.jogHead("z", "pos"))
		self.btnZMinus.clicked.connect(lambda: self.jogHead("z", "neg"))
		self.btnHomeXY.clicked.connect(lambda: self.homeHead(["x", "y"]))
		self.btnHomeZ.clicked.connect(lambda: self.homeHead(["z"]))
		self.btnAutoLevel.clicked.connect(lambda: self.issueCommand("G29"))
		self.btnHundred.clicked.connect(lambda: self.handleCommand("hundred"))
		self.btnTen.clicked.connect(lambda: self.handleCommand("ten"))
		self.btnOne.clicked.connect(lambda: self.handleCommand("one"))
		self.btnPointOne.clicked.connect(lambda: self.handleCommand("pointone"))
		self.btnPostConnect.clicked.connect(lambda: self.handleCommand("postconnect"))
		self.listFile.itemClicked.connect(self.selectFile)
		self.btnStart.clicked.connect(lambda: self.handleCommand("printselected"))
		self.btnStop.clicked.connect(lambda: self.handleCommand("printstop"))
		self.btnSet.clicked.connect(lambda: self.handleCommand("setTemp"))		
		#Timed updates to variables and GUI every 5 seconds
		self.timer = QtCore.QTimer(self)
		self.timer.setInterval(5000)
		self.timer.timeout.connect(self.update)

	#Start and stop timer at will
	def start(self):
		self.timer.start()
	def stop(self):
		self.timer.stop()
	#Timed update function

	@QtCore.pyqtSlot()
	def update(self):
		#Declare global variables
		global jobData
		global progress
		global job
		global size
		global timeLeft
		global timeSpent
		global sizePrinted
		global state
		global headTemp
		global bedTemp
		global printerData
		#Try to get /api/connection json data
		#If not None, update global variables, update GUI to reflect relevant values
		if apiKey is not None and serverAddr is not None:
			response = connectTest(apiKey, serverAddr)
			if connectTest is not None:
				state = getState(apiKey, serverAddr)
			else:
				state = "Closed"
		if state is not None:
			self.labelState.setText(state)
			if "Closed" not in state and "Error" not in state:
				self.btnPostConnect.setEnabled(False)
				self.btnConnect.setEnabled(False)
				#Try to get /api/printer json data
				#If not None, update global variables, update GUI to reflect relevant values
				if apiKey is not None and serverAddr is not None:
					printerData = getPrinterData(apiKey, serverAddr)
				else:
					printerData = None
				if "Printing"not in state:
					self.btnControl.setEnabled(True)
					self.btnPrint.setEnabled(True)
					self.btnFile.setEnabled(True)
					self.btnPrintSelected.setEnabled(True)
				else:
					self.btnControl.setEnabled(False)
					self.btnPrintSelected.setEnabled(False)
					self.btnPrint.setEnabled(True)
			else:
				self.btnPostConnect.setEnabled(True)
				self.btnControl.setEnabled(False)
				self.btnPrint.setEnabled(False)
				self.btnFile.setEnabled(False)
		else:
			self.labelState.setText("Error")
		#Try to get /api/job json data
		#If not None, update global variables, update GUI to reflect relevant values
		if apiKey is not None and serverAddr is not None:
			jobData = getJobData(apiKey, serverAddr)
		if jobData is not None:
			timeLeft = getTimeLeft(jobData)
			timeSpent = getTimeSpent(jobData)
			size = getSize(jobData)
			job = getJob(jobData)
			progress = getProgress(jobData)
			self.labelJob.setText(job)
			self.labelSize.setText(size)
			self.labelTimeLeft.setText(self.convMinSecStr(timeLeft))
			self.labelPrintTime.setText(self.convMinSecStr(timeSpent))
			self.printBar.setValue(progress)
		#Update printer temps and feeds from data
		if printerData is not None:
			headTemp = getHeadTemp(printerData)
			bedTemp = getBedTemp(printerData)
			self.numHead.display(headTemp)
			self.numBed.display(bedTemp)
		self.numFeed.display(feedRate)
		#self.tempHead.setValue(headTarget)
		#self.tempBed.setValue(bedTarget)

def main():
	app = QApplication(sys.argv)
	form = MainWindow()
	form.show()
	form.start()
	sys.exit(app.exec_())
 
if __name__ == "__main__":
	main()
