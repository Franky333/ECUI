import json

from utils import *

class SequenceController():

	def __init__(self, jsonData=None):

		if jsonData is not None:
			self.loadSequence(jsonData)

		self._loaded = False


	def load(self, jsonFile):

		if self.isJson(jsonFile):

			jsonData = json.loads(jsonFile)
			self._globals = jsonData["globals"]
			self._data = jsonData["data"]

			self._fetchStamps()

			self._loaded = True
		else:
			raise ValueError("loadSequence: String not a valid JSON object")

	def exportJson(self, exportMode):

		jsonStr = None

		if self._loaded:
			if exportMode == SequenceExportMode.LEGACY:
				jsonStr = self._exportLegacy()
				jsonStr = json.dumps(jsonStr, indent=4)

			elif exportMode == SequenceExportMode.NEW:
				jsonStr = self._exportNew()
				jsonStr = self._reformatJson(jsonStr)

		return jsonStr

	def exportAdditionalLegacyFiles(self):

		if self._loaded:
			fuel = self._globals["fuelServo"]
			ox = self._globals["oxidizerServo"]


			fuelStr = json.dumps(fuel, indent=4)
			oxStr = json.dumps(ox, indent=4)

		return fuelStr, oxStr

	def removeEntry(self, timestamp, currKey):

		ind = self._stamps[timestamp]
		if currKey in self.getData()[ind]["actions"]:
			self.getData()[ind]["actions"].pop(currKey)


	def addOrUpdateEntry(self, timestamp, currKey, currVal):

		ind = self._stamps[timestamp]
		currAction = self.getData()[ind]["actions"]
		currAction[currKey] = currVal

	#TODO: make it clean and move substring stuff to sequence monitor
	def updateGlobal(self, currKey, currVal):

		if "min" in currKey:
			currKey = currKey[3:-1]
			currKey = currKey[0].lower() + currKey[1:]
			self._globals[currKey][0] = currVal
		elif "max" in currKey:
			currKey = currKey[3:-1]
			currKey = currKey[0].lower() + currKey[1:]
			self._globals[currKey][1] = currVal
		else:
			self._globals[currKey[:-1]] = currVal

	def isJson(self, str):
		try:
			json.loads(str)
		except ValueError as e:
			return False
		return True

	def getData(self):

		return self._data

	def getGlobals(self):

		return self._globals


	def _reformatJson(self, jsonStr):

		if jsonStr is not None:
			jsonStr = json.loads(jsonStr)
			jsonStr = json.dumps(jsonStr, indent=4)

		return jsonStr

	def _fetchStamps(self):
		self._stamps = {}
		for i in range(len(self.getData())):

			self._stamps[self.getData()[i]["timestamp"]] = i
		print(self._stamps)

	def _exportLegacy(self):

		legJson = []
		for entry in self.getData():
			stamp = entry["timestamp"]
			actions = entry["actions"].copy()
			if stamp == "START":
				stamp = self._globals["startTime"]
			elif stamp == "END":
				stamp = self._globals["endTime"]
			actions["timestamp"] = stamp
			legJson.append(actions)
		print(legJson)

		return legJson

	def _exportNew(self):

		jsonStr = "{\n\"globals\":" + json.dumps(self._globals)
		jsonStr += ", \"data\":" + json.dumps(self._data) + "\n}"

		return jsonStr