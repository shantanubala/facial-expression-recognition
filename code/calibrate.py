from config import *



def calibrate(capture):
	#Capture frame and get head position
	frame = cvQueryFrame(capture)
	img, pos1 = detect(frame,True)

	pan = (servo_limits[0][1] - servo_limits[0][0])*(20.0/90) + start_servo_position[0]
	set_servo(pan)

	cvWaitKey(0)

	#Capture frame and get head position again
	frame = cvQueryFrame(capture)
	img, pos2 = detect(frame,True)

	print pos1[1] - pos1[0]


	cvWaitKey(0)
