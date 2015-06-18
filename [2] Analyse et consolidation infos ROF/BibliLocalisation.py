# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 20:56:44 2015

@author: Charles

Ce script est une bibliothèque de fonctions servant à calculer la localisation GPS d'un objet vu par la caméra du drone
en fonction d'informations sur la position (GPS et altitude) du drone et de la position de l'objet sur l'image

Sommaire des fonctions :

  - sinus
      -> sinus d'un angle en degrés
      
  - cosinus
      -> idem en cos
     
  - posPixToPosRelativeDrone
      -> transforme la position d'un point sur l'image (ligne et colonne) en position relative par rapport au drone (mètres)
  
  - angleFlecheToCap
      -> à partir de l'angle d'une flèche et du cap du drone, donne le cap absolu de la flèche
  
  - posRelativeToPosNSEW
      -> à partir de la position relative en mètres d'un objet par rapport au drone, donne la position relative selon les axes
         Nord-Sud et Est-Ouest
  
  - posNSEWtoCoordsGPS
      -> à partir de la position relative par rapport au drone selon les axes Nord-Sud et Est-Ouest, donne les coordonnées GPS
         de l'objet vu à l'image
  
  - coordsGPSobjet
      -> passe directement de la position sur l'image (en lignes et colonnes) aux coordonnées GPS de l'objet vu
      
  - coordsNextWaypoint
      -> à partir des coordonnées d'une flèche donne les coordonnées d'un waypoint 15m plus loin dans la direction de la flèche
      
