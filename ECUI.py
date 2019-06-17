#!/usr/local/bin/python3.7
import csv
import datetime

from hedgehog.client import connect
from contextlib import ExitStack

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from CountdownTimer import CountdownTimer
from Relay import Relay
from Sequence import Sequence
from SequencePlot import SequencePlot
from Servo import Servo


class ECUI(QWidget):
	def __init__(self, parent=None):
		super(ECUI, self).__init__(parent)

		self.stack = ExitStack()
		self.hedgehog = self.stack.enter_context(connect(endpoint='tcp://raspberrypi.local:10789'))  # FIXME

		self.countdownTimer = CountdownTimer(self.countdownEvent)
		self.sequence = Sequence()
		self.servo_fuel = Servo(hedgehog=self.hedgehog, port=0, name='fuel')
		self.servo_oxidizer = Servo(hedgehog=self.hedgehog, port=1, name='oxidizer')
		self.relay_igniter = Relay(hedgehog=self.hedgehog, port=0, name='igniter')  # Arc
		#self.relay_igniter = Relay(hedgehog=self.hedgehog, port=1, name='igniter')  # Pyro

		self.batteryVoltage = 0.0

		self.loggingvalues = []

		# Main tab
		self.tab_main = QWidget()
		self.tab_main.layout = QVBoxLayout(self)
		self.tab_main.setLayout(self.tab_main.layout)

		self.label_countdownClock = QLabel(self.countdownTimer.getTimeString(), self)
		self.label_countdownClock.setStyleSheet('color: #000000')
		self.label_countdownClock.setToolTip("Countdown Clock")

		self.label_batteryVoltage = QLabel("0.0V", self)
		self.label_batteryVoltage.setStyleSheet('color: #000000')
		self.label_batteryVoltage.setToolTip("Battery Voltage")

		self.btn_countdownStartStop = QPushButton("Start", self)
		self.btn_countdownStartStop.setToolTip("Start the Countdown")
		self.btn_countdownStartStop.clicked.connect(self.countdownStartStopReset)
		self.btn_countdownStartStop.resize(self.btn_countdownStartStop.sizeHint())
		self.btn_countdownStartStop.setStyleSheet('background-color: #00ff00;')

		self.layout_countdown = QHBoxLayout()
		self.layout_countdown.addWidget(self.label_batteryVoltage)
		self.layout_countdown.addWidget(self.label_countdownClock)
		self.layout_countdown.addWidget(self.btn_countdownStartStop)

		self.tab_main.layout.addLayout(self.layout_countdown)

		self.sequencePlot = SequencePlot(self, sequence=self.sequence, countdownTimer=self.countdownTimer, width=5, height=4)
		self.tab_main.layout.addWidget(self.sequencePlot)

		self.checkbox_manualControl = QCheckBox("Manual Control", self)
		self.checkbox_manualControl.setToolTip("Enable Manual Control")
		self.checkbox_manualControl.clicked.connect(self.manualControlEnableDisable)
		self.checkbox_manualControl.resize(self.checkbox_manualControl.sizeHint())

		self.checkbox_manualControlIgniter = QCheckBox("Igniter", self)
		self.checkbox_manualControlIgniter.setToolTip("Igniter Manual Control")
		self.checkbox_manualControlIgniter.clicked.connect(self.manualControlIgniterEnableDisable)
		self.checkbox_manualControlIgniter.resize(self.checkbox_manualControlIgniter.sizeHint())
		self.checkbox_manualControlIgniter.setEnabled(False)

		self.label_manualControlFuel = QLabel("Fuel: %d" % self.servo_fuel.getPositionPercent(), self)
		self.slider_manualControlFuel = QSlider(Qt.Horizontal)  # FIXME: buggy when slided manually, goes out of range or doesnt reach limits
		self.slider_manualControlFuel.setToolTip("Fuel Manual Control")
		self.slider_manualControlFuel.setRange(0, 100)
		self.slider_manualControlFuel.sliderMoved.connect(self.manualControlFuelChange)
		self.slider_manualControlFuel.resize(self.slider_manualControlFuel.sizeHint())
		self.slider_manualControlFuel.setEnabled(False)
		self.layout_manualControlFuel = QVBoxLayout()
		self.layout_manualControlFuel.addWidget(self.label_manualControlFuel)
		self.layout_manualControlFuel.addWidget(self.slider_manualControlFuel)

		self.label_manualControlOxidizer = QLabel("Oxidizer: %d%%" % self.servo_oxidizer.getPositionPercent(), self)
		self.slider_manualControlOxidizer = QSlider(Qt.Horizontal)  # FIXME: buggy when slided manually, goes out of range or doesnt reach limits
		self.slider_manualControlOxidizer.setToolTip("Oxidizer Manual Control")
		self.slider_manualControlOxidizer.setRange(0, 100)
		self.slider_manualControlOxidizer.sliderMoved.connect(self.manualControlOxidizerChange)
		self.slider_manualControlOxidizer.resize(self.slider_manualControlOxidizer.sizeHint())
		self.slider_manualControlOxidizer.setEnabled(False)
		self.layout_manualControlOxidizer = QVBoxLayout()
		self.layout_manualControlOxidizer.addWidget(self.label_manualControlOxidizer)
		self.layout_manualControlOxidizer.addWidget(self.slider_manualControlOxidizer)

		self.layout_manualControl = QVBoxLayout()
		self.layout_manualControl.addWidget(self.checkbox_manualControl)
		self.layout_manualControl.addWidget(self.checkbox_manualControlIgniter)
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
		self.setGeometry(500, 200, 900, 700)
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
		elif self.btn_countdownStartStop.text() == "Abort":
			self.countdownTimer.stop()
			self.sequence.setStatus('abort')
			self.countdownEvent()
			self.label_countdownClock.setStyleSheet('color: #ff0000')
			self.btn_countdownStartStop.setText("Reset and Save Log")
			self.btn_countdownStartStop.setToolTip("Reset the countdown and save logging data to a file")
			self.btn_countdownStartStop.setStyleSheet('background-color: #EEEEEE;')

		elif self.btn_countdownStartStop.text() == "Reset and Save Log":

			logfilename = f"{datetime.datetime.now():%Y%m%d_%H%M%S}.csv"
			with open('log/'+logfilename, 'w', newline='') as csvfile:
				fieldnames = ['Timestamp', 'ServoFuel', 'ServoOxidizer', 'PressureFuel', 'PressureOxidizer', 'PressureChamber', 'TemperatureFuel']
				writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

				writer.writeheader()
				for line in self.loggingvalues:
					writer.writerow(line)

			self.loggingvalues.clear()
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

	def countdownEvent(self):
		self.label_countdownClock.setText(self.countdownTimer.getTimeString())
		self.servo_fuel.setPositionPercent(self.sequence.getFuelAtTime(self.countdownTimer.getTime()))
		self.servo_oxidizer.setPositionPercent(self.sequence.getOxidizerAtTime(self.countdownTimer.getTime()))
		self.relay_igniter.set(self.sequence.getIgniterAtTime(self.countdownTimer.getTime()))
		self.checkbox_manualControlIgniter.setChecked(self.sequence.getIgniterAtTime(self.countdownTimer.getTime()))
		self.label_manualControlFuel.setText("Fuel: %d%%" % self.servo_fuel.getPositionPercent())
		self.label_manualControlOxidizer.setText("Oxidizer: %d%%" % self.servo_oxidizer.getPositionPercent())
		self.slider_manualControlFuel.setValue(self.sequence.getFuelAtTime(self.countdownTimer.getTime()))
		self.slider_manualControlOxidizer.setValue(self.sequence.getOxidizerAtTime(self.countdownTimer.getTime()))
		self.sequencePlot.redrawMarkers()

		pressure_fuel = (self.hedgehog.get_analog(0) - 240) * 0.01626  # TODO: move sensors to own class, improve cal, plot measured values
		pressure_oxidizer = (self.hedgehog.get_analog(1) - 240) * 0.01626
		pressure_chamber = (self.hedgehog.get_analog(2) - 240) * 0.01626
		temperature_fuel = (self.hedgehog.get_analog(8) - 384) * 0.18
		self.loggingvalues.append({'Timestamp': self.countdownTimer.getTime(),
		                           'ServoFuel': self.servo_fuel.getPositionPercent(),
		                           'ServoOxidizer': self.servo_oxidizer.getPositionPercent(),
		                           'PressureFuel': pressure_fuel,
		                           'PressureOxidizer': pressure_oxidizer,
		                           'PressureChamber': pressure_chamber,
		                           'TemperatureFuel': temperature_fuel})

		voltageNew = self.hedgehog.get_analog(0x80) / 1000  # FIXME:  move to regular event
		self.batteryVoltage = self.batteryVoltage * 0.6 + voltageNew * 0.4
		self.label_batteryVoltage.setText("Battery: %.1fV" % self.batteryVoltage)

	def manualControlEnable(self):
		print("Manual Control Enabled")
		self.checkbox_manualControl.setChecked(True)
		self.btn_countdownStartStop.setEnabled(False)  # FIXME: doesn't do anything?!
		self.checkbox_calibration.setEnabled(False)
		self.calibrationDisable()
		self.checkbox_manualControlIgniter.setEnabled(True)
		self.slider_manualControlFuel.setEnabled(True)
		self.slider_manualControlOxidizer.setEnabled(True)

	def manualControlDisable(self):
		print("Manual Control Disabled")
		self.checkbox_manualControl.setChecked(False)
		self.btn_countdownStartStop.setEnabled(True)
		self.checkbox_calibration.setEnabled(True)
		self.checkbox_manualControlIgniter.setEnabled(False)
		self.checkbox_manualControlIgniter.setChecked(False)
		self.manualControlIgniterDisable()
		self.slider_manualControlFuel.setEnabled(False)
		self.slider_manualControlOxidizer.setEnabled(False)

	def manualControlEnableDisable(self):  # TODO: rename to checkbox_manualControl_onClick, same for other callbacks
		if self.checkbox_manualControl.isChecked():
			self.manualControlEnable()
		else:
			self.manualControlDisable()

	def manualControlIgniterEnable(self):
		print("Manual Igniter ON")
		self.relay_igniter.set(True)

	def manualControlIgniterDisable(self):
		print("Manual Igniter OFF")
		self.relay_igniter.set(False)

	def manualControlIgniterEnableDisable(self):
		if self.checkbox_manualControlIgniter.isChecked():
			self.manualControlIgniterEnable()
		else:
			self.manualControlIgniterDisable()

	def manualControlFuelChange(self):
		print("Manuel Fuel Changed")
		self.servo_fuel.setPositionPercent(self.slider_manualControlFuel.value())
		self.label_manualControlFuel.setText("Fuel: %d%%" % self.servo_fuel.getPositionPercent())

	def manualControlOxidizerChange(self):
		print("Manuel Oxidizer Changed")
		self.servo_oxidizer.setPositionPercent(self.slider_manualControlOxidizer.value())
		self.label_manualControlOxidizer.setText("Oxidizer: %d%%" % self.servo_oxidizer.getPositionPercent())

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

	def calibrationDisable(self):
		print("Calibration Mode Disabled")
		self.btn_countdownStartStop.setEnabled(True)
		self.checkbox_manualControl.setEnabled(True)
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
			self.servo_oxidizer.setPositionUs(self.spinbox_cal_oxidizer.value())

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
			self.label_cal_oxidizer.setText("Oxidizer (min=%dus, max=%dus)" % (self.servo_oxidizer.getMinUs(), self.servo_oxidizer.getMaxUs()))

	def calOxidizerSetMax(self):
		if self.checkbox_calibration.isChecked():
			self.servo_oxidizer.setMaxUs(self.spinbox_cal_oxidizer.value())
			self.label_cal_oxidizer.setText("Oxidizer (min=%dus, max=%dus)" % (self.servo_oxidizer.getMinUs(), self.servo_oxidizer.getMaxUs()))


if __name__ == '__main__':
	import sys

	app = QApplication(sys.argv)

	screen = ECUI()
	screen.show()

	app_return = app.exec_()

	screen.cleanup()

	sys.exit(app_return)
