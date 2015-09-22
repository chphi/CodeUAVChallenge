# -*- coding: utf-8 -*-
"""
Created on Fri Feb 20 16:37:13 2015

@author: Charles

Programme test pour calibrer la détection d'un rectangle noir
Syntaxe pour open cv 3.0.0
"""


import sys
import cv2
import numpy as np


# Définition des variables, initialisation du programme -------------------------------------------------

conf_path = 'D:/Charles/Documents/Sumo/Dassault UAV Challenge/Code/CodeUAVChallenge'

is_cam_embarquee = False

# variables réglables
n_zone = 71                              # taille de la zone considérée pour le seuil adaptatif
v_moy = 40                               # valeur à enlever au seuil moyen
t_o = 5                                  # taille du noyau pour l'opening
n_gauss = 5                              # ordre du filtre gaussien pour flouter le patron
kernel = np.ones((t_o,t_o),np.uint8)     # noyau pour l'opening
seuil_aire = 0.95                        # rapport max entre l'aire d'un contour et l'aire du rectangle fitté 

# définition du rectangle noir
valeur_cible = 0                         
s_min = 0.9                              # solidité min
aire_min = 200                           # aire en dessous de laquelle un contour n'est pas considéré pertinent
aire_max = 30000                         # aire max. Les deux sont à adapter à l'altitude
r_min = .4                               # ratio grande dimension/petite dimension min
r_max = .6                               # ratio grande dimension/petite dimension max

rectangle = []


# Initialisations --------------------------------------------------------------

# importe la configuration
sys.path.append(conf_path)
import conf_drone as cf

# importe biblis persos
sys.path.append(cf.libpath)
import BibliTracking as track

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
    th = cv2.adaptiveThreshold(frame2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, n_zone,v_moy)
    opening = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)
    
    # Calcul des contours
    _, contours, hierarchy = cv2.findContours(opening.copy(), cv2.RETR_EXTERNAL ,cv2.CHAIN_APPROX_SIMPLE)
    
    # 1ère passe : filtrage des contours pertinents (aire, solidité, ratio de longueurs)
    cnt_pertinents = track.trouveObjetsProbables(opening, aire_min, aire_max, cf.s_min, 1, cf.r_min, cf.r_max)
    
    # 2ème passe : fittage de rectangle (si on le fait après l'approx tout ressemble à un rectangle)        
    rect_probables = []
    for cnt in cnt_pertinents:
       # fitte un rectangle
        rect = cv2.minAreaRect(cnt)
        # calcule l'aire du rectangle fitté
        aire_rect = rect[1][0] * rect[1][1]
        # calcule l'aire du contour trouvé
        M = cv2.moments(cnt)
        aire_cnt = M['m00'] 
        if aire_cnt/aire_rect > seuil_aire:
           rect_probables.append(cnt)
           cv2.drawContours(frame, [cnt], -1, (255, 0, 0), 1)        
  
    # 3ème passe : on approxime les contours restants et on ne garde que ceux à 4 coins
    for cnt in rect_probables:
      epsilon = cf.epsi_ratio*cv2.arcLength(cnt,True)
      approx = cv2.approxPolyDP(cnt,epsilon,True)
      if len(approx) == 4:   
            M = cv2.moments(approx)
            cv2.drawContours(frame, [approx], -1, (255,255,255), 2)
            cx, cy = int(M['m10']/M['m00']) , int(M['m01']/M['m00'])
            cv2.circle(frame, (cx,cy), 1, (255,255,255), 3)

    
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




















