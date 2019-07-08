from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class SequenceListItem(QWidget):

	def __init__(self, boundListItem=None, objName=None, parent=None):
		super(SequenceListItem, self).__init__(parent)

		self.listItem = boundListItem

		if objName is not None:
			self.setObjectName(objName)

		self.setStyleSheet("background-color: #4F9CFF; border-radius: 3px;")

		self.hLayout = QHBoxLayout()
		self.l = QVBoxLayout()
		self.wi = QWidget()
		self.wi.setLayout(self.hLayout)
		self.l.addWidget(self.wi)
		self.setLayout(self.l)

		self.updateGeometry()

		self.properties = {}

	#TODO: fix rescale when loading sequences (sizehint)
	def addProperty(self, key, value, unit=""):

		self.properties[key] = [value, unit]
		self.hLayout.addWidget(QLineEdit(str(key)))
		self.hLayout.addWidget(QLabel(": "))
		self.hLayout.addWidget(QLineEdit(str(value)))
		if unit != "":
			self.hLayout.addWidget(QLabel(str(unit)))
		self.hLayout.addStretch()

		print(self.wi.sizeHint())

		self.hLayout.update()
		self.wi.setLayout(self.hLayout)

		print(self.hLayout.sizeHint())
		print(self.wi.sizeHint())
		print("=======")
		self.adjustSize()
		self.listItem.setSizeHint(QSize(self.sizeHint().width(), self.sizeHint().height()+40))

	def sizeHint(self):

		return self.wi.sizeHint()
