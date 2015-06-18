# -*- coding: utf-8 -*-
"""
Created on Mon Jun 08 22:29:59 2015

@author: Charles


Programme testant la consolidation des infos de la ROF : confirmation de détection, 


TODO : calculer les incertitudes (si caméra inclinée par exemple). prendre en 
compte l'intensité des vibrations qui font bouger le centre de l'objet (en pixels)

"""

# TODO : vérifier ce qu'il se passe dans le cas où on ne voit pas de flèche (listes vides)

import BibliLocalisation as loc
import Fleche



# Variables --------------------------------------------------------------------------------------------------

  # Variables réglables

seuil_sigma_pos = 2                     # seuil d'écart type en dessous duquel on considère avoir bien vu la position de l'objet
seuil_sigma_cap = 5                     # idem pour les angles (cas d'une flèche)
taille_memoire = 3                      # nb d'infos gardées en mémoire (initialiser les listes associées au bon nb d'élts)

  # Variables d'entrée

coords_drone = (48.7077, 2.1602)
alt_drone = 10                          # altitude du drone en mètres
cap_drone = 0                           # cap du drone (en degrés)
orientation_cam = (0,0)                 # caméra à plat, devant = haut de l'image.
# rappel : l'image fait 480x640px (lignes puis colonnes)
position_fleche = (240, 320)            # position fictive d'un objet sur une image filmée à partir du drone (pour test)
angle_fleche = 0                        # angle de la flèche fictive à l'écran par rapport à la verticale de l'image, en degrés
fleche = Fleche.Fleche([], 0, 0.8, .35, .65, [], [], [], False)
# Détection d'une flèche fictive sur l'image
fleche.angle = [angle_fleche]           # angle de la flèche à l'image / des flèches (d'où le format de liste, cf classe Fleche)
fleche.position = [position_fleche]     # position sur image, peut être (liste si plusieurs flèches à l'image)
fleche.estDetectee = True
# parcours déjà suivi
coords_decollage = (48.7076, 2.1603)
cap_decollage = 0
coords_1ere_fleche = (48.7077, 2.1603)
cap_1ere_fleche = 170.5
parcours = [ (coords_decollage, cap_decollage), (coords_1ere_fleche, cap_1ere_fleche) ]

  # Création fausse alerte

position_fausse_alerte = (400, 600)
position_relative_fa = loc.posPixToPosRelativeDrone(position_fausse_alerte, orientation_cam, alt_drone)
coords_gps_fa = loc.coordsGPSobjet(coords_drone, cap_drone, alt_drone, position_fausse_alerte, orientation_cam)
angle_fausse_alerte = 35

  # Création des localisations vues à l'instant précédent

e = 0.00001   # erreur de localisation gps des précédentes flèches (erreur d'un ordre de grandeur acceptable)
liste_coords = [ [(48.7077 + e, 2.1602)], [(48.7077, 2.1602 + e), coords_gps_fa], [(48.7077 - e, 2.1602)] ]
liste_caps = [ [-4], [-3, angle_fausse_alerte], [3] ]  # CAPS de la flèche sur les 3 dernières images



# Utilisation sur un exemple : détection d'une flèche ------------------------------------------------------

  # Consolidation des infos en analysant une série de 3 images, moyennage et calcul des incertitudes

fleche_validee, coords_fleche, sigma_pos, cap_fleche, sigma_cap = loc.analyseReconnaissanceFleche(fleche, liste_coords, liste_caps, seuil_sigma_pos, seuil_sigma_cap, coords_drone, cap_drone, alt_drone, orientation_cam)

# mémorise l'objet dans la liste des formes repérées (décrit le parcours déjà suivi)
parcours.append( (coords_fleche, cap_fleche) )



  # Calcul position prochaine flèche et incertitude

# A faire ailleurs car utilise les infos transmises. Peut être fait dans le script de l'automate ou dans les fonctions
# de commande du drone

if fleche_validee:
    coords_next_WP = loc.coordsNextWaypoint(coords_fleche, cap_fleche, 0)
    sigma_next_WP = 15 * loc.sinus(sigma_cap) + sigma_pos
    












