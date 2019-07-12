from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from utils import Utils

class SequenceListItem(QWidget):

	def __init__(self, id, updateCallback=None, updateCallbackTimestep=None, boundListItem=None, objName=None, parent=None):

		super(SequenceListItem, self).__init__(parent)

		self.updateCallback = updateCallback
		self.updateCallbackTimestep = updateCallbackTimestep

		self.parent = parent

		self.listItem = boundListItem
		self.id = id

		if objName is not None:
			self.setObjectName(objName)

		self.setStyleSheet("border-radius: 3px;")

		self.hLayout = QHBoxLayout()
		self.l = QVBoxLayout()
		self.wi = QWidget()
		self.wi.setLayout(self.hLayout)
		self.l.addWidget(self.wi)
		self.setLayout(self.l)

		self.updateGeometry()

		self.properties = {}

		self._theme = {"timestamp": "#4F9CFF", "actions": "#6EAF6E"}

	def getItemWidget(self):

		return self.listItem

	#TODO: fix rescale when loading sequences (sizehint)
	def addProperty(self, key, value, unit=""):

		if key == "timestamp":
			backColor = self._theme["timestamp"]
			keyEnabled = False
			self.isTimestamp = True
		else:
			backColor = self._theme["actions"]
			keyEnabled = True
			self.isTimestamp = False

		self.setStyleSheet(self.styleSheet() + "background-color: " + backColor)
		self._prevKey = key

		self.properties[key] = [value, unit]
		keyLineEdit = QLineEdit(str(key))
		keyLineEdit.setObjectName("keyLineEdit" + str(self.id))
		keyLineEdit.textChanged.connect(lambda e: self._onKeyChanged(e, keyLineEdit))
		keyLineEdit.editingFinished.connect(lambda: self._onKeyFinished(keyLineEdit.objectName()))
		self.hLayout.addWidget(keyLineEdit)
		self.hLayout.addWidget(QLabel(": "))
		valLineEdit = QLineEdit()
		valLineEdit.setText(str(value))
		validator = QDoubleValidator()
		validator.setDecimals(2)
		valLineEdit.setValidator(validator)
		valLineEdit.textChanged.connect(lambda e: self._onValueChanged(e, valLineEdit))
		valLineEdit.setObjectName("valLineEdit" + str(self.id))
		valLineEdit.editingFinished.connect(lambda: self._onValueFinished(valLineEdit.objectName()))
		self.hLayout.addWidget(valLineEdit)
		if unit != "":
			self.hLayout.addWidget(QLabel(str(unit)))
		self.hLayout.addStretch()

		# print(self.wi.sizeHint())

		self.hLayout.update()
		self.wi.setLayout(self.hLayout)

		# print(self.hLayout.sizeHint())
		# print(self.wi.sizeHint())
		# print("=======")
		self.adjustSize()

		if self.listItem is not None:
			self.listItem.setSizeHint(QSize(self.sizeHint().width(), self.sizeHint().height()+40))

	def sizeHint(self):

		return self.wi.sizeHint()

	def dropEvent(self, e):

		print(self)

	#Basic fuctionality for timestep change implemented SequenceList and Monitor as well as Controller
	#need to be implemented
	def _onValueFinished(self, e):

		valLine = self.findChild(QLineEdit, e)
		keyLine = self.findChild(QLineEdit, e.replace("val", "key"))

		val = valLine.text()
		key = keyLine.text()

		val, succ = Utils.tryParseFloat(val)
		val, succ = Utils.tryParseInt(val)

		oldVal = self.properties[key][0]
		if "timestamp" in self.properties.keys():
			if val != "START" and val != "END":
				valid = self.parent.isValidTimestamp(val)
				if valid == 0:
					if isinstance(self.properties[key], list):
						self.properties[key] = [val, self.properties[key][1]]
					else:
						self.properties[key] = [val, '']

					if self.updateCallbackTimestep is not None and self.listItem is not None:
						self.updateCallbackTimestep(self.listItem, oldVal, val)
				elif valid < 0:
					print("invalid timestamp, value is smaller than START")
					valLine.setText(oldVal)
				else:
					print("invalid timestamp, value is greater than END")
					valLine.setText(oldVal)
		else:
			if isinstance(self.properties[key], list):
				self.properties[key] = [val, self.properties[key][1]]
			else:
				self.properties[key] = [val, '']

			if self.updateCallback is not None and self.listItem is not None:
				self.updateCallback(self.listItem, key, val)

	def _onKeyFinished(self, e):

		print(e)
		keyLine = self.findChild(QLineEdit, e)
		valLine = self.findChild(QLineEdit, e.replace("key", "val"))

		val = valLine.text()
		key = keyLine.text()

		val, succ = Utils.tryParseFloat(val)
		val, succ = Utils.tryParseInt(val)
		if "timestamp" not in self.properties.keys():

			del self.properties[self._prevKey]
			self.properties[key] = [val, '']

			if self.updateCallback is not None and self.listItem is not None:
				self.updateCallback(self.listItem, key, val, True, self._prevKey)

			self._prevKey = key

	def _onValueChanged(self, e, valLine):

		self._currValChange = e
		if "timestamp" in self.properties.keys():
			if "START" in self.properties["timestamp"]:
				print("START may not be changed")
				valLine.setText("START")
			elif "END" in self.properties["timestamp"]:
				print("END may not be changed")
				valLine.setText("END")

	def _onKeyChanged(self, e, keyLine):

		print(e)

		if "timestamp" in self.properties.keys():
			print("timestamp key may not be changed")
			keyLine.setText("timestamp")