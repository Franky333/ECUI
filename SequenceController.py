import json

class SequenceController():

	def __init__(self, jsonData=None):

		if jsonData is not None:
			self.loadSequence(jsonData)


	def load(self, jsonFile):

		if self.isJson(jsonFile):

			jsonData = json.loads(jsonFile)
			self._globals = jsonData["globals"]
			self._data = jsonData["data"]

			self._fetchStamps()
		else:
			raise ValueError("loadSequence: String not a valid JSON object")

	def save(self, exportMode):

		#TODO: implement
		print(exportMode.name)

	def removeEntry(self, timestamp, currKey, currVal):

		ind = self._stamps[timestamp]
		self.getData()[ind]["actions"].pop(currKey)


	def addOrUpdateEntry(self, timestamp, currKey, currVal):

		ind = self._stamps[timestamp]
		currAction = self.getData()[ind]["actions"]
		currAction[currKey] = currVal


	def isJson(self, str):
		try:
			json.loads(str)
		except ValueError as e:
			return False
		return True

	def getData(self):

		return self._data

	def _fetchStamps(self):
		self._stamps = {}
		for i in range(len(self.getData())):

			self._stamps[self.getData()[i]["timestamp"]] = i
		print(self._stamps)
