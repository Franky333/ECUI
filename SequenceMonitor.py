from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import json

from SequenceListItem import SequenceListItem

class SequenceMonitor(QWidget):

	def __init__(self, parent=None):
		super(SequenceMonitor, self).__init__(parent)

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

		hLayout = QHBoxLayout()
		hLayout.addWidget(loadButton)
		hLayout.addWidget(saveButton)

		header = QWidget()
		header.setLayout(hLayout)

		return header

	def createSeqList(self):

		# Create ListWidget and add 10 items to move around.
		listWidget = QListWidget()
		# Enable drag & drop ordering of items.
		listWidget.setDragDropMode(QAbstractItemView.InternalMove)
		listWidget.setStyleSheet("background-color: #323232; border-radius: 3px; height:30px")
		listWidget.setSizeAdjustPolicy(QListWidget.AdjustToContents)

		for x in range(1, 11):

			listWidgetItem = QListWidgetItem(listWidget)
			item = SequenceListItem("Item {:02d}".format(x), listWidgetItem)

			# Add QListWidgetItem into QListWidget
			listWidget.addItem(listWidgetItem)
			listWidget.setItemWidget(listWidgetItem, item)
			item.addProperty("Time", str(x*20), "us")
			item.addProperty("Time", str(x*20), "us")


			if x % 2 == 0:
				item.addProperty("Time", str(x*20), "us")

		vLayout = QVBoxLayout()
		vLayout.addWidget(listWidget)

		seqList = QWidget()
		seqList.setLayout(vLayout)
		seqList.setObjectName("seqList")

		return seqList

	def loadSequence(self):

		fname = QFileDialog.getOpenFileName(self, "Open file", ".", "*.seq")


		print(fname)


	def saveSequence(self):

		#TODO: implement
		sname = QFileDialog.getSaveFileName(self, "Save file", ".", "*.seq")

		print(sname)