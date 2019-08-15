class PressureSensor(object):
	def __init__(self, name, hedgehog, port):
		self.name = name
		self.hedgehog = hedgehog
		self.port = port

	def getValue(self):
		return (self.hedgehog.get_analog(self.port) - 621) * 0.0141
