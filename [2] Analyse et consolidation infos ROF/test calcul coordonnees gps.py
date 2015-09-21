# -*- coding: utf-8 -*-
"""
Created on Mon Jun 08 22:29:59 2015

@author: Charles


Programme testant la conversion de la position d'un objet sur l'image en 
position par rapport au drone (mètres, cap) puis en coordonnées GPS de l'objet

TODO : 
- vérifier avant enregistrement d'un nouvel objet (flèche sur cet exemple) si 
ce n'est pas un ancien objet qu'on revoit en le comparant au parcours enregistré
- dans BibliLocalisation, moyenner le cap modulo 360° et tenir compte de cette
congruence dans la recherche du parcours de liste à écart-type minimal

"""

import sys


# Variables --------------------------------------------------------------------

conf_path = 'D:/Charles/Documents/Sumo/Dassault UAV Challenge/Code/CodeUAVChallenge'

coords_drone = (48.7077, 2.1602)
altitude_drone = 10                    # altitude du drone en mètres
cap_drone = 0                          # cap du drone (en degrés)
orientation_camera = (0,0)             # caméra à plat, devant = haut de l'image.

# rappel : l'image fait env. 640x480px (webcam) ou 720x576 (embarqué) (col. puis lignes inversées : repère "windows")
position_objet = (320, 40)             # position fictive d'un objet sur une image filmée à partir du drone (pour test)
cap_fleche = 30                        # cap de la flèche fictive à l'écran (suppose qu'on connaissait le cap du drone pour calculer ça)


# Initialisations --------------------------------------------------------------

# importe le fichier de configuration des scripts
sys.path.append(conf_path)
import conf_drone as cf

# importe les biblis persos
sys.path.append(cf.libpath)
import BibliLocalisation as loc


# Utilisation sur un exemple : détection d'une flèche --------------------------

pos_relative_fleche = loc.posPixToPosRelativeDrone(position_objet, orientation_camera, altitude_drone)
coords_fleche = loc.coordsGPSobjet(coords_drone, cap_drone, altitude_drone, position_objet, orientation_camera)
coords_next_waypoint = loc.coordsNextWaypoint(coords_fleche, cap_fleche)

# on peut tester le code en rentrant les coordonnées sur Mission Planner







