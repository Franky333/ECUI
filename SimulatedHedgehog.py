class SimulatedHedgehog(object):
	def __init__(self):
		pass

	def get_analog(self, port):
		return 0

	def set_servo_raw(self, port, us):
		if us is False:
			print('SimulatedHedgehog Servo %d disabled' % port)
		else:
			print('SimulatedHedgehog Servo %d set to %dus' % (port, us))

	def move_motor(self, port, power):
		print('SimulatedHedgehog Motor %d set to %d' % (port, power))

	def motor_off(self, port):
		print('SimulatedHedgehog Motor %d switched off' % port)
