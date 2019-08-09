from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class PNID(QTabWidget):

	def __init__(self, parent=None):
		super(PNID, self).__init__(parent)

		self.pnidLabel = QLabel()
		self.pnidLabel.setPixmap(QPixmap("/Volumes/Data/markus/Programming/SpaceTeam/TXV_ECUI/pnid_v0.1.png"))

		self.



if __name__ == '__main__':

	import sys

	app = QApplication(sys.argv)

	mainWindow = QMainWindow()
	mainWindow.setCentralWidget(PNID())
	mainWindow.setMinimumSize(QSize(1920/2,1000))

	mainWindow.setStyle(QStyleFactory.create("Macintosh"))

	mainWindow.show()

	sys.exit(app.exec_())