#!/usr/local/bin/python3.7
import csv
import datetime

import time
import os

from hedgehog.client import connect
from contextlib import ExitStack
from SimulatedHedgehog import SimulatedHedgehog

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from CountdownTimer import CountdownTimer
from Igniter import Igniter
from Sequence import Sequence
from SequencePlot import SequencePlot
from Servo import Servo
from PressureSensor import PressureSensor
from TemperatureSensor import TemperatureSensor


class ECUI(QWidget):
	def __init__(self, parent=None):
		super(ECUI, self).__init__(parent)

		# Settings
		self.autoabortEnabled = True

		# Hedgehog
		self.stack = ExitStack()
		self.hedgehog = self.stack.enter_context(connect(endpoint='tcp://raspberrypi.local:10789'))  # FIXME

		# Simulated Hedgehog
		#self.hedgehog = SimulatedHedgehog()

		# Actuators and Sensors
		self.servo_fuel = Servo(name='fuel', hedgehog=self.hedgehog, servoPort=0, feedbackPort=0)
		self.servo_oxidizer = Servo(name='oxidizer', hedgehog=self.hedgehog, servoPort=1, feedbackPort=1)
		self.igniter_arc = Igniter(name='arc', hedgehog=self.hedgehog, igniterPort=0)
		self.igniter_pyro = Igniter(name='pyro', hedgehog=self.hedgehog, igniterPort=1, feedbackPort=7)
		self.pressureSensor_fuel = PressureSensor(name='fuel', hedgehog=self.hedgehog, port=2)
		self.pressureSensor_oxidizer = PressureSensor(name='oxidizer', hedgehog=self.hedgehog, port=3)
		self.pressureSensor_chamber = PressureSensor(name='chamber', hedgehog=self.hedgehog, port=4)
		self.temperatureSensor_chamber = TemperatureSensor(name='chamber', hedgehog=self.hedgehog, port=8)

		# Countdown Timer and Sequence
		self.countdownTimer = CountdownTimer(self.countdownEvent)
		self.sequence = Sequence()

		# Regular Timer
		self.timer = QTimer()
		self.timer.setInterval(100)
		self.timer.timeout.connect(self.__timerTick)

		self.inputVoltage = 0.0

		self.loggingValues = []

		# Main tab
		self.tab_main = QWidget()
		self.tab_main.layout = QVBoxLayout(self)
		self.tab_main.setLayout(self.tab_main.layout)

		self.label_countdownClock = QLabel(self.countdownTimer.getTimeString(), self)
		self.label_countdownClock.setStyleSheet('color: #000000')
		self.label_countdownClock.setToolTip("Countdown Clock")

		self.label_inputVoltage = QLabel("Input Voltage: 0.0V", self)
		self.label_inputVoltage.setStyleSheet('color: #000000')
		self.label_inputVoltage.setToolTip("Input Voltage")

		self.btn_countdownStartStop = QPushButton("Start", self)
		self.btn_countdownStartStop.setToolTip("Start the Countdown")
		self.btn_countdownStartStop.clicked.connect(self.countdownStartStopReset)
		self.btn_countdownStartStop.resize(self.btn_countdownStartStop.sizeHint())
		self.btn_countdownStartStop.setStyleSheet('background-color: #00ff00;')

		self.layout_countdown = QHBoxLayout()
		self.layout_countdown.addWidget(self.label_inputVoltage, alignment=Qt.AlignLeft)
		self.layout_countdown.addWidget(self.label_countdownClock, alignment=Qt.AlignCenter)
		self.layout_countdown.addWidget(self.btn_countdownStartStop, alignment=Qt.AlignRight)

		self.tab_main.layout.addLayout(self.layout_countdown)

		self.sequencePlot = SequencePlot(self, sequence=self.sequence, countdownTimer=self.countdownTimer, width=5, height=4)
		self.tab_main.layout.addWidget(self.sequencePlot, alignment=Qt.AlignTop)

		self.checkbox_manualControl = QCheckBox("Manual Control", self)
		self.checkbox_manualControl.setToolTip("Enable Manual Control")
		self.checkbox_manualControl.clicked.connect(self.manualControlEnableDisable)
		self.checkbox_manualControl.resize(self.checkbox_manualControl.sizeHint())

		self.checkbox_manualControlIgniter = QCheckBox("Igniter", self)
		self.checkbox_manualControlIgniter.setToolTip("Igniter Manual Control")
		self.checkbox_manualControlIgniter.clicked.connect(self.manualControlIgniterEnableDisable)
		self.checkbox_manualControlIgniter.resize(self.checkbox_manualControlIgniter.sizeHint())
		self.checkbox_manualControlIgniter.setEnabled(False)

		self.label_manualControlFuel = QLabel("Fuel Target: %3d%%   Fuel Currently: %3d%%   Fuel Pressure: %2.1fbar" % (self.servo_fuel.getPositionTargetPercent(), self.servo_fuel.getPositionCurrentPercent(), self.pressureSensor_fuel.getValue()), self)
		self.slider_manualControlFuel = QSlider(Qt.Horizontal)  # FIXME: buggy when slided manually, goes out of range or doesnt reach limits
		self.slider_manualControlFuel.setToolTip("Fuel Manual Control")
		self.slider_manualControlFuel.setRange(0, 100)
		self.slider_manualControlFuel.sliderMoved.connect(self.manualControlFuelChange)
		self.slider_manualControlFuel.resize(self.slider_manualControlFuel.sizeHint())
		self.slider_manualControlFuel.setEnabled(False)
		self.layout_manualControlFuel = QVBoxLayout()
		self.layout_manualControlFuel.addWidget(self.label_manualControlFuel, alignment=Qt.AlignLeft)
		self.layout_manualControlFuel.addWidget(self.slider_manualControlFuel, alignment=Qt.AlignTop)

		self.label_manualControlOxidizer = QLabel("Oxidizer Target: %3d%%   Oxidizer Currently: %3d%%   Oxidizer Pressure: %2.1fbar" % (self.servo_oxidizer.getPositionTargetPercent(), self.servo_oxidizer.getPositionCurrentPercent(), self.pressureSensor_oxidizer.getValue()), self)
		self.slider_manualControlOxidizer = QSlider(Qt.Horizontal)  # FIXME: buggy when slided manually, goes out of range or doesnt reach limits
		self.slider_manualControlOxidizer.setToolTip("Oxidizer Manual Control")
		self.slider_manualControlOxidizer.setRange(0, 100)
		self.slider_manualControlOxidizer.sliderMoved.connect(self.manualControlOxidizerChange)
		self.slider_manualControlOxidizer.resize(self.slider_manualControlOxidizer.sizeHint())
		self.slider_manualControlOxidizer.setEnabled(False)
		self.layout_manualControlOxidizer = QVBoxLayout()
		self.layout_manualControlOxidizer.addWidget(self.label_manualControlOxidizer, alignment=Qt.AlignLeft)
		self.layout_manualControlOxidizer.addWidget(self.slider_manualControlOxidizer, alignment=Qt.AlignTop)

		self.layout_manualControl = QVBoxLayout()
		self.layout_manualControl.addWidget(self.checkbox_manualControl, alignment=Qt.AlignLeft)
		self.layout_manualControl.addWidget(self.checkbox_manualControlIgniter, alignment=Qt.AlignLeft)
		self.layout_manualControl.addLayout(self.layout_manualControlFuel)
		self.layout_manualControl.addLayout(self.layout_manualControlOxidizer)

		self.tab_main.layout.addLayout(self.layout_manualControl)

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
		self.spinbox_cal_fuel.setValue(self.servo_fuel.getPositionTargetUs())
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
		self.spinbox_cal_oxidizer.setValue(self.servo_oxidizer.getPositionTargetUs())
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
		self.layout_calibration_fuel.addWidget(self.label_cal_fuel, alignment=Qt.AlignTop)
		self.layout_calibration_fuel.addWidget(self.spinbox_cal_fuel, alignment=Qt.AlignTop)
		self.layout_calibration_fuel.addWidget(self.btn_cal_fuel_min, alignment=Qt.AlignTop)
		self.layout_calibration_fuel.addWidget(self.btn_cal_fuel_max, alignment=Qt.AlignTop)

		self.layout_calibration_oxidizer = QHBoxLayout()
		self.layout_calibration_oxidizer.addWidget(self.label_cal_oxidizer, alignment=Qt.AlignTop)
		self.layout_calibration_oxidizer.addWidget(self.spinbox_cal_oxidizer, alignment=Qt.AlignTop)
		self.layout_calibration_oxidizer.addWidget(self.btn_cal_oxidizer_min, alignment=Qt.AlignTop)
		self.layout_calibration_oxidizer.addWidget(self.btn_cal_oxidizer_max, alignment=Qt.AlignTop)

		self.layout_calibration = QVBoxLayout()
		self.layout_calibration.addWidget(self.checkbox_calibration, alignment=Qt.AlignTop)
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
		self.layout.addWidget(self.tabs, alignment=Qt.AlignTop)
		self.setLayout(self.layout)
		self.setGeometry(500, 200, 900, 700)
		self.setWindowTitle("Engine Control UI")
		self.setWindowIcon(QIcon('icon.png'))

		#Timer
		self.timer.start()

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
		self.servo_fuel.disable()
		self.servo_oxidizer.disable()
		self.stack.close()
		self.countdownTimer.stop()
		self.sequence.saveSequence()
		self.servo_fuel.saveSettings()
		self.servo_oxidizer.saveSettings()

	def countdownStartStopReset(self):
		if self.btn_countdownStartStop.text() == "Start":
			self.checkbox_calibration.setEnabled(False)
			self.calibrationDisable()
			self.checkbox_manualControl.setEnabled(False)
			self.manualControlDisable()
			self.countdownTimer.start()
			self.sequence.setStatus('running')
			self.btn_countdownStartStop.setText("Abort")
			self.btn_countdownStartStop.setToolTip("Stop the Countdown")
			self.btn_countdownStartStop.setStyleSheet('background-color: #FF0000;')
			self.servo_fuel.enable()
			self.servo_oxidizer.enable()

		elif self.btn_countdownStartStop.text() == "Abort":
			self.countdownTimer.stop()  # TODO: make timer continue
			self.sequence.setStatus('abort')
			self.countdownEvent()
			self.label_countdownClock.setStyleSheet('color: #ff0000')
			self.btn_countdownStartStop.setText("Reset and Save Log")
			self.btn_countdownStartStop.setToolTip("Reset the countdown and save logging data to a file")
			self.btn_countdownStartStop.setStyleSheet('background-color: #EEEEEE;')

		elif self.btn_countdownStartStop.text() == "Reset and Save Log":
			logfile_name = f"{datetime.datetime.now():%Y%m%d_%H%M%S}.csv"  # TODO: move logging to own class
			logfile_name_dir = 'log/'+logfile_name
			os.makedirs(os.path.dirname(logfile_name_dir), exist_ok=True)  # generate log directory if non existent
			with open(logfile_name_dir, 'w', newline='') as logfile:
				fieldnames = ['Timestamp', 'ServoFuelPercentageTarget', 'ServoOxidizerPercentageTarget', 'ServoFuelPercentageCurrent', 'ServoOxidizerPercentageCurrent', 'PressureFuel', 'PressureOxidizer', 'PressureChamber', 'TemperatureChamber']
				writer = csv.DictWriter(logfile, fieldnames=fieldnames)
				writer.writeheader()
				for line in self.loggingValues:
					writer.writerow(line)
			self.loggingValues.clear()

			self.checkbox_calibration.setEnabled(True)
			self.checkbox_manualControl.setEnabled(True)
			self.countdownTimer.reset()
			self.sequence.setStatus('reset')
			self.countdownEvent()
			self.label_countdownClock.setStyleSheet('color: #000000')
			self.btn_countdownStartStop.setText("Start")
			self.btn_countdownStartStop.setToolTip("Start the Countdown")
			self.btn_countdownStartStop.setStyleSheet('background-color: #00FF00;')

		else:
			print("Error: invalid button state")

	def __timerTick(self):  # FIXME: bc of the hedgehog commands this often takes longer than 100ms, slowing down the countdown
		self.servo_fuel.updatePositionCurrentPercent()
		self.servo_oxidizer.updatePositionCurrentPercent()
		self.igniter_pyro.updateArmed()
		self.pressureSensor_fuel.updateValue()
		self.pressureSensor_oxidizer.updateValue()
		self.pressureSensor_chamber.updateValue()
		self.temperatureSensor_chamber.updateValue()

		voltageNew = self.hedgehog.get_analog(0x80) / 1000
		self.inputVoltage = self.inputVoltage * 0.6 + voltageNew * 0.4
		self.label_inputVoltage.setText("Input Voltage: %.1fV" % self.inputVoltage)

		self.label_manualControlFuel.setText("Fuel Target: %3d%%   Fuel Currently: %3d%%   Fuel Pressure: %2.1fbar" % (self.servo_fuel.getPositionTargetPercent(), self.servo_fuel.getPositionCurrentPercent(), self.pressureSensor_fuel.getValue()))
		self.label_manualControlOxidizer.setText("Oxidizer Target: %3d%%   Oxidizer Currently: %3d%%   Oxidizer Pressure: %2.1fbar" % (self.servo_oxidizer.getPositionTargetPercent(), self.servo_oxidizer.getPositionCurrentPercent(), self.pressureSensor_oxidizer.getValue()))

		if self.igniter_pyro.getArmed() is not None:
			if self.igniter_pyro.getArmed() is True:
				self.checkbox_manualControlIgniter.setText("Igniter (Armed)")
			else:
				self.checkbox_manualControlIgniter.setText("Igniter (Disarmed)")
		else:
			self.checkbox_manualControlIgniter.setText("Igniter (Unknown)")

	def countdownEvent(self):
		# abort if no ignition detected TODO: improve
		if self.autoabortEnabled:
			if self.pressureSensor_chamber.getValue() < self.sequence.getChamberPressureMinAtTime(self.countdownTimer.getTime()):
				os.system("espeak \"auto abort\" &")
				self.countdownTimer.stop()  # TODO: make timer continue
				self.sequence.setStatus('abort')
				self.label_countdownClock.setStyleSheet('color: #ff0000')
				self.btn_countdownStartStop.setText("Reset and Save Log")
				self.btn_countdownStartStop.setToolTip("Reset the countdown and save logging data to a file")
				self.btn_countdownStartStop.setStyleSheet('background-color: #EEEEEE;')

		# outputs set values
		self.label_countdownClock.setText(self.countdownTimer.getTimeString())
		self.servo_fuel.setPositionTargetPercent(self.sequence.getFuelAtTime(self.countdownTimer.getTime()))
		self.servo_oxidizer.setPositionTargetPercent(self.sequence.getOxidizerAtTime(self.countdownTimer.getTime()))
		self.igniter_arc.set(self.sequence.getIgniterAtTime(self.countdownTimer.getTime()))
		self.igniter_pyro.set(self.sequence.getIgniterAtTime(self.countdownTimer.getTime()))
		self.sequencePlot.redrawMarkers()

		# update ui
		self.checkbox_manualControlIgniter.setChecked(self.sequence.getIgniterAtTime(self.countdownTimer.getTime()))
		self.slider_manualControlFuel.setValue(self.sequence.getFuelAtTime(self.countdownTimer.getTime()))
		self.slider_manualControlOxidizer.setValue(self.sequence.getOxidizerAtTime(self.countdownTimer.getTime()))

		# sensors get values
		self.loggingValues.append({'Timestamp': self.countdownTimer.getTime(),
		                           'ServoFuelPercentageTarget': self.servo_fuel.getPositionTargetPercent(),
		                           'ServoOxidizerPercentageTarget': self.servo_oxidizer.getPositionTargetPercent(),
		                           'ServoFuelPercentageCurrent': self.servo_fuel.getPositionCurrentPercent(),
		                           'ServoOxidizerPercentageCurrent': self.servo_oxidizer.getPositionCurrentPercent(),
		                           'PressureFuel': self.pressureSensor_fuel.getValue(),
		                           'PressureOxidizer': self.pressureSensor_oxidizer.getValue(),
		                           'PressureChamber': self.pressureSensor_chamber.getValue(),
		                           'TemperatureChamber': self.temperatureSensor_chamber.getValue()})

	def manualControlEnable(self):
		print("Manual Control Enabled")
		self.checkbox_manualControl.setChecked(True)
		self.btn_countdownStartStop.setEnabled(False)  # FIXME: doesn't do anything?!
		self.checkbox_calibration.setEnabled(False)
		self.calibrationDisable()
		self.checkbox_manualControlIgniter.setEnabled(True)
		self.slider_manualControlFuel.setEnabled(True)
		self.slider_manualControlOxidizer.setEnabled(True)
		self.servo_fuel.enable()
		self.servo_oxidizer.enable()

	def manualControlDisable(self):
		print("Manual Control Disabled")
		self.checkbox_manualControl.setChecked(False)
		self.checkbox_manualControlIgniter.setEnabled(False)
		self.checkbox_manualControlIgniter.setChecked(False)
		self.slider_manualControlFuel.setEnabled(False)
		self.slider_manualControlOxidizer.setEnabled(False)
		self.manualControlIgniterDisable()
		self.countdownEvent()
		self.btn_countdownStartStop.setEnabled(True)
		self.checkbox_calibration.setEnabled(True)

	def manualControlEnableDisable(self):  # TODO: rename to __checkbox_manualControl_onClick, same for other callbacks
		if self.checkbox_manualControl.isChecked():
			self.manualControlEnable()
		else:
			self.manualControlDisable()

	def manualControlIgniterEnable(self):
		print("Manual Igniter ON")
		self.igniter_arc.set(True)
		self.igniter_pyro.set(True)

	def manualControlIgniterDisable(self):
		print("Manual Igniter OFF")
		self.igniter_arc.set(False)
		self.igniter_pyro.set(False)

	def manualControlIgniterEnableDisable(self):
		if self.checkbox_manualControlIgniter.isChecked():
			self.manualControlIgniterEnable()
		else:
			self.manualControlIgniterDisable()

	def manualControlFuelChange(self):
		self.servo_fuel.setPositionTargetPercent(self.slider_manualControlFuel.value())
		self.label_manualControlFuel.setText("Fuel Target: %3d%%   Fuel Currently: %3d%%   Fuel Pressure: %2.1fbar" % (self.servo_fuel.getPositionTargetPercent(), self.servo_fuel.getPositionCurrentPercent(), self.pressureSensor_fuel.getValue()))

	def manualControlOxidizerChange(self):
		self.servo_oxidizer.setPositionTargetPercent(self.slider_manualControlOxidizer.value())
		self.label_manualControlOxidizer.setText("Oxidizer Target: %3d%%   Oxidizer Currently: %3d%%   Oxidizer Pressure: %2.1fbar" % (self.servo_oxidizer.getPositionTargetPercent(), self.servo_oxidizer.getPositionCurrentPercent(), self.pressureSensor_oxidizer.getValue()))

	def calibrationEnable(self):
		print("Calibration Mode Enabled")
		self.btn_countdownStartStop.setEnabled(False)
		self.checkbox_manualControl.setEnabled(False)
		self.manualControlDisable()
		self.checkbox_calibration.setChecked(True)
		self.spinbox_cal_fuel.setEnabled(True)
		self.spinbox_cal_oxidizer.setEnabled(True)
		self.btn_cal_fuel_min.setEnabled(True)
		self.btn_cal_fuel_max.setEnabled(True)
		self.btn_cal_oxidizer_min.setEnabled(True)
		self.btn_cal_oxidizer_max.setEnabled(True)
		self.servo_fuel.enable()
		self.servo_oxidizer.enable()

	def calibrationDisable(self):
		print("Calibration Mode Disabled")
		self.checkbox_calibration.setChecked(False)
		self.spinbox_cal_fuel.setEnabled(False)
		self.spinbox_cal_oxidizer.setEnabled(False)
		self.btn_cal_fuel_min.setEnabled(False)
		self.btn_cal_fuel_max.setEnabled(False)
		self.btn_cal_oxidizer_min.setEnabled(False)
		self.btn_cal_oxidizer_max.setEnabled(False)
		self.countdownEvent()
		self.btn_countdownStartStop.setEnabled(True)
		self.checkbox_manualControl.setEnabled(True)

	def calibrationEnableDisable(self):
		if self.checkbox_calibration.isChecked():
			self.calibrationEnable()
		else:
			self.calibrationDisable()

	def calFuelValueChanged(self):
		if self.checkbox_calibration.isChecked():
			self.servo_fuel.setPositionTargetUs(self.spinbox_cal_fuel.value())

	def calOxidizerValueChanged(self):
		if self.checkbox_calibration.isChecked():
			self.servo_oxidizer.setPositionTargetUs(self.spinbox_cal_oxidizer.value())

	def calFuelSetMin(self):
		if self.checkbox_calibration.isChecked():
			self.servo_fuel.calMin()
			self.label_cal_fuel.setText("Fuel (min=%dus, max=%dus)" % (self.servo_fuel.getMinUs(), self.servo_fuel.getMaxUs()))

	def calFuelSetMax(self):
		if self.checkbox_calibration.isChecked():
			self.servo_fuel.calMax()
			self.label_cal_fuel.setText("Fuel (min=%dus, max=%dus)" % (self.servo_fuel.getMinUs(), self.servo_fuel.getMaxUs()))

	def calOxidizerSetMin(self):
		if self.checkbox_calibration.isChecked():
			self.servo_oxidizer.calMin()
			self.label_cal_oxidizer.setText("Oxidizer (min=%dus, max=%dus)" % (self.servo_oxidizer.getMinUs(), self.servo_oxidizer.getMaxUs()))

	def calOxidizerSetMax(self):
		if self.checkbox_calibration.isChecked():
			self.servo_oxidizer.calMax()
			self.label_cal_oxidizer.setText("Oxidizer (min=%dus, max=%dus)" % (self.servo_oxidizer.getMinUs(), self.servo_oxidizer.getMaxUs()))


if __name__ == '__main__':
	import sys

	app = QApplication(sys.argv)

	screen = ECUI()
	screen.show()

	app_return = app.exec_()

	screen.cleanup()

	sys.exit(app_return)
