import numpy as np
import cv2

cap = cv2.VideoCapture(0)


startTracking = True
while startTracking:
    startTracking = False
    
    # take first frame of the video
    _,frame = cap.read()
    frame = cv2.flip(frame, 1)
    frame = cv2.GaussianBlur(frame, (5, 5), 5)
    
    # setup initial location of window
    r,h,c,w = 200,45,300,80  # simply hardcoded the values
    track_window = (c,r,w,h)
    orig_track = [(c,r),(c+w, r+h)]
    
    # set up the ROI for tracking
    roi = frame[r:r+h, c:c+w]
    hsv_roi =  cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_roi, np.array((0., 60.,32.)), np.array((180.,255.,255.)))
    roi_hist = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180])
    cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX)

    roi = cv2.bitwise_and(roi, roi, mask=mask)
    cv2.imshow('img1',roi)
    
    # Setup the termination criteria, either 10 iteration or move by atleast 1 pt
    term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
    
    while(1):
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        frame = cv2.GaussianBlur(frame, (5, 5), 5)
    
        if ret == True:
            
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            bp = cv2.calcBackProject([hsv],[0],roi_hist,[0,180],1)
    
            # apply meanshift to get the new location
            ret, track_window = cv2.CamShift(bp, track_window, term_crit)
    
            # Draw it on image
            pts = cv2.boxPoints(ret)
            pts = np.int0(pts)
            
            hsv[:,:,1:2] = 255
            output = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            
            cv2.rectangle(output,orig_track[0], orig_track[1],(255,0,0),2)
            cv2.polylines(output,[pts],True, (0,255,255),2)
            cv2.imshow('img2',output)
    
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('t'):
                startTracking = True
                break
    
        else:
            break

cv2.destroyAllWindows()
cap.release()

