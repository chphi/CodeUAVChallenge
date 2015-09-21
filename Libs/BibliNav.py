# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 21:34:22 2015

@author: Charles

Bibliothèque de fonctions servant à calculer la localisation GPS d'un objet vu par la
caméra du drone en fonction d'informations sur la position (GPS et altitude) du drone et de la position de 
l'objet sur l'image

Bibli simplifiée sans numpy et sans les fonctions de "discrimination" des objets
 à l'écran (fonctions laissées dans BibliLocalisation).
=> pour compatibilité avec Mission Planner.

Sommaire des fonctions :

  - sinus
      -> sinus d'un angle en degrés
      
  - cosinus
      -> cosinus d'un angle en degrés
     
  - posPixToPosRelativeDrone
      -> transforme la position d'un point sur l'image (ligne et colonne) en position relative par rapport au
      drone (mètres)
  
  - angleFlecheToCap
      -> à partir de l'angle d'une flèche et du cap du drone, donne le cap absolu de la flèche
  
  - posRelativeToPosNSEW
      -> à partir de la position relative en mètres d'un objet par rapport au drone, donne la position relative
      selon les axes Nord-Sud et Est-Ouest
  
  - posNSEWtoCoordsGPS
      -> à partir de la position relative par rapport au drone selon les axes Nord-Sud et Est-Ouest, donne les
      coordonnées GPS de l'objet vu à l'image
  
  - coordsGPSobjet
      -> passe directement de la position sur l'image (en lignes et colonnes) aux coordonnées GPS de l'objet vu
      
  - coordsNextWaypoint
      -> à partir des coordonnées d'une flèche donne les coordonnées d'un waypoint 15m plus loin dans la direction
      de la flèche
      
  - differenceCoords
      -> calcule la différence d'un tuple de coordonnées
  
  - distance
      -> calcule la distance entre deux points donnés par leurs coordonnées
"""

import sys
import math


# Variables --------------------------------------------------------------------

conf_path = 'D:/Charles/Documents/Sumo/Dassault UAV Challenge/Code/CodeUAVChallenge'


# Initialisation ---------------------------------------------------------------

# importe le fichier de configuration des scripts
sys.path.append(conf_path)
import conf_drone as cf


# Constantes -------------------------------------------------------------------

RT = cf.RT                                              # rayon de la terre en mètres
Pi = math.pi                                            # définition de Pi
taille_image = cf.taille_image
centre_image = cf.centre_image
ouverture_camera = cf.ouverture_camera                  # angle d'ouverture de la caméra, en degrés

sin_ouverture = math.sin(ouverture_camera / 180.0 * Pi) # sinus de l'angle d'ouverture, utile pour calculer les distances


# Fonctions --------------------------------------------------------------------

def sinus(angle_degres):
    """
    Sinus d'un angle en degrés à partir de np.sin
    
    angle_degrés -> sin(angle_degrés)
    """
    return math.sin(angle_degres/180.0*Pi)
    
    
def cosinus(angle_degres):
    """
    Cosinus d'un angle en degrés à partir de np.cos
    
    angle_degrés -> cos(angle_degrés)
    """
    return math.cos(angle_degres/180.0*Pi)


def posPixToPosRelativeDrone(pos_sur_image, angle_camera, altitude_drone):
    """
    Transforme la position d'un point sur l'image (ligne et colonne) en position relative par rapport au drone (mètres)
    Utilise implicitement l'angle d'ouverture de la caméra
    
    position_sur_image, altitude_drone -> position_relative
    """
    
    # TODO : prendre en compte l'angle caméra
    
    # pos_sur_image : (ligne, colonne)
    
    pos_centree_x = pos_sur_image[0] - centre_image[0]          # d'abord les colonnes dans l'indexage donc ici : 2ème coord pour x
    pos_centree_y = centre_image[1] - pos_sur_image[1]          # axe des lignes vers le bas
    
    facteur_echelle_x = altitude_drone * sin_ouverture / taille_image[1]
    facteur_echelle_y = altitude_drone * sin_ouverture / taille_image[0]
    
    pos_relative_metres_x = pos_centree_x * facteur_echelle_x
    pos_relative_metres_y = pos_centree_y * facteur_echelle_y
    
    return (pos_relative_metres_x, pos_relative_metres_y)       # "(colonne, ligne)", i.e la 1ère grandeur est celle perpendiculaire au drone
    

def angleFlecheToCap(cap_drone, angle_fleche): # caps en degrés
    """
    A partir de l'angle d'une flèche (sur l'image) et du cap du drone, donne le cap absolu de la flèche
    
    cap_drone, angle_flèche -> cap_flèche
    """
    return angle_fleche + cap_drone # retourne le cap de la flèche en degrés
    

def posRelativeToPosNSEO(cap_drone, pos_relative):   # rend la distance de l'objet au drone selon l'axe Est-Ouest et Nord-Sud
    """
    A partir de la position relative en mètres d'un objet par rapport au drone, donne la position relative selon les axes
    Nord-Sud et Est-Ouest. Ces informations servent ensuite à calculer les coordonnées GPS de l'objet vu.
    
    cap_drone, position_relative_objet -> (dist_relative_nord_sud, dist_relative_est_ouest)
    """
    theta = cap_drone # angle de rotation du repère en degrés
    (x,y) = pos_relative # x = distance perpendiculairement à l'axe du drone, y = distance dans l'axe   
    
    d_EO = x*cosinus(theta) + y*sinus(theta)    # distance Est-Ouest
    d_NS = y*cosinus(theta) - x*sinus(theta)    # distance Nord-Sud
    
    return (d_NS, d_EO)  # distance Nord-Sud puis Est-Ouest
    
    # NB : pour trouver la pos. relative Est-Ouest et Nord-Sud de la prochaine flèche par rapport à celle qu'on vient de voir:
    # il faut donner en argument le cap de la flèche vue et en pos_relative : (0,15)   (15m dans l'axe de la flèche)
    # Conclusion : pour des raisons de compréhension cette fonction est écrite pour trouver la position relative selon l'axe 
    # Est-Ouest et Nord-Sud d'un objet vu du drone mais on peut s'en servir aussi pour déterminer la position de la prochaine
    # flèche.
    
    
def posNSEOtoCoordsGPS(pos_NSEO_objet, coords_drone):
    """
    A partir de la position relative d'un objet par rapport au drone selon les axes Nord-Sud et Est-Ouest, donne les
    coordonnées GPS de l'objet vu à l'image
    
    pos_relative_nseo_objet, coords_drone, alt_drone -> coords_GPS_objet
    """
    (lat, longit) = coords_drone
    (d_NS, d_EW) = pos_NSEO_objet
    
    lat_objet = lat + (d_NS/RT) * 180.0/Pi
    longit_objet = longit + d_EW/(RT*cosinus(lat_objet)) * 180.0/Pi
    
    return (lat_objet, longit_objet)
    
    
def coordsGPSobjet(coords_drone, cap_drone, altitude_drone, pos_objet_sur_image, angle_camera):
    """
    à partir de la position d'un objet à l'image et des données de localisation du drone, donne les coordonnées GPS de
    l'objet vu sur l'image
    
    coords_drone, cap_drone, altitude_drone, pos_objet_sur_image, angle_camera -> coords_GPS_objet
    """
    pos_relative = posPixToPosRelativeDrone(pos_objet_sur_image, angle_camera, altitude_drone)
    pos_relative_NS_EO = posRelativeToPosNSEO(cap_drone, pos_relative)
    coords_cible_sur_ecran = posNSEOtoCoordsGPS(pos_relative_NS_EO, coords_drone)
    
    return coords_cible_sur_ecran


def coordsNextWaypoint(coords_fleche, cap_fleche):
    """
    à partir des coordonnées d'une flèche donne les coordonnées d'un waypoint 15m plus loin dans la direction de la flèche
    
    coords_fleche, angle_fleche, cap_drone -> coords_next_waypoint
    """
    (lat, longit) = coords_fleche
    
    (d_NS, d_EW) = posRelativeToPosNSEO(cap_fleche, (0, 15))  # prochain WP dans 15m en direction de la flèche vue
    
    lat_WP = lat + d_NS/RT * 180.0/Pi
    longit_WP = longit + d_EW/(RT*cosinus(lat_WP)) * 180.0/Pi
    
    return (lat_WP, longit_WP)
    

def differenceCoords(coords1, coords2):
    """
    calcul l'écart en latitude et longitude entre deux coordonnées gps (différence de coordonnées)
    """
    return (coords1[0] - coords2[0], coords1[1] - coords2[1])
    
    
def distance(coords1, coords2):
    """
    Calcule la distance en mètre en ligne droite (=au sol si on néglige la courbure de la terre sur les petites distances)
    entre deux points définis par leurs coordonnées GPS
    """
    d_lat, d_long = differenceCoords(coords1, coords2)
    
    d_NS = d_lat * RT * (Pi/180)
    d_EO = d_long * RT * cosinus(coords1[0]) * (Pi/180)
    
    return math.sqrt(d_NS**2 + d_EO**2)
