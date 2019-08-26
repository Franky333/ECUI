from PyQt5.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class SequencePlot(FigureCanvas):

	def __init__(self, parent=None, width=5, height=4, dpi=100, sequence=None, countdownTimer=None):
		fig = Figure(figsize=(width, height), dpi=dpi)
		FigureCanvas.__init__(self, fig)
		self.setParent(parent)
		FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)

		self.sequence = sequence
		self.countdownTimer = countdownTimer

		self.axes = fig.add_subplot(111)

		self.axes.set_title("Fuel and Oxidizer Valve and Igniter Sequence")
		self.axes.set_xlabel("Time in Seconds")
		self.axes.set_ylabel("Valve Opening and Igniter Power in Percent")
		self.axes.set_autoscaley_on(False)
		x_min = int(self.sequence.getSmallestTimestamp() - 1)
		y_min = int(self.sequence.getLargestTimestamp() + 1)
		self.axes.set_xlim(x_min, y_min)
		self.axes.set_ylim(-1, 101)
		self.axes.set_xticks(range(x_min, y_min+1))
		self.axes.set_yticks(range(0, 110, 10))
		self.axes.grid()
		self.fuelSequence, = self.axes.plot(sequence.getTimestampList(), sequence.getFuelList(), 'r-', label="Fuel")
		self.oxidizerSequence, = self.axes.plot(sequence.getTimestampList(), sequence.getOxidizerList(), 'b-', label="Oxidizer")
		self.igniterSequence, = self.axes.plot(sequence.getTimestampList(), sequence.getIgniterList(), 'g-', label="Igniter")
		self.fuelMarker, = self.axes.plot(self.countdownTimer.getTime(), sequence.getFuelAtTime(self.countdownTimer.getTime()), 'rx')
		self.oxidizerMarker, = self.axes.plot(self.countdownTimer.getTime(), sequence.getOxidizerAtTime(self.countdownTimer.getTime()), 'bx')
		self.igniterMarker, = self.axes.plot(self.countdownTimer.getTime(), sequence.getIgniterAtTime(self.countdownTimer.getTime()), 'gx')
		self.timeMarker, = self.axes.plot([self.countdownTimer.getTime(), self.countdownTimer.getTime()], [0, 100], color='#AAAAAA', linewidth=1)
		self.axes.legend(handles=[self.fuelSequence, self.oxidizerSequence, self.igniterSequence], loc='upper left')
		self.draw_idle()

	def redrawMarkers(self):
		self.fuelMarker.set_data(self.countdownTimer.getTime(), self.sequence.getFuelAtTime(self.countdownTimer.getTime()))
		self.oxidizerMarker.set_data(self.countdownTimer.getTime(), self.sequence.getOxidizerAtTime(self.countdownTimer.getTime()))
		self.igniterMarker.set_data(self.countdownTimer.getTime(), self.sequence.getIgniterAtTime(self.countdownTimer.getTime()))
		self.timeMarker.set_data([self.countdownTimer.getTime(), self.countdownTimer.getTime()], [0, 100])
		self.draw_idle()
