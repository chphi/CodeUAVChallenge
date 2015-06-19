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

# import numpy as np
import BibliLocalisation as loc


# Variables -------------------------------------------------------------------

coords_drone = (48.7077, 2.1602)
altitude_drone = 10                    # altitude du drone en mètres
cap_drone = 0                          # cap du drone (en degrés)
orientation_camera = (0,0)             # caméra à plat, devant = haut de l'image.

# rappel : l'image fait env. 640x480px (webcam) ou 720x576 (embarqué) (col. puis lignes inversées : repère "windows")
position_objet = (320, 40)             # position fictive d'un objet sur une image filmée à partir du drone (pour test)
angle_fleche = 30                      # angle de la flèche fictive à l'écran par rapport à la verticale de l'image, en degrés (orienté sens horaire)


# Utilisation sur un exemple : détection d'une flèche -------------------------

pos_relative_fleche = loc.posPixToPosRelativeDrone(position_objet, orientation_camera, altitude_drone)
coords_fleche = loc.coordsGPSobjet(coords_drone, cap_drone, altitude_drone, position_objet, orientation_camera)
coords_next_waypoint = loc.coordsNextWaypoint(coords_fleche, angle_fleche, cap_drone)

# on peut tester le code en rentrant les coordonnées sur Mission Planner







