# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 15:56:48 2015

@author: Charles

Fichier de configuration des scripts du drone. 
Il faut indiquer l'adresse de ce fichier dans les scripts que l'on veut exécuter
"""


# Variables liées à la mission -------------------------------------------------

initial_target = (48.7078, 2.1603)

# Variables d'environnement ------------------------------------------------------------

# emplacement des biblis persos pour le code du drone
libpath = 'D:/Charles/Documents/Sumo/Dassault UAV Challenge/Code/CodeUAVChallenge/Libs'

# Variables ROF ------------------------------------------------------------------------

is_cam_embarquee = True                   # utilisation de la webcam ou de la caméra embarquée
emb_cam_num = 0                           # n° de device de la caméra du drone (tester pour chaque pc)
webcam_num = 0                            # idem pour la webcam (à tester aussi)

# variables communes ROF
dh = 30                                  # valeurs autour de la teinte de référence qu'on va tracker
sat_min = 60                             # saturation min d'une couleur à tracker (base hsv)
val_min = 60                             # valeur min d'une couleur à tracker (base hsv)
n_blur = 7                               # ordre du filtre gaussien (tracking)
t_o = 5                                  # taille du noyau pour l'opening
Amax = 1000*1000                         # aire max. Les deux sont éventuellement à adapter à l'altitude
n_gauss = 3                              # ordre du filtre gaussien pour flouter le patron et l'objet à matcher

# définition de la flèche
Amin_fleche = 1000                       # aire en dessous de laquelle un contour n'est pas considéré pertinent
teinte_fleche = 0
s_max_fleche = 0.8                       # solidité max
r_min_fleche = .35                       # ratio petite dimension/grande dimension min
r_max_fleche = .65                       # ratio petite dimension/grande dimension max
pas_angle_fleche = 5                     # pas de test des orientations pour le template matching (peut buguer si modifié)
seuil_certitude_fleche = 0.80            # seuil de corrélation avec un patron au dessus duquel on matche

# définition de la croix
Amin_croix = 500 
teinte_croix = 35
n_zone_croix = 51                        # doit être impair
v_moy_croix = -12
s_max_croix = 0.8                        # solidité max
r_min_croix = .70                        # ratio petite dimension/grande dimension min
r_max_croix = 1.                         # ratio petite dimension/grande dimension max
pas_angle_croix = 10                     # pas de test des orientations pour le template matching (peut buguer si modifié)
seuil_certitude_croix = 0.75
    
# définition du rectangle
Amin_rect = 2000 
n_zone = 135                             # taille de la zone pour calculer le seuil adaptatif (doit être impair)
v_moy = 2                               # valeur à enlever au seuil moyen
s_min = 0.7                             # solidité min
r_min = .40                              # ratio grande dimension/petite dimension min
r_max = .60                              # ratio grande dimension/petite dimension max    
seuil_aire = 0.80                        # rapport max entre l'aire d'un contour et l'aire du rectangle fitté 
epsi_ratio = 0.05                        # longueur min de l'approx des contours, en rapport au périmètre d'un contour


# Variables  localisation ------------------------------------------------------

RT = 6368000.0                           # rayon de la terre (en mètres)
taille_image = (640, 480)
centre_image = (320, 240)
ouverture_camera = 60.0     

taille_mem = 4                           # nb d'infos gardées en mémoire (initialiser les listes associées au bon nb d'élts)
seuil_sigma_pos = 2                      # seuil d'écart type en dessous duquel on considère avoir bien vu la position de l'objet
seuil_sigma_cap = 5                      # idem pour les angles (cas d'une flèche)
d_seuil = 3                              # distance en dessous de laquelle on considère que deux objets vus sont les mêmes
dist_max = 15                            # distance max entre deux formes (si on dépasse cette distance et qu'on a rien vu : demi-tour)


# Variables automate -----------------------------------------------------------

ignore_invalid_triggers = True


# Variables mission ------------------------------------------------------------

max_time = 300                           # temps max pour l'exécution de la mission, au delà on s'arrête
dropping_time = 1                        # temps de largage de bombe (en secondes)
max_alt = 20                             # altitude de consigne max autorisée (en mètres)
landing_alt = 3                          # altitude à laquelle on se place au dessus de la zone d'atterro pour atterrissage vertical
takeoff_alt = 5                          # alt à laquelle on décolle à la verticale avant de se déplacer (pour pouvoir voir les formes)
nav_alt = 7                              # altitude par défaut pour la navigation
dropping_alt = 2                         # altitude à laquelle on largue les bombes
min_rof_alt = 1.5                        # altitude mini de prise en compte des infos de la reconnaissance de formes


# Divers -----------------------------------------------------------------------

size_factor = 0.7                        # facteur de taille de la police
bleu = (255,0,0)
vert = (0,255,0)
rouge = (0,0,255)
jaune = (0,255,255)
blanc = (255,255,255)