"""


import numpy as np

RT = 6368000.0                                          # rayon de la terre en mètres
Pi = np.pi                                              # définition de Pi
taille_image = (640, 480)
centre_image = (320, 240)
ouverture_camera = 60.0                                 # angle d'ouverture de la caméra, en degrés
sin_ouverture = np.sin(ouverture_camera / 180.0 * Pi)   # sinus de l'angle d'ouverture, utile pour calculer les distances


def sinus(angle_degres):
    """
    Sinus d'un angle en degrés à partir de np.sin
    
    angle_degrés -> sin(angle_degrés)
    """
    return np.sin(angle_degres/180.0*Pi)
    
    
def cosinus(angle_degres):
    """
    Cosinus d'un angle en degrés à partir de np.cos
    
    angle_degrés -> cos(angle_degrés)
    """
    return np.cos(angle_degres/180.0*Pi)


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


def coordsNextWaypoint(coords_fleche, angle_fleche, cap_drone):
    """
    à partir des coordonnées d'une flèche donne les coordonnées d'un waypoint 15m plus loin dans la direction de la flèche
    
    coords_fleche, angle_fleche, cap_drone -> coords_next_waypoint
    """
    (lat, longit) = coords_fleche
    
    cap_fleche = angleFlecheToCap(cap_drone, angle_fleche)
    
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
    
    return np.sqrt(d_NS**2 + d_EO**2)

def moyenne(tab):
    
    return np.mean(tab)

def ecartType(tab):
    
    m=moyenne(tab)
    return moyenne([(x-m)**2 for x in tab]) **0.5  


def supprValeursAberrantes(tab, taille_finale):
    """
    supprime les valeurs d'un tableau de nombres le plus éloignées de la moyenne tant qu'on est au dessus de la taille min
    """
    while (len(tab)) > taille_finale:
        ecarts_valeur_moy = abs(tab - moyenne(tab))
        i_valeur_la_plus_aberrante = np.argmax(ecarts_valeur_moy)
        tab = np.delete(tab, i_valeur_la_plus_aberrante)
        
    return tab
     
     
def filtreCaps(caps):

    taille_mem = len(caps)          # taille mémoire    
    l = np.concatenate(caps) 
    
    caps_coherents = supprValeursAberrantes(l, taille_mem)
    
    return caps_coherents
        
def filtreCoordonnees(localisations):
    """
    idem que la fonction précédente pour des tuples à la place des nombres : travaille séparément sur les 1ers et seconds élts
    """

    taille_mem = len(localisations)          # taille mémoire    
    l = np.concatenate(localisations)
    
    l = np.concatenate(l)                    # concatène toutes les coordonnées : [lat1, long1, lat2, long2, ...]
    n = len(l)
    
    latitudes = l[0:n-1:2]                   # récupère les latitudes (indices pairs)
    longitudes = l[1:n:2]
    
    lat_coherentes = supprValeursAberrantes(latitudes, taille_mem)
    longit_coherentes = supprValeursAberrantes(longitudes, taille_mem)
    
    return lat_coherentes, longit_coherentes
        
    

def rassembleCoords(latitudes, longitudes):
    
    coords = []
    
    for i in range(len(latitudes)):
        
        coords.append( (latitudes[i], longitudes[i]) )
        
    return coords
    

def supprimeCoordsEtCapsAberrants(liste_coordonnees, liste_caps):
    
    lats_filtrees, longits_filtrees = filtreCoordonnees(liste_coordonnees)
    caps_filtres = filtreCaps(liste_caps)
    
    return lats_filtrees, longits_filtrees, caps_filtres
    
    
def memoriseNewCoords(liste_coords, liste_pos_objet_sur_image, coords_drone, cap_drone, alt_drone, orientation_cam):    
    
    list_new_coords = []
    
    for i in range(len(liste_pos_objet_sur_image)):
        list_new_coords.append(coordsGPSobjet(coords_drone, cap_drone, alt_drone, liste_pos_objet_sur_image[i], orientation_cam))

    del liste_coords[0]
    liste_coords.append(list_new_coords)
    
    return liste_coords
    
    
def memoriseNewCaps(liste_caps, liste_angle_fleche_sur_image, cap_drone):

    new_caps = []

    for i in range(len(liste_angle_fleche_sur_image)):
        new_caps.append( angleFlecheToCap(liste_angle_fleche_sur_image[i], cap_drone) )    
    
    del liste_caps[0]
    liste_caps.append(new_caps)
    
    return liste_caps
    

def calculeMoyenneEtSigmaPosition(lats, longits):
    
    # calcul de la position GPS moyenne
    coords_moyennes = ( np.mean(lats), np.mean(longits) )
    
    # calcul de l'écart-type sur cette position
    serie_coords = rassembleCoords(lats, longits)
    d = []
    for i in range(3):
        d.append( distance(serie_coords[i], coords_moyennes) )  # calcul le vecteur de distances à la loc. moyenne
    sigma_pos = np.sqrt( np.dot(d,d) ) # calcule l'écart-type en mètres sur la localisation de l'objet
    
    return coords_moyennes, sigma_pos
    
    
def calculeMoyenneEtSigmaCap(caps_filtres):    
   
   # moyenne du cap
   cap_moyen = np.mean(caps_filtres)
   
   # écart-type du cap
   d = caps_filtres - cap_moyen
   sigma_cap = np.sqrt( np.dot(d,d) ) 
   
   return cap_moyen, sigma_cap


def testeReconnaissancesSuccessives(liste_caps, taille_mem):

    b = True
    
    for i in range(taille_mem):
        b = b and len(liste_caps[i]) > 0

    return b
    
   
def analyseReconnaissanceFleche(fleche, liste_coords, liste_caps, taille_mem, seuil_sigma_pos, seuil_sigma_cap, coords_drone, cap_drone, alt_drone, orientation_cam):
    
    pos_fleche = fleche.position
    angle_fleche = fleche.angle
    
    # Mémorisation nouvelles infos
    liste_coords = memoriseNewCoords(liste_coords, pos_fleche, coords_drone, cap_drone, alt_drone, orientation_cam)
    liste_caps = memoriseNewCaps(liste_caps, angle_fleche, cap_drone)
    
    if testeReconnaissancesSuccessives(liste_caps, taille_mem): # vérifie qu'on a reconnu au moins 
        # Calcul du chemin à écart-type minimal dans les listes et suppression des autres (positions/angles erronés)
        lats_filtrees, longits_filtrees, caps_filtres = supprimeCoordsEtCapsAberrants(liste_coords, liste_caps)
        
        # Calcul de la position GPS moyenne et cap moyen, et les écarts-types associés
        loc_moyenne, sigma_pos = calculeMoyenneEtSigmaPosition(lats_filtrees, longits_filtrees)
        cap_moyen, sigma_cap = calculeMoyenneEtSigmaCap(caps_filtres)
        
        # Validation flèche
        # la 3ème condition est de l'avoir effectivement détectée sur l'image en cours (sinon les calculs n'ont aucun sens)
        fleche_validee = (sigma_pos < seuil_sigma_pos) and (sigma_cap < seuil_sigma_cap) and fleche.estDetectee
        
        # Sortie : transmettre à l'automate info sur la flèche, position, cap (moyennés), et afficher à l'écran
        if fleche_validee:
            return True, loc_moyenne, sigma_pos, cap_moyen, sigma_cap 
        else:
            return False, (0,0), sigma_pos, 0, sigma_cap
    
    else:
        return False, (0,0), 0, 0, 0
    
    
    
    
    
    
    
    
    
    
    