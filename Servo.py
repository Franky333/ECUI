import json


class Servo(object):
	def __init__(self, hedgehog, port, name):
		self.hedgehog = hedgehog
		self.port = port
		self.name = name
		self.position_percent = None
		self.position_us = None
		self.min_us = None
		self.max_us = None

		self.loadSettings()

		self.setPositionPercent(0)

	def setPositionPercent(self, position_percent):  # 0-100
		if not position_percent == self.position_percent:
			self.position_percent = position_percent
			self.setPositionUs(int(self.min_us + (self.max_us - self.min_us) * (position_percent / 100) + 0.5))

	def getPositionPercent(self):
		return self.position_percent

	def setPositionUs(self, position_us):
		if not position_us == self.position_us:
			self.position_us = position_us
			print("servo %s set to %dus" % (self.name, self.position_us))
			self.hedgehog.set_servo_raw(self.port, position_us*2)

	def getPositionUs(self):
		return self.position_us

	def setMinUs(self, position_us):
		self.min_us = position_us
		print("servo %s minimum set to %dus" % (self.name, self.min_us))

	def getMinUs(self):
		return self.min_us

	def setMaxUs(self, position_us):
		self.max_us = position_us
		print("servo %s maximum set to %dus" % (self.name, self.max_us))

	def getMaxUs(self):
		return self.max_us

	def saveSettings(self):
		print("saving settings for servo \"" + self.name + "\" to file")
		with open('config/servo_' + self.name + '.json', 'w') as f:
			json.dump((self.min_us, self.max_us), f, sort_keys=True, indent=4, ensure_ascii=False)

	def loadSettings(self):
		print("loading settings for servo \"" + self.name + "\" from file")
		with open('config/servo_' + self.name + '.json', 'r') as f:
			(self.min_us, self.max_us) = json.load(f)
