class TemperatureSensor(object):
	def __init__(self, name, hedgehog, port):
		self.name = name
		self.hedgehog = hedgehog
		self.port = port
		self.value = 0

	def getValue(self):
		return self.value

	def updateValue(self):
		self.value = (self.hedgehog.get_analog(self.port) - 384) * 0.18
