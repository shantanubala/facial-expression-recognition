

devicePort = "/dev/ttyUSB0"



import serial

import time


device = serial.Serial(port=devicePort,baudrate=19200, timeout=0)

#print device.read(10)

device.write("\r\n")

print "Data Written"

time.sleep(0.1)


while len(device.readline()) < 5:
    pass

print device.readline()

print "Data Read"

device.close()
