# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 17:18:08 2015

@author: Charles
"""


import cv2

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')


cap = cv2.VideoCapture(0)

while(True):



    _, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        frame = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)

    cv2.imshow('frame', frame)

   
        # Condition de fin de la boucle ---------------------------------------

    k = cv2.waitKey(10) & 0xFF
    if k == ord('q'):
       break

# Fin de la boucle ----------------------------------------------------------------------------------------------


# fin du script
cap.release()
cv2.destroyAllWindows()





