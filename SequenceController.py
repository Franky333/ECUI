import json

class SequenceController():

	def __init__(self, jsonData=None):

		if jsonData is not None:
			self.loadSequence(jsonData)


	def load(self, jsonFile):

		if self.isJson(jsonFile):

			self._jsonData = json.loads(jsonFile)
			self._globals = self._jsonData["globals"]
			self._data = self._jsonData["data"]

		else:
			raise ValueError("loadSequence: String not a valid JSON object")

	def save(self, exportMode):

		#TODO: implement
		print(exportMode.name)

	def removeEntry(self, timeBefore, currKey, currVal):
		pass

	def addEntry(self, timeBefore, currKey, currVal):
		pass

	#returns none if no json Data or invalid string entered in loadSequence
	def getJsonData(self):

		return self._jsonData

	def isJson(self, str):
		try:
			json.loads(str)
		except ValueError as e:
			return False
		return True

	def getData(self):

		return self._data