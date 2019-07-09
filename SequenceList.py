from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from SequenceListItem import SequenceListItem

class SequenceList(QListWidget):

	def __init__(self, dropCallback=None, boundListItem=None, objName=None, parent=None):
		super(SequenceList, self).__init__(parent)

		self.__nextItemId = 0

		self.dropCallback = dropCallback


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

		if self.dropCallback is not None:
			if indBefore > indAfter:
				timeBefore, valBefore = self.getCorrespondingTimestampItem(indBefore)
				timeAfter, valAfter = self.getCorrespondingTimestampItem(indAfter)
			else:
				timeBefore, valBefore = self.getCorrespondingTimestampItem(indBefore-1)
				timeAfter, valAfter = self.getCorrespondingTimestampItem(indAfter-1)


			dropItemProperties = self.itemWidget(self.item(indAfter)).properties
			currKey = list(dropItemProperties.keys())[0]
			currVal = dropItemProperties[currKey][0]

			if timeBefore is not None and timeAfter is not None:
				self.dropCallback(valBefore, valAfter, currKey, currVal)



	def createItem(self, objName=None):


		listWidgetItem = QListWidgetItem(self)
		item = SequenceListItem(self.__getNextId(), listWidgetItem, objName, self)

		# Add QListWidgetItem into QListWidget
		self.addItem(listWidgetItem)
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

		return item, value