from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class PNID(QTabWidget):

	def __init__(self, parent=None):
		super(PNID, self).__init__(parent)

		self.pnidWidget = QWidget()
		self.pnidLabel = QLabel("", self)

		self.addTab(self.pnidLabel, "PNID")

		#self.pnidLayout = QHBoxLayout()
		#self.pnidLayout.addWidget(self.pnidLabel)

		#self.setLayout(self.pnidLayout)



	def loadPNID(self, path):
		self.pnidPixmap = QPixmap(path)
		w = self.pnidLabel.width()
		h = self.pnidLabel.height()
		print(w, h)
		self.pnidLabel.setPixmap(self.pnidPixmap.scaled(w, h, Qt.KeepAspectRatio))


if __name__ == '__main__':

	import sys

	app = QApplication(sys.argv)

	pnid = PNID()

	mainWindow = QMainWindow()
	mainWindow.setCentralWidget(pnid)
	mainWindow.setMinimumSize(QSize(1920/2,1000))

	mainWindow.setStyle(QStyleFactory.create("Macintosh"))

	mainWindow.show()

	pnid.loadPNID("/Volumes/Data/markus/Programming/SpaceTeam/TXV_ECUI/pnid_v0.1.png")

	sys.exit(app.exec_())