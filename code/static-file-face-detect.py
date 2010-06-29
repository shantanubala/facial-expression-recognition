#!/usr/bin/python

# face_detect.py

# Face Detection using OpenCV. Based on sample code from:
# http://python.pastebin.com/m76db1d6b

# Usage: python face_detect.py <image_file>

import sys, os
from opencv.cv import *
from opencv.highgui import *

def detectObjects(image, name="image"):
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
    for f in faces:
      print("[(%d,%d) -> (%d,%d)]" % (f.x, f.y, f.x+f.width, f.y+f.height))
      cvRectangle(image, cvPoint( int(f.x), int(f.y)), cvPoint(int(f.x + f.width), int(f.y + f.height)), 255, 3, 8, 0)

  cvSaveImage(name + '-face.jpg', image)
 

def main():
  arg = sys.argv[1]
  image = cvLoadImage(arg)
  detectObjects(image, arg)

if __name__ == "__main__":
  main()
