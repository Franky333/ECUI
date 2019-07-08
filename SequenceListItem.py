from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class SequenceListItem(QWidget):

	def __init__(self, objName=None, boundListItem=None, parent=None):
		super(SequenceListItem, self).__init__(parent)

		self.listItem = boundListItem

		if objName is not None:
			self.setObjectName(objName)

		self.setStyleSheet("background-color: #4F9CFF; border-radius: 3px;")

		self.vLayout = QVBoxLayout()
		self.l = QVBoxLayout()
		self.wi = QWidget()
		self.wi.setLayout(self.vLayout)

		self.l.addWidget(self.wi)
		self.setLayout(self.l)

		self.updateGeometry()

		self.properties = {}

	def addProperty(self, key, value, unit=''):

		self.properties[key] = [value, unit]
		self.vLayout.addWidget(QLineEdit(key + ": " + value + " " + unit))
		print(self.wi.sizeHint())

		self.updateGeometry()
		self.listItem.setSizeHint(self.sizeHint())

	def sizeHint(self):

		return self.wi.sizeHint()
