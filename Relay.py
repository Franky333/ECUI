class Relay(object):
	def __init__(self, name, hedgehog, port):
		self.name = name
		self.hedgehog = hedgehog
		self.port = port
		self.enabled = False

	def set(self, enabled):
		if enabled and not self.enabled:
			self.enabled = True
			print("relay %s enabled" % self.name)
			self.hedgehog.move_motor(self.port, 1000)
		if not enabled and self.enabled:
			self.enabled = False
			print("relay %s disabled" % self.name)
			self.hedgehog.motor_off(self.port)

	def get(self):
		return self.enabled
