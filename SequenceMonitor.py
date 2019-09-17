from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import json

from hedgehog.client import connect
from contextlib import ExitStack
from SimulatedHedgehog import SimulatedHedgehog

from Igniter import Igniter
from Servo import Servo
from PressureSensor import PressureSensor
from TemperatureSensor import TemperatureSensor

from SequenceList import SequenceList
from SequenceListItem import SequenceListItem
from SequenceController import SequenceController
from CountdownTimer import CountdownTimer

from utils import *

#TODO: update controller when changing globals and timstamps
class SequenceMonitor(QWidget):

	def __init__(self, parent=None):
		super(SequenceMonitor, self).__init__(parent)

		# Hedgehog
		#self.stack = ExitStack()
		#self.hedgehog = self.stack.enter_context(connect(endpoint='tcp://raspberrypi.local:10789'))  # FIXME

		# Simulated Hedgehog
		self.hedgehog = SimulatedHedgehog()

		# Actuators and Sensors
		self.servo_fuel = Servo(name='fuel', hedgehog=self.hedgehog, servoPort=0, feedbackPort=0)
		self.servo_oxidizer = Servo(name='oxidizer', hedgehog=self.hedgehog, servoPort=1, feedbackPort=1)
		self.igniter_arc = Igniter(name='arc', hedgehog=self.hedgehog, igniterPort=0)
		self.igniter_pyro = Igniter(name='pyro', hedgehog=self.hedgehog, igniterPort=1, feedbackPort=7)
		self.pressureSensor_fuel = PressureSensor(name='fuel', hedgehog=self.hedgehog, port=2)
		self.pressureSensor_oxidizer = PressureSensor(name='oxidizer', hedgehog=self.hedgehog, port=3)
		self.pressureSensor_chamber = PressureSensor(name='chamber', hedgehog=self.hedgehog, port=4)
		self.temperatureSensor_chamber = TemperatureSensor(name='chamber', hedgehog=self.hedgehog, port=8)


		self.controller = SequenceController()
		self.parent = parent

		header = self.createHeader()
		seqList = self.createSeqList()

		#sequence Start
		top = QWidget()
		hLayout = QHBoxLayout()


		self.toggleSequenceButton = QPushButton("Start Sequence")
		self.toggleSequenceButton.setVisible(False)
		self.toggleSequenceButton.setStyleSheet("background-color: #E99B00; height: 60px; font-size: 40px;")
		self.toggleSequenceButton.clicked.connect(self._onToggleSequence)


		self.countDownTimer = QLabel()
		self.countDownTimer.setVisible(False)
		self.countDownTimer.setStyleSheet("font-size: 40px; color: #E99B00")
		self.isSequenceStarted = False

		hLayout.addWidget(self.toggleSequenceButton)
		hLayout.addStretch(2)
		hLayout.addWidget(self.countDownTimer)

		top.setLayout(hLayout)

		vLayout = QVBoxLayout()
		vLayout.addWidget(top)
		vLayout.addWidget(header)
		vLayout.addWidget(seqList)

		self.setLayout(vLayout)

	def createHeader(self):

		newButton = QPushButton("New")
		newButton.clicked.connect(self.newSequence)

		openButton = QPushButton("Open")
		openButton.clicked.connect(self.openSequence)

		saveButton = QPushButton("Save")
		saveButton.clicked.connect(self.saveSequence)


		exportComboBox = QComboBox()
		exportComboBox.setObjectName("exportComboBox")
		exportComboBox.addItem(SequenceExportMode.LEGACY.name)
		exportComboBox.addItem(SequenceExportMode.NEW.name)
		exportComboBox.setCurrentIndex(1)

		hLayout = QHBoxLayout()
		hLayout.addWidget(newButton)
		hLayout.addWidget(openButton)
		hLayout.addWidget(saveButton)
		hLayout.addWidget(QLabel("Export Mode: "))
		hLayout.addWidget(exportComboBox)

		header = QWidget()
		header.setLayout(hLayout)

		return header

	def createSeqList(self):

		# Create ListWidget and add 10 items to move around.
		self.listWidget = SequenceList(self.updateController, self.removeControllerTimestamp, None, None, self)
		# Enable drag & drop ordering of items.
		self.listWidget.setDragDropMode(QAbstractItemView.InternalMove)
		self.listWidget.setStyleSheet("background-color: #323232; border-radius: 3px; height:30px")
		self.listWidget.setSizeAdjustPolicy(QListWidget.AdjustToContents)

		#layout for globals
		self.globals = QWidget()
		self.globalsLayout = QGridLayout()
		self.globals.setLayout(self.globalsLayout)


		self.addTimeButton = QPushButton("Add timestamp")
		self.addTimeButton.setVisible(False)
		self.addTimeButton.clicked.connect(self._onAddTimestampItem)

		self.addActionButton = QPushButton("Add action")
		self.addActionButton.setVisible(False)
		self.addActionButton.clicked.connect(self._onAddActionItem)

		#layout for seqList section
		self.listLayout = QVBoxLayout()
		self.listLayout.addWidget(self.addTimeButton)
		self.listLayout.addWidget(self.addActionButton)
		self.listLayout.addWidget(self.listWidget)
		self.listLayout.insertWidget(0, self.globals)


		seqList = QWidget()
		seqList.setLayout(self.listLayout)
		seqList.setObjectName("seqList")

		return seqList

	#TODO: delete globals section when loading new file
	def loadSeqGlobals(self):

		counter = 0
		line = 0
		globs = self.controller.getGlobals()
		for glob in globs:

			entry = globs[glob]
			if isinstance(entry, list):

				if len(entry) == 2:
					if counter % 2 != 0:
						counter += 1
						line += 1
					self._createGlobalElement("min" + glob[0].upper() + glob[1:], entry[0], line, counter)
					self._createGlobalElement("max" + glob[0].upper() + glob[1:], entry[1], line, counter+2)
					counter = 0
					line += 1
				else:
					print("globals of length" + len(entry) + "are not supported yet")

			else:
				print(glob, counter)
				self._createGlobalElement(glob, entry, line, counter)
				counter += 2
				if counter % 4 == 0:
					line += 1
					counter = 0

	def _createGlobalElement(self, name, val, row, col):

		currLable = QLabel(name + ":")
		currLine = QLineEdit()

		if isinstance(val, (int, float)):
			val = str(val)
		currLine.setText(val)
		currLine.setValidator(QDoubleValidator())
		currLine.setObjectName(name + "LineEdit")
		currLine.textChanged.connect(self._onGlobalChanged)
		currLine.editingFinished.connect(lambda: self._onGlobalFinished(currLable, currLine))

		self.globalsLayout.addWidget(currLable, row, col)
		self.globalsLayout.addWidget(currLine, row, col+1)


	def newSequence(self):

		self.loadSequence("./sequences/test.seq")

	def openSequence(self, path=None):

		fname = QFileDialog.getOpenFileName(self, "Open file", QDir.currentPath(), "*.seq")
		#fname = ["/Volumes/Data/markus/Programming/SpaceTeam/TXV_ECUI/sequences/test.seq", 'asdf']
		print(fname)
		if fname[0] != "":
			self.loadSequence(fname[0])

	def loadSequence(self, path):
		self.listWidget.clear()

		self.listLayout.removeWidget(self.globals)

		import sip
		self.globalsLayout.removeWidget(self.globals)
		sip.delete(self.globals)
		self.globals = None
		#self.globalsLayout.setParent(None)

		self.globals = QWidget()
		self.globalsLayout = QGridLayout()
		self.globals.setLayout(self.globalsLayout)

		with open(path) as jsonFile:
			self.controller.load(jsonFile.read())

		#set addbutton visible
		self.addTimeButton.setVisible(True)
		self.addActionButton.setVisible(True)
		self.toggleSequenceButton.setVisible(True)

		#globals
		self.loadSeqGlobals()
		self.listLayout.insertWidget(0, self.globals)

		startTime = self.getStartTime()
		self.countDownTimer.setText(str(startTime))
		self.countDownTimer.setVisible(True)

		#data
		for entry in self.controller.getData():
			time = entry["timestamp"]
			#TODO: implement static START timestamp
			# if time == "START":
			# 	item = SequenceListItem('', None, None, None, self)
			# 	self.listLayout.insertWidget(0, item)
			# else:
			item = self.listWidget.createTimestampItem(time)

			for val in entry["actions"].keys():
				if val != "timestamp":
					item = self.listWidget.createItem(str(val), str(entry["actions"][val]))


	#NOTE: legacy export fule and oxidizer file names are hardcoded!!!
	def saveSequence(self):

		import re

		mode = self.findChild(QComboBox, "exportComboBox").currentText()
		if mode == "LEGACY":

			#sname = QFileDialog.getSaveFileName(self, "Save file", QDir.currentPath(), "*.json")
			sname = ["/Volumes/Data/markus/Programming/SpaceTeam/TXV_ECUI/sequences/asdf.json", 'asdf']

			jsonStr = self.controller.exportJson(SequenceExportMode.LEGACY)
			servoFuelStr, servoOxStr = self.controller.exportAdditionalLegacyFiles()
			dir = re.sub(r"[^/]*\.json", "", sname[0])

			fuelFile = dir + "servo_fuel.json"
			oxFile = dir + "servo_oxidizer.json"
			seqFile = sname[0]

			self._writeToFile(fuelFile, servoFuelStr)
			self._writeToFile(oxFile, servoOxStr)
			self._writeToFile(seqFile, jsonStr)

			print("Wrote Sequence in LEGACY mode to: ")
			print("\t" + fuelFile)
			print("\t" + oxFile)
			print("\t" + seqFile)

		elif mode == "NEW":

			#sname = QFileDialog.getSaveFileName(self, "Save file", QDir.currentPath(), "*.seq")
			sname = ["/Volumes/Data/markus/Programming/SpaceTeam/TXV_ECUI/sequences/asdf.seq", 'asdf']

			jsonStr = self.controller.exportJson(SequenceExportMode.NEW)
			self._writeToFile(sname[0], jsonStr)
			print("Wrote Sequence in NEW mode to: ")
			print("\t" + sname[0])

	def _writeToFile(self, path, data):

		with open(path, "w") as textFile:
			textFile.write(data)


	def updateController(self, currKey, currVal, timeAfter, timeBefore=None, removeOld=False, oldKey=None):

		currVal, succ = Utils.tryParseFloat(currVal)
		currVal, succ = Utils.tryParseInt(currVal)
		if removeOld:
			self.controller.removeEntry(timeAfter, oldKey)
		if timeBefore is not None:
			self.controller.removeEntry(timeBefore, currKey)

		if timeAfter is not None:
			self.controller.addOrUpdateEntry(timeAfter, currKey, currVal)

	def removeControllerTimestamp(self, timestamp):

		print("remove Timestep")
		self.controller.removeTimestamp(timestamp)


	def updateGlobal(self, currKey, currVal):

		currVal, succ = Utils.tryParseFloat(currVal)
		currVal, succ = Utils.tryParseInt(currVal)
		self.controller.updateGlobal(currKey, currVal)
		if "startTime" in currKey:
			self.listWidget.setTimeStart(currVal)
			self.countDownTimer.setText(str(currVal))
		elif "endTime" in currKey:
			self.listWidget.setTimeEnd(currVal)

	def getController(self):

		return self.controller

	def _onGlobalFinished(self, lable, line):

		self.updateGlobal(lable.text(), line.text())

	def _onGlobalChanged(self, e):

		self._currValChange = e

	def _onAddTimestampItem(self, e):

		val, okPressed = QInputDialog.getDouble(self, "new Timestamp", "Value:", 0, self.getStartTime(), self.getEndTime(), 2)
		if okPressed:
			print(val)
			if self.listWidget.timestampExists(val):
				print("can't add timestamp, already existing")
			else:
				slot, stampInd = self.listWidget.getTimestampSlot(val)
				item = self.listWidget.createTimestampItem(val, None, slot)
				self.controller.addTimestamp(stampInd, val)

	def _onAddActionItem(self, e):

		item = self.listWidget.createItem("newAction", 0, None, 1)

	def _onToggleSequence(self):

		print(self.getStartTime(), self.getEndTime())
		if not self.isSequenceStarted:
			self.isSequenceStarted = True
			self.toggleSequenceButton.setText("Abort Sequence")
			self.timer = CountdownTimer(self._countdownEvent, self.getStartTime(), 0.1)
			self.timer.start()
			self.servo_fuel.enable()
			self.servo_oxidizer.enable()
		else:
			self.isSequenceStarted = False
			self._resetTimer()

	def _countdownEvent(self):

		time = self.timer.getTime()
		self.listWidget.highlightTimestamp(time)
		self.countDownTimer.setText(str(time))

		if time >= self.getEndTime():
			self._resetTimer()
		else:
			timestamp = self.listWidget.getTimestampSlot(time)
			self._execActions(timestamp)

	def _execActions(self, timestamp):

		for entry in self.controller.getData():
			currTimestamp = entry["timestamp"]
			
			if currTimestamp == timestamp:
				actions = entry["actions"]
				if "fuel" in actions:
					self.servo_fuel.setPositionTargetPercent(actions["fuel"])
				if "oxidizer" in actions:
					self.servo_oxidizer.setPositionTargetPercent(actions["oxidizer"])
				if "igniter" in actions:
					self.igniter_arc.set(actions["igniter"])
					self.igniter_pyro.set(actions["igniter"])

	def _resetTimer(self):
		self.timer.stop()
		self.timer.reset()
		startTime = self.getStartTime()
		self.toggleSequenceButton.setText("Start Sequence")
		self.countDownTimer.setText(str(startTime))
		self.isSequenceStarted = False


	def getStartTime(self):

		startTime = self.findChild(QLineEdit, "startTimeLineEdit")
		print(startTime.text())
		return float(startTime.text())

	def getEndTime(self):

		endTime = self.findChild(QLineEdit, "endTimeLineEdit")
		return float(endTime.text())