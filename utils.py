
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