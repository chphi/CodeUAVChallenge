# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 15:56:48 2015

@author: Charles

Fichier de configuration des scripts du drone. 
Il faut indiquer l'adresse de ce fichier dans les scripts que l'on veut exécuter
"""

# Variables d'environnement ------------------------------------------------------------

# emplacement des biblis persos pour le code du drone
libpath = 'D:/Charles/Documents/Sumo/Dassault UAV Challenge/Code/CodeUAVChallenge/Libs'

# Variables ROF ------------------------------------------------------------------------

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


# Variables  localisation ------------------------------------------------------

taille_mem = 4                           # nb d'infos gardées en mémoire (initialiser les listes associées au bon nb d'élts)
seuil_sigma_pos = 2                      # seuil d'écart type en dessous duquel on considère avoir bien vu la position de l'objet
seuil_sigma_cap = 5                      # idem pour les angles (cas d'une flèche)
d_seuil = 3                              # distance en dessous de laquelle on considère que deux objets vus sont les mêmes


# Divers -----------------------------------------------------------------------

size_factor = 0.7                        # facteur de taille de la police
bleu = (255,0,0)
vert = (0,255,0)
rouge = (0,0,255)
jaune = (0,255,255)
blanc = (255,255,255)