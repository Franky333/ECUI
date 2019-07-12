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
		self._timestampList = []

		self.updateCallback = updateCallback


	def dragMoveEvent(self, event):
		if event.mimeData().hasUrls():
			event.setDropAction(Qt.CopyAction)
			event.accept()

		else:
			super(SequenceList, self).dragMoveEvent(event)


	def dropEvent(self, event):

		name = event.source();

		indBefore = name.currentRow()

		dropItemProperties = self.itemWidget(self.item(indBefore)).properties
		for val in dropItemProperties.values():
			if "START" in val:
				print("dragging START is invalid")
				pass
			else:

				indexToInsert = self.indexAt(event.pos()).row()
				if indexToInsert == 0:
					print("drop before START invalid")
				else:

					if "timestamp" in dropItemProperties.keys():
						if "END" in val and (indexToInsert < self._timestampList[len(self._timestampList)-2][0]):
							print("dropping END before any other timestamp is invalid")
						else:

							if indexToInsert >= self._timestampList[len(self._timestampList)-1][0]:
								print("dropping timestamp after END is invalid")
							else:
								print("timestamp")

								timestampInd = self._getTimestampListIndex(indBefore)
								print(timestampInd, self._timestampList[timestampInd-1][0], self._timestampList[timestampInd+1][0])
								if indexToInsert > self._timestampList[timestampInd-1][0] and indexToInsert+1 <= self._timestampList[timestampInd+1][0]:
									print("drop valid")

								else:
									print("drop invalid")


					else:

						event.setDropAction(Qt.CopyAction)
						super(SequenceList, self).dropEvent(event)

						indAfter = name.currentRow()

						dropItemProperties = self.itemWidget(self.item(indAfter)).properties

						if self.updateCallback is not None:

							print("before: ", self._timestampList)
							if indBefore > indAfter:
								timeBefore, valBefore = self.getCorrespondingTimestampItem(indBefore)
								timeAfter, valAfter = self.getCorrespondingTimestampItem(indAfter)
								self._updateTimestampList(indBefore, indAfter)
							else:
								timeBefore, valBefore = self.getCorrespondingTimestampItem(indBefore-1)
								timeAfter, valAfter = self.getCorrespondingTimestampItem(indAfter-1)
								self._updateTimestampList(indAfter, indBefore)
							print("after: ", self._timestampList)

							if timeAfter is not None:

								if timeBefore is not None:
									valBefore, succ = Utils.tryParseFloat(valBefore)
								else:
									valBefore = "START"
								valAfter, succ = Utils.tryParseFloat(valAfter)

								for currKey, currVal in dropItemProperties.items():

									self.updateCallback(currKey, currVal[0], valAfter, valBefore)


	def createTimestampItem(self, time, objName=None, index=None):

		if index is None:
			self._timestampList.append([self.count(), time])
		else:
			#EDIT: element can still be inserted after END timestamp (maybe fix)
			self._timestampList.append([index, time])
			self._timestampList = self._timestampListSort(self._timestampList)

		item = self.createItem(objName, index)

		item.addProperty("timestamp", time)

		return item

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

	#can be optimized with binary search and self._timestampList
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

		print(key)
		if key == "timestamp":
			print("time")
		else:
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

	def _timestampListSort(self, timestampList):

		timestampList.sort(key = lambda val : val[0])

	def _getTimestampListIndex(self, val, indexOfValueInList=0):

		counter = 0
		for timestamp in self._timestampList:
			if val == timestamp[indexOfValueInList]:
				break
			else:
				counter += 1
		return counter

	def _updateTimestampList(self, fromIndex, toIndex):

		for x in range(fromIndex, toIndex, -1):

			currItem = self.itemWidget(self.item(x))
			if "timestamp" in currItem.properties:

				value = currItem.properties["timestamp"][0]
				timestampListInd = self._getTimestampListIndex(value, 1)
				self._timestampList[timestampListInd][0] = x