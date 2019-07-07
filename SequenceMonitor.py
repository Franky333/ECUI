from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

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

		vLayout = QVBoxLayout()

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