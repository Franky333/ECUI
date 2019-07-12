from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from SequenceListItem import SequenceListItem
from utils import Utils

class SequenceList(QListWidget):

	def __init__(self, updateCallback=None, updateCallbackTimestamp=None, boundListItem=None, objName=None, parent=None):
		super(SequenceList, self).__init__(parent)

		self.parent = parent

		self.__nextItemId = 0
		self._timestampList = []

		self.updateCallback = updateCallback

		self.updateCallbackTimestamp = updateCallbackTimestamp


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

									#TODO: OPTIONAL: implement timestamp drag
									# event.setDropAction(Qt.CopyAction)
									# super(SequenceList, self).dropEvent(event)
									#
									# indAfter = name.currentRow()
									#
									# if indBefore > indAfter:
									# 	updateController(self, currKey, currVal, timeAfter, timeBefore=None, removeOld=False, oldKey=None)

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

		timeVal = time


		if index is None:
			self._timestampList.append([self.count(), timeVal])
		else:
			#EDIT: element can still be inserted after END timestamp (maybe fix)
			print("before", self._timestampList)
			self._timestampList.append([index, timeVal])
			self._timestampList.sort(key=lambda val: (val[0], val[1]))


		item = self.createItem("timestamp", time, objName, index)

		return item

	def setTimeStart(self, start):

		self._timestampList[0][1] = start

	def setTimeEnd(self, end):

		self._timestampList[len(self._timestampList)-1][1] = end

	def createItem(self, key, val, objName=None, index=None):


		listWidgetItem = QListWidgetItem()
		item = SequenceListItem(self.__getNextId(), self.onListItemChanged, self.onListItemChangedTimestep, listWidgetItem, objName, self)

		# Add QListWidgetItem into QListWidget
		if index is None:
			self.addItem(listWidgetItem)
		else:
			print(index)
			self.insertItem(index, listWidgetItem)
		self.setItemWidget(listWidgetItem, item)

		item.addProperty(key, val)

		if index is not None:
			self._updateTimestampList(self.count()-1, index)
			print("after", self._timestampList)

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

	def onListItemChangedTimestep(self, item, oldVal, newVal):

		#TODO: not implemented yet (optional)
		pass

	def onListItemChanged(self, item, key, val, removeOld=False, oldKey=None):

		print(key)
		index = self.row(item)
		print(index)
		timeItem, time = self.getCorrespondingTimestampItem(index)
		time, succ = Utils.tryParseFloat(time)
		print(timeItem, time)
		self.updateCallback(key, val, time, None, removeOld, oldKey)

	def isValidTimestamp(self, val):

		if self.parent.getStartTime() > val:
			return -1
		elif self.parent.getEndTime() < val:
			return 1
		else:
			return 0

	def keyPressEvent(self, event):

		if type(event) == QKeyEvent:
			if event.key() == Qt.Key_Backspace:
				event.accept()
				self._removeSel()
		else:
			event.ignore()

	def _removeSel(self):
		listItems = self.selectedItems()
		if not listItems:
			return
		for item in listItems:

			key, val = self._getProperty(item)
			val, succ = Utils.tryParseFloat(val)
			val, succ = Utils.tryParseInt(val)

			index = self.row(item)
			if key == "timestamp":
				timestampListIndex = self._getTimestampListIndex(val, 1)
				timeBefore = self._timestampList[timestampListIndex][1]
				index = self._timestampList[timestampListIndex][0]
				startIndex = index
				endIndex = self._timestampList[timestampListIndex+1][0]-1
				timeAfter = self._timestampList[timestampListIndex-1][1]
				self.takeItem(self.row(item))
				for i in range(startIndex, endIndex):

					actionKey, actionVal = self._getProperty(self.item(i))
					actionVal, succ = Utils.tryParseFloat(actionVal)
					actionVal, succ = Utils.tryParseInt(actionVal)

					print(actionKey, actionVal)
					self.updateCallback(actionKey, actionVal, timeAfter, timeBefore)
				self._timestampList.pop(timestampListIndex)
				self.updateCallbackTimestamp(timeBefore)

			else:

				timeItem, time = self.getCorrespondingTimestampItem(index)
				time, succ = Utils.tryParseFloat(time)
				self.updateCallback(key, val, None, time)
				self.takeItem(self.row(item))

			self._updateTimestampList(self.count()-1, index)

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

		return timestampList.sort(key=lambda val : val[0])

	def _getTimestampListIndex(self, val, indexOfValueInList=0):

		counter = 0
		for timestamp in self._timestampList:
			if val == timestamp[indexOfValueInList]:
				break
			else:
				counter += 1
		return counter

	def _convertTime(self, time):

		timeVal = time
		if time == "START":
			timeVal = self.parent.getStartTime()
		elif time == "END":
			timeVal = self.parent.getEndTime()

		return timeVal

	def _updateTimestampList(self, fromIndex, toIndex):

		for x in range(fromIndex, toIndex-1, -1):

			currItem = self.itemWidget(self.item(x))
			if "timestamp" in currItem.properties:

				value = currItem.properties["timestamp"][0]
				print(value)
				timestampListInd = self._getTimestampListIndex(value, 1)
				print(self.row(currItem.listItem))
				print(x)
				self._timestampList[timestampListInd][0] = x

	def getTimestampSlot(self, val):

		index = stampIndex = -1
		low = 0
		high = len(self._timestampList)-1

		while low <= high:

			mid = int((low + high) / 2)
			midEntry = self._timestampList[mid][1]
			midp1Entry = self._timestampList[mid+1][1]

			midEntry = self._convertTime(midEntry)
			midp1Entry = self._convertTime(midp1Entry)

			if midEntry < val and val <= midp1Entry:

				index = self._timestampList[mid+1][0]
				stampIndex = mid+1
				break

			elif midEntry < val:
				low = mid + 1
			elif midEntry >= val:
				high = mid - 1

		return index, stampIndex

	def timestampExists(self, val):

		exists = False
		for timestamp in self._timestampList:
			if val == timestamp[1]:
				exists = True
				break
		return exists