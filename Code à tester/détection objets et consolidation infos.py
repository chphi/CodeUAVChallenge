# -*- coding: utf-8 -*-
"""
Created on Fri Feb 20 16:37:13 2015

@author: Charles

Script mettant en oeuvre la détection d'objets et consolidation infos pour la flèche.
"""

# syntaxe pour open cv 3.0.0

# détecte les flèches et les croix

import cv2
import numpy as np
import BibliTracking as track
import BibliLocalisation as loc
import Fleche as class_fleche
import Croix as class_croix
import Rectangle as class_rect


# Définition des variables ------------------------------------------------------------------------

is_cam_embarquee = True                 # utilisation de la webcam ou de la caméra embarquée

# caractéristiques associées au drone
coords_drone = (48.7077, 2.1602)
alt_drone = 10                          # altitude du drone en mètres
cap_drone = 0                           # cap du drone (en degrés)
orientation_cam = (0,0)                 # caméra à plat, devant = haut de l'image.

# variables communes ROF
dh = 20                                  # valeurs autour de la teinte de référence qu'on va tracker
t_o = 5                                  # taille du noyau pour l'opening
n_blur = 3                               # ordre du filtre gaussien (tracking)
Amin = 400                               # aire en dessous de laquelle un contour n'est pas considéré pertinent
Amax = 640*480                           # aire max. Les deux sont à adapter à l'altitude
n_gauss = 5                              # ordre du filtre gaussien pour flouter le patron et l'objet à matcher
seuil_certitude = 0.82                   # seuil de corrélation avec un patron au dessus duquel on considère la forme identique
sat_min = 40                             # saturation min d'une couleur à tracker (base hsv)
val_min = 20                             # valeur min d'une couleur à tracker (base hsv)
font = cv2.FONT_HERSHEY_SIMPLEX 
K = np.ones((t_o,t_o),np.uint8)          # noyau pour l'opening
bleu = (255,0,0)
vert = (0,255,0)
rouge = (0,0,255)

# variables communes consolidation infos
taille_mem = 4                           # nb d'infos gardées en mémoire (initialiser les listes associées au bon nb d'élts)
seuil_sigma_pos = 2                      # seuil d'écart type en dessous duquel on considère avoir bien vu la position de l'objet
seuil_sigma_cap = 5                      # idem pour les angles (cas d'une flèche)

# définition de la flèche
teinte_fleche = 0
s_max_fleche = 0.8                              # solidité max
r_min_fleche = .35                              # ratio petite dimension/grande dimension min
r_max_fleche = .65                              # ratio petite dimension/grande dimension max
pas_angle_fleche = 5                            # pas de test des orientations pour le template matching (NE PAS CHANGER)
patron_fleche = cv2.imread('patron_fleche.png') # patron : vertical (orienté vers le haut, 50x50px)
fleche = class_fleche.Fleche(patron_fleche, teinte_fleche, s_max_fleche, r_min_fleche, r_max_fleche, [], [], [], False)
patrons_fleche = track.creePatrons(patron_fleche, pas_angle_fleche, n_gauss)
liste_coords_fleche = [[],[]]
liste_caps_fleche = [[], []]
for i in range(taille_mem-2): liste_caps_fleche.append([]); liste_coords_fleche.append([])


# définition de la croix
teinte_croix = 35
s_max_croix = 0.8                               # solidité max
r_min_croix = .70                               # ratio petite dimension/grande dimension min
r_max_croix = 1.                                # ratio petite dimension/grande dimension max
pas_angle_croix = 10                            # pas de test des orientations pour le template matching (NE PAS CHANGER)
patron_croix = cv2.imread('patron_croix.png')   # patron : en "+", 50x50px
croix = class_croix.Croix(patron_croix, teinte_croix, s_max_croix, r_min_croix, r_max_croix, [], [], False)
patrons_croix = track.creePatrons(patron_croix, pas_angle_croix, n_gauss)
    
# définition du rectangle
n_zone = 101                                    # taille de la zone pour calculer le seuil adaptatif (doit être impair)
v_moy = 25                                      # valeur à enlever au seuil moyen
s_min = 0.90                                    # solidité min
r_min = .4                                      # ratio grande dimension/petite dimension min
r_max = .6                                      # ratio grande dimension/petite dimension max    
seuil_aire = 0.9                                # rapport max entre l'aire d'un contour et l'aire du rectangle fitté 
rectangle = class_rect.Rectangle(s_min, r_min, r_max, [], [], False)


# Lancement acquisition vidéo 
capture = track.initVideoFlow(is_cam_embarquee)


# Boucle -------------------------------------------------------------------------------------------------

while(True):

    # Lecture vidéo
    frame = track.getImage(is_cam_embarquee, capture)
   
    # Détection objets
    fleche.detecteFleche(frame, dh, n_blur, K, Amin, Amax, patrons_fleche, pas_angle_fleche, seuil_certitude, sat_min, val_min, n_gauss)
    croix.detecteCroix(frame, dh, n_blur, K, Amin, Amax, patrons_croix, pas_angle_croix, (seuil_certitude-0.05), sat_min, val_min, n_gauss)
    rectangle.detecteRectangle(frame, n_blur, K, Amin, Amax, seuil_certitude, seuil_aire, n_zone, v_moy)

    fleche_validee, coords_fleche, sigma_pos, cap_fleche, sigma_cap = loc.analyseReconnaissanceFleche(fleche, liste_coords_fleche, liste_caps_fleche, taille_mem, seuil_sigma_pos, seuil_sigma_cap, coords_drone, cap_drone, alt_drone, orientation_cam)

    if fleche.estDetectee:
         # affichage ecarts-types
        sigma_pos_str = "%.1f" % sigma_pos
        cv2.putText(frame, 'incertitude position : ' + sigma_pos_str, (30,440), font, 1, rouge, 2, cv2.LINE_AA)
        sigma_cap_str = "%.1f" % sigma_cap
        cv2.putText(frame, 'incertitude cap : ' + sigma_cap_str, (30,470), font, 1, rouge, 2, cv2.LINE_AA)
    
        if fleche_validee:
            cv2.putText(frame, 'fleche validee !', (30,30), font, 1, rouge, 2, cv2.LINE_AA)
            # affichage cap
            cap_str = "%.1f" % cap_fleche     
            texte = 'cap fleche = ' + cap_str + ' deg'
            cv2.putText(frame, texte, (30,60), font, 1, rouge, 2, cv2.LINE_AA) # affichage de l'angle de la flèche
            # affichage coords
            lat = "%.6f" % coords_fleche[0]
            longit = "%.6f" % coords_fleche[1]
            texte2 = 'coords : (' + lat + ', ' + longit + ')'
            cv2.putText(frame, texte2, (30,90), font, 1, rouge, 2, cv2.LINE_AA)       
    
    
    # Affichage flux vidéo
    cv2.imshow('frame', frame)
   
    # Condition de fin de la boucle
    k = cv2.waitKey(10) & 0xFF
    if k == ord('q'):
       break


# Fin de la boucle ----------------------------------------------------------------------------------------------


# arrêt du script
track.endVideoFlow(is_cam_embarquee, capture)


