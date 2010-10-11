import cv
import sys
import os
import math
import filters
import pdb
import conversion
from config import *

import pygame
#from pygame.camera import *

from pygame.locals import *

import glove

#returns a region of an image as a new image object
def getRegion(img, x, y, width, height):
    dst = cv.CreateImage((int(width),int(height)),img.depth, img.nChannels)
    cv.GetRectSubPix(img,dst,(x+width/2,y+height/2))
    return dst

#returns an Canny-edge-detected version of an image
def edge(image):
    grayscale = cv.CreateImage((image.width, image.height), 8, 1)
    cv.CvtColor(image, grayscale, cv.CV_BGR2GRAY)

    edges = cv.CreateImage(cv.GetSize(image),8, 1)
    cv.Canny(grayscale,edges,60,60)

    #cv.Smooth(edges,edges,cv.CV_BLUR)

    return edges
    
def grayedge(grayscale):

    edges = cv.CreateImage(cv.GetSize(grayscale),8, 1)
    cv.Canny(grayscale,edges,60,60)

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
    
    usb_interface.set_target(1, tilt)
    usb_interface.set_target(0, pan)

faceNum = 0

#the main detection logic
def detect(image):
    #Converts an image to grayscale for haar object detection
    grayscale = cv.CreateImage((image.width, image.height), 8, 1)
    cv.CvtColor(image, grayscale, cv.CV_BGR2GRAY)
    
    foundFace = find_frontal_face(grayscale, image)
            
    #if not foundFace:
    #   find_profile_face(grayscale, image)

    if servo_track_face and servo_ready:
        track_face()

    return image
    
#Eye state detection
calibdist = []
normaldist = 0

def eyeDetect(image):
    global normaldist
    global calibdist
    
    dist = 0
    
    lines = []
    
    line = None
    
    for x in range(numlines):
        lines.append(getRegion(image, image.width/2 - numlines/2 + x , 0 , 1 , image.height))
        
        if x == 0:
            line = lines[x]
        else:
            cv.Add(line,lines[x],line)
        
    cv.Smooth(line,line,cv.CV_BLUR)
    
    if showlines:
        inten = cv.CreateImage((255, image.height), 8, 3)
        cv.Set(inten,(0,0,0))
        
        inten2 = cv.CreateImage((50, image.height), 8, 3)
        cv.Set(inten2,(0,0,0))
        
        for x in range(image.height):
            intensity = cv.Get2D(line,x,0)[0]
            cv.Line(inten, (0,x), ((intensity),x), (255,255,255))
            
            if x > 0:
                slope = (cv.Get2D(line,x,0)[0] - cv.Get2D(line,x-1,0)[0]) / 255
                
                cv.Line(inten2, (25,x), ((slope*25) + 25,x), (255,255,255))
                
        zero = []
        
        for x in range(image.height):
            if x > 1:
                slope1 = (cv.Get2D(line,x,0)[0] - cv.Get2D(line,x-1,0)[0])
                slope2 = (cv.Get2D(line,x-1,0)[0] - cv.Get2D(line,x-2,0)[0])
                
                intensity = cv.Get2D(line,x,0)[0] / 255
                
                if slope1 > 0 and slope2 < 0 and intensity < intensityCutoff:
                    zero.append(x)
                    
        for x in zero:
            cv.Line(inten2, (0,x), (50,x), (255,0,0))
            
            cv.Line(image, (0,x), (image.width,x), (255,0,0))
            
        if len(zero) > 1:
            
            cv.Line(inten2, (0,x), (50,x), (255,0,0))
            dist = (zero[1] - zero[0])/float(image.height)
            
            cv.Line(inten2, (0,zero[1]-normaldist*image.height), (50,zero[1]-normaldist*image.height), (0,255,0))
            
            #cv.Line(image, (0,zero[0]), (image.width,zero[0]), (255,0,0))
            
            #cv.Line(image, (0,zero[1]), (image.width,zero[1]), (255,0,0))
            
            
            if len(calibdist) < calibmax:
                calibdist.append(dist)
                
                normaldist = 0
                for i in calibdist:
                    normaldist = normaldist + i
                    
                normaldist = normaldist/len(calibdist)
            '''else:
                if dist > normaldist*1.05:
                    print "Eyebrows Up"
                else:
                    print "Eyebrows Down"'''
            
        cv.ShowImage("Eye Intensity",  inten)
        
        large = cv.CreateImage((50*3, image.height*3), 8, 3)
        cv.Resize(inten2, large)
        cv.ShowImage("Eye Intensity Deriv",  large)
            
        
        cv.ShowImage("Eye Line",  line)
        cv.SaveImage("eyeline//" + str(faceNum) + ".jpg", line)
        
    return dist

frames = 0

#finds a frontal face with simple ratio-based features
def find_frontal_face(grayscale, image, foundFace=False):
    global face_locations
    global faceNum
    global frames
    
    storage = cv.CreateMemStorage(0)
    faces = cv.HaarDetectObjects(grayscale, cascade, storage, 2.0, 2, cv.CV_HAAR_DO_CANNY_PRUNING, (50,50))
    #print faces
    f_x = None
    f_y = None
    f_width = None
    f_height = None
    
    leye = None
    reye = None
    
    if faces:
        for ((x, y, w, h), n) in faces:
            foundFace = True            
            #print("[(%d,%d) -> (%d,%d)]" % (x, y, w, h))
            if save_objects:
                cv.SaveImage("face//" + str(faceNum) + ".jpg", getRegion(image, x, y, w, h))
                    
            if use_kalman_filtering:
                filters.face.correct(x, y, w)
                p = filters.face.get_prediction()
                f_x = p[0, 0]
                f_y = p[1, 0]
                f_width = p[2, 0]
                f_height = f_width
            else:
                f_x = x
                f_y = y
                f_width = w
                f_height = h

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
                            cv.ShowImage("Left Eye",  edge(getRegion(image, boxX,boxY,boxWidth,boxHeight)))
                        else:
                            
                            leye = getRegion(grayscale, boxX,boxY,boxWidth,boxHeight)
                            
                            cv.EqualizeHist(leye,leye)
                            
                            
                    if save_objects:
                        cv.SaveImage("lefteye//" + str(faceNum) + ".jpg", getRegion(image, boxX,boxY,boxWidth,boxHeight))
                        
                    cv.ShowImage("Left Eye",  leye)
                        
                elif box == feature_boxes[1]:
                    if show_objects:
                        if show_object_edges:
                            cv.ShowImage( "Right Eye",  edge(getRegion(image,boxX,boxY,boxWidth,boxHeight)))
                        else:
                            #cv.ShowImage( "Right Eye",  getRegion(grayscale,boxX,boxY,boxWidth,boxHeight))
                            
                            reye = getRegion(grayscale,boxX,boxY,boxWidth,boxHeight)
                            
                            cv.EqualizeHist(reye,reye)
                            
                    if save_objects:
                        cv.SaveImage("righteye//" + str(faceNum) + ".jpg", getRegion(image, boxX,boxY,boxWidth,boxHeight))
                        
                    cv.ShowImage("Right Eye", reye)
                    
                elif box == feature_boxes[2]:
                    if show_objects:
                        if show_object_edges:
                            cv.ShowImage("Mouth",  edge(getRegion(image, boxX,boxY,boxWidth,boxHeight)))
                        else:
                            cv.ShowImage("Mouth",  getRegion(grayscale, boxX,boxY,boxWidth,boxHeight))
                    if save_objects:
                        cv.SaveImage("mouth//" + str(faceNum) + ".jpg", getRegion(image, boxX,boxY,boxWidth,boxHeight))
                
                if draw_rect:
                    cv.Rectangle(image, ( int(boxX), int(boxY) ), (int(boxX + boxWidth), int(boxY + boxHeight)), 255, 3, 8, 0)
    else:
        glove.turn_off()
        
    if emotion and leye and reye:
        ldist = eyeDetect(leye)
        
        rdist = eyeDetect(reye)
        
        
        if (len(calibdist) >= calibmax) and ldist > 0 and rdist > 0:
            #print ldist * leye.height,  rdist * reye.height
            #print rdist * reye.height
            
            frames += 1
            
            dist = (ldist + rdist)/2
            
            if frames == 3:
                glove.turn_off()
            
            if frames > 10:
            
                if dist > normaldist*1.1:
                    print "Up"
                    glove.send_left(2)
                    glove.send_right(2)
                else:
                    print "Down"
                    glove.send_left(1)
                    glove.send_right(1)
                
                '''if rdist > normaldist*1.1:
                    print "Right - Up"
                    glove.send_right(2)
                else:
                    print "Right - Down"
                    glove.send_right(1)'''
                    
                frames = 0
        else:
            glove.turn_off()
            
        
    if draw_rect and f_x and f_y and f_width and f_height:
        cv.Rectangle(image, ( int(f_x), int(f_y)), (int(f_x + f_width), int(f_y + f_height)), 255, 3, 8, 0)
    return foundFace

#locates profile faces
def find_profile_face(grayscale, image, foundFace=False):
    global face_locations
    storage = cv.CreateMemStorage(0)

    faces = cv.HaarDetectObjects(grayscale, profileCascade, storage, 2.0, 2, cv.CV_HAAR_DO_CANNY_PRUNING, (50,50))

    for f in faces:
        if use_kalman_filtering and filters.face.prediction != None:
            p = filters.face.prediction
            f_width = p[2, 0]
            f_height = f_width
            #since the profile face produces a much large square, we use the width of the frontal face kalman instead
            width_diff = (f.width - f_width) / 2
            filters.face.correct(f.x - width_diff, f.y + width_diff)
            p = filters.face.get_prediction()
            f_x = p[0, 0]
            f_y = p[1, 0]
        else:
            f_x = f.x
            f_y = f.y
            f_width = f.width
            f_height = f.height
        if draw_rect:
            cv.Rectangle(image, cvPoint( int(f_x), int(f_y)), cvPoint(int(f_x + f_width), int(f_y + f_height)), 255, 3, 8, 0)
        foundFace = True
        face_locations.append((f_x + (f_width / 2), f_y + (f_height / 2)))

    if not foundFace:
        cv.Flip(grayscale,None, 1)

        storage = cv.CreateMemStorage(0)

        faces = cv.HaarDetectObjects(grayscale, profileCascade, storage, 2.0, 2, cv.CV_HAAR_DO_CANNY_PRUNING, (50,50))

        for f in faces:
            if use_kalman_filtering and filters.face.prediction != None:
                p = filters.face.prediction
                f_width = p[2, 0]
                f_height = f_width
                #since the profile face produces a much large square, we use the width of the frontal face kalman instead
                width_diff = (f.width - f_width) / 2
                filters.face.correct(cam_resolution[0] - (f.x - width_diff), cam_resolution[1] + width_diff)
                p = filters.face.get_prediction()
                f_x = p[0, 0]
                f_y = p[1, 0]
            else:
                f_x = f.x
                f_y = f.y
                f_width = f.width
                f_height = f.height
            if draw_rect:
                cv.Rectangle(image, cvPoint( cam_resolution[0] - int(f_x), int(f_y)), cvPoint(cam_resolution[0] - int(f_x + f_width), int(f_y + f_height)), 255, 3, 8, 0)
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
            

'''
if __name__ == "__main__":
    if servo_track_face:
        set_servo() #defaults servos to original position
    counter = 0 #the counter for the servo movement interval
    pygame.camera.init()
    #checks to see if a camera is connected and exits if one is not
    
    camlist = pygame.camera.list_cameras()
    
    
    if not camlist:
        sys.exit()
    
    for c in camlist:
        cam = pygame.camera.Camera(c, cam_resolution)
        if cam:
            break
    cam.start()
    
    #capture = None
    
    #if len(sys.argv)==1:
    #capture = cv.CaptureFromCAM(-1)
   # elif len(sys.argv)==2:
        #capture = cv.CaptureFromFile( sys.argv[1] ) 
        
   #if not capture:
     #   print "Could not initialize capturing..."
      #  sys.exit(-1)
    
    #the main highgui window for the camera frames
    cv.NamedWindow( "Face Detection", 1 )
    
    #the windows for features (if enabled in configuration)
    if show_objects:
        cv.NamedWindow( "Left Eye", 1 )
        cv.NamedWindow( "Right Eye", 1 )
        cv.NamedWindow( "Mouth", 1 )
        
    clock = pygame.time.Clock()
    
    screen = pygame.display.set_mode((800,600))

    while True:
        #clock.tick()
        pyframe = cam.get_image()
        #clock.tick()
        #print "capture in ", str(clock.get_time())
        #frame = 
        
        #print
        
        screen.blit(pyframe, pyframe.get_rect())
        
        pygame.display.flip()
        
        #frame = cv.QueryFrame(capture)
        #clock.tick()
        #print "Converted in " + str(clock.get_time())
        
        if pyframe:
            clock.tick()
            img = conversion.surf2CV(pyframe)
            clock.tick()
            print "detect in ", str(clock.get_time())
            cv.ShowImage("Face Detection",  img)
            if counter >= servo_move_interval:
                servo_ready = True
                counter = 0
        
            counter += 1
        if cv.WaitKey(5) != -1:
            break
        
    cv.DestroyWindow("Face Detection")
    

'''

if __name__ == "__main__":
    glove.turn_off()
    #capture = None #declares the capture variable
    set_servo() #defaults servos to original position
    counter = 0 #the counter for the servo movement interval
        
        #checks to see if a camera is connected and exits if one is not
    #if len(sys.argv)==1:
    capture = cv.CaptureFromCAM( -1 )
    #elif len(sys.argv)==2:
        #capture = cv.CaptureFromFile( sys.argv[1] ) 
    
    if not capture:
        print "Could not initialize capturing..."
        sys.exit(-1)
        
        #width and height are not actually set due to OpenCV bug
        
        #the main highgui window for the camera frames
    cv.NamedWindow( "Face Detection", 1 )
        
        #the windows for features (if enabled in configuration)
    if show_objects:
        cv.NamedWindow( "Left Eye", 1 )
        cv.NamedWindow( "Right Eye", 1 )
        cv.NamedWindow( "Mouth", 1 )
        
    if showlines:
        cv.NamedWindow( "Eye Line", 1 )
        cv.NamedWindow( "Eye Intensity", 1 )
        cv.NamedWindow( "Eye Intensity Deriv", 1 )
                
    #clock = pygame.time.Clock()

    while True:
        #clock.tick()
        frame = cv.QueryFrame(capture)
        #clock.tick()
        #print "capture in ", str(clock.get_time())
        
        if frame:
            #clock.tick()
            img = detect(frame)
            #clock.tick()
            #print "detect in ", str(clock.get_time())
            cv.ShowImage("Face Detection",  img)
            if counter >= servo_move_interval:
                servo_ready = True
                counter = 0
                
            counter += 1
        if cv.WaitKey(10) != -1:
            break
                
    cv.DestroyWindow("Face Detection")
    glove.turn_off()
