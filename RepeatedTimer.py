import threading
import time


class RepeatedTimer(object):
	def __init__(self, interval, callback, *args, **kwargs):
		self._timer = None
		self.interval = interval
		self.callback = callback
		self.args = args
		self.kwargs = kwargs
		self.is_running = False
		self.next_call = time.time()

	def _run(self):
		self.next_call += self.interval
		self._timer = threading.Timer(self.next_call - time.time(), self._run)
		self._timer.start()
		self.callback(*self.args, **self.kwargs)

	def start(self):
		if not self.is_running:
			self.next_call = time.time() + self.interval
			self._timer = threading.Timer(self.next_call - time.time(), self._run)
			self._timer.start()
			self.is_running = True

	def stop(self):
		if self.is_running:
			self._timer.cancel()
			self.is_running = False
