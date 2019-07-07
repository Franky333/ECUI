from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class SequenceMonitor(QWidget):

	def __init__(self, parent=None):
		super(SequenceMonitor, self).__init__(parent)

		header = self.createHeader()

		hLayout = QHBoxLayout()
		hLayout.addWidget(header)

		self.setLayout(hLayout)

	def createHeader(self):

		loadButton = QPushButton("Load")
		loadButton.clicked.connect(self.loadSequence)



		vLayout = QVBoxLayout()
		vLayout.addWidget(loadButton)

		header = QWidget()
		header.setLayout(vLayout)

		return header


	def loadSequence(self):

		fname = QFileDialog.getOpenFileName(self, 'Open file', '.', "*.py")

		print(fname)