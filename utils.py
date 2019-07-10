
from enum import Enum

class SequenceExportMode(Enum):
	LEGACY = 1
	NEW = 2

class Utils():

	@staticmethod
	def tryParseFloat(val):


		success = False
		try:
			f = float(val)
			val = f
			success = True
		except ValueError:
			pass

		return val, success

	@staticmethod
	def tryParseInt(val):


		success = False
		try:
			f = int(val)
			val = f
			success = True
		except ValueError:
			pass

		return val, success