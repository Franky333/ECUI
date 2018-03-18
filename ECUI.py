#!/usr/bin/python3

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *

from CountdownTimer import CountdownTimer
from Sequence import Sequence
from SequencePlot import SequencePlot
from Servo import Servo


class ECUI(QWidget):
	def __init__(self, parent=None):
		super(ECUI, self).__init__(parent)

		self.countdownTimer = CountdownTimer(self.countdownEvent)
		self.sequence = Sequence()
		self.servo_fuel = Servo('fuel')
		self.servo_oxidizer = Servo('oxidizer')

		# Main tab
		self.tab_main = QWidget()
		self.tab_main.layout = QVBoxLayout(self)
		self.tab_main.setLayout(self.tab_main.layout)

		self.label_countdownClock = QLabel(self.countdownTimer.getTimeString(), self)
		self.label_countdownClock.setStyleSheet('color: #000000')
		self.label_countdownClock.setToolTip("Countdown Clock")

		self.btn_countdownStartStop = QPushButton("Start", self)
		self.btn_countdownStartStop.setToolTip("Start the Countdown")
		self.btn_countdownStartStop.clicked.connect(self.countdownStartStopReset)
		self.btn_countdownStartStop.resize(self.btn_countdownStartStop.sizeHint())
		self.btn_countdownStartStop.setStyleSheet('background-color: #00ff00;')

		self.layout_countdown = QHBoxLayout()
		self.layout_countdown.addWidget(self.label_countdownClock)
		self.layout_countdown.addWidget(self.btn_countdownStartStop)

		self.tab_main.layout.addLayout(self.layout_countdown)

		self.sequencePlot = SequencePlot(self, sequence=self.sequence, countdownTimer=self.countdownTimer, width=5, height=4)
		self.tab_main.layout.addWidget(self.sequencePlot)

		# Settings tab
		self.tab_settings = QWidget()
		self.tab_settings.layout = QHBoxLayout(self)
		self.tab_settings.setLayout(self.tab_settings.layout)

		self.checkbox_calibration = QCheckBox("Servo Calibration", self)
		self.checkbox_calibration.setToolTip("Enable Servo Calibration Mode")
		self.checkbox_calibration.clicked.connect(self.calibrationEnableDisable)
		self.checkbox_calibration.resize(self.checkbox_calibration.sizeHint())

		self.label_cal_fuel = QLabel("Fuel (min=%dus, max=%dus)" % (self.servo_fuel.getMinUs(), self.servo_fuel.getMaxUs()), self)

		self.spinbox_cal_fuel = QSpinBox(self)
		self.spinbox_cal_fuel.setMinimum(500)
		self.spinbox_cal_fuel.setMaximum(2500)
		self.spinbox_cal_fuel.setSingleStep(1)
		self.spinbox_cal_fuel.setValue(self.servo_fuel.getPositionUs())
		self.spinbox_cal_fuel.setEnabled(False)
		self.spinbox_cal_fuel.valueChanged.connect(self.calFuelValueChanged)

		self.btn_cal_fuel_min = QPushButton("Set Min", self)
		self.btn_cal_fuel_min.setToolTip("Set the Minimum Value, corresponds to 0%")
		self.btn_cal_fuel_min.clicked.connect(self.calFuelSetMin)
		self.btn_cal_fuel_min.setEnabled(False)
		self.btn_cal_fuel_min.resize(self.btn_cal_fuel_min.sizeHint())

		self.btn_cal_fuel_max = QPushButton("Set Max", self)
		self.btn_cal_fuel_max.setToolTip("Set the Maximum Value, corresponds to 100%")
		self.btn_cal_fuel_max.clicked.connect(self.calFuelSetMax)
		self.btn_cal_fuel_max.setEnabled(False)
		self.btn_cal_fuel_max.resize(self.btn_cal_fuel_max.sizeHint())

		self.label_cal_oxidizer = QLabel("Oxidizer (min=%dus, max=%dus)" % (self.servo_oxidizer.getMinUs(), self.servo_oxidizer.getMaxUs()), self)

		self.spinbox_cal_oxidizer = QSpinBox(self)
		self.spinbox_cal_oxidizer.setMinimum(500)
		self.spinbox_cal_oxidizer.setMaximum(2500)
		self.spinbox_cal_oxidizer.setSingleStep(1)
		self.spinbox_cal_oxidizer.setValue(self.servo_oxidizer.getPositionUs())
		self.spinbox_cal_oxidizer.setEnabled(False)
		self.spinbox_cal_oxidizer.valueChanged.connect(self.calOxidizerValueChanged)

		self.btn_cal_oxidizer_min = QPushButton("Set Min", self)
		self.btn_cal_oxidizer_min.setToolTip("Set the Minimum Value, corresponds to 0%")
		self.btn_cal_oxidizer_min.clicked.connect(self.calOxidizerSetMin)
		self.btn_cal_oxidizer_min.setEnabled(False)
		self.btn_cal_oxidizer_min.resize(self.btn_cal_oxidizer_min.sizeHint())

		self.btn_cal_oxidizer_max = QPushButton("Set Max", self)
		self.btn_cal_oxidizer_max.setToolTip("Set the Maximum Value, corresponds to 100%")
		self.btn_cal_oxidizer_max.clicked.connect(self.calOxidizerSetMax)
		self.btn_cal_oxidizer_max.setEnabled(False)
		self.btn_cal_oxidizer_max.resize(self.btn_cal_oxidizer_max.sizeHint())

		self.layout_calibration_fuel = QHBoxLayout()
		self.layout_calibration_fuel.addWidget(self.label_cal_fuel)
		self.layout_calibration_fuel.addWidget(self.spinbox_cal_fuel)
		self.layout_calibration_fuel.addWidget(self.btn_cal_fuel_min)
		self.layout_calibration_fuel.addWidget(self.btn_cal_fuel_max)

		self.layout_calibration_oxidizer = QHBoxLayout()
		self.layout_calibration_oxidizer.addWidget(self.label_cal_oxidizer)
		self.layout_calibration_oxidizer.addWidget(self.spinbox_cal_oxidizer)
		self.layout_calibration_oxidizer.addWidget(self.btn_cal_oxidizer_min)
		self.layout_calibration_oxidizer.addWidget(self.btn_cal_oxidizer_max)

		self.layout_calibration = QVBoxLayout()
		self.layout_calibration.addWidget(self.checkbox_calibration)
		self.layout_calibration.addLayout(self.layout_calibration_fuel)
		self.layout_calibration.addLayout(self.layout_calibration_oxidizer)

		self.tab_settings.layout.addLayout(self.layout_calibration)

		# Tabs
		self.tabs = QTabWidget()
		self.tabs.resize(300, 200)
		self.tabs.addTab(self.tab_main, "Main")
		self.tabs.addTab(self.tab_settings, "Settings")

		# Window
		self.layout = QVBoxLayout(self)
		self.layout.addWidget(self.tabs)
		self.setLayout(self.layout)
		self.setGeometry(500, 200, 800, 600)
		self.setWindowTitle("Engine Control UI")
		self.setWindowIcon(QIcon('icon.png'))

	def closeEvent(self, event):
		if self.btn_countdownStartStop.text() == "Abort":
			reply = QMessageBox.question(self, 'Message', "The countdown is running.\nQuit anyways?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
		else:
			reply = QMessageBox.Yes

		if reply == QMessageBox.Yes:
			event.accept()
		else:
			event.ignore()

	def cleanup(self):
		self.countdownTimer.stop()
		self.sequence.saveSequence()
		self.servo_fuel.saveSettings()
		self.servo_oxidizer.saveSettings()

	def countdownStartStopReset(self):
		if self.btn_countdownStartStop.text() == "Start":
			self.checkbox_calibration.setEnabled(False)
			self.calibrationDisable()
			self.countdownTimer.start()
			self.sequence.setStatus('running')
			self.btn_countdownStartStop.setText("Abort")
			self.btn_countdownStartStop.setToolTip("Stop the Countdown")
			self.btn_countdownStartStop.setStyleSheet('background-color: #FF0000;')
		elif self.btn_countdownStartStop.text() == "Abort":
			self.countdownTimer.stop()
			self.sequence.setStatus('abort')
			self.countdownEvent()
			self.label_countdownClock.setStyleSheet('color: #ff0000')
			self.btn_countdownStartStop.setText("Reset")
			self.btn_countdownStartStop.setToolTip("Reset the Countdown")
			self.btn_countdownStartStop.setStyleSheet('background-color: #EEEEEE;')
		elif self.btn_countdownStartStop.text() == "Reset":
			self.checkbox_calibration.setEnabled(True)
			self.countdownTimer.reset()
			self.sequence.setStatus('reset')
			self.countdownEvent()
			self.label_countdownClock.setStyleSheet('color: #000000')
			self.btn_countdownStartStop.setText("Start")
			self.btn_countdownStartStop.setToolTip("Start the Countdown")
			self.btn_countdownStartStop.setStyleSheet('background-color: #00FF00;')
		else:
			print("Error: invalid button state")

	def countdownEvent(self):
		self.label_countdownClock.setText(self.countdownTimer.getTimeString())
		self.servo_fuel.setPositionPercent(self.sequence.getFuelAtTime(self.countdownTimer.getTime()))
		self.servo_oxidizer.setPositionPercent(self.sequence.getOxidizerAtTime(self.countdownTimer.getTime()))
		self.sequencePlot.redrawMarkers()

	def calibrationEnable(self):
		print("Calibration Mode Enabled")
		self.btn_countdownStartStop.setEnabled(False)
		self.checkbox_calibration.setChecked(True)
		self.spinbox_cal_fuel.setEnabled(True)
		self.spinbox_cal_oxidizer.setEnabled(True)
		self.btn_cal_fuel_min.setEnabled(True)
		self.btn_cal_fuel_max.setEnabled(True)
		self.btn_cal_oxidizer_min.setEnabled(True)
		self.btn_cal_oxidizer_max.setEnabled(True)

	def calibrationDisable(self):
		print("Calibration Mode Disabled")
		self.btn_countdownStartStop.setEnabled(True)
		self.checkbox_calibration.setChecked(False)
		self.spinbox_cal_fuel.setEnabled(False)
		self.spinbox_cal_oxidizer.setEnabled(False)
		self.btn_cal_fuel_min.setEnabled(False)
		self.btn_cal_fuel_max.setEnabled(False)
		self.btn_cal_oxidizer_min.setEnabled(False)
		self.btn_cal_oxidizer_max.setEnabled(False)
		self.countdownEvent()

	def calibrationEnableDisable(self):
		if self.checkbox_calibration.isChecked():
			self.calibrationEnable()
		else:
			self.calibrationDisable()

	def calFuelValueChanged(self):
		if self.checkbox_calibration.isChecked():
			self.servo_fuel.setPositionUs(self.spinbox_cal_fuel.value())

	def calOxidizerValueChanged(self):
		if self.checkbox_calibration.isChecked():
			self.servo_oxidizer.setPositionUs(self.spinbox_cal_oxidizerl.value())

	def calFuelSetMin(self):
		if self.checkbox_calibration.isChecked():
			self.servo_fuel.setMinUs(self.spinbox_cal_fuel.value())
			self.label_cal_fuel.setText("Fuel (min=%dus, max=%dus)" % (self.servo_fuel.getMinUs(), self.servo_fuel.getMaxUs()))

	def calFuelSetMax(self):
		if self.checkbox_calibration.isChecked():
			self.servo_fuel.setMaxUs(self.spinbox_cal_fuel.value())
			self.label_cal_fuel.setText("Fuel (min=%dus, max=%dus)" % (self.servo_fuel.getMinUs(), self.servo_fuel.getMaxUs()))

	def calOxidizerSetMin(self):
		if self.checkbox_calibration.isChecked():
			self.servo_oxidizer.setMinUs(self.spinbox_cal_oxidizer.value())
			self.label_cal_fuel.setText("Oxidizer (min=%dus, max=%dus)" % (self.servo_oxidizer.getMinUs(), self.servo_oxidizer.getMaxUs()))

	def calOxidizerSetMax(self):
		if self.checkbox_calibration.isChecked():
			self.servo_oxidizer.setMaxUs(self.spinbox_cal_oxidizer.value())
			self.label_cal_fuel.setText("Oxidizer (min=%dus, max=%dus)" % (self.servo_oxidizer.getMinUs(), self.servo_oxidizer.getMaxUs()))


if __name__ == '__main__':
	import sys

	app = QApplication(sys.argv)

	screen = ECUI()
	screen.show()

	app_return = app.exec_()

	screen.cleanup()

	sys.exit(app_return)
