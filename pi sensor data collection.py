#!/usr/bin/env python
import serial
import datetime

port = "/dev/ttyUSB0"
rate = 115200

s1 = serial.Serial(port, rate)
s1.flushInput()
saveFile = open('workfile','w')

while True:
     inputValue = s1.readline()

     timeStr = str(datetime.datetime.now())
     print (inputValue)
     saveFile.write(str(inputValue)+' '+timeStr)
