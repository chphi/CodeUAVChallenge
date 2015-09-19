# -*- coding: utf-8 -*-
"""
Created on Fri Feb 20 16:37:13 2015

@author: Charles
"""


# Tracke une couleur, et les barycentres possibles de l'objet recherché. Pour le calcul des barycentres on filtre
# les zones ne correspondant pas à notre objet (une flèche ou une croix) avec des tests simples sur les contours

# Ces zones, correspondant aux contours "pertinents" sont en général au nombre d'une dizaine. On peut faire une
# reconnaissance de formes (SVM) sur ces quelques points ou une "RST-invariant template matching"

# Une fois qu'on sera sûr d'avoir une flèche  (avec la SVM), on pourra peut-être passer sur du camshift
# et/ou réajuster la teinte à tracker etc...


import cv2
import numpy as np
import sys


# Définition des variables, initialisation du programme -------------------------------------------------

# emplacement du fichier de configuration
conf_path = 'D:/Charles/Documents/Sumo/Dassault UAV Challenge/Code/CodeUAVChallenge'


# variables réglables
trackbar_activated = True                   # active la barre pour réglage manuel de h_cible
h_cible = 5
marge_h = 20                                # valeurs autour de la teinte de référence qu'on va tracker
n_blur = 11
s_min = 40
v_min = 40
t_o = 5                                     # taille du noyau pour l'opening
aire_min = 400                              # aire en dessous de laquelle un contour n'est pas considéré pertinent
aire_max = 10000                            # aire max. Les deux sont à adapter à l'altitude
                                            # avec ces valeurs détecte le modèle de flèche entre 20 et 50cm environ

# autres variables (définies principalement à partir des var précédentes)
font = cv2.FONT_HERSHEY_SIMPLEX
lower_blue = np.array([h_cible-marge_h,100,100])                         # define range of blue color in HSV
upper_blue = np.array([h_cible+marge_h,255,255]) 


# Initialisation du programme --------------------------------------------------

# importe la configuration
sys.path.append(conf_path)
import conf_drone as cf

# importe les biblis perso
sys.path.append(cf.libpath)
import BibliTracking as track

# lancement vidéo
capture = track.initVideoFlow(cf.is_cam_embarquee)

# initialisation trackbars
def nothing(x): pass

if trackbar_activated == True:
    cv2.createTrackbar('H','frame',0,180,nothing)
    cv2.createTrackbar('dH','frame',1,30,nothing)
    cv2.createTrackbar('n_opening','frame',2,20,nothing)
    cv2.createTrackbar('n_blur', 'frame', 1, 15, nothing)

        
        


# Boucle -------------------------------------------------------------------------------------------------

while(True):

        # Lecture vidéo -------------------------------------------------------

    frame = track.getImage(cf.is_cam_embarquee, capture)
   
   
        # Get current positions of trackbar -----------------------------------
    if trackbar_activated == True:
        h_cible = cv2.getTrackbarPos('H','frame')
        marge_h = cv2.getTrackbarPos('dH', 'frame')
        t_o = cv2.getTrackbarPos('n_opening', 'frame')
        n_blur_brut = cv2.getTrackbarPos('n_blur', 'frame')
        n_blur = n_blur_brut + ( 1 - np.mod(n_blur_brut,2) )         # 1er impair plus grand ou égal à n_blur_brut
   
       # tracking couleur
    
    kernel = np.ones((t_o,t_o),np.uint8)        # noyau pour l'opening    
    
    frame_track = track.trackeTeinte(frame, h_cible, marge_h, n_blur, kernel, 50, 50)
    _, frame_track = cv2.threshold(frame_track,1,255,cv2.THRESH_BINARY)
                
    
        # Affichage flux vidéo ------------------------------------------------
    
    cv2.imshow('frame', frame_track)
   
        # Condition de fin de la boucle ---------------------------------------

    k = cv2.waitKey(10) & 0xFF
    if k == ord('q'):
       break

# Fin de la boucle ----------------------------------------------------------------------------------------------


# fin du script
track.endVideoFlow(cf.is_cam_embarquee, capture)


