from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from SequenceListItem import SequenceListItem
from utils import Utils

class SequenceList(QListWidget):

	def __init__(self, updateCallback=None, boundListItem=None, objName=None, parent=None):
		super(SequenceList, self).__init__(parent)

		self.parent = parent

		self.__nextItemId = 0

		self.updateCallback = updateCallback


	def dragMoveEvent(self, event):
		if event.mimeData().hasUrls():
			event.setDropAction(Qt.CopyAction)
			event.accept()

		else:
			super(SequenceList, self).dragMoveEvent(event)


	#TODO: check if item is timestamp and process accordingly
	def dropEvent(self, event):
		print('dropEvent')

		name = event.source();

		indBefore = name.currentRow()

		event.setDropAction(Qt.CopyAction)
		super(SequenceList, self).dropEvent(event)

		indAfter = name.currentRow()

		dropItemProperties = self.itemWidget(self.item(indAfter)).properties
		if "timestamp" in dropItemProperties.keys():
			#TODO: process timestamp movement accordingly
			pass
		else:
			if self.updateCallback is not None:
				if indBefore > indAfter:
					timeBefore, valBefore = self.getCorrespondingTimestampItem(indBefore)
					timeAfter, valAfter = self.getCorrespondingTimestampItem(indAfter)
				else:
					timeBefore, valBefore = self.getCorrespondingTimestampItem(indBefore-1)
					timeAfter, valAfter = self.getCorrespondingTimestampItem(indAfter-1)


				if timeAfter is not None:

					if timeBefore is not None:
						valBefore, succ = Utils.tryParseFloat(valBefore)
					else:
						valBefore = "START"
					valAfter, succ = Utils.tryParseFloat(valAfter)

					for currKey, currVal in dropItemProperties.items():

						self.updateCallback(currKey, currVal[0], valAfter, valBefore)




	def createItem(self, objName=None, index=None):


		listWidgetItem = QListWidgetItem()
		item = SequenceListItem(self.__getNextId(), self.onListItemChanged, listWidgetItem, objName, self)

		# Add QListWidgetItem into QListWidget
		if index is None:
			self.addItem(listWidgetItem)
		else:
			print(index)
			self.insertItem(index, listWidgetItem)
		self.setItemWidget(listWidgetItem, item)

		return item



	def __getNextId(self):

		next = self.__nextItemId
		self.__nextItemId += 1
		return next

	def getCorrespondingTimestampItem(self, index):

		item = None
		value = None
		for x in range(index, -1, -1):

			#additional for loop condition
			if item is not None:
				break

			currItem = self.itemWidget(self.item(x))
			if "timestamp" in currItem.properties:
				item = currItem
				value = currItem.properties["timestamp"][0]
		if item is None:
			value = "START"
		return item, value

	def onListItemChanged(self, item, key, val, removeOld=False, oldKey=None):

		index = self.row(item)
		print(index)
		timeItem, time = self.getCorrespondingTimestampItem(index)
		time, succ = Utils.tryParseFloat(time)
		print(timeItem, time)
		self.updateCallback(key, val, time, None, removeOld, oldKey)

	def keyPressEvent(self, event):

		if type(event) == QKeyEvent:
			if event.key() == Qt.Key_Backspace:
				event.accept()
				self._removeSel()
		else:
			event.ignore()

	def _removeSel(self):
		listItems = self.selectedItems()
		if not listItems: return
		for item in listItems:
			controller = self.parent.getController()

			index = self.row(item)
			print(index)
			timeItem, time = self.getCorrespondingTimestampItem(index)
			time, succ = Utils.tryParseFloat(time)
			key, val = self._getProperty(item)
			self.updateCallback(key, val, None, time)

			self.takeItem(self.row(item))

	def _getProperty(self, item):

		seqItem = self.itemWidget(item)

		lineEdits = seqItem.findChildren(QLineEdit)

		for line in lineEdits:
			if "keyLineEdit" in line.objectName():
				key = line.text()
			elif "valLineEdit" in line.objectName():
				val = line.text()

		return key, val