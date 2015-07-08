#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 16:45:23 2015

@author: nick
"""

import sys
sys.path.append('../counter-miniUSB')
sys.path.append('../nvoutreach')
import cv2
import time
import glob
import serial
import numpy as np
from PyQt4 import QtGui, uic
from PyQt4.QtCore import QTimer
import pyqtgraph as pg
import Counter as cm
from piezo import *

form_class = uic.loadUiType("diamondgui.ui")[0] 

	

def serial_ports():
    """Lists serial ports

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of available serial ports
    """
    if sys.platform.startswith('win'):
        ports = ['COM' + str(i + 1) for i in range(256)]

    elif sys.platform.startswith('linux'):
        # this is to exclude your current terminal "/dev/tty"
        ports = glob.glob('/dev/serial/by-id/usb-C*')

    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')

    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result




class MyWindowClass(QtGui.QMainWindow, form_class):
	connected = bool(False)
	counter = None 
	runtime = 0
	timelimit = 120
	timeinterval = 200 # in milli seconds
	ypos = 200
	xpos = 200
	pztypos = 0
	pztxpos = 0
	channel = 1
	max_counts = 0
	


	
	def __init__(self, parent=None):
		QtGui.QMainWindow.__init__(self, parent)
		self.setupUi(self)
		self.pushUp.clicked.connect(self.pushUp_clicked)# Bind the event handlers
		self.pushDown.clicked.connect(self.pushDown_clicked)
		self.pushLeft.clicked.connect(self.pushLeft_clicked)
		self.pushRight.clicked.connect(self.pushRight_clicked)
		self.resetButton.clicked.connect(self.reset)
		self.startButton.clicked.connect(self.StartButton_clicked)
		self.stopButton.clicked.connect(self.StopButton_clicked)
		self.comboSerialBox.addItems(serial_ports()) #Gets a list of avaliable serial ports to connect to and adds to combo box
		self.imageview.setImage(self.null_image(),levels=(0,1000))
		self.freq_samples = []
		self.xdata = []
		self.ydata = []
		self.home_position()
		
		
	def StartButton_clicked(self,connection):
		if not self.connected:
			self.counter = cm.Countercomm(str(self.comboSerialBox.currentText()))
			self.timer = QTimer()
			self.connected = True
			self.timer.timeout.connect(self.update)
			self.timer.setInterval(self.timeinterval)
			self.timer.start()
			self.control_label.setText('connected to ' + str(self.comboSerialBox.currentText()))
			self.counter.set_gate_time(self.timeinterval/2.0) # sets gate time to 100ms
			self.gate_time  = float(self.counter.get_gate_time())
			self.count = float(self.counter.get_counts().split(' ')[self.channel])
			self.label_count.setText(str(self.count))
			self.home_position()
			self.ypos_samples = []
			self.xpos_samples = []
			self.count_samples = []
			
	def StopButton_clicked(self):
		self.timer.stop()
		self.counter.close()
		self.connected = False
		self.control_label.setText('Not connected')
		self.reset()
	
	def home_position(self):
		self.xcen = self.doubleSpinBox.value()
		self.ycen = self.doubleSpinBox_2.value()
		self.zcen = self.doubleSpinBox_3.value()
		move(0,self.xcen)
		move(1,self.ycen)
		move(2,self.zcen)

			
	def null_image(self):
		self.imgArray = np.zeros((400,400,3))+3000
		cv2.circle(self.imgArray,(self.ypos,self.xpos),3,color=[0,3000,0],thickness=-1)
		return self.imgArray

	def reset(self):
		self.ypos = 200
		self.xpos = 200
		self.pztypos = 0
		self.pztxpos = 0
		self.runtime = 0
		self.null_image()
		self.home_position()
		self.ypos_samples = []
		self.xpos_samples = []
		self.count_samples = []


	
	def pushUp_clicked(self,value):
		self.ypos = self.ypos -10
		self.pztypos = (self.ypos - 200)/20.0
		self.label_msg.setText('')
		if self.ypos < 0:
			self.ypos = 0
			self.pztypos = (self.ypos - 200)/20.0
			self.label_msg.setText('Vertical travel limit reached')
			
			


	def pushDown_clicked(self,value):
		self.ypos = self.ypos +10
		self.pztypos = (self.ypos - 200)/20.0
		self.label_msg.setText('')
		if self.ypos > 400:
			self.ypos = 400
			self.pztypos = (self.ypos - 200)/20.0
			self.label_msg.setText('Vertical travel limit reached')
			
		

	def pushLeft_clicked(self,value):
		self.xpos = self.xpos -10
		self.pztxpos = (self.xpos - 200)/20.0
		self.label_msg.setText('')
		if self.xpos < 0:
			self.xpos = 0
			self.pztxpos = (self.xpos - 200)/20.0
			self.label_msg.setText('Horizontal travel limit reached')
			

	def pushRight_clicked(self,value):
		self.xpos = self.xpos +10
		self.pztxpos = (self.xpos - 200)/20.0
		self.label_msg.setText('')
		if self.xpos > 400:
			self.xpos = 400
			self.pztxpos = (self.xpos - 200)/20.0
			self.label_msg.setText('Horizontal travel limit reached')
			

	def count_max(self,value):
		if value > self.max_counts:
			self.max_counts = value
		
		
	
	def keyPressEvent(self,event):
		print 'a'
			
			

		
	def update(self):
		self.label_xpos.setText(str(getposition(0)))
		self.label_ypos.setText(str(getposition(1)))
		self.label_zpos.setText(str(getposition(2)))
		self.runtime += self.timeinterval/1000.0
		if self.runtime < self.timelimit:
			moveall(self.pztxpos+self.xcen,self.pztypos+self.ycen,self.zcen)
			self.count = float(self.counter.get_counts().split(' ')[self.channel])
			self.xpos_samples.append(self.xpos)
			self.ypos_samples.append(self.ypos)
			self.count_samples.append(self.count)
			self.count_max(self.count)
			self.color = [self.count,0,0]
			self.label_count.setText(str(self.count))
			self.label_time.setText("{:2.1f}".format(self.timelimit-self.runtime))
			self.label_count_max.setText(str(self.max_counts))
			cv2.rectangle(self.imgArray,(self.ypos-5,self.xpos-5),(self.ypos+5,self.xpos+5),color = self.color,thickness = -1)
			cv2.circle(self.imgArray,(self.ypos,self.xpos),2,color=[0,3000,0],thickness=-1)
			if self.xpos_samples[-2] != self.xpos or self.ypos_samples[-2] != self.ypos:
				x = self.xpos_samples[-2]
				y = self.ypos_samples[-2]
				col = [self.count_samples[-1],0,0]
				cv2.rectangle(self.imgArray,(y-5,x-5),(y+5,x+5),color = col,thickness = -1)
			if self.max_counts > 750:
				self.color_range = self.max_counts
			else:
				self.color_range = 750			
			self.imageview.setImage(self.imgArray,levels=(50,self.color_range))
		else:
			self.label_msg.setText('The search is over your score '+ str(self.max_counts))
										
		
		
		

app = QtGui.QApplication(sys.argv)
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()
