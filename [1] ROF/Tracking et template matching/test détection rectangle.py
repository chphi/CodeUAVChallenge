# -*- coding: utf-8 -*-
"""
Created on Fri Feb 20 16:37:13 2015

@author: Charles

Programme test pour calibrer la détection d'un rectangle noir
Syntaxe pour open cv 3.0.0
"""



import cv2
import numpy as np
import BibliTracking as track


# Définition des variables, initialisation du programme -------------------------------------------------

is_cam_embarquee = True

# variables réglables
n_zone = 71                              # taille de la zone considérée pour le seuil adaptatif
v_moy = 40                               # valeur à enlever au seuil moyen
t_o = 5                                  # taille du noyau pour l'opening
n_gauss = 5                              # ordre du filtre gaussien pour flouter le patron
kernel = np.ones((t_o,t_o),np.uint8)     # noyau pour l'opening
seuil_aire = 0.9                         # rapport max entre l'aire d'un contour et l'aire du rectangle fitté 

# définition du rectangle noir
valeur_cible = 0                         
s_min = 0.9                              # solidité min
aire_min = 200                           # aire en dessous de laquelle un contour n'est pas considéré pertinent
aire_max = 30000                         # aire max. Les deux sont à adapter à l'altitude
r_min = .4                               # ratio grande dimension/petite dimension min
r_max = .6                               # ratio grande dimension/petite dimension max

rectangle = []

# lancement vidéo
capture = track.initVideoFlow(is_cam_embarquee)

# init trackbar
def nothing(x): pass 
cv2.createTrackbar('n_zone','frame',2, 151, nothing)
cv2.createTrackbar('v_moy', 'frame', 2, 100, nothing)


# Boucle -------------------------------------------------------------------------------------------------

while(True):

    # Lecture vidéo
    frame = track.getImage(is_cam_embarquee, capture)
    
    # récupération de la valeur de la trackbar, forçage à un nombre impair
    n_zone = cv2.getTrackbarPos('n_zone', 'frame')
    n_zone = n_zone + ( 1 - np.mod(n_zone,2) )         # 1er impair plus grand ou égal à n_blur_brut
    v_moy = cv2.getTrackbarPos('v_moy', 'frame')
    
    # Tracking du noir
    frame2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame2 = cv2.adaptiveThreshold(frame2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, n_zone, v_moy)
#    frame2 = cv2.GaussianBlur(frame2,(n_gauss,n_gauss),0)  # ajoute bcp de bruit
    frame2 = cv2.morphologyEx(frame2, cv2.MORPH_OPEN, kernel)

    # Calcul des contours
    _, contours, hierarchy = cv2.findContours(frame2.copy(), cv2.RETR_EXTERNAL ,cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(frame,contours, -1, (0,127,255), 1)
    
    # filtrage des contours pertinents
    rect_probables = track.trouveObjetsProbables(frame2, aire_min, aire_max, s_min, 1, r_min, r_max)
    for cnt in rect_probables:
        cv2.drawContours(frame, [cnt], -1, (0,255,0), 2)      # en vert  
        # fitte un rectangle
        rect = cv2.minAreaRect(cnt)
        # calcule l'aire du rectangle fitté
        aire_rect = rect[1][0] * rect[1][1]
        # calcule l'aire du contour trouvé
        M = cv2.moments(cnt)
        aire_cnt = M['m00'] 
        # si les aires sont suffisamment proches ( = contour très proche du rectangle en forme)
        if aire_cnt/aire_rect > seuil_aire:        
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(frame,[box],0,(0,0,255),3)
            M = cv2.moments(cnt)
            cx, cy = int(M['m10']/M['m00']) , int(M['m01']/M['m00'])
            cv2.circle(frame, (cx,cy), 1, (255,255,255), 3)
            rectangle = cnt
    
    # Affichage flux vidéo
    cv2.imshow('frame', frame)
    cv2.imshow('th', frame2)
   
    # Condition de fin de la boucle
    k = cv2.waitKey(10) & 0xFF
    if k == ord('q'):
       break


# Fin de la boucle ----------------------------------------------------------------------------------------------


# arrêt du script
track.endVideoFlow(is_cam_embarquee, capture)




















