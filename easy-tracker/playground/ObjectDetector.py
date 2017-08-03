#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
Detector de Objetos
===================

Teclas:
'e' - Bordes
'g' - Blanco y negro
'r' - Rectángulos
'm' - Modo espejo | modo normal
'ESC' - Terminar

"""

import cv2 
import numpy as np
from math import sqrt

MAIN_WINDOW_NAME = "detector"
TRACKBAR_THRESHOLD1_NAME = "thres1"
TRACKBAR_THRESHOLD2_NAME = "thres2"

TRACKBAR_THRESHOLD1_INIT_VALUE = 100
TRACKBAR_THRESHOLD2_INIT_VALUE = 200

TRACKBAR_MIN_RECT_DIAG_NAME = "min-diag"
TRACKBAR_MIN_RECT_DIAG_INIT_VALUE = 100

IMG_DEST_GRAY = 0
IMG_DEST_EDGES = 1
IMG_DEST_RECTS = 2

class Origin(object):
    '''
    Referencia para determinar el riesgo de un objeto
    '''    
    
    def __init__(self, width, height):
        '''
        Constructor
        '''
        
        self._center = (width//2, height)
        self._color = (0, 0, 255)
        self._thickness = 3
        self._halfLength = 10 #1/2 de la longitud de las líneas que representan el origen
    
    def getScreenDistance(self, x, y):
        '''
        Obtiene la distancia entre un punto y el origen
        '''
        
        return sqrt((x-self._center[0])**2 + (y-self._center[1])**2)
        

    def drawHairCross(self, frame):
        '''
        Dibuja el origen en un frame
        '''
        
        hairCross = self._getHairCrossCoordinates()
        
        cv2.line(frame, hairCross[0], hairCross[1], self._color, self._thickness)
        cv2.line(frame, hairCross[2], hairCross[3], self._color, self._thickness)
        
    def _getHairCrossCoordinates(self):
        originCross = [
                        (self._center[0] - self._halfLength, self._center[1] - 1),
                        (self._center[0] + self._halfLength, self._center[1] - 1),
                        (self._center[0], self._center[1] - 1),
                        (self._center[0], self._center[1] - self._halfLength)
                       ]
        
        return originCross
    

class BoundingRectangle(object):
    '''
    Envuelve una característica (feature) en un rectángulo
    '''
    
    def __init__(self, boxPoints):
        '''
        Constructor
        '''
        
        self.boxPoints = boxPoints
        
    def getDiagonalLengthSq(self):
        '''
        Obtiene el cuadrado de la distancia de la diagonal (por eficiencia no se devuelve la raíz)
        '''
        
        return (self.boxPoints[2][0] - self.boxPoints[0][0])**2 \
            + (self.boxPoints[2][1] - self.boxPoints[0][1])**2
            
    def getBoxPoints(self):
        '''
        Obtiene los puntos de las esquinas del rectángulo
        '''
        
        return self.boxPoints
        

def onTrackbarChange(x):
    pass

class ObjectDetector(object):
    
    def __init__(self, videoSourceId, mirrorMode):
        
        self.cam = cv2.VideoCapture(videoSourceId)
        self.message = ""
        self.showImageMode = IMG_DEST_RECTS
        self.mirrorMode = mirrorMode
        
        cv2.namedWindow(MAIN_WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(MAIN_WINDOW_NAME, 512, 300)
        
        cv2.createTrackbar(TRACKBAR_THRESHOLD1_NAME, MAIN_WINDOW_NAME, 0, 255, onTrackbarChange)
        cv2.setTrackbarPos(TRACKBAR_THRESHOLD1_NAME, MAIN_WINDOW_NAME, TRACKBAR_THRESHOLD1_INIT_VALUE)
        cv2.createTrackbar(TRACKBAR_THRESHOLD2_NAME, MAIN_WINDOW_NAME, 0, 255, onTrackbarChange)
        cv2.setTrackbarPos(TRACKBAR_THRESHOLD2_NAME, MAIN_WINDOW_NAME, TRACKBAR_THRESHOLD2_INIT_VALUE)
        
        cv2.createTrackbar(TRACKBAR_MIN_RECT_DIAG_NAME, MAIN_WINDOW_NAME, 0, 500, onTrackbarChange)
        cv2.setTrackbarPos(TRACKBAR_MIN_RECT_DIAG_NAME, MAIN_WINDOW_NAME, TRACKBAR_MIN_RECT_DIAG_INIT_VALUE)
        
        #Determinar geometría de la pantalla
        _, frame = self.cam.read()        
        self.origin = Origin(frame.shape[1], frame.shape[0]) 
        
    def detect(self):
        
        while True:
            
            _, frame = self.cam.read()
            if self.mirrorMode:
                frame = cv2.flip(frame, 1)
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.blur(gray, (5,5))
            gray = cv2.equalizeHist(gray)
            
            thres1 = cv2.getTrackbarPos(TRACKBAR_THRESHOLD1_NAME, MAIN_WINDOW_NAME)
            thres2 = cv2.getTrackbarPos(TRACKBAR_THRESHOLD2_NAME, MAIN_WINDOW_NAME)
            edges = cv2.Canny(gray, thres1, thres2)
      
            try:
                _, contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            except:
                contours = []
            boundingRectangles = []
            
            minRectArea = cv2.getTrackbarPos(TRACKBAR_MIN_RECT_DIAG_NAME, MAIN_WINDOW_NAME)            
            for contour in contours:
                rect = cv2.minAreaRect(contour)
                box = np.int0(cv2.boxPoints(rect))
                boundingRect = BoundingRectangle(box)               
                if boundingRect.getDiagonalLengthSq() >= minRectArea**2:                     
                    boundingRectangles.append(boundingRect)                
            
            if self.showImageMode == IMG_DEST_RECTS:
                destImage = frame
                for rectangle in boundingRectangles:
                    box = rectangle.getBoxPoints()
                    cv2.polylines(frame, [box], True, (0,255,255), 2)
                    
            elif self.showImageMode == IMG_DEST_GRAY:
                destImage = gray
                            
            elif self.showImageMode == IMG_DEST_EDGES:
                destImage = edges
            
            self.showFrame(destImage)
            
            key = cv2.waitKey(5) & 0xff
            if key == 27:
                break
            elif key == ord('g'):
                self.showImageMode = IMG_DEST_GRAY
            elif key == ord('r'):
                self.showImageMode = IMG_DEST_RECTS
            elif key == ord('e'):
                self.showImageMode = IMG_DEST_EDGES
            elif key == ord('m'):
                self.mirrorMode = not self.mirrorMode
            
            
        cv2.destroyAllWindows()
        
    def showFrame(self, frame):
        #Añadir mensaje (si existe)
        if(self.message):
            cv2.putText(frame, self.message, (8,16), cv2.FONT_HERSHEY_PLAIN, 1.0, (0,255,255), thickness=1, lineType=cv2.CV_AA)
        
        self.origin.drawHairCross(frame)
        
        cv2.imshow(MAIN_WINDOW_NAME, frame)
        
            
if __name__ == '__main__':
    import sys
    try:
        videoSourceId = int(sys.argv[1])
        mirrorMode = False
    except:
        videoSourceId = 0
        mirrorMode = True
    
    if __doc__ != None:    
        print(__doc__)
    
    ObjectDetector(videoSourceId, mirrorMode).detect()
    