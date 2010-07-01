#!/usr/bin/python
from opencv.cv import *
from opencv.highgui import *
import sys
import os
import math
from maestro import test

image_scale = 4
#all configuration tuples follow the following patterns: 
#       (pan, tilt) and/or (x, y) and/or (min, max) and/or (servo_adjustment, pixel_width)
#path to the pololu command line application
#the resolution of the camera
cam_resolution = (640, 480)
center_box_dim = (35, 10)
start_servo_position = (5984, 6400)
current_servo_position = (5984, 6400)
servo_limits = ((3968, 8000), (4800, 8000))

servo_app = ((210, 100), (210, 100))
#servo_app = ((100, 100), (100, 100))

servo_move_interval = 3
servo_ready = True
face_locations = []

#the following configuration variables are automatically set
cam_center = (cam_resolution[0] / 2, cam_resolution[1] / 2)
center_box = ((cam_center[0] - (center_box_dim[0] / 2), cam_center[0] + (center_box_dim[0] / 2)), 
				(cam_center[1] - (center_box_dim[1] / 2), cam_center[1] + (center_box_dim[1] / 2)))

cascade = cvLoadHaarClassifierCascade('/usr/share/opencv/haarcascades/haarcascade_eye.xml', cvSize(1,1))
usb_interface = test.PololuUsb()


def set_servo(pan=start_servo_position[0], tilt=start_servo_position[1]):
	if pan < servo_limits[0][0]:
		pan = servo_limits[0][0]
	if pan > servo_limits[0][1]:
		pan = servo_limits[0][1]
	if tilt < servo_limits[1][0]:
		tilt = servo_limits[1][0]
	if tilt > servo_limits[1][1]:
		tilt = servo_limits[1][1]

	global current_servo_position
	current_servo_position = (pan, tilt)
	
	usb_interface.set_target(0, tilt)
	usb_interface.set_target(1, pan)


def detect(image,move):
	global face_locations
	global cascade
	
	f_x = 0
	f_y = 0

	"""Converts an image to grayscale and prints the locations of any 
	faces found"""
	grayscale = cvCreateImage(cvSize(image.width, image.height), 8, 1)
	cvCvtColor(image, grayscale, CV_BGR2GRAY)

	storage = cvCreateMemStorage(0)
	cvClearMemStorage(storage)
	cvEqualizeHist(grayscale, grayscale)
	
	faces = cvHaarDetectObjects(grayscale, cascade, storage, 2.0, 2, CV_HAAR_DO_CANNY_PRUNING, cvSize(50,50))
	global servo_ready
	if faces:
		for f in faces:
			print("[(%d,%d) -> (%d,%d)]" % (f.x, f.y, f.x+f.width, f.y+f.height))
			cvRectangle(image, cvPoint( int(f.x), int(f.y)), cvPoint(int(f.x + f.width), int(f.y + f.height)), 255, 3, 8, 0)
			face_locations.append((f.x + (f.width / 2), f.y + (f.height / 2)))
		if servo_ready:
			servo_ready = False
			l = len(face_locations)
			if l > 0:
				total_x = 0
				total_y = 0
				for f in face_locations:
					total_x += f[0]
					total_y += f[1]
				
				del face_locations[:]

				f_x = total_x / l
				f_y = total_y / l
		
				if move == True:
					if math.sqrt(pow(f_x - cam_center[0],2) + pow(f_y - cam_center[1],2)) > 40:
						adjust_x = (f_x - cam_center[0]) * servo_app[0][0] / servo_app[0][1]
						adjust_y = (cam_center[0] - f_y) * servo_app[1][0] / servo_app[1][1]
						
						set_servo(adjust_x + current_servo_position[0], adjust_y + current_servo_position[1])

	return image, (f_x, f_y)

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
	

if __name__ == "__main__":
	capture = None
	set_servo()
	counter = 0
	if len(sys.argv)==1:
		capture = cvCreateCameraCapture( 0 )
	elif len(sys.argv)==2 and sys.argv[1].isdigit():
		capture = cvCreateCameraCapture( int(sys.argv[1]) )
	elif len(sys.argv)==2:
		capture = cvCreateFileCapture( sys.argv[1] ) 
	
	if not capture:
		print "Could not initialize capturing..."
		sys.exit(-1)
	
	cvSetCaptureProperty( capture, CV_CAP_PROP_FRAME_WIDTH, cam_resolution[0] )
	cvSetCaptureProperty( capture, CV_CAP_PROP_FRAME_HEIGHT, cam_resolution[1] )
	cvNamedWindow( "Face Detection", 1 )

	calibrate(capture)

	while True:
		frame = cvQueryFrame( capture )
		if not frame:
			cvWaitKey(0)
			break
		img, pos = detect(frame,True)
		cvShowImage("Face Detection",  img)
		if counter >= servo_move_interval:
			servo_ready = True
			counter = 0
	
		counter += 1
		
		if cvWaitKey(10) != -1:
			break
		
	cvDestroyWindow("Face Detection")