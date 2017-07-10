'''
Created on 9 jul. 2017

@author: david
'''

import cv2

def main():
    
    cap = cv2.VideoCapture(0)
    
    done = False
    
    while not done:
    
        # Take each frame
        _, frame = cap.read()
    
        cv2.imshow('frame',frame)
        k = cv2.waitKey(5) & 0xFF
        done = k == 27 #ESC

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()