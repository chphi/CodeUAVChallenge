# -*- coding: utf-8 -*-
"""
Created on Fri Feb 20 16:37:13 2015

@author: Charles

Script mettant en oeuvre la détection d'objets et consolidation infos pour la flèche.

syntaxe pour open cv 3.0.0

détecte les flèches et les croix
"""


import cv2
import sys
import BibliTracking as track
import BibliLocalisation as loc
import BibliSysteme as bibsys
import Fleche as class_fleche
import Croix as class_croix
import Rectangle as class_rect


# Définition des variables ------------------------------------------------------------------------

is_cam_embarquee = False                 # utilisation de la webcam ou de la caméra embarquée

# variables communes ROF
dh = 20                                  # valeurs autour de la teinte de référence qu'on va tracker
sat_min = 60                             # saturation min d'une couleur à tracker (base hsv)
val_min = 60                             # valeur min d'une couleur à tracker (base hsv)
n_blur = 3                               # ordre du filtre gaussien (tracking)
t_o = 5                                  # taille du noyau pour l'opening
Amin = 400                               # aire en dessous de laquelle un contour n'est pas considéré pertinent
Amax = 640*480                           # aire max. Les deux sont à adapter à l'altitude
n_gauss = 5                              # ordre du filtre gaussien pour flouter le patron et l'objet à matcher
seuil_certitude = 0.82                   # seuil de corrélation avec un patron au dessus duquel on considère la forme identique

# définition de la flèche
teinte_fleche = 0
s_max_fleche = 0.8                       # solidité max
r_min_fleche = .35                       # ratio petite dimension/grande dimension min
r_max_fleche = .65                       # ratio petite dimension/grande dimension max
pas_angle_fleche = 5                     # pas de test des orientations pour le template matching (NE PAS CHANGER)

# définition de la croix
teinte_croix = 35
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

# caractéristiques associées au drone
coords_drone = (48.7077, 2.1602)
alt_drone = 10                           # altitude du drone en mètres
cap_drone = 0                            # cap du drone (en degrés)
orientation_cam = (0,0)                  # caméra à plat, devant = haut de l'image.

# variables communes consolidation infos
taille_mem = 4                           # nb d'infos gardées en mémoire (initialiser les listes associées au bon nb d'élts)
seuil_sigma_pos = 2                      # seuil d'écart type en dessous duquel on considère avoir bien vu la position de l'objet
seuil_sigma_cap = 5                      # idem pour les angles (cas d'une flèche)
d_seuil = 3                              # distance en dessous de laquelle on considère que deux objets vus sont les mêmes


# Initialisation du programme ----------------------------------------------------------------------------

# Parcours déjà suivi (TODO : à modifier pour prendre en compte coords initiales drone)
coords_decollage = (48.7076, 2.1603)
cap_decollage = 0
coords_1ere_fleche = (48.7077, 2.1603)
cap_1ere_fleche = 170.5
parcours = [ (coords_decollage, cap_decollage), (coords_1ere_fleche, cap_1ere_fleche) ]

# divers
font = cv2.FONT_HERSHEY_SIMPLEX          # police utilisée à l'image
size_factor = 0.7                        # facteur de taille de la police
K = cv2.getStructuringElement(cv2.MORPH_RECT,(t_o,t_o))          # noyau pour l'opening
bleu = (255,0,0)
vert = (0,255,0)
rouge = (0,0,255)
jaune = (0,255,255)
blanc = (255,255,255)

# instanciation de la classe flèche
patron_fleche = cv2.imread('patron_fleche.png') # patron : vertical (orienté vers le haut, 50x50px)
fleche = class_fleche.Fleche(patron_fleche, teinte_fleche, s_max_fleche, r_min_fleche, r_max_fleche, [], [], [], False)
patrons_fleche = track.creePatrons(patron_fleche, pas_angle_fleche, n_gauss)
liste_coords_fleche = [[],[]]
liste_caps_fleche = [[], []]
for i in range(taille_mem-2): liste_caps_fleche.append([]); liste_coords_fleche.append([])

# instanciation de la classe croix
patron_croix = cv2.imread('patron_croix.png')   # patron : en "+", 50x50px
croix = class_croix.Croix(patron_croix, teinte_croix, s_max_croix, r_min_croix, r_max_croix, [], [], False)
patrons_croix = track.creePatrons(patron_croix, pas_angle_croix, n_gauss)
liste_coords_croix = [[],[]]
for i in range(taille_mem-2): liste_coords_croix.append([])

# instanciation de la classe rectangle
rectangle = class_rect.Rectangle(s_min, r_min, r_max, [], [], False)
liste_coords_rectangle = [[],[]]
for i in range(taille_mem-2): liste_coords_rectangle.append([])

# lancement vidéo
capture = track.initVideoFlow(is_cam_embarquee)   


# Boucle -------------------------------------------------------------------------------------------------

while(True):

    # récupération infos sur le drone
    data = sys.stdin.readline().strip()
    sys.stdin.flush()
    coords_drone, alt_drone, cap_drone = bibsys.unwrap_args_rof(data)

    # Lecture vidéo
    frame = track.getImage(is_cam_embarquee, capture)
   
    # Détection objets
    fleche.detecteFleche(frame, dh, n_blur, K, Amin, Amax, patrons_fleche, pas_angle_fleche, seuil_certitude, sat_min, val_min, n_gauss)
    croix.detecteCroix(frame, dh, n_blur, K, Amin, Amax, patrons_croix, pas_angle_croix, (seuil_certitude-0.05), sat_min, val_min, n_gauss)
    rectangle.detecteRectangle(frame, n_blur, K, Amin, Amax, seuil_certitude, seuil_aire, n_zone, v_moy)

    # validation détection et consolidation infos
    donnees_fleche = loc.analyseReconnaissanceFleche(fleche, liste_coords_fleche, liste_caps_fleche, taille_mem, seuil_sigma_pos, seuil_sigma_cap, coords_drone, cap_drone, alt_drone, orientation_cam)
    donnees_croix = loc.analyseReconnaissanceObjet(croix, liste_coords_croix, taille_mem, seuil_sigma_pos, coords_drone, cap_drone, alt_drone, orientation_cam)
    donnees_rectangle = loc.analyseReconnaissanceObjet(rectangle, liste_coords_rectangle, taille_mem, seuil_sigma_pos, coords_drone, cap_drone, alt_drone, orientation_cam)
    
    # affichage validation objets
    if donnees_fleche[0]:          # si la flèche a été validée
        cv2.putText(frame, 'fleche valide', (20,30), font, size_factor, rouge, 2, cv2.LINE_AA)
    if donnees_croix[0]:
        cv2.putText(frame, 'croix valide', (20,60), font, size_factor, jaune, 2, cv2.LINE_AA)
    if donnees_rectangle[0]:
        cv2.putText(frame, 'rectangle valide', (20,90), font, size_factor, blanc, 2, cv2.LINE_AA)

    # vérification si objets pas encore vus, choix du plus pertinent (si plusieurs valides en même temps à l'image)
    parcours, donnees_objet_discrimine = loc.discrimineObjetsValides(donnees_fleche, donnees_croix, donnees_rectangle, parcours, d_seuil, coords_drone)
    
    # résultat de l'algo
    type_objet, coords, incertitude_coords, cap, incertitude_cap = donnees_objet_discrimine
    
    # si on a effectivement vu un nouvel objet, affichage du nouveau point sur le parcours
#    if type_objet != 'none':        
#        print('objet ajoute au parcours : ' + type_objet )
#        print parcours[-1]
    
    # Affichage flux vidéo
    cv2.imshow('frame', frame)
    
    # envoi arguments au script maître
    output = bibsys.wrap_output_rof(type_objet, coords, incertitude_coords, cap, incertitude_cap)
    sys.stdout.write(output + "\n")
    sys.stdout.flush()
   
    # Condition de fin de la boucle
    k = cv2.waitKey(10) & 0xFF
    if k == ord('q'):
       break


# Fin de la boucle ----------------------------------------------------------------------------------------------


# arrêt du script
track.endVideoFlow(is_cam_embarquee, capture)


