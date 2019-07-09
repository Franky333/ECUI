
class Utils():

	@staticmethod
	def tryParseFloat(val):


		success = False
		try:
			f = float(val)
			val = f
			success = True
		except ValueError:
			print("Not a float")

		return val, success