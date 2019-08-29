class PressureSensor(object):
	def __init__(self, name, hedgehog, port):
		self.name = name
		self.hedgehog = hedgehog
		self.port = port
		self.value = 0

	def getValue(self):
		return self.value

	def updateValue(self):
		self.value = (self.hedgehog.get_analog(self.port) - 621) * 0.0141
