import json


class Sequence(object):
	def __init__(self):
		self.sequence = []

		# self.sequence += [{'timestamp': 0.0, 'fuel': 0, 'oxidizer': 0}]
		# self.sequence += [{'timestamp': 0.1, 'fuel': 0, 'oxidizer': 7}]
		# self.sequence += [{'timestamp': 0.5, 'fuel': 0, 'oxidizer': 7}]
		# self.sequence += [{'timestamp': 0.6, 'fuel': 9, 'oxidizer': 7}]
		# self.sequence += [{'timestamp': 2.0, 'fuel': 9, 'oxidizer': 7}]
		# self.sequence += [{'timestamp': 4.0, 'fuel': 90, 'oxidizer': 70}]
		# self.sequence += [{'timestamp': 9.0, 'fuel': 90, 'oxidizer': 70}]
		# self.sequence += [{'timestamp': 10.0, 'fuel': 0, 'oxidizer': 0}]

		self.loadSequence()

		# add endpoints and sort
		self.sequence = sorted(self.sequence, key=lambda k: k['timestamp'])
		if not self.sequence[0]['timestamp'] == -1000000:
			self.sequence += [{'timestamp': -1000000, 'fuel': 0, 'oxidizer': 0}]
			print("added start endpoint to sequence")
		if not self.sequence[self.sequence.__len__() - 1]['timestamp'] == 1000000:
			self.sequence += [{'timestamp': 1000000, 'fuel': 0, 'oxidizer': 0}]
			print("added end endpoint to sequence")
		self.sequence = sorted(self.sequence, key=lambda k: k['timestamp'])

		self.status = 'reset'

	def __getListFromKey(self, key):
		_list = []
		for s in self.sequence:
			_list += [s[key]]
		return _list

	def getTimestampList(self):
		return self.__getListFromKey('timestamp')

	def getFuelList(self):
		return self.__getListFromKey('fuel')

	def getOxidizerList(self):
		return self.__getListFromKey('oxidizer')

	def getIndexTimeBelowOrEqual(self, time):
		timestamps = self.getTimestampList()
		for i in range(0, self.sequence.__len__()):
			if timestamps[i] > time:
				return i - 1

	def getIndexTimeAbove(self, time):
		timestamps = self.getTimestampList()
		for i in range(0, self.sequence.__len__()):
			if timestamps[i] > time:
				return i

	def getFuelAtTime(self, time):
		if self.status == 'abort':
			return 0
		index_belowOrEqual = self.getIndexTimeBelowOrEqual(time)
		index_above = self.getIndexTimeAbove(time)
		timestamps = self.getTimestampList()
		fuel = self.getFuelList()

		if timestamps[index_belowOrEqual] == time:
			return fuel[index_belowOrEqual]
		slope = ((fuel[index_above] - fuel[index_belowOrEqual]) / (timestamps[index_above] - timestamps[index_belowOrEqual]))
		return fuel[index_belowOrEqual] + slope * (time - timestamps[index_belowOrEqual])

	def getOxidizerAtTime(self, time):
		if self.status == 'abort':
			return 0
		index_belowOrEqual = self.getIndexTimeBelowOrEqual(time)
		index_above = self.getIndexTimeAbove(time)
		timestamps = self.getTimestampList()
		oxidizer = self.getOxidizerList()

		if timestamps[index_belowOrEqual] == time:
			return oxidizer[index_belowOrEqual]
		slope = ((oxidizer[index_above] - oxidizer[index_belowOrEqual]) / (timestamps[index_above] - timestamps[index_belowOrEqual]))
		return oxidizer[index_belowOrEqual] + slope * (time - timestamps[index_belowOrEqual])

	def getSmallestTimestamp(self):
		return self.getTimestampList()[1]

	def getLargestTimestamp(self):
		return self.getTimestampList()[self.sequence.__len__() - 2]

	def saveSequence(self):
		print("saving sequence to file")
		with open('sequence.json', 'w') as f:
			json.dump(self.sequence, f, sort_keys=True, indent=4, ensure_ascii=False)

	def loadSequence(self):
		print("loading sequence from file")
		with open('sequence.json', 'r') as f:
			self.sequence = json.load(f)

	def setStatus(self, status):
		self.status = status
