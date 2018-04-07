

class Relay(object):
	def __init__(self, hedgehog, port, name):
		self.hedgehog = hedgehog
		self.port = port
		self.name = name
		self.enabled = False

	def set(self, enabled):
		if enabled:
			self.enabled = True
			print("relay %s enabled" % self.name)
			self.hedgehog.move(self.port, 1000)
		else:
			self.enabled = False
			print("relay %s disabled" % self.name)
			self.hedgehog.move(self.port, 0)

	def get(self):
		return self.enabled
