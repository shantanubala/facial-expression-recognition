#!/usr/bin/python
from opencv.cv import *
from opencv.highgui import *
import sys
import os
import math
import filters
import conversion
from config import *

import pygame



#returns a region of an image as a new image object
def getRegion(img, x, y, width, height):
	dst = cvCreateImage(cvSize(int(width),int(height)),img.depth, img.nChannels)
	cvGetRectSubPix(img,dst,(x+width/2,y+height/2))
	return dst

#returns an Canny-edge-detected version of an image
def edge(image):
	grayscale = cvCreateImage(cvSize(image.width, image.height), 8, 1)
	cvCvtColor(image, grayscale, CV_BGR2GRAY)

	edges = cvCreateImage(cvGetSize(image),8, 1)
	cvCanny(grayscale,edges,60,60)

	cvSmooth(edges,edges,CV_GAUSSIAN, 5,0,0, 0)

	return edges

#sets the position of the pan and tilt servos and performs limit checks
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
	
	#usb_interface.set_target(1, tilt)
	#usb_interface.set_target(0, pan)

faceNum = 0

#the main detection logic
def detect(image):
	#Converts an image to grayscale for haar object detection
	grayscale = cvCreateImage(cvSize(image.width, image.height), 8, 1)
	cvCvtColor(image, grayscale, CV_BGR2GRAY)
	
	foundFace = find_frontal_face(grayscale, image)
			
	#if not foundFace:
	#	find_profile_face(grayscale, image)

	if servo_track_face and servo_ready:
		track_face()

	return image


#finds a frontal face with simple ratio-based features
def find_frontal_face(grayscale, image, foundFace=False):
	global face_locations
	global faceNum
	storage = cvCreateMemStorage(0)
	cvClearMemStorage(storage)
	faces = cvHaarDetectObjects(grayscale, cascade, storage, 2.0, 2, CV_HAAR_DO_CANNY_PRUNING, cvSize(50,50))
	f_x = None
	f_y = None
	f_width = None
	f_height = None
	if faces:
		for f in faces:
			foundFace = True
			print("[(%d,%d) -> (%d,%d)]" % (f.x, f.y, f.x+f.width, f.y+f.height))
			if save_objects:
				cvSaveImage("face//" + str(faceNum) + ".jpg", getRegion(image, f.x, f.y, f.width, f.height))
					
			if use_kalman_filtering:
				filters.face_x.correct(f.x)
				filters.face_y.correct(f.y)
				filters.face_l.correct(f.width)
				f_x = filters.face_x.get_prediction()
				f_y = filters.face_y.get_prediction()
				f_width = filters.face_l.get_prediction()
				f_height = f_width
			else:
				f_x = f.x
				f_y = f.y
				f_width = f.width
				f_height = f.height

			face_locations.append((f_x + (f_width / 2), f_y + (f_height / 2)))

			faceNum += 1
			for box in feature_boxes:
				boxX = f_x + (box[0] * (f_width/20))
				boxY = f_y + (box[1] * (f_height/20))
				boxWidth = box[2] * (f_width/20)
				boxHeight = box[3] * (f_height/20)
				
				if box == feature_boxes[0]:
					if show_objects:
						if show_object_edges:
							cvShowImage("Left Eye",  edge(getRegion(image, boxX,boxY,boxWidth,boxHeight)))
						else:
							cvShowImage("Left Eye",  getRegion(image, boxX,boxY,boxWidth,boxHeight))
					if save_objects:
						cvSaveImage("lefteye//" + str(faceNum) + ".jpg", getRegion(image, boxX,boxY,boxWidth,boxHeight))
				elif box == feature_boxes[1]:
					if show_objects:
						if show_object_edges:
							cvShowImage( "Right Eye",  edge(getRegion(image,boxX,boxY,boxWidth,boxHeight)))
						else:
							cvShowImage( "Right Eye",  getRegion(image,boxX,boxY,boxWidth,boxHeight))
					if save_objects:
						cvSaveImage("righteye//" + str(faceNum) + ".jpg", getRegion(image, boxX,boxY,boxWidth,boxHeight))
				elif box == feature_boxes[2]:
					if show_objects:
						if show_object_edges:
							cvShowImage("Mouth",  edge(getRegion(image, boxX,boxY,boxWidth,boxHeight)))
						else:
							cvShowImage("Mouth",  edge(getRegion(image, boxX,boxY,boxWidth,boxHeight)))
					if save_objects:
						cvSaveImage("mouth//" + str(faceNum) + ".jpg", getRegion(image, boxX,boxY,boxWidth,boxHeight))
				
				if draw_rect:
					cvRectangle(image, cvPoint( int(boxX), int(boxY) ), cvPoint(int(boxX + boxWidth), int(boxY + boxHeight)), 255, 3, 8, 0)
	if draw_rect and f_x and f_y and f_width and f_height:
		cvRectangle(image, cvPoint( int(f_x), int(f_y)), cvPoint(int(f_x + f_width), int(f_y + f_height)), 255, 3, 8, 0)
	return foundFace

#locates profile faces
def find_profile_face(grayscale, image, foundFace=False):
	global face_locations
	storage = cvCreateMemStorage(0)
	cvClearMemStorage(storage)

	faces = cvHaarDetectObjects(grayscale, profileCascade, storage, 2.0, 2, CV_HAAR_DO_CANNY_PRUNING, cvSize(50,50))

	for f in faces:
		if use_kalman_filtering and filters.face_x.prediction is not None and filters.face_y.prediction is not None and filters.face_l.prediction is not None:
			f_width = filters.face_l.get_prediction()
			f_height = f_width
			#since the profile face produces a much large square, we use the width of the frontal face kalman instead
			width_diff = (f.width - f_width) / 2
			filters.face_x.correct(f.x - width_diff)
			filters.face_y.correct(f.y + width_diff)
			f_x = filters.face_x.get_prediction()
			f_y = filters.face_y.get_prediction()
		else:
			f_x = f.x
			f_y = f.y
			f_width = f.width
			f_height = f.height
		if draw_rect:
			cvRectangle(image, cvPoint( int(f_x), int(f_y)), cvPoint(int(f_x + f_width), int(f_y + f_height)), 255, 3, 8, 0)
		foundFace = True
		face_locations.append((f_x + (f_width / 2), f_y + (f_height / 2)))

	if not foundFace:
		cvFlip(grayscale,None, 1)

		storage = cvCreateMemStorage(0)
		cvClearMemStorage(storage)

		faces = cvHaarDetectObjects(grayscale, profileCascade, storage, 2.0, 2, CV_HAAR_DO_CANNY_PRUNING, cvSize(50,50))

		for f in faces:
			if use_kalman_filtering and filters.face_x.prediction is not None and filters.face_y.prediction is not None and filters.face_l.prediction is not None:
				f_width = filters.face_l.get_prediction()
				f_height = f_width
				#since the profile face produces a much large square, we use the width of the frontal face kalman instead
				width_diff = (f.width - f_width) / 2
				filters.face_x.correct(cam_resolution[0] - (f.x - width_diff))
				filters.face_y.correct(cam_resolution[1] + width_diff)
				f_x = filters.face_x.get_prediction()
				f_y = filters.face_y.get_prediction()
			else:
				f_x = f.x
				f_y = f.y
				f_width = f.width
				f_height = f.height
			if draw_rect:
				cvRectangle(image, cvPoint( cam_resolution[0] - int(f_x), int(f_y)), cvPoint(cam_resolution[0] - int(f_x + f_width), int(f_y + f_height)), 255, 3, 8, 0)
			foundFace = True
			face_locations.append(( 640 - (f_x + (f_width / 2)), f_y + (f_height / 2)))

#moves servos according to the positions of faces
def track_face():
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
		
		#if the face is not within a radius of the center of the image, adjust servos
		if math.sqrt(pow(f_x - cam_center[0],2) + pow(f_y - cam_center[1],2)) > tracking_radius:
			adjust_x = (f_x - cam_center[0]) * servo_app[0][0] / servo_app[0][1]
			adjust_y = (cam_center[0] - f_y) * servo_app[1][0] / servo_app[1][1]
			
			set_servo(adjust_x + current_servo_position[0], adjust_y + current_servo_position[1])

if __name__ == "__main__":

    #pygame.camera.init()
    
    capture = None #declares the capture variable
    set_servo() #defaults servos to original position
    counter = 0 #the counter for the servo movement interval
	
	#checks to see if a camera is connected and exits if one is not
    if len(sys.argv)==1:
        capture = cvCreateCameraCapture( 0 )
    elif len(sys.argv)==2 and sys.argv[1].isdigit():
        capture = cvCreateCameraCapture( int(sys.argv[1]) )
    elif len(sys.argv)==2:
        capture = cvCreateFileCapture( sys.argv[1] ) 
	
    if not capture:
        print "Could not initialize capturing..."
        sys.exit(-1)
	
	#width and height are not actually set due to OpenCV bug
    cvSetCaptureProperty( capture, CV_CAP_PROP_FRAME_WIDTH, cam_resolution[0] )
    cvSetCaptureProperty( capture, CV_CAP_PROP_FRAME_HEIGHT, cam_resolution[1] )
	
	#the main highgui window for the camera frames
    cvNamedWindow( "Face Detection", 1 )
	
	#the windows for features (if enabled in configuration)
    if show_objects:
        cvNamedWindow( "Left Eye", 1 )
        cvNamedWindow( "Right Eye", 1 )
        cvNamedWindow( "Mouth", 1 )
		
    clock = pygame.time.Clock()

    while True:
        clock.tick()
        frame = cvQueryFrame(capture)
        clock.tick()
        print "capture in " + str(clock.get_time())
        
        if frame:
            img = detect(frame)
            cvShowImage("Face Detection",  frame)
            if counter >= servo_move_interval:
                servo_ready = True
                counter = 0
		
            counter += 1
        if cvWaitKey(10) != -1:
            break
		
    cvDestroyWindow("Face Detection")
