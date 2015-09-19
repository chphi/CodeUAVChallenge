# -*- coding: utf-8 -*-
"""
Created on Fri Feb 20 16:37:13 2015

@author: Charles

TODO : mettre à jour en prenant les variables dans "conf_drone"

syntaxe pour open cv 3.0.0

On fait un template matching sur les zones d'intérêt (tracking couleur et filtrage des contours)

affiche tous les contours en rouge, les contours pertinents en bleu, et les croix en vert.
"""

import sys
import cv2
import numpy as np


# Définition des variables, initialisation du programme -------------------------------------------------

conf_path = 'D:/Charles/Documents/Sumo/Dassault UAV Challenge/Code/CodeUAVChallenge'

is_cam_embarquee = False                 # utilisation de la webcam ou de la caméra embarquée

# variables réglables
h_cible = 35                             # à adapter à chaque fois qu'une flèche est détectée
marge_h = 20                             # valeurs autour de la teinte de référence qu'on va tracker
t_o = 5                                  # taille du noyau pour l'opening
n_blur = 3                               # ordre du filtre gaussien (tracking)
kernel = np.ones((t_o,t_o),np.uint8)     # noyau pour l'opening
s_max = 0.8                              # solidité max
aire_min = 200                           # aire en dessous de laquelle un contour n'est pas considéré pertinent
aire_max = 10000                         # aire max. Les deux sont à adapter à l'altitude
r_min = .70                              # ratio grande dimension/petite dimension min
r_max = 1.                               # ratio grande dimension/petite dimension max
n_gauss = 4                              # ordre du filtre gaussien pour flouter le patron et l'objet à matcher
pas_angle = 10                           # pas de test des orientations pour le template matching (NE PAS CHANGER)
seuil_certitude = 0.75                   # seuil de corrélation au dessus duquel on considère la croix trouvée

# autres variables (définies principalement à partir des var précédentes)
lower_blue = np.array([h_cible-marge_h,50,50])            # define range of color in HSV
upper_blue = np.array([h_cible+marge_h,255,255]) 

# Initialisations --------------------------------------------------------------

# importe la configuration
sys.path.append(conf_path)
import conf_drone as cf

# importe biblis persos
sys.path.append(cf.libpath)
import BibliTracking as track


# init patron
patron = cv2.imread(cf.libpath + '/' + 'patron_croix.png')  # patron : vertical (orienté vers le haut)
w_p, h_p = np.shape(patron[:,:,1])
patron = cv2.cvtColor(patron, cv2.COLOR_BGR2GRAY)
patron = cv2.blur(patron,(n_gauss,n_gauss))
all_angles = np.arange(0,360, pas_angle)                       # initialisation de tous les angles
patrons = np.zeros((w_p,h_p, np.int0(360/pas_angle)), 'uint8') # initialisation du tableau des patrons orientés
for angle in all_angles:                                       # remplissage du tableau
    indice = angle/pas_angle
    M = cv2.getRotationMatrix2D((h_p/2,w_p/2),-angle,1)        # rotation dans le sens horaire (comme une boussole)
    patron_oriente = cv2.warpAffine(patron,M,(h_p,w_p))
    patrons[:,:,indice] = patron_oriente

# lancement vidéo
capture = track.initVideoFlow(is_cam_embarquee) 


# Boucle -------------------------------------------------------------------------------------------------

while(True):

        # Lecture vidéo -------------------------------------------------------

    frame = track.getImage(is_cam_embarquee, capture)
   
   
        # Tracking classique --------------------------------------------------
    
    opening = track.trackeTeinte(frame, h_cible, marge_h, n_blur, kernel, 100, 100) 
    fleches_probables = track.trouveObjetsProbables(opening.copy(), aire_min, aire_max, 0, s_max, r_min, r_max) 
    
    
        # Calcul de tous les contours de l'image ------------------------------
    
    _, contours, hierarchy = cv2.findContours(opening.copy(), cv2.RETR_EXTERNAL ,cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(frame,contours, -1, (0,0,255), 1)
    
    
        # Filtrage des contours intéressants et calcul de leur barycentre -----
    
    fleches_probables = []
    for i in range(0,len(contours)): 
        cnt = contours[i]
        if track.aireNonNulle(cnt):
            # calcul des caractéristiques du contour i :
            caracs = track.caracteristiques(cnt)
            # choix de considérer ce contour pertinent au vu des caractéristiques :
            if track.estPertinent(caracs, aire_min, aire_max, 0, s_max, r_min, r_max): 
                fleches_probables.append( cnt )                    # considère le barycentre trouvé comme pertinent
                cv2.drawContours(frame, [cnt], -1, (255,0,0), 1)   # dessine les contours pertinents en bleu
                
    
        # Template matching sur les zones trouvées ----------------------------

    for cnt in fleches_probables:
        
    # pour chaque contour détermine une zone dans laquelle elle est incluse et une orientation probable 
        (x,y),radius = cv2.minEnclosingCircle(cnt)        # fitte un cercle autour du contour
        x,y = (int(x),int(y))                             # centre probable
        radius = int(radius)                              
    
    # extrait la ROI 
    # on prend une ROI carrée qui contient le cercle dans lequel est inscrit l'objet (-> pas de pb pour faire une rotation)
        x,y,w,h = x-radius, y-radius, 2*radius, 2*radius
        zone_a_tester = opening[y:(y+h), x:(x+w)]   # indices : lignes puis colonnes
        if np.int0(min(np.shape(zone_a_tester))) > 1:
            zone_a_tester = cv2.resize(zone_a_tester, (h_p, w_p)) # met la ROI à l'échelle du patron (100px)
            zone_a_tester = cv2.blur(zone_a_tester, (n_gauss, n_gauss))
    
    # définit les angles à tester (différentes tailles à tester -> plus tard)
            angles_a_tester = all_angles
            indices_patrons_a_tester = np.int0( (1./pas_angle) * angles_a_tester)
            
    # teste la correspondance par template matching (corrélation). On récupère le plus grand corr_coeff et sa pos.
            coeff_max = 0
            for i in indices_patrons_a_tester:
               coeff = cv2.matchTemplate(zone_a_tester,patrons[:,:,i],cv2.TM_CCOEFF_NORMED)
               if coeff[0][0] > coeff_max:
                   coeff_max = coeff[0][0]
                   indice_max = i
                   
    # si on a trouvé une croix : on extrait les caractéristiques et on affiche l'objet
            if coeff_max > seuil_certitude:
               M = cv2.moments(cnt)
               pos_fleche = int(M['m10']/M['m00']) , int(M['m01']/M['m00'])     # barycentre de la croix (position)
               cv2.drawContours(frame,[cnt], -1, (0,255,0), 2)                  # dessine les contours de la croix
               cv2.circle(frame,pos_fleche, 3, (0,255,0), -1)                   # dessine le centre de la croix
               cv2.imshow('patron matché', patrons[:,:,indice_max])
               cv2.imshow('zone testee', zone_a_tester)
            else:
                pos_fleche = -1, -1
    
    
        # Affichage flux vidéo ------------------------------------------------

    cv2.imshow('frame', frame)
   
   
        # Condition de fin de la boucle ---------------------------------------

    k = cv2.waitKey(10) & 0xFF
    if k == ord('q'):
       break

# Fin de la boucle ----------------------------------------------------------------------------------------------


# fin du script
track.endVideoFlow(is_cam_embarquee, capture)


