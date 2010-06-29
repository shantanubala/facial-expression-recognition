#!/usr/bin/python
###########################################################################################
# Filename: 
#     micromaestro.py
###########################################################################################
# Project Authors: 
#     Juhapekka Piiroinen
#     Brian Wu
# 
# Changes:
#     June 14, 2010 by Juhapekka Piiroinen - changes committed to svn
#           - added comments for the device commands according to the manual from Pololu
#           - added latest draft code for rotating base servo (Parallax Continuous Rotating Servo)
#           - note! you should be able to clear error flags with .get_errors function according to the manual
#           - renamed CameraDriver to LegacyCameraDriver as Brian Wu has done better one
#           - integrated batch of changes provided by Brian Wu
#
#     June 11, 2010 by Brian Wu - Changes committed thru email
#           - Decoupling the implementation from the program
#
#     April 19, 2010 by Juhapekka Piiroinen
#           - Initial Release
# 
# Email:
#     juhapekka.piiroinen@gmail.com
#
# License: 
#     GNU/GPLv3
#
# Description:
#     A python-wrapper for Pololu Micro Maestro 6-Channel USB Servo Controller
#
############################################################################################
# /!\ Notes /!\
# You will have to enable _USB Dual Port_ mode from the _Pololu Maestro Control Center_.
#
############################################################################################
# Device Documentation is available @ http://www.pololu.com/docs/pdf/0J40/maestro.pdf
############################################################################################
# (C) 2010 Juhapekka Piiroinen
#          Brian Wu
############################################################################################
import Device
import LegacyCameraDriver
import CameraDriver
import time
import sys

#############################################################################################
def test_CameraDriver():
    print "Test CameraDriver"
    cd = CameraDriver.CameraDriver()
    cd.load_file("random.txt")
    print cd.status()  		# prints out the positions of the servos
    cd.step()  				# Executes current instruction, moves instruction line by 1
    print cd.frame_number	# prints out the index of the next instruction
    print "\n"

    cd.steps(10, True)  			#executes the next 10 steps and print out their directions
    cd.set_frame(20)  		# sets the index to the 21st command
    cd.step()					# execute the 20th command

    cd.shift_frame(-5) 		#adds -5 to the frame index
    cd.step()					#Executes it

    cd.execute_frame(0) 			# goes to and executes the 0th frame
    print cd.frame_number	

    cd.execute_procedure([0, 10, 5]) #executes the 0th, then 11th, then 5th frame.  index will then point to the 6th frame
    print cd.frame_number
    print cd.status()
    cd.reset()    			#resets the index to 0
    cd.unmount()  			#clears the port
    print "CameraDriver tested"
    
#############################################################################################
def test_LegacyCameraDriver():
    print "Test Legacy Camera Driver"
    c = LegacyCameraDriver()
    print c.status_report()
    c.pan(50)
    c.pan(-50)
    c.tilt(50)
    c.tilt(-50)
    ## Rotate function for Parallax Continuous Rotating Servo
    c.rotate(50) #left
    time.sleep(0.2)
    c.rotate(-50) #stop
    time.sleep(0.2)
    c.rotate(-50) #right
    time.sleep(0.2)
    c.rotate(50) #stop
    time.sleep(0.2)
    ## END - Rotate
    c.reset()
    del c
    print "Legacy Camera Driver tested"

#############################################################################################
def test_Device():
    print "Test Device"
    d = Device("COM6","COM7")
    servos = [0,1]
    for servo_id in servos:
        print "-- servo:",servo_id
        print "Go Home"
        d.go_home()
        print "Get Errors"
        print d.get_errors()
        
        print "Get Position"
        pos = d.get_position(servo_id)
        print pos        
        
        newsetpos = pos-50
        print "Set Target:",newsetpos
        d.set_target(servo_id,newsetpos)
        d.wait_until_at_target()
        newpos = d.get_position(servo_id)
        print "%s==%s" % (newsetpos,newpos),
        print newsetpos==newpos
        
        newsetpos = pos+50
        print "Set Target:",newsetpos
        d.set_target(servo_id,newsetpos)
        d.wait_until_at_target()
        newpos = d.get_position(servo_id)
        print "%s==%s" % (newsetpos,newpos),
        print newsetpos==newpos
        
        d.go_home()
        print d.get_errors()
    del d
    print "Device tested"

####################################
if __name__=="__main__":
    test_Device()
    # test_CameraDriver()
    # test_LegacyCameraDriver()

## EOF
