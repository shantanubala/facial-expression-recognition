#!/usr/bin/python
from opencv.cv import *
from opencv.highgui import *
import sys
import os

image_scale = 4
#all configuration tuples follow the following patterns: 
#	(pan, tilt) and/or (x, y) and/or (min, max) and/or (servo_adjustment, pixel_width)
#path to the pololu command line application
usc_cmd = '/home/sreekar/Documents/pololu/UscCmd'
#the resolution of the camera
cam_resolution = (640, 480)
center_box_dim = (80, 60)
start_servo_position = (1496, 1600)
current_servo_position = (1496, 1600)
servo_limits = ((992, 2000), (1200, 2000))
servo_app = ((500, 100), (600, 100))
servo_move_interval = 30

#the following configuration variables are automatically set
cam_center = (cam_resolution[0] / 2, cam_resolution[1] / 2)
center_box = ((cam_center[0] - (center_box_dim[0] / 2), cam_center[0] + (center_box_dim[0] / 2)), 
				(cam_center[1] - (center_box_dim[1] / 2), cam_center[1] + (center_box_dim[1] / 2))
servo_ready = True

def set_servo(pan=start_servo_position[0], tilt=start_srvo_position[1]):
	if pan < servo_limits[0][0]:
		pan = servo_limits[0][0]
	if pan > servo_limits[0][1]:
		pan = servo_limits[0][1]
	if pan < servo_limits[1][0]:
		tilt = servo_limits[1][0]
	if pan > servo_limits[1][1]:
		tilt = servo_limits[1][1]
	current_servo_position = (pan, tilt)
	os.system('/home/sreekar/Documents/pololu/UscCmd --servo 1,' + str(pan)
	os.system('/home/sreekar/Documents/pololu/UscCmd --servo 0,' + str(tilt)

def detect(image):
	"""Converts an image to grayscale and prints the locations of any 
	faces found"""
	grayscale = cvCreateImage(cvSize(image.width, image.height), 8, 1)
	cvCvtColor(image, grayscale, CV_BGR2GRAY)

	storage = cvCreateMemStorage(0)
	cvClearMemStorage(storage)
	cvEqualizeHist(grayscale, grayscale)
	cascade = cvLoadHaarClassifierCascade(
	'/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml',
	cvSize(1,1))
	faces = cvHaarDetectObjects(grayscale, cascade, storage, 1.2, 2,
			         CV_HAAR_DO_CANNY_PRUNING, cvSize(50,50))

	if faces:
		f = faces[0]
		print("[(%d,%d) -> (%d,%d)]" % (f.x, f.y, f.x+f.width, f.y+f.height))
		cvRectangle(image, cvPoint( int(f.x), int(f.y)), cvPoint(int(f.x + f.width), int(f.y + f.height)), 255, 3, 8, 0)
		if servo_ready:
			servo_ready = False
			f_x = f.x + (f.width / 2)
			f_y = f.y + (f.height / 2)
		
			if f_x < center_box[0][0] or f_x > center_box[0][1]:
				adjust_x = (cam_center[0] - f_x) * servo_app[0][0] / servo_app[0][1]
			else:
				adjust_x = 0
			if f_y < center_box[1][0] or f_y > center_box[1][1]:
				adjust_y = (cam_center[1] - f_y) * servo_app[1][0] / servo_app[1][1]
			else:
				adjust_y = 0
			
			set_servo(adjust_x + current_servo_position[0], adjust_y + current_servo_position[1])

	return image

if __name__ == "__main__":
    capture = None
    
    if len(sys.argv)==1:
        capture = cvCreateCameraCapture( 0 )
    elif len(sys.argv)==2 and sys.argv[1].isdigit():
        capture = cvCreateCameraCapture( int(sys.argv[1]) )
    elif len(sys.argv)==2:
        capture = cvCreateFileCapture( sys.argv[1] ) 

    if not capture:
        print "Could not initialize capturing..."
        sys.exit(-1)
        
    cvNamedWindow( "Face Detection", 1 )
	set_servo()
	counter = 0
    while True:
        frame = cvQueryFrame( capture )
        if not frame:
            cvWaitKey(0)
            break
		
		detect(frame)
        
		#cvShowImage("Face Detection", detect(frame) )
		
		if counter >= servo_move_interval:
			servo_ready = True
			counter = 0
		
		counter += 1
		
        if cvWaitKey(10) != -1:
            break
	set_servo()
    cvDestroyWindow("Laplacian")
