import numpy as np
import cv2

cap = cv2.VideoCapture(0)
cv2.namedWindow("viewer")
cv2.moveWindow("viewer", 400, 0)

finish = False
while not finish:

    #Identificar objeto
    w,h = 240, 180
    x,y = int((640-w)/2), int((480-h)/2)
    trackWindow = (x,y,w,h)
    
    identificationDone = False
    while not identificationDone:
        _, frame = cap.read()
        frame = cv2.flip(frame, 1)
        
        cv2.rectangle(frame, (x,y), (x+w, y+h), 255)
        
        cv2.imshow("viewer", frame)
        key = cv2.waitKey(1) & 0xFF
        if key != 0xFF:
            identificationDone = True
    
    
    # set up the ROI for tracking
    roi = frame[y:y+h, x:x+w]
    cv2.imshow("target", roi)
    cv2.moveWindow("target", 0, 0)
    hsv_roi =  cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_roi, np.array((0., 60.,32.)), np.array((180.,255.,255.)))
    roi_hist = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180])
    cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX)
    
    # Setup the termination criteria, either 10 iteration or move by atleast 1 pt
    termCrit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
    
    done = False
    while(not done):
        
        _,frame = cap.read()
        frame = cv2.flip(frame, 1)
     
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv],[0],roi_hist,[0,180],1)

        # apply meanshift to get the new location
        points, trackWindow = cv2.CamShift(dst, trackWindow, termCrit)

        # Draw it on image
        pts = cv2.boxPoints(points)
        pts = np.int0(pts)
        cv2.polylines(frame,[pts],True, 255,2)
        cv2.imshow("viewer",frame)
   
        key = cv2.waitKey(1) & 0xFF
        if key != 0xFF:
            done = True            
            cv2.destroyWindow("target")
            if key == ord("q"):
                finish = True
 
cv2.destroyAllWindows()
cap.release()

