# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 20:56:44 2015

@author: Charles

Bibliothèque de fonctions servant à analyser les résultats de la reconnaissance
optique de formes en fonction d'informations sur la position (GPS et altitude) 
du drone et de la position du/des objets sur l'image

En pratique on va repérer les objets déjà vus, ne considérer un objet valide
que s'il a été vu sur plusieurs images à la suite et que les données sont
cohérentes, et sélectionner l'objet le plus plausible si on en voit plusieurs.

Sommaire des fonctions :
  
  - moyenne
      ->
  
  - ecartType
      ->
  
  - supprValeursAberrantes
      ->
  
  - filtreCaps
      ->
  
  - filtreCoordonnees
      ->
  
  - rassembleCoords
      ->
  
  - supprimeCoordsEtCapsAberrants
      ->
  
  - memoriseNewCoords
      ->
  
  - memoriseNewCaps
      ->
  
  - calculeMoyenneEtSigmaPosition
      ->
  
  - calculeMoyenneEtSigmaCap
      ->
  
  - testeReconnaissancesSuccessives
      ->
  
  - analyseReconnaissanceFleche
      ->

"""


import numpy as np
import sys


# Variables --------------------------------------------------------------------

conf_path = 'D:/Charles/Documents/Sumo/Dassault UAV Challenge/Code/CodeUAVChallenge'

# Initialisation ---------------------------------------------------------------

# importe le fichier de configuration des scripts
sys.path.append(conf_path)
import conf_drone as cf

# importe les biblis persos
sys.path.append(cf.libpath)
import BibliNav as nav

# Constantes -------------------------------------------------------------------

RT = cf.RT                                              # rayon de la terre en mètres
Pi = np.pi                                              # définition de Pi
taille_image = cf.taille_image
centre_image = cf.centre_image
ouverture_camera = cf.ouverture_camera                  # angle d'ouverture de la caméra, en degrés


sin_ouverture = np.sin(ouverture_camera / 180.0 * Pi)   # sinus de l'angle d'ouverture, utile pour calculer les distances

# Fonctions --------------------------------------------------------------------

#def sinus(angle_degres):
#    """
#    Sinus d'un angle en degrés à partir de np.sin
#    
#    angle_degrés -> sin(angle_degrés)
#    """
#    return np.sin(angle_degres/180.0*Pi)
#    
#    
#def cosinus(angle_degres):
#    """
#    Cosinus d'un angle en degrés à partir de np.cos
#    
#    angle_degrés -> cos(angle_degrés)
#    """
#    return np.cos(angle_degres/180.0*Pi)
#
#
#def posPixToPosRelativeDrone(pos_sur_image, angle_camera, altitude_drone):
#    """
#    Transforme la position d'un point sur l'image (ligne et colonne) en position relative par rapport au drone (mètres)
#    Utilise implicitement l'angle d'ouverture de la caméra
#    
#    position_sur_image, altitude_drone -> position_relative
#    """
#    
#    # TODO : prendre en compte l'angle caméra
#    
#    # pos_sur_image : (ligne, colonne)
#    
#    pos_centree_x = pos_sur_image[0] - centre_image[0]          # d'abord les colonnes dans l'indexage donc ici : 2ème coord pour x
#    pos_centree_y = centre_image[1] - pos_sur_image[1]          # axe des lignes vers le bas
#    
#    facteur_echelle_x = altitude_drone * sin_ouverture / taille_image[1]
#    facteur_echelle_y = altitude_drone * sin_ouverture / taille_image[0]
#    
#    pos_relative_metres_x = pos_centree_x * facteur_echelle_x
#    pos_relative_metres_y = pos_centree_y * facteur_echelle_y
#    
#    return (pos_relative_metres_x, pos_relative_metres_y)       # "(colonne, ligne)", i.e la 1ère grandeur est celle perpendiculaire au drone
#    
#
#def angleFlecheToCap(cap_drone, angle_fleche): # caps en degrés
#    """
#    A partir de l'angle d'une flèche (sur l'image) et du cap du drone, donne le cap absolu de la flèche
#    
#    cap_drone, angle_flèche -> cap_flèche
#    """
#    return angle_fleche + cap_drone # retourne le cap de la flèche en degrés
#    
#
#def posRelativeToPosNSEO(cap_drone, pos_relative):   # rend la distance de l'objet au drone selon l'axe Est-Ouest et Nord-Sud
#    """
#    A partir de la position relative en mètres d'un objet par rapport au drone, donne la position relative selon les axes
#    Nord-Sud et Est-Ouest. Ces informations servent ensuite à calculer les coordonnées GPS de l'objet vu.
#    
#    cap_drone, position_relative_objet -> (dist_relative_nord_sud, dist_relative_est_ouest)
#    """
#    theta = cap_drone # angle de rotation du repère en degrés
#    (x,y) = pos_relative # x = distance perpendiculairement à l'axe du drone, y = distance dans l'axe   
#    
#    d_EO = x*cosinus(theta) + y*sinus(theta)    # distance Est-Ouest
#    d_NS = y*cosinus(theta) - x*sinus(theta)    # distance Nord-Sud
#    
#    return (d_NS, d_EO)  # distance Nord-Sud puis Est-Ouest
#    
#    # NB : pour trouver la pos. relative Est-Ouest et Nord-Sud de la prochaine flèche par rapport à celle qu'on vient de voir:
#    # il faut donner en argument le cap de la flèche vue et en pos_relative : (0,15)   (15m dans l'axe de la flèche)
#    # Conclusion : pour des raisons de compréhension cette fonction est écrite pour trouver la position relative selon l'axe 
#    # Est-Ouest et Nord-Sud d'un objet vu du drone mais on peut s'en servir aussi pour déterminer la position de la prochaine
#    # flèche.
#    
#    
#def posNSEOtoCoordsGPS(pos_NSEO_objet, coords_drone):
#    """
#    A partir de la position relative d'un objet par rapport au drone selon les axes Nord-Sud et Est-Ouest, donne les
#    coordonnées GPS de l'objet vu à l'image
#    
#    pos_relative_nseo_objet, coords_drone, alt_drone -> coords_GPS_objet
#    """
#    (lat, longit) = coords_drone
#    (d_NS, d_EW) = pos_NSEO_objet
#    
#    lat_objet = lat + (d_NS/RT) * 180.0/Pi
#    longit_objet = longit + d_EW/(RT*cosinus(lat_objet)) * 180.0/Pi
#    
#    return (lat_objet, longit_objet)
#    
#    
#def coordsGPSobjet(coords_drone, cap_drone, altitude_drone, pos_objet_sur_image, angle_camera):
#    """
#    à partir de la position d'un objet à l'image et des données de localisation du drone, donne les coordonnées GPS de
#    l'objet vu sur l'image
#    
#    coords_drone, cap_drone, altitude_drone, pos_objet_sur_image, angle_camera -> coords_GPS_objet
#    """
#    pos_relative = posPixToPosRelativeDrone(pos_objet_sur_image, angle_camera, altitude_drone)
#    pos_relative_NS_EO = posRelativeToPosNSEO(cap_drone, pos_relative)
#    coords_cible_sur_ecran = posNSEOtoCoordsGPS(pos_relative_NS_EO, coords_drone)
#    
#    return coords_cible_sur_ecran
#
#
#def coordsNextWaypoint(coords_fleche, cap_fleche):
#    """
#    à partir des coordonnées d'une flèche donne les coordonnées d'un waypoint 15m plus loin dans la direction de la flèche
#    
#    coords_fleche, angle_fleche, cap_drone -> coords_next_waypoint
#    """
#    (lat, longit) = coords_fleche
#    
#    (d_NS, d_EW) = posRelativeToPosNSEO(cap_fleche, (0, 15))  # prochain WP dans 15m en direction de la flèche vue
#    
#    lat_WP = lat + d_NS/RT * 180.0/Pi
#    longit_WP = longit + d_EW/(RT*cosinus(lat_WP)) * 180.0/Pi
#    
#    return (lat_WP, longit_WP)
#    
#
#def differenceCoords(coords1, coords2):
#    """
#    calcul l'écart en latitude et longitude entre deux coordonnées gps (différence de coordonnées)
#    """
#    return (coords1[0] - coords2[0], coords1[1] - coords2[1])
#    
#    
#def distance(coords1, coords2):
#    """
#    Calcule la distance en mètre en ligne droite (=au sol si on néglige la courbure de la terre sur les petites distances)
#    entre deux points définis par leurs coordonnées GPS
#    """
#    d_lat, d_long = differenceCoords(coords1, coords2)
#    
#    d_NS = d_lat * RT * (Pi/180)
#    d_EO = d_long * RT * cosinus(coords1[0]) * (Pi/180)
#    
#    return np.sqrt(d_NS**2 + d_EO**2)


# ------------------------------------------------------------------------------

def moyenne(tab):
    """
    retourne la moyenne d'un tableau de nombres (numpy array)
    """
    return np.mean(tab)

def ecartType(tab):
    """
    retourne l'écart type d'un tableau de nombres (numpy array)
    """
    m=moyenne(tab)
    return moyenne([(x-m)**2 for x in tab]) **0.5  


def supprValeursAberrantes(tab, taille_finale):
    """
    supprime les valeurs d'un tableau de nombres les plus éloignées de la moyenne, tant qu'on est
    au dessus de la taille finale
    """
    while (len(tab)) > taille_finale:
        ecarts_valeur_moy = abs(tab - moyenne(tab))
        i_valeur_la_plus_aberrante = np.argmax(ecarts_valeur_moy)
        tab = np.delete(tab, i_valeur_la_plus_aberrante)
        
    return tab
     
     
def filtreCaps(caps):
    """
    Applique la fonction précédente à un tableau de listes de caps (tableau des caps de la flèche à chaque
    instant, c'est pour ça que si on voit plusieurs flèches sur une image, il y aura une liste de caps)
    """
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
    """
    rassemble un tableau de latitudes et de longitudes pour faire un tableau de coordonnées (array de tuples)
    """
    coords = []
    for i in range(len(latitudes)):
        coords.append( (latitudes[i], longitudes[i]) )
        
    return coords
    

def supprimeCoordsEtCapsAberrants(liste_coordonnees, liste_caps):
    """
    Filtre les caps et coordonnées en même temps pour ne garder que les plus cohérents. Utilise les
    sous-fonctions relatives à ces deux grandeurs.
    """
    lats_filtrees, longits_filtrees = filtreCoordonnees(liste_coordonnees)
    caps_filtres = filtreCaps(liste_caps)
    
    return lats_filtrees, longits_filtrees, caps_filtres
    
    
def memoriseNewCoords(liste_coords, liste_pos_objet_sur_image, coords_drone, cap_drone, alt_drone, orientation_cam):    
    """
    Mémorise les coordonnées de l'objet (ou des objets) vus à l'image dans la liste "mémoire" liste_coords
    Cette liste est de taille fixe (mémoire à court terme, taille fixée par le script)
    
    Cette fonction ne tient pas compte de la tailel fixe : elle enlève l'élément le plus ancien et ajoute le
    nouveau. Il est donc important d'initialiser liste_coords au bon nombre d'éléments.
    """
    list_new_coords = []
    for i in range(len(liste_pos_objet_sur_image)):
        list_new_coords.append(nav.coordsGPSobjet(coords_drone, cap_drone, alt_drone, liste_pos_objet_sur_image[i], orientation_cam))
    del liste_coords[0]
    liste_coords.append(list_new_coords)
    
    return liste_coords
    
    
