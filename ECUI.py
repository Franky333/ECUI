from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from SequenceMonitor import SequenceMonitor
from Dashboard import Dashboard

class ECUI(QWidget):

	def __init__(self, parent=None):
		super(ECUI, self).__init__(parent)

		#sequence Monitor
		self.seqMonitor = SequenceMonitor(self)

		self.dashboard = Dashboard()


		hLayout = QHBoxLayout()
		hLayout.addWidget(self.dashboard)
		hLayout.addWidget(self.seqMonitor)

		self.setLayout(hLayout)

	def cleanup():
		self.dashboard.cleanup()


if __name__ == '__main__':

	import sys

	app = QApplication(sys.argv)

	ecui = ECUI()

	mainWindow = QMainWindow()
	mainWindow.setCentralWidget(ecui)
	mainWindow.setMinimumSize(QSize(1280/2,1000))

	mainWindow.setStyle(QStyleFactory.create("Macintosh"))

	mainWindow.show()

	app = app.exec_()

	ecui.cleanup()

	sys.exit(app)