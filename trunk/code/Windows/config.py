#from maestro import test
import cv

image_scale = 4
#all configuration tuples follow the following patterns: 
#       (pan, tilt) and/or (x, y) and/or (min, max) and/or (servo_adjustment, pixel_width)
cam_resolution = (320,240) #the resolution of captured image - this is a placeholder
start_servo_position = (5984, 6400) #the positions - (pan, tilt) - to set the servos when the script is first run
current_servo_position = (5984, 6400) #holds the position of the servos - (pan, tilt)
servo_limits = ((3968, 8000), (4800, 8000)) #the extremities of servo motion
#NOTE: servo positions are set in integer values of quarter microseconds for the PWM

servo_app = ((100, 100), (100, 100)) #the change in servo position corresponding to the change in pixel position
#                                           follows the format: ((pan_change, x_px_change), (tilt_change, y_px_change))

servo_move_interval = 3 #the interval in frames at which the servo tracks the face
tracking_radius = 75 #the servos will not move if the face is within this number of px from the center
servo_ready = True #holds the state of the servo according to the servo interval
face_locations = [] #holds the locations of faces between servo intervals (replace with Kalman filter)
#usb_interface = test.PololuUsb() #the object interface for the pololu usb maestro
draw_rect = True #option to display blue rectangles around a detected object
save_objects = False #option to save detected objects to separate files
show_objects = True #option to show detected objects in separate windows
show_object_edges = True #option to show the edges of detected objects in their respective windows
servo_track_face = False #option to track faces
use_kalman_filtering = True #option to use Kalman filtering on face tracking

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
cam_center = (cam_resolution[0] / 2, cam_resolution[1] / 2) #center point of camera - (x, y)
#all of the Haar XML cascades
profileCascade = cv.Load('C:\OpenCV2.1\data\haarcascades\haarcascade_profileface.xml')
cascade = cv.Load('C:\OpenCV2.1\data\haarcascades\haarcascade_frontalface_alt.xml')
#bigeye_cascade = cv.Load('C:\OpenCV2.1\data\haarcascades\haarcascade__mcs_righteye.xml')
#smalleye_cascade = cv.Load('C:\OpenCV2.1\data\haarcascades\haarcascade_mcs_eyepair_small.xml')
#mouth_cascade = cv.Load('C:\OpenCV2.1\data\haarcascades\haarcascade_mcs_mouth.xml')

