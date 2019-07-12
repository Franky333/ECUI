from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import json

from SequenceList import SequenceList
from SequenceListItem import SequenceListItem
from SequenceController import SequenceController

from utils import *

#TODO: update controller when changing globals and timstamps
class SequenceMonitor(QWidget):

	def __init__(self, parent=None):
		super(SequenceMonitor, self).__init__(parent)

		self.controller = SequenceController()
		self.parent = parent

		header = self.createHeader()
		seqList = self.createSeqList()

		#sequence Start
		top = QWidget()
		hLayout = QHBoxLayout()


		self.startSequenceButton = QPushButton("Start Sequence")
		self.startSequenceButton.setVisible(False)
		self.startSequenceButton.setStyleSheet("background-color: #E99B00; height: 60px; font-size: 40px;")
		self.startSequenceButton.clicked.connect(self._onStartSequence)

		print(self.startSequenceButton)
		self.countDownTimer = QLabel()
		self.countDownTimer.setVisible(False)
		self.countDownTimer.setStyleSheet("font-size: 40px; color: #E99B00")


		hLayout.addWidget(self.startSequenceButton)
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

		self.loadSequence("./sequences/new.seq")

	def openSequence(self, path=None):

		fname = QFileDialog.getOpenFileName(self, "Open file", QDir.currentPath(), "*.seq")
		#fname = ["/Volumes/Data/markus/Programming/SpaceTeam/TXV_ECUI/sequences/test.seq", 'asdf']
		print(fname)
		if fname[0] != "":
			self.loadSequence(fname[0])

	def loadSequence(self, path):
		self.listWidget.clear()

		self.listLayout.removeWidget(self.globals)
		self.globals = QWidget()
		self.globalsLayout = QGridLayout()
		self.globals.setLayout(self.globalsLayout)

		with open(path) as jsonFile:
			self.controller.load(jsonFile.read())

		#set addbutton visible
		self.addTimeButton.setVisible(True)
		self.addActionButton.setVisible(True)
		self.startSequenceButton.setVisible(True)

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

	def _onStartSequence(self):

		print("go!")
		self.timer = QTimer()
		self.timer

	def getStartTime(self):

		startTime = self.findChild(QLineEdit, "startTimeLineEdit")
		print(startTime.text())
		return float(startTime.text())

	def getEndTime(self):

		endTime = self.findChild(QLineEdit, "endTimeLineEdit")
		return float(endTime.text())