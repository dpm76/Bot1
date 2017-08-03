import cv2
import numpy as np

MIN_MATCH_COUNT = 5
LINE_AA = 16

cap = cv2.VideoCapture(0)
cv2.namedWindow("viewer")
finder = cv2.ORB_create()

FLANN_INDEX_KDTREE = 0
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks = 50)
#matcher = cv2.FlannBasedMatcher(index_params, search_params) 
matcher = cv2.BFMatcher(cv2.NORM_HAMMING2, crossCheck=True)

finish = False
while not finish:
    #Identificar objeto
    w,h = 240, 180
    x,y = (640-w)//2, (480-h)//2 
    
    identifyDone = False
    while not identifyDone:
        _, frame = cap.read()
        frame = cv2.flip(frame, 1)
        cv2.rectangle(frame, (x,y), (x+w, y+h), 255)
        
        cv2.imshow("viewer", frame)
        key = cv2.waitKey(1) & 0xFF
        if key != 0xFF:
            identifyDone = True
    
    #Obtener keypoints del objeto
    target = frame[y:y+h, x:x+w]
    
    kp1, des1 = finder.detectAndCompute(target, None)
    target = cv2.drawKeypoints(target, kp1, target, color=(0, 255, 255), flags= 0)
    
    cv2.imshow("target", target)
    cv2.moveWindow("target", 640, 0)
            
    done = False
    while not done:
        _, frame = cap.read()
        frame = cv2.flip(frame, 1)
        
        kp2, des2 = finder.detectAndCompute(frame, None)
        #matches = matcher.knnMatch(np.asarray(des1,np.float32), np.asarray(des2, np.float32), k=2)
        matches = matcher.match(des1, des2)

        # Sort them in the order of their distance.
        goodMatches = sorted(matches, key = lambda x:x.distance)[:10]
        '''
        goodMatches = []
        for m,n in matches:
            if m.distance < 0.7*n.distance:
                goodMatches.append(m)
        '''
        
        if len(goodMatches)>MIN_MATCH_COUNT:
            src_pts = np.float32([ kp1[m.queryIdx].pt for m in goodMatches ]).reshape(-1,1,2)
            dst_pts = np.float32([ kp2[m.trainIdx].pt for m in goodMatches ]).reshape(-1,1,2)
        
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
            matchesMask = mask.ravel().tolist()
        
            h,w,_ = target.shape
            pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
            dst = cv2.perspectiveTransform(pts,M)
        
            cv2.polylines(frame,[np.int32(dst)],True,(0, 255, 0),2, LINE_AA)
        else:
            # Draw first N matches.
            for m in goodMatches:
                # draw the keypoints
                # print m.queryIdx, m.trainIdx, m.distance
                cv2.circle(frame, (int(kp2[m.trainIdx].pt[0]), int(kp2[m.trainIdx].pt[1])), 2, (0,255,255))
            
        
        cv2.imshow("viewer", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key != 0xFF:
            done = True            
            cv2.destroyWindow("target")
            if key == ord("q"):
                finish = True

print("Finalizando")
cv2.destroyAllWindows()
cap.release()