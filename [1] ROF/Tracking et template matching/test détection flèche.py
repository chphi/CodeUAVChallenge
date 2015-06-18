# -*- coding: utf-8 -*-
"""
Created on Fri Feb 20 16:37:13 2015

@author: Charles


syntaxe pour open cv 3.0.0

On fait un template matching sur les zones d'intérêt qui ont été trouvées par tracking
de couleur et filtrage sur les contours, avec un facteur de rotation donné par l'angle
de l'ellipse fittée (ou du rectangle)

Une fois qu'on sera sûr d'avoir une flèche, on pourra peut-être passer sur du camshift
et/ou réajuster la teinte à tracker etc...

affiche tous les contours en rouge, les contours pertinents en bleu, et les flèches en vert.
"""



import cv2
import numpy as np
import BibliTracking as track
#from scipy import ndimage


# Définition des variables, initialisation du programme -------------------------------------------------

is_cam_embarquee = True                  # utilisation de la webcam ou de la caméra embarquée

# variables réglables
patron = cv2.imread('patron_fleche.png') # patron : vertical (orienté vers le haut)
w_p, h_p = np.shape(patron[:,:,1])
taille_patron = 45                       # taille de la flèche dans le patron
h_cible = 0                              # teinte à tracker
marge_h = 20                             # valeurs autour de la teinte de référence qu'on va tracker
t_o = 5                                  # taille du noyau pour l'opening
n_blur = 3                               # ordre du filtre médian (tracking)
kernel = np.ones((t_o,t_o),np.uint8)     # noyau pour l'opening
s_max = 0.8;                             # solidité max
r_min = .35                              # ratio grande dimension/petite dimension min
r_max = .65                              # ratio grande dimension/petite dimension max
aire_min = 200                           # aire en dessous de laquelle un contour n'est pas considéré pertinent
aire_max = 10000                         # aire max. Les deux sont à adapter à l'altitude
n_gauss = 6                              # ordre du filtre gaussien pour flouter le patron et l'objet à matcher
pas_angle = 5                            # pas de test des orientations pour le template matching (NE PAS CHANGER)
max_angle = 20                           # orientation max qu'on vérifie par rapport à l'angle probable
pas_size = 0.1                           # pas de test des tailles
max_size = 0.1                           # changement de taille max (en %) qu'on vérifie par rapport à la taille probable
seuil_certitude = 0.82                   # seuil de corrélation au dessus duquel on considère la flèche trouvée


# autres variables (définies principalement à partir des var précédentes)
font = cv2.FONT_HERSHEY_SIMPLEX
lower_blue = np.array([h_cible-marge_h,40,40])              # define range of blue color in HSV
upper_blue = np.array([h_cible+marge_h,255,255]) 
range_angles = np.arange(-max_angle,max_angle+1,pas_angle)    # angles à tester autour de angle_probable
range_sizes = 1 + np.arange(-max_size, max_size, pas_size)    # tailles à tester autour de taille_probable
patron = cv2.cvtColor(patron, cv2.COLOR_BGR2GRAY)
patron = cv2.blur(patron,(n_gauss,n_gauss))

# initialisations
angle_fleche = -1
pos_fleche = -1,-1
patrons = np.zeros((h_p,w_p, np.int0(360/5)), 'uint8')      # initialisation du tableau des patrons orientés
all_angles = np.arange(0,360, pas_angle)                    # initialisation de tous les angles
for angle in all_angles:
    indice = angle/pas_angle
    M = cv2.getRotationMatrix2D((h_p/2,w_p/2),-angle,1)     # rotation dans le sens horaire (comme une boussole)
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
                
    
        # Template matching sur les zones trouvées ----------------------------

    for cnt in fleches_probables:
        
    # pour chaque contour détermine une zone dans laquelle elle est incluse et une orientation probable 
        _, _, angle_probable = cv2.fitEllipse(cnt)        # orientation probable (à 180° près)
        (x,y),radius = cv2.minEnclosingCircle(cnt)        # fitte un cercle autour du contour
        x,y = (int(x),int(y))                             # centre probable
        radius = int(radius)                              
        taille_probable = 2*radius                        # taille probable
    
    # extrait la ROI 
    # on prend une ROI carrée qui contient le cercle dans lequel est inscrit l'objet (-> pas de pb pour faire une rotation)
        x,y,w,h = x-radius, y-radius, 2*radius, 2*radius
        zone_a_tester = opening[y:(y+h), x:(x+w)]   # indices : lignes puis colonnes
        if np.int0(min(np.shape(zone_a_tester))) > 1:   # vérif si on n'a pas pris une zone juste au bord
            zone_a_tester = cv2.resize(zone_a_tester, (h_p, w_p)) # met la ROI à l'échelle du patron (100px)
            zone_a_tester = cv2.blur(zone_a_tester, (n_gauss, n_gauss))
            
    # définit les angles à tester (différentes tailles à tester -> plus tard)
            angles_a_tester_1 = np.mod(angle_probable + range_angles, 360)
            angles_a_tester_2 = np.mod(180 + angle_probable + range_angles, 360)
            angles_a_tester = np.int0(np.concatenate((angles_a_tester_1, angles_a_tester_2)))
            indices_patrons_a_tester = np.int0(.2 * angles_a_tester)
            
    # teste la correspondance par template matching ou corrélation. On récupère le plus grand corr_coeff et sa pos.
            coeff_max = 0
            for i in indices_patrons_a_tester:
               coeff = cv2.matchTemplate(zone_a_tester,patrons[:,:,i],cv2.TM_CCOEFF_NORMED)
               if coeff[0][0] > coeff_max:
                   coeff_max = coeff[0][0]
                   indice_max = i
                   
                   
    # si on a trouvé une flèche : on extrait les caractéristiques et on affiche l'objet
            if coeff_max > seuil_certitude:
               M = cv2.moments(cnt)
               angle_fleche = pas_angle*indice_max                              # angle de la flèche
               pos_fleche = int(M['m10']/M['m00']) , int(M['m01']/M['m00'])     # barycentre de la flèche (position)
               cv2.drawContours(frame,[cnt], -1, (0,255,0), 2)                  # dessine les contours de la flèche
               cv2.circle(frame,pos_fleche, 3, (0,255,0), -1)                   # dessine le centre de la flèche
               cv2.putText(frame,str(angle_fleche),(30,30), font, 1,(0,255,0),2,cv2.LINE_AA)
               cv2.imshow('patron matché', patrons[:,:,indice_max])
               cv2.imshow('zone testee', zone_a_tester)
            else:
                angle_fleche = -1
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


