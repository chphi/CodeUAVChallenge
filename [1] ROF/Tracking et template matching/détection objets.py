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
import BibliTracking as track
import Fleche as class_fleche
import Croix as class_croix
import Rectangle as class_rect


# Définition des variables, initialisation du programme -------------------------------------------------

is_cam_embarquee = True                  # utilisation de la webcam ou de la caméra embarquée

# variables communes de la reconnaissance de formes
dh = 20                                  # valeurs autour de la teinte de référence qu'on va tracker
sat_min = 60                             # saturation min d'une couleur à tracker (base hsv)
val_min = 60                             # valeur min d'une couleur à tracker (base hsv)
n_blur = 3                               # ordre du filtre gaussien (tracking)
t_o = 5                                  # taille du noyau pour l'opening
Amin = 400                               # aire en dessous de laquelle un contour n'est pas considéré pertinent
Amax = 640*480                           # aire max
n_gauss = 4                              # ordre du filtre gaussien pour flouter le patron et l'objet à matcher
seuil_certitude = 0.82                   # seuil de corrélation du template matching

# définition des caractéristiques de la flèche
teinte_fleche = 0                        # teinte de la flèche (base hsv)
s_max_fleche = 0.8                       # solidité max
r_min_fleche = .35                       # ratio petite dimension/grande dimension min
r_max_fleche = .65                       # ratio petite dimension/grande dimension max
pas_angle_fleche = 5                     # pas de test des orientations pour le template matching (NE PAS CHANGER)

# définition de la croix
teinte_croix = 35                        # teinte de la croix (base hsv)
s_max_croix = 0.8                        # solidité max
r_min_croix = .70                        # ratio petite dimension/grande dimension min
r_max_croix = 1.                         # ratio petite dimension/grande dimension max
pas_angle_croix = 10                     # pas de test des orientations pour le template matching (NE PAS CHANGER)

# définition du rectangle
n_zone = 101                             # taille de la zone pour calculer le seuil adaptatif (doit être impair)
v_moy = 25                               # valeur à enlever au seuil moyen
s_min = 0.90                             # solidité min
r_min = .4                               # ratio grande dimension/petite dimension min
r_max = .6                               # ratio grande dimension/petite dimension max    
seuil_aire = 0.9                         # rapport max entre l'aire d'un contour et l'aire du rectangle fitté 

    
# Initialisation du programme ----------------------------------------------------------------------------

# divers
font = cv2.FONT_HERSHEY_SIMPLEX          # police utilisée à l'image
K = np.ones((t_o,t_o),np.uint8)          # noyau pour l'opening
bleu = (255,0,0)
vert = (0,255,0)
rouge = (0,0,255)

# instanciation de la classe flèche
patron_fleche = cv2.imread('patron_fleche.png') # patron : vertical (orienté vers le haut, 50x50px)
fleche = class_fleche.Fleche(patron_fleche, teinte_fleche, s_max_fleche, r_min_fleche, r_max_fleche, [], [], [], False)
patrons_fleche = track.creePatrons(patron_fleche, pas_angle_fleche, n_gauss)

# instanciation de la classe croix
patron_croix = cv2.imread('patron_croix.png')   # patron : en "+", 50x50px
croix = class_croix.Croix(patron_croix, teinte_croix, s_max_croix, r_min_croix, r_max_croix, [], [], False)
patrons_croix = track.creePatrons(patron_croix, pas_angle_croix, n_gauss)

# instanciation de la classe rectangle
rectangle = class_rect.Rectangle(s_min, r_min, r_max, [], [], False)

# lancement vidéo
capture = track.initVideoFlow(is_cam_embarquee)   


# Boucle -------------------------------------------------------------------------------------------------

while(True):

    # Lecture vidéo
    frame = track.getImage(is_cam_embarquee, capture)
   
    # Détection objets
    fleche.detecteFleche(frame, dh, n_blur, K, Amin, Amax, patrons_fleche, pas_angle_fleche, seuil_certitude, sat_min, val_min, n_gauss)
    croix.detecteCroix(frame, dh, n_blur, K, Amin, Amax, patrons_croix, pas_angle_croix, (seuil_certitude-0.05), sat_min, val_min, n_gauss)
    rectangle.detecteRectangle(frame, n_blur, K, Amin, Amax, seuil_certitude, seuil_aire, n_zone, v_moy)

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
track.endVideoFlow(is_cam_embarquee, capture)


