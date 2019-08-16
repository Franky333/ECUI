class Igniter(object):
	def __init__(self, name, hedgehog, igniterPort, feedbackPort=None):
		self.name = name
		self.hedgehog = hedgehog
		self.igniterPort = igniterPort
		self.feedbackPort = feedbackPort
		self.enabled = False

	def set(self, enabled):
		if enabled and not self.enabled:
			self.enabled = True
			print("relay %s enabled" % self.name)
			self.hedgehog.move_motor(self.igniterPort, 1000)
		if not enabled and self.enabled:
			self.enabled = False
			print("relay %s disabled" % self.name)
			self.hedgehog.motor_off(self.igniterPort)

	def get(self):
		return self.enabled

	def getArmed(self):
		if self.feedbackPort is None:
			return None
		else:
			return self.hedgehog.get_analog(self.feedbackPort) < 2048
