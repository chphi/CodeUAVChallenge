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


# Variables --------------------------------------------------------------------

conf_path = 'D:/Charles/Documents/Sumo/Dassault UAV Challenge/Code/CodeUAVChallenge'

# infos sur le drone
coords_drone = (48.7077, 2.1602)
alt_drone = 10                           # altitude du drone en mètres
cap_drone = 0                            # cap du drone (en degrés)
orientation_cam = (0,0)                  # caméra à plat, devant = haut de l'image.

# Initialisation du programme --------------------------------------------------

# importe le fichier de configuration des scripts
sys.path.append(conf_path)
import conf_drone as cf

# importe les biblis persos
sys.path.append(cf.libpath)
import BibliTracking as track
import BibliConsolidateTracking as constra
import BibliSysteme as bibsys
import Fleche as class_fleche
import Croix as class_croix
import Rectangle as class_rect

# Parcours déjà suivi (TODO : à modifier pour prendre en compte coords initiales drone)
coords_decollage = (48.7076, 2.1603)
cap_decollage = 0
coords_1ere_fleche = (48.7077, 2.1603)
cap_1ere_fleche = 170.5
parcours = [ (coords_decollage, cap_decollage), (coords_1ere_fleche, cap_1ere_fleche) ]

# divers
font = cv2.FONT_HERSHEY_SIMPLEX          # police utilisée à l'image
size_factor = 0.7                        # facteur de taille de la police
K = cv2.getStructuringElement(cv2.MORPH_RECT,(cf.t_o,cf.t_o))          # noyau pour l'opening
bleu = (255,0,0)
vert = (0,255,0)
rouge = (0,0,255)
jaune = (0,255,255)
blanc = (255,255,255)

# instanciation de la classe flèche
patron_fleche = cv2.imread(cf.libpath + '/' + 'patron_fleche.png') # patron : vertical (orienté vers le haut, 50x50px)
fleche = class_fleche.Fleche(patron_fleche, cf.teinte_fleche, cf.s_max_fleche, cf.r_min_fleche, cf.r_max_fleche, [], [], [], False)
patrons_fleche = track.creePatrons(patron_fleche, cf.pas_angle_fleche, cf.n_gauss)
liste_coords_fleche = [[],[]]
liste_caps_fleche = [[], []]
for i in range(cf.taille_mem-2): liste_caps_fleche.append([]); liste_coords_fleche.append([])

# instanciation de la classe croix
patron_croix = cv2.imread(cf.libpath + '/' + 'patron_croix.png')   # patron : en "+", 50x50px
croix = class_croix.Croix(patron_croix, cf.teinte_croix, cf.s_max_croix, cf.r_min_croix, cf.r_max_croix, [], [], False)
patrons_croix = track.creePatrons(patron_croix, cf.pas_angle_croix, cf.n_gauss)
liste_coords_croix = [[],[]]
for i in range(cf.taille_mem-2): liste_coords_croix.append([])

# instanciation de la classe rectangle
rectangle = class_rect.Rectangle(cf.s_min, cf.r_min, cf.r_max, [], [], False)
liste_coords_rectangle = [[],[]]
for i in range(cf.taille_mem-2): liste_coords_rectangle.append([])

# lancement vidéo
capture = track.initVideoFlow(cf.is_cam_embarquee)   


# Boucle -------------------------------------------------------------------------------------------------

while(True):

    # récupération infos sur le drone
    data = sys.stdin.readline().strip()
    sys.stdin.flush()
    coords_drone, alt_drone, cap_drone = bibsys.unwrap_args_rof(data)

    # Lecture vidéo
    frame = track.getImage(cf.is_cam_embarquee, capture)
   
    # Détection objets
    fleche.detecteFleche(frame, cf.dh, cf.n_blur, K, cf.Amin, cf.Amax, patrons_fleche, cf.pas_angle_fleche, cf.seuil_certitude_fleche, cf.sat_min, cf.val_min, cf.n_gauss)
    croix.detecteCroix(frame, cf.dh, cf.n_blur, K, cf.Amin, cf.Amax, patrons_croix, cf.pas_angle_croix, cf.seuil_certitude_croix, cf.sat_min, cf.val_min, cf.n_gauss)
    rectangle.detecteRectangle(frame, cf.n_blur, K, cf.Amin, cf.Amax, cf.seuil_aire, cf.n_zone, cf.v_moy, cf.epsi_ratio)

    # validation détection et consolidation infos
    donnees_fleche = constra.analyseReconnaissanceFleche(fleche, liste_coords_fleche, liste_caps_fleche, cf.taille_mem, cf.seuil_sigma_pos, cf.seuil_sigma_cap, coords_drone, cap_drone, alt_drone, orientation_cam)
    donnees_croix = constra.analyseReconnaissanceObjet(croix, liste_coords_croix, cf.taille_mem, cf.seuil_sigma_pos, coords_drone, cap_drone, alt_drone, orientation_cam)
    donnees_rectangle = constra.analyseReconnaissanceObjet(rectangle, liste_coords_rectangle, cf.taille_mem, cf.seuil_sigma_pos, coords_drone, cap_drone, alt_drone, orientation_cam)
    
    # affichage validation objets
    if donnees_fleche[0]:          # si la flèche a été validée
        cv2.putText(frame, 'fleche valide', (20,30), font, size_factor, rouge, 2, cv2.LINE_AA)
    if donnees_croix[0]:
        cv2.putText(frame, 'croix valide', (20,60), font, size_factor, jaune, 2, cv2.LINE_AA)
    if donnees_rectangle[0]:
        cv2.putText(frame, 'rectangle valide', (20,90), font, size_factor, blanc, 2, cv2.LINE_AA)

    # vérification si objets pas encore vus, choix du plus pertinent (si plusieurs valides en même temps à l'image)
    # si nouvel objet détecté : ajout au parcours
    parcours, donnees_objet_discrimine = constra.discrimineObjetsValides(donnees_fleche, donnees_croix, donnees_rectangle, parcours, cf.d_seuil, coords_drone)
    
    # "décompactage" des résultat de l'algo
    type_objet, coords, incertitude_coords, cap, incertitude_cap = donnees_objet_discrimine
    
    # Affichage flux vidéo
    cv2.imshow('frame', frame)
    
    # détection interactions utilisateur (codé ici car pratique avec opencv)
    k = cv2.waitKey(10) & 0xFF
    user_input = ''
    # début mission
    if k == ord('s'):
       user_input = 'start'
    # arrêt mission
    if k == ord('a'):
       user_input = 'abort'
    # arrêt hard mission
    if k == ord('e'):
       user_input = 'emergency'
    # fin du programme
    if k == ord('q'):
       user_input = 'quit'
    
    # communication avec le script maitre
    # si pas d'appui sur une touche : déroulement normal (objet à "none" si on n'a rien vu)
    if user_input == '':
      output = bibsys.wrap_output_rof(type_objet, coords, incertitude_coords, cap, incertitude_cap)
    # sinon : on transmet le code de l'action
    else:
      output = user_input
    
    sys.stdout.write(output + "\n")
    sys.stdout.flush()
   


# Fin de la boucle ----------------------------------------------------------------------------------------------



