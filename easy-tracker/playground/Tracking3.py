import cv2
import numpy as np

cap = cv2.VideoCapture(0)

ret, frame1 = cap.read()
frame1 = cv2.flip(frame1, 1)
prvs = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
hsv = np.zeros_like(frame1)
hsv[...,1] = 255

flow = None

while(1):
    ret, frame2 = cap.read()
    frame2 = cv2.flip(frame2, 1) 
    gray = cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)

    flow = cv2.calcOpticalFlowFarneback(prvs,gray, flow, 0.5,3,15,3,5,1.2,0)

    mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
    hsv[...,0] = ang*180/np.pi/2
    hsv[...,2] = cv2.normalize(mag,None,0,255,cv2.NORM_MINMAX)
    rgb = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)

    cv2.imshow('frame2',rgb)
    k = cv2.waitKey(30) & 0xff
    if k == ord('q'):
        break
    
    prvs = gray

cap.release()
cv2.destroyAllWindows()
