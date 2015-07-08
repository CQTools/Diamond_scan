#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 16:45:23 2015

@author: nick
"""

import sys
sys.path.append('../counter-miniUSB')
import cv2
import time
import glob
import serial
import numpy as np
from PyQt4 import QtGui, uic
from PyQt4.QtCore import QTimer
import pyqtgraph as pg
import Counter as cm


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
	time = 0
	ypos = 200
	xpos = 200
	channel = 1
	


	
	def __init__(self, parent=None):
		QtGui.QMainWindow.__init__(self, parent)
		self.setupUi(self)
		self.pushUp.clicked.connect(self.pushUp_clicked)# Bind the event handlers
		self.pushDown.clicked.connect(self.pushDown_clicked)
		self.pushLeft.clicked.connect(self.pushLeft_clicked)
		self.pushRight.clicked.connect(self.pushRight_clicked)
		#self.ButtonUpdate_channel.clicked.connect(self.ButtonUpdate_channel_clicked)
		self.ButtonConnect.clicked.connect(self.ButtonConnect_clicked)
		self.comboSerialBox.addItems(serial_ports()) #Gets a list of avaliable serial ports to connect to and adds to combo box
		self.imageview.setImage(self.null_image(),levels=(0,30000))
		self.freq_samples = []
		self.xdata = []
		self.ydata = []
		
	def ButtonConnect_clicked(self,connection):
		if not self.connected:
			self.counter = cm.Countercomm(str(self.comboSerialBox.currentText()))
			self.timer = QTimer()
			self.connected = True
			self.timer.timeout.connect(self.update)
			self.timer.setInterval(100)
			self.timer.start()
			self.control_label.setText('connected to ' + str(self.comboSerialBox.currentText()))
			self.counter.set_gate_time(10) # sets gate time to 100ms
			self.gate_time  = float(self.counter.get_gate_time())
			#self.label_gate.setText(str(self.gate_time) +" ms")
			#starttime = time.time()
			self.count = float(self.counter.get_counts().split(' ')[self.channel])
			print self.counter.get_counts().split(' ')
			self.label_count.setText(str(self.count))
			#gate_time  = float(self.counter.get_gate_time())
			
			
	def null_image(self):
		#imgArray = np.random.randint(255, size=(2, 2, 3))
		self.imgArray = np.zeros((400,400,3))+30000
		cv2.circle(self.imgArray,(self.ypos,self.xpos),3,color=[0,30000,0],thickness=-1)
		return self.imgArray

	#def blob(self):
		
	
	def pushUp_clicked(self,value):
		self.ypos = self.ypos -10
		if self.ypos < 0:
			self.ypos = 0
			


	def pushDown_clicked(self,value):
		self.ypos = self.ypos +10
		if self.ypos > 400:
			self.ypos = 400
		

	def pushLeft_clicked(self,value):
		self.xpos = self.xpos -10
		if self.xpos < 0:
			self.xpos = 0

	def pushRight_clicked(self,value):
		self.xpos = self.xpos +10
		if self.xpos > 400:
			self.xpos = 400

	def count_max(self,value):
		max_counts = 70,000
		if value > self.max_counts:
			max_counts = value
		return max_counts
		
	
	def keyPressEvent(self,event):
		print 'a'
			
			

		
	def update(self):
		self.count = float(self.counter.get_counts().split(' ')[self.channel])
		self.color = [self.count,self.count,self.count]
		self.label_count.setText(str(self.count))
		cv2.rectangle(self.imgArray,(self.ypos-5,self.xpos-5),(self.ypos+5,self.xpos+5),color = self.color,thickness = -1)
		cv2.circle(self.imgArray,(self.ypos,self.xpos),2,color=[0,30000,0],thickness=-1)
		self.imageview.setImage(self.imgArray,levels=(50,30000))		
										
		
		
		

app = QtGui.QApplication(sys.argv)
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()