def memoriseNewCaps(liste_caps, liste_angle_fleche_sur_image, cap_drone):
    """
    Mémorise les caps de la flèche (ou les flèches) vues à l'image dans la liste "mémoire" liste_caps
    Cette liste est de taille fixe (mémoire à court terme, taille fixée par le script)
    
    Cette fonction ne tient pas compte de la tailel fixe : elle enlève l'élément le plus ancien et ajoute le
    nouveau. Il est donc important d'initialiser liste_caps au bon nombre d'éléments (même nombre que la liste
    des coordonnées).
    """
    new_caps = []
    for i in range(len(liste_angle_fleche_sur_image)):
        new_caps.append( nav.angleFlecheToCap(liste_angle_fleche_sur_image[i], cap_drone) )    
    del liste_caps[0]
    liste_caps.append(new_caps)
    
    return liste_caps
    

def calculeMoyenneEtSigmaPosition(lats, longits):
    """
    Calcule en une fois la moyenne et l'écart-type sur une liste de coordonnées (à rentrer sous forme séparée
    latitudes et longitudes.
    """
    # calcul de la position GPS moyenne
    coords_moyennes = ( moyenne(lats), moyenne(longits) )
    # calcul de l'écart-type sur cette position
    serie_coords = rassembleCoords(lats, longits)
    d = []
    for i in range(3):
        d.append( nav.distance(serie_coords[i], coords_moyennes) )  # calcul le vecteur de distances à la loc. moyenne
    sigma_pos = np.sqrt( np.dot(d,d) ) # calcule l'écart-type en mètres sur la localisation de l'objet
    
    return coords_moyennes, sigma_pos
    
    
def calculeMoyenneEtSigmaCap(caps_filtres):    
   """
   Calcule en une fois la moyenne et l'écart-type sur une liste de caps
   """
   # moyenne du cap
   cap_moyen = np.mean(caps_filtres)
   # écart-type du cap
   d = caps_filtres - cap_moyen
   sigma_cap = np.sqrt( np.dot(d,d) ) 
   
   return cap_moyen, sigma_cap


def testeReconnaissancesSuccessives(liste_coords, taille_mem):
    """
    Détermine si on a bien reconnu l'objet sur les taille_mem dernières images successives
    
    NB : dans le cas où on a reconnu 1 objet sur les images sauf la dernière où on ne l'a pas vu : 
    pour la dernière image la liste vide sera ajoutée à liste_coords, elle n'aura donc pas la 
    taille voulue et cela va lever une exception
    """
    b = True
    try:
      for i in range(taille_mem):
          b = b and len(liste_coords[i]) > 0
    except Exception, e:
      b = False
   
    return b


def dejaVu(parcours_valide, coords_nouvel_objet, d_seuil): 
    """
    détermine si un objet détecté puis validé n'avait pas déjà été survolé et inscrit dans le parcours.
    parcours = liste de tuples (coordonnees, cap). cap = 0 si croix
    """
    deja_vu = False
    for i in range(len(parcours_valide)):
        d = nav.distance(coords_nouvel_objet, parcours_valide[i][0])
        if d < d_seuil:
            deja_vu = True
            break
    
    return deja_vu        
        
   
def analyseReconnaissanceFleche(fleche, liste_coords, liste_caps, taille_mem, seuil_sigma_pos, seuil_sigma_cap, coords_drone, cap_drone, alt_drone, orientation_cam):
    """
    Fonction synthétique déterminant si on peut confirmer la détection d'une flèche vue à l'image.
    Rend un booléen confirmant ou non cette détection, ainsi que la valeur et l'écart-type de la 
    position GPS et du cap mesurés.
    """
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
            return (True, loc_moyenne, sigma_pos, cap_moyen, sigma_cap) 
        else:
            return (False, (0,0), sigma_pos, 0, sigma_cap)
    
    else:
        return (False, (0,0), 0, 0, 0)
    
    
