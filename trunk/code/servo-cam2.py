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

#servo_app = ((210, 100), (210, 100))
servo_app = ((50, 100), (50, 100))

servo_move_interval = 1
servo_ready = True
face_locations = []

draw_rect = True

#this is for additional boxes to be drawn (out of 20x20) over the face
#the configuration is in the form of 4-element tuples
#the boxes are in the form of (x, y, length, width)
feature_boxes = [
	#left eye
	(2, 5, 6, 6),
	#right eye
	(11, 5, 6, 6),
	#mouth
	(4, 12.5, 12, 6)
]

#the following configuration variables are automatically set
cam_center = (cam_resolution[0] / 2, cam_resolution[1] / 2)
center_box = ((cam_center[0] - (center_box_dim[0] / 2), cam_center[0] + (center_box_dim[0] / 2)), 
				(cam_center[1] - (center_box_dim[1] / 2), cam_center[1] + (center_box_dim[1] / 2)))

profileCascade = cvLoadHaarClassifierCascade('/usr/share/opencv/haarcascades/haarcascade_profileface.xml', cvSize(1,1))

cascade = cvLoadHaarClassifierCascade('/usr/share/opencv/haarcascades/haarcascade_frontalface_alt.xml', cvSize(1,1))
bigeye_cascade = cvLoadHaarClassifierCascade('/usr/share/opencv/haarcascades/haarcascade__mcs_righteye.xml', cvSize(1,1))
smalleye_cascade = cvLoadHaarClassifierCascade('/usr/share/opencv/haarcascades/haarcascade_mcs_eyepair_small.xml', cvSize(1,1))
mouth_cascade = cvLoadHaarClassifierCascade('/usr/share/opencv/haarcascades/haarcascade_mcs_mouth.xml', cvSize(1,1))
feature_locate_interval = 100
usb_interface = test.PololuUsb()

def getRegion(img,x,y,width,height):
	#cvSetImageROI(img,cvRect(x,y,width,height))
	#subimage = cvCreateImage(cvGetSize(image),image.depth, image.nChannels)
	#subimage.origin = image.origin
	#cvCopy(image, subimage, NULL)
	dst = cvCreateImage(cvSize(int(width),int(height)),img.depth, img.nChannels)
	cvGetRectSubPix(img,dst,(x+width/2,y+height/2))
	return dst

def edge(image):
	grayscale = cvCreateImage(cvSize(image.width, image.height), 8, 1)
	cvCvtColor(image, grayscale, CV_BGR2GRAY)

	edges = cvCreateImage(cvGetSize(image),8, 1)
	cvCanny(grayscale,edges,60,60)

	cvSmooth(edges,edges,CV_GAUSSIAN, 5,0,0, 0)

	return edges

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

def locate_features(face_img):

	face_x_size = 20.0 /face_img.width
	face_y_size = 20.0 /face_img.height

	storage = cvCreateMemStorage(0)
	cvClearMemStorage(storage)
	
	eyepair = cvHaarDetectObjects(face_img, smalleye_cascade, storage, 1.2, 2, CV_HAAR_DO_CANNY_PRUNING)

	for f in eyepair:
		cvRectangle(face_img, cvPoint( int(f.x), int(f.y)), cvPoint(int(f.x + f.width), int(f.y + f.height)), 255, 3, 8, 0)
		feature_boxes[0] = (f.x * face_x_size,f.y * face_y_size, f.width * face_x_size * 0.4, f.height * face_y_size)

		feature_boxes[1] = ((f.x + f.width * 0.6) * face_x_size,f.y * face_y_size, f.width * face_x_size * 0.4, f.height * face_y_size)

	storage = cvCreateMemStorage(0)
	cvClearMemStorage(storage)
	
	'''mouth = cvHaarDetectObjects(face_img, mouth_cascade, storage, 1.2, 2, CV_HAAR_DO_CANNY_PRUNING)

	for f in mouth:
		cvRectangle(face_img, cvPoint( int(f.x), int(f.y)), cvPoint(int(f.x + f.width), int(f.y + f.height)), 255, 3, 8, 0)
	'''

	'''cvClearMemStorage(storage)
	r_eye = cvHaarDetectObjects(face_img, r_eye_cascade, storage, 1.2, 2, CV_HAAR_DO_CANNY_PRUNING)
	
	cvClearMemStorage(storage)
	mouth = cvHaarDetectObjects(face_img, mouth_cascade, storage, 1.2, 2, CV_HAAR_DO_CANNY_PRUNING)
	
	face_x_size = 20 / cvGetSize(face_img).width
	face_y_size = 20 / cvGetSize(face_img).height
	
	for f in l_eye:
		
		'''

