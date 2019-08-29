import json


class Servo(object):
	def __init__(self, name, hedgehog, servoPort, feedbackPort):
		self.name = name
		self.hedgehog = hedgehog
		self.servoPort = servoPort
		self.feedbackPort = feedbackPort
		self.enabled = False
		self.position_target_percent = None
		self.position_target_us = None
		self.position_current_percent = 0
		self.us_min = None
		self.us_max = None
		self.feedback_min = None
		self.feedback_max = None

		self.loadSettings()

		self.setPositionTargetPercent(0)

	def enable(self):
		if not self.enabled:
			self.enabled = True
			self.hedgehog.set_servo_raw(self.servoPort, self.position_target_us * 2)

	def disable(self):
		if self.enabled:
			self.enabled = False
			self.hedgehog.set_servo_raw(self.servoPort, False)

	def getEnabled(self):
		return self.enabled

	def setPositionTargetPercent(self, position_percent):  # 0-100
		if not position_percent == self.position_target_percent:
			self.position_target_percent = position_percent
			self.setPositionTargetUs(int(self.us_min + (self.us_max - self.us_min) * (position_percent / 100) + 0.5))

	def getPositionTargetPercent(self):
		return self.position_target_percent

	def setPositionTargetUs(self, position_us):
		if not position_us == self.position_target_us:
			self.position_target_us = position_us
			print("servo %s set to %dus" % (self.name, self.position_target_us))
			if self.enabled:
				self.hedgehog.set_servo_raw(self.servoPort, position_us*2)

	def getPositionTargetUs(self):
		return self.position_target_us

	def getPositionCurrentPercent(self):
		return self.position_current_percent

	def calMin(self):
		self.us_min = self.position_target_us
		self.feedback_min = self.hedgehog.get_analog(self.feedbackPort)
		print("servo %s minimum set to %dus, feedback %d" % (self.name, self.us_min, self.feedback_min))

	def calMax(self):
		self.us_max = self.position_target_us
		self.feedback_max = self.hedgehog.get_analog(self.feedbackPort)
		print("servo %s maximum set to %dus, feedback %d" % (self.name, self.us_max, self.feedback_max))

	def getMinUs(self):
		return self.us_min

	def getMaxUs(self):
		return self.us_max

	def saveSettings(self):
		print("saving settings for servo \"" + self.name + "\" to file")
		with open('config/servo_' + self.name + '.json', 'w') as f:
			json.dump((self.us_min, self.us_max, self.feedback_min, self.feedback_max), f, sort_keys=True, indent=4, ensure_ascii=False)

	def loadSettings(self):
		print("loading settings for servo \"" + self.name + "\" from file")
		with open('config/servo_' + self.name + '.json', 'r') as f:
			(self.us_min, self.us_max, self.feedback_min, self.feedback_max) = json.load(f)

	def updatePositionCurrentPercent(self):
		feedback = self.hedgehog.get_analog(self.feedbackPort)
		feedback_span = (self.feedback_max - self.feedback_min)
		position_current_percent = (feedback - self.feedback_min) / feedback_span * 100
		self.position_current_percent = round(position_current_percent, 0)
		# self.position_current_percent = round(max(min(100, position_current_percent), 0), 0)  # TODO: use this?
