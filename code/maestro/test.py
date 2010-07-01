import serial
import time
import sys
import shelve
import usb

import usb_util

#servos = shelve.open('servos.shelve')

MAESTRO_VENDOR_ID, MAESTRO_PRODUCT_ID = 0x1ffb, 0x0089

# Request enum from Usc_protocol.cs
class uscRequest(object):
	REQUEST_GET_PARAMETER = 0x81
	REQUEST_SET_PARAMETER = 0x82
	REQUEST_GET_VARIABLES = 0x83
	REQUEST_SET_SERVO_VARIABLE = 0x84
	REQUEST_SET_TARGET = 0x85
	REQUEST_CLEAR_ERRORS = 0x86
	REQUEST_REINITIALIZE = 0x90
	REQUEST_ERASE_SCRIPT = 0xA0
	REQUEST_WRITE_SCRIPT = 0xA1
	REQUEST_SET_SCRIPT_DONE = 0xA2
	REQUEST_RESTART_SCRIPT_AT_SUBROUTINE = 0xA3
	REQUEST_RESTART_SCRIPT_AT_SUBROUTINE_WITH_PARAMETER = 0xA4
	REQUEST_RESTART_SCRIPT = 0xA5
	REQUEST_START_BOOTLOADER = 0xFF

class PololuUsb(object):
	def __init__(self):
		self._device = usb_util.get_device(MAESTRO_VENDOR_ID)
		interface = self._device.configurations[0].interfaces[4][0]
		print "using interface with class %s (%s)" % (interface.interfaceClass,
			usb_util.interfaceClass2string[interface.interfaceClass])
		self._handle = usb_util.get_handle(self._device, interface)

	def control_transfer(self, requestType, request, value, index, data=''):
		"""
		controlMsg(requestType, request, buffer, value=0, index=0, timeout=100) -> bytesWritten|buffer
    
		Performs a control request to the default control pipe on a device.
		Arguments:
		        requestType: specifies the direction of data flow, the type
		    		 of request, and the recipient.
		        request: specifies the request.
		        buffer: if the transfer is a write transfer, buffer is a sequence 
		    	    with the transfer data, otherwise, buffer is the number of
		    	    bytes to read.
		        value: specific information to pass to the device. (default: 0)
		        index: specific information to pass to the device. (default: 0)
		        timeout: operation timeout in miliseconds. (default: 100)
		Returns the number of bytes written.

		"""
		return self._handle.controlMsg(requestType=requestType, request=request,
					value=value, index=index, buffer=data, timeout=5000)

	def get_raw_parameter(self):
		self.control_transfer(0xC0, uscRequest.REQUEST_GET_PARAMETER, 0, parameter, array)

	def set_target(self, servo, value):
		self.control_transfer(0x40, uscRequest.REQUEST_SET_TARGET, value, servo)

	def get_position(servo):
		return ''.join(map(chr, [0x90, servo]))