def analyseReconnaissanceObjet(objet, liste_coords, taille_mem, seuil_sigma_pos, coords_drone, cap_drone, alt_drone, orientation_cam):
    """
    Fonction synthétique déterminant si on peut confirmer la détection d'une croix ou d'un rectangle
    vu à l'image (PAS une flèche).
    Rend un booléen confirmant ou non cette détection, ainsi que la valeur et l'écart-type de la 
    position GPS.
    """    
    pos_objet = objet.position
    
    # Mémorisation nouvelles infos
    liste_coords = memoriseNewCoords(liste_coords, pos_objet, coords_drone, cap_drone, alt_drone, orientation_cam)
    
    if testeReconnaissancesSuccessives(liste_coords, taille_mem): # vérifie qu'on a reconnu au moins 
        # Calcul du chemin à écart-type minimal dans les listes et suppression des autres (positions/angles erronés)
        lats_filtrees, longits_filtrees = filtreCoordonnees(liste_coords)
        
        # Calcul de la position GPS moyenne et cap moyen, et les écarts-types associés
        loc_moyenne, sigma_pos = calculeMoyenneEtSigmaPosition(lats_filtrees, longits_filtrees)
        
        # Validation flèche
        # la 3ème condition est de l'avoir effectivement détectée sur l'image en cours (sinon les calculs n'ont aucun sens)
        objet_valide = (sigma_pos < seuil_sigma_pos) and objet.estDetecte
        
        # Sortie : transmettre à l'automate info sur la flèche, position, cap (moyennés), et afficher à l'écran
        if objet_valide:
            return (True, loc_moyenne, sigma_pos) 
        else:
            return (False, (0,0), sigma_pos)
    
    else:
        return (False, (0,0), 0)
    
    
def discrimineObjetsValides(donnees_fleche, donnees_croix, donnees_rectangle, parcours, d_seuil, coords_drone):
    """
    Vérifie que l'objet ou les objets validés n'ont pas déjà été vus, et s'il y en a plusieurs rend uniquement
    celui le plus proche du drone. On peut aussi privilégier l'objet le plus en avant par rapport au drone (le
    plus haut dans l'image)
    """    
    (fleche_validee, coords_fleche, sigma_pos_fleche, cap_fleche, sigma_cap) = donnees_fleche
    (croix_validee, coords_croix, sigma_pos_croix) = donnees_croix
    (rectangle_valide, coords_rectangle, sigma_pos_rectangle) = donnees_rectangle    
    
    nouvelle_fleche = dejaVu(parcours, coords_fleche, d_seuil) # booléen valant vrai si la flèche est un nouvel objet
    nouvelle_croix = dejaVu(parcours, coords_croix, d_seuil)
    nouveau_rectangle = dejaVu(parcours, coords_rectangle, d_seuil)
    
    types_objets = ['fleche','croix','rectangle']
    liste_donnees = [donnees_fleche, donnees_croix, donnees_rectangle]
    l = [nouvelle_fleche, nouvelle_croix, nouveau_rectangle]
    
    # suppression des objets pas nouveaux ou pas validés
    n = len(l)
    i = 0
    while i < n:
        if (not l[i]) and liste_donnees[i][0]: # si l'objet a été validé et est nouveau, on le laisse dans la liste
            i = i + 1
        else:                            # sinon on supprime les infos associées
            del l[i]
            del types_objets[i]
            del liste_donnees[i]
            n = n - 1
    
    # dans ce qui reste on prend le plus proche du drone. Attention, l peut être vide à cette étape, d'où l'exception
    distances = []
    for i in range(len(l)):
        distances.append(nav.distance(coords_drone, liste_donnees[i][1]))
    try:                                            # fait comme si l n'était pas vide
        i_min = np.argmin(distances)
        # résultats  
        if types_objets[i_min] == 'fleche':         # si c'est la flèche on renvoie tel quel
            parcours.append((coords_fleche, cap_fleche))
            return parcours, ('fleche', coords_fleche, sigma_pos_fleche, cap_fleche, sigma_cap)
        else:                                       # sinon on ajoute un faux cap et une fausse incertitude
            parcours.append((liste_donnees[i_min][1], 0))
            return parcours, (types_objets[i_min], liste_donnees[i_min][1], liste_donnees[i_min][2], 0, 0)
    except Exception, e:                            # exception attrapée si la liste l est vide
        return parcours, ('none', (0,0), 0, 0, 0)             # si aucun objet n'avait été confirmé (aucun qui soit neuf et validé)
    
    
    
    
