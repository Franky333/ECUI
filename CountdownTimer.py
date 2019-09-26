from PyQt5.QtCore import QTimer
import os

class CountdownTimer(object):
	def __init__(self, callback, *args, **kwargs):
		self.countdown_step = 0.1
		self.countdown_reset = -10

		self.timer = QTimer()
		self.timer.setInterval(self.countdown_step * 1000)
		self.timer.timeout.connect(self.__countdownTick)

		self.countdownTime = self.countdown_reset

		self.callback = callback
		self.args = args
		self.kwargs = kwargs

	def __countdownTick(self):
		self.countdownTime = round(self.countdownTime + self.countdown_step, 1)
		if abs(self.countdownTime - round(self.countdownTime, 0)) < 0.0001:
			number = round(self.countdownTime, 0)
			if number <= 0:
				text = '%d' % (round(-self.countdownTime, 0))
				print("Countdown: " + text)
				text = text.replace("0", "ignition")
				os.system("espeak -v en+f3 '" + text + "' &")
		self.callback(*self.args, **self.kwargs)

	def start(self):
		self.timer.start()

	def stop(self):
		self.timer.stop()

	def reset(self):
		self.timer.stop()
		self.countdownTime = self.countdown_reset

	def getTime(self):
		return self.countdownTime

	def getTimeString(self):
		countdownTime = self.countdownTime
		sign = "+"
		if countdownTime < 0:
			sign = "−"
			countdownTime = -countdownTime
		hours = int(countdownTime // 3600)
		minutes = int(countdownTime % 3600 // 60)
		seconds = int(countdownTime % 60)
		milliseconds = int(countdownTime % 1 * 1000)
		hundred_milliseconds = int(milliseconds // 100)
		return "t%s %02d:%02d:%02d.%1d" % (sign, hours, minutes, seconds, hundred_milliseconds)
