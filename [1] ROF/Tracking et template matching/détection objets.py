# -*- coding: utf-8 -*-
"""
Created on Fri Feb 20 16:37:13 2015

@author: Charles

Syntaxe pour open cv 3.0.0

Ce script fait implicitement appel à la bibliothèque "VideoCapture" pour Python dans
le cas où on veut tester la reconnaissance avec la caméra embarquée du drone. Il faut 
aussi dans ce cas s'assurer qu'on a bien installé le driver et qu'on peut visualiser 
le flux vidéo dans Mission Planner.

Script servant à détecter les flèches, croix et rectangles à l'image. Les paramètres de 
la reconnaissance d'image ont été optimisés à la main pour chaque objet, et pour la
caméra embarquée.

On peut visualiser le résultat à l'image (formes en surimpression et centre marqué d'un
point de la couleur de l'objet.

"""

import cv2
import numpy as np
import sys


# Définition des variables -----------------------------------------------------------------------------

conf_path = 'D:/Charles/Documents/Sumo/Dassault UAV Challenge/Code/CodeUAVChallenge'
    
# Initialisation du programme ----------------------------------------------------------------------------

# importe la configuration
sys.path.append(conf_path)
import conf_drone as cf

# importe biblis persos
sys.path.append(cf.libpath)
import BibliTracking as track
import Fleche as class_fleche
import Croix as class_croix
import Rectangle as class_rect

# divers
font = cv2.FONT_HERSHEY_SIMPLEX          # police utilisée à l'image
K = np.ones((cf.t_o,cf.t_o),np.uint8)          # noyau pour l'opening
bleu = (255,0,0)
vert = (0,255,0)
rouge = (0,0,255)

# instanciation de la classe flèche
patron_fleche = cv2.imread(cf.libpath + '/' + 'patron_fleche.png') # patron : vertical (orienté vers le haut, 50x50px)
fleche = class_fleche.Fleche(patron_fleche, cf.teinte_fleche, cf.s_max_fleche, cf.r_min_fleche, cf.r_max_fleche, [], [], [], False)
patrons_fleche = track.creePatrons(patron_fleche, cf.pas_angle_fleche, cf.n_gauss)

# instanciation de la classe croix
patron_croix = cv2.imread(cf.libpath + '/' + 'patron_croix.png')   # patron : en "+", 50x50px
croix = class_croix.Croix(patron_croix, cf.teinte_croix, cf.s_max_croix, cf.r_min_croix, cf.r_max_croix, [], [], False)
patrons_croix = track.creePatrons(patron_croix, cf.pas_angle_croix, cf.n_gauss)

# instanciation de la classe rectangle
rectangle = class_rect.Rectangle(cf.s_min, cf.r_min, cf.r_max, [], [], False)

# lancement vidéo
capture = track.initVideoFlow(cf.is_cam_embarquee)   


# Boucle -------------------------------------------------------------------------------------------------

while(True):

  # Lecture vidéo
  frame = track.getImage(cf.is_cam_embarquee, capture)
 
  # Détection objets
  fleche.detecteFleche(frame, cf.dh, cf.n_blur, K, cf.Amin, cf.Amax, patrons_fleche, cf.pas_angle_fleche, cf.seuil_certitude_fleche, cf.sat_min, cf.val_min, cf.n_gauss)
  croix.detecteCroix(frame, cf.dh, cf.n_blur, K, cf.Amin, cf.Amax, patrons_croix, cf.pas_angle_croix, cf.seuil_certitude_croix, cf.sat_min, cf.val_min, cf.n_gauss)
  rectangle.detecteRectangle(frame, cf.n_blur, K, cf.Amin, cf.Amax, cf.seuil_aire, cf.n_zone, cf.v_moy, cf.epsi_ratio)

  if fleche.estDetectee and len(fleche.position) == 1:
    texte = 'angle fleche = ' + str(fleche.angle[0]) + ' deg'
    cv2.putText(frame, texte, (30,30), font, 1, rouge, 2, cv2.LINE_AA) # affichage de l'angle de la flèche
    cv2.putText(frame, 'pos fleche : ' + str(fleche.position[0]), (30,60), font, 1, rouge, 2, cv2.LINE_AA)
   
  # Affichage flux vidéo
  cv2.imshow('frame', frame)
   
  # Condition de fin de la boucle
  k = cv2.waitKey(10) & 0xFF
  if k == ord('q'):
    break


# Fin de la boucle ----------------------------------------------------------------------------------------------


# arrêt du script
track.endVideoFlow(cf.is_cam_embarquee, capture)


