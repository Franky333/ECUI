from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import json

from SequenceList import SequenceList
from SequenceListItem import SequenceListItem
from SequenceController import SequenceController

from enum import Enum


class SequenceExportMode(Enum):
	LEGACY = 1
	NEW = 2


class SequenceMonitor(QWidget):

	def __init__(self, parent=None):
		super(SequenceMonitor, self).__init__(parent)

		self.controller = SequenceController()
		self.parent = parent

		header = self.createHeader()
		seqList = self.createSeqList()

		vLayout = QVBoxLayout()
		vLayout.addWidget(header)
		vLayout.addWidget(seqList)

		self.setLayout(vLayout)

	def createHeader(self):

		loadButton = QPushButton("Load")
		loadButton.clicked.connect(self.loadSequence)

		saveButton = QPushButton("Save")
		saveButton.clicked.connect(self.saveSequence)


		exportComboBox = QComboBox()
		exportComboBox.setObjectName("exportComboBox")
		exportComboBox.addItem(SequenceExportMode.LEGACY.name)
		exportComboBox.addItem(SequenceExportMode.NEW.name)

		hLayout = QHBoxLayout()
		hLayout.addWidget(loadButton)
		hLayout.addWidget(saveButton)
		hLayout.addWidget(QLabel("Export Mode: "))
		hLayout.addWidget(exportComboBox)

		header = QWidget()
		header.setLayout(hLayout)

		return header

	def createSeqList(self):

		# Create ListWidget and add 10 items to move around.
		self.listWidget = SequenceList(self.updateController)
		# Enable drag & drop ordering of items.
		self.listWidget.setDragDropMode(QAbstractItemView.InternalMove)
		self.listWidget.setStyleSheet("background-color: #323232; border-radius: 3px; height:30px")
		self.listWidget.setSizeAdjustPolicy(QListWidget.AdjustToContents)

		#self.loadSequence()
		vLayout = QVBoxLayout()
		vLayout.addWidget(self.listWidget)

		seqList = QWidget()
		seqList.setLayout(vLayout)
		seqList.setObjectName("seqList")

		return seqList

	def loadSequence(self):

		self.listWidget.clear()

		#fname = QFileDialog.getOpenFileName(self, "Open file", QDir.currentPath(), "*.seq")
		fname = ["/Volumes/Data/markus/Programming/SpaceTeam/TXV_ECUI/sequences/test.seq", 'asdf']
		print(fname)

		with open(fname[0]) as jsonFile:
			self.controller.load(jsonFile.read())

		for entry in self.controller.getData():
			item = self.listWidget.createItem()
			item.addProperty("timestamp", str(entry["timestamp"]))
			for val in entry["actions"].keys():
				if val != "timestamp":
					item = self.listWidget.createItem()
					item.addProperty(str(val), str(entry["actions"][val]))

	def saveSequence(self):

		#TODO: implement
		sname = QFileDialog.getSaveFileName(self, "Save file", ".", "*.seq")

		mode = self.findChild(QComboBox, "exportComboBox").currentText()
		if mode == "LEGACY":
			self.controller.save(SequenceExportMode.LEGACY)
		elif mode == "NEW":
			self.controller.save(SequenceExportMode.NEW)

		print(sname)

	def updateController(self, timeBefore, timeAfter, currKey, currVal):

		print(timeBefore, timeAfter, currKey, currVal)
		self.controller.removeEntry(timeBefore, currKey, currVal)
		self.controller.addOrUpdateEntry(timeBefore, currKey, currVal)