frameNum = 0

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
	#cvEqualizeHist(grayscale, grayscale)
	
	faces = cvHaarDetectObjects(grayscale, cascade, storage, 2.0, 2, CV_HAAR_DO_CANNY_PRUNING, cvSize(50,50))
	global servo_ready

	foundFace = False

	global frameNum

	if faces:
		for f in faces:
			foundFace = True
			print("[(%d,%d) -> (%d,%d)]" % (f.x, f.y, f.x+f.width, f.y+f.height))
			faceimg = getRegion(grayscale, f.x, f.y, f.width, f.height)
			cvSaveImage("face//" + str(frameNum) + ".jpg", getRegion(image, f.x, f.y, f.width, f.height))
			#locate_features(faceimg)			
			
			if draw_rect:
				cvRectangle(image, cvPoint( int(f.x), int(f.y)), cvPoint(int(f.x + f.width), int(f.y + f.height)), 255, 3, 8, 0)

			face_locations.append((f.x + (f.width / 2), f.y + (f.height / 2)))

			frameNum += 1
			for box in feature_boxes:
				boxX = f.x + box[0]*(f.width/20)
				boxY = f.y + box[1]*(f.height/20)
				boxWidth = box[2]*(f.width/20)
				boxHeight = box[3]*(f.height/20)
				
				if box == feature_boxes[0]:
					cvShowImage("Left Eye",  edge(getRegion(image, boxX,boxY,boxWidth,boxHeight)))
					cvSaveImage("lefteye//" + str(frameNum) + ".jpg", getRegion(image, boxX,boxY,boxWidth,boxHeight))
					
				if box == feature_boxes[1]:
					cvShowImage( "Right Eye",  edge(getRegion(image,boxX,boxY,boxWidth,boxHeight)))
					cvSaveImage("righteye//" + str(frameNum) + ".jpg", getRegion(image, boxX,boxY,boxWidth,boxHeight))

				if box == feature_boxes[2]:
					cvShowImage("Mouth",  edge(getRegion(image, boxX,boxY,boxWidth,boxHeight)))
					cvSaveImage("mouth//" + str(frameNum) + ".jpg", getRegion(image, boxX,boxY,boxWidth,boxHeight))
				
				if draw_rect:
					cvRectangle(image, cvPoint( int(boxX), int(boxY) ), cvPoint(int(boxX + boxWidth), int(boxY + boxHeight)), 255, 3, 8, 0)
			
			
		if foundFace == False:
			storage = cvCreateMemStorage(0)
			cvClearMemStorage(storage)

			faces = cvHaarDetectObjects(grayscale, profileCascade, storage, 2.0, 2, CV_HAAR_DO_CANNY_PRUNING, cvSize(50,50))

			for f in faces:
				if draw_rect:
					cvRectangle(image, cvPoint( int(f.x), int(f.y)), cvPoint(int(f.x + f.width), int(f.y + f.height)), 255, 3, 8, 0)
				foundFace = True
				face_locations.append((f.x + (f.width / 2), f.y + (f.height / 2)))

			if foundFace == False:
				cvFlip(grayscale,None, 1)

				storage = cvCreateMemStorage(0)
				cvClearMemStorage(storage)

				faces = cvHaarDetectObjects(grayscale, profileCascade, storage, 2.0, 2, CV_HAAR_DO_CANNY_PRUNING, cvSize(50,50))

				for f in faces:
					if draw_rect:
						cvRectangle(image, cvPoint( 640 - int(f.x), int(f.y)), cvPoint(640 - int(f.x + f.width), int(f.y + f.height)), 255, 3, 8, 0)
					foundFace = True
					face_locations.append(( 640 - (f.x + (f.width / 2)), f.y + (f.height / 2)))



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
	counter2 = 0
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
	cvSetCaptureProperty( capture, CV_CAP_PROP_FPS, 16 )

	cvNamedWindow( "Face Detection", 1 )

	cvNamedWindow( "Left Eye", 1 )
	cvNamedWindow( "Right Eye", 1 )
	cvNamedWindow( "Mouth", 1 )
	
	#TODO: refine calibration using corner detection
	#calibrate(capture)

	while True:
		frame = cvQueryFrame(capture)
		if frame:
			img, pos = detect(frame,True)
			cvShowImage("Face Detection",  img)
			if counter >= servo_move_interval:
				servo_ready = True
				counter = 0
		
			counter += 1
			counter2 += 1
			if cvWaitKey(10) != -1:
				break
		
	cvDestroyWindow("Face Detection")
