# -*- coding: utf-8 -*-
"""
Created on Sun Sep 20 16:55:57 2015

@author: Charles

Script de test de l'automate à états implémentant le comportement du drone.

Un scénario est rentré dans le script, et on a un suivi sur la console.
"""

import sys
import time

# Variables --------------------------------------------------------------------

conf_path = 'D:/Charles/Documents/Sumo/Dassault UAV Challenge/Code/CodeUAVChallenge'

# infos sur le drone
motors_armed = True                      # dit si le drone est prêt à décoller ou non
standby_coords = (48.70770, 2.16000)
initial_coords = (48.70771, 2.16021)

alt_drone = 10                           # altitude du drone en mètres
cap_drone = 0                            # cap du drone (en degrés)
orientation_cam = (0,0)                  # caméra à plat, devant = haut de l'image.

# 1ère flèche fictive au sol
first_arrow_coords = (48.70769, 2.16018)
first_arrow_heading = 30

# croix
cross_coords = (48.70775, 2.16018)

# deuxième flèche
scnd_arrow_coords = (48.7077, 2.1603)
scnd_arrow_heading = 240

# zone d'atterrissage
landing_coords = (48.707806, 2.1603)

# Initialisation du programme --------------------------------------------------

# importe le fichier de configuration des scripts
sys.path.append(conf_path)
import conf_drone as cf

# importe les biblis persos
sys.path.append(cf.libpath)
import Drone as classDrone
import BibliNav as nav


# Test de l'automate -----------------------------------------------------------

# à faire avant initialisation de l'automate : init du drone (GPS OK, moteurs armés)
# permet entre autres d'avoir les coords de décollage
while( not(motors_armed) ):
  time.sleep(0.5)

# initialise la machine à états
drone = classDrone.Drone((standby_coords, cap_drone, alt_drone), initial_coords)


  # Etat initial

print('\n')
print('état initial : ' + drone.state)


  # Ordre de décoller

print('>> ordre de décollage')
drone.take_off_order()


  # Détection flèche

coords_drone = (48.7077, 2.1602) # le drone a bougé entre temps
print('\nétat actuel : ' + drone.state)
print('>> détection flèche')
drone.arrow_detected(first_arrow_coords, first_arrow_heading)


  # Détection croix

print('\nétat actuel : ' + drone.state)
print('>> détection croix')
# on passe en argument l'endroit où on allait avant de voir la croix
drone.cross_detected(cross_coords)


  # Teste le cas du drone perdu

print('\nétat actuel : ' + drone.state)
print('>> est allé trop loin')
drone.coords = (48.70781, 2,16033) # le drone est parti trop loin
distance = nav.distance(drone.last_known_location, drone.coords)
# le test se fait hors automate (à faire à chaque boucle)
if distance > cf.dist_max:
  drone.is_lost()


  # Retrouve une flèche

print('\nétat actuel : ' + drone.state)
print('>> flèche détectée')
drone.arrow_detected(scnd_arrow_coords, scnd_arrow_heading)


  # Détecte la zone d'atterrissage

print('\nétat actuel : ' + drone.state)
print('>> zone d\'atterrissage détectée')
drone.landing_detected(landing_coords)

















