from config import *

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
