# -*- coding: utf-8 -*-
"""
Created on Wed Aug 05 18:05:46 2015

@author: Jean-Christophe
"""

                ####################################################
                #                                                  #
                #              Bibliothèque des action             #
                #                                                  #
                ####################################################

"""

Ce script est une bibliothèque de fonctions servant à executer les action sur le drone

Sommaire des fonctions :

  - droneArme
      -> Indique si le drone est armé ou pas
      
  - fonction1
      -> arme le drone puis le désarme, rend le contrôle au pilote (mode stabilize).

  - fonction2
      -> arme le drone, décolle à la verticale, attend N secondes (loiter) et atterrit.
      
  - fonction3
      -> arme le drone, décolle à la verticale, va vers un point GPS et atterrit.

  - bombe
      -> largue la bombe
  
  - Croix_detectee
      -> stabilise le drone au dessus de la croix, largue la bombe et attend 10s
      
  - Fleche_detectee
      -> guide le drone vers le point suivant


"""

# import sys    Apparemment pas important
import os
import clr
import time
import sys

sys.path.append(os.getcwd())

import MissionPlanner
# import *
clr.AddReference("MissionPlanner.Utilities")                     # includes the Utilities class
#import BibliLocalisation                                         # importe la bibliothèque de localisation



#import Script                                                    # A retirer, juste pour éviter les erreurs
#import MAV                                                       # A retirer, juste pour éviter les erreurs
#import cs                                                        # A retirer, juste pour éviter les erreurs

def print_cwd():
    print(os.getcwd())

def droneArme():
    """
    Indique si le drone est armé
    """
    if (cs.armed == True): 
        return "drone armé"                                       # Indique si le drone est armé
    else:
        return "drone desarmé"                                    # Indique si le drone est désarmé



def fonction1():
    """
    Arme le drone puis le désarme, rend le contrôle au pilote (mode stabilize).
    """
    print "début du script"
    time.sleep(3)                                               # On attend 10s
    MAV.doARM("true")                                            # on arme les moteurs
    time.sleep(1)
    droneArme()                                                  # On indique l'état du drone
    time.sleep(5)
    
    MAV.doARM("false")                                           # On désarme les moteurs
    time.sleep(5)
    droneArme()                                                  # On indique l'état du drone
    time.sleep(5)
    
    Script.ChangeMode("stabilize")
    time.sleep(10)
    print "script terminé"

"""
Ici il semblerait qu'on puisse utiliser également "Script.WaitFor('ARMING MOTORS',30000)" je ne sais pas bien quelle est la différence...
"""    
    
    
def fonction2(n, inputAlt):
    """
    Arme le drone, décolle à la verticale, attend N secondes (loiter) et atterrit.
    """
    time.sleep(10)                                             # wait 10 seconds before starting
    print 'Starting Mission'
    Script.ChangeMode("Guided")                                # changes mode to "Guided"
    print 'Guided Mode'

    item = MissionPlanner.Utilities.Locationwp()               # creating waypoint
    lat = cs.lat                                               # Latitude value
    lng = cs.lng                                               # Longitude value
    alt = inputAlt                                             # altitude value
    MissionPlanner.Utilities.Locationwp.lat.SetValue(item,lat) # sets latitude
    MissionPlanner.Utilities.Locationwp.lng.SetValue(item,lng) # sets longitude
    MissionPlanner.Utilities.Locationwp.alt.SetValue(item,alt) # sets altitude
    


    #Décollage
    MAV.doARM("true")                                          # on arme les moteurs
    
    droneArme()                                                # Indique si le drone est armé 
    
    MAV.setGuidedModeWP(item)                                  # tells UAV "go to" the set lat/long @ alt
    
    
    #Pause
    
    time.sleep(10)
    print 'Mission Complete'
    
    #MAV.setMode(RETURN_TO_LAUNCH)
    Script.ChangeMode("RTL")                                   # Return to Launch point
    print 'Returning to Launch'
    
    #Atterrissage
    
    time.sleep(10)
    Script.ChangeMode("LOITER")                                # switch to "LOITER" mode
    print 'LOITERING'
    time.sleep(10)
    
    #Desarmement des moteurs
    MAV.doARM("false")                                         # On désarme les moteurs
    time.sleep(5)
    droneArme()                                                # Indique si le drone est désarmé
    time.sleep(5)
    
    Script.ChangeMode("stabilize")                             # On rend lescommandes
    time.sleep(10)
    
    
def fonction3(lat, lng, alt):
    """
    Arme le drone, décolle à la verticale, va vers un point GPS et atterrit.
    """
    time.sleep(10)                                             # wait 10 seconds before starting
    print 'Starting Mission'
    Script.ChangeMode("Guided")                                # changes mode to "Guided"
    print 'Guided Mode'

    item = MissionPlanner.Utilities.Locationwp()               # creating waypoint
    MissionPlanner.Utilities.Locationwp.lat.SetValue(item,lat) # sets latitude
    MissionPlanner.Utilities.Locationwp.lng.SetValue(item,lng) # sets longitude
    MissionPlanner.Utilities.Locationwp.alt.SetValue(item,alt) # sets altitude
    

    #Décollage
    MAV.doARM("true")                                          # on arme les moteurs
    
    droneArme()                                                # Indique si le drone est armé 
    
    MAV.setGuidedModeWP(item)                                  # tells UAV "go to" the set lat/long @ alt
#    Script.WaitFor( ??? )                                     # On attend d'être arrivé sur le point
    
    #Pause
    
    time.sleep(10)
    print 'Mission Complete'
       
    #Atterrissage
    
    time.sleep(10)
    Script.ChangeMode("LOITER")                                # switch to "LOITER" mode
    print 'LOITERING'
    time.sleep(10)
    
    #Desarmement des moteurs
    MAV.doARM("false")                                         # On désarme les moteurs
    time.sleep(5)
    droneArme()                                                # Indique si le drone est armé
    time.sleep(5)
    
    Script.ChangeMode("stabilize")                             # On rend lescommandes
    time.sleep(10)
    




def bombe(n):
    """
    Largue la bombe n (1 ou 2).
    """
#    Script.SendRC(voir ce quil faut faire)                     # larguer les bombs
    

def Croix_detectee(coords_croix, n):
    """
    Stabilise le drône au dessus de la croix, descend de x mètre, largue la bombe n, et repart 15m plus loin dans la même direction.
    """
    time.sleep(1)                                                # wait 1 seconds before starting
    print 'Croix détectée'
    Script.ChangeMode("Guided")                                  # changes mode to "Guided"
    print 'Guided Mode'
    item = MissionPlanner.Utilities.Locationwp()                 # creating waypoint
    alt = cs.lat                                                 # altitude value
    (lat, lng) = coords_croix                                    # latitude and longitude value
    MissionPlanner.Utilities.Locationwp.lat.SetValue(item,lat)   # sets latitude
    MissionPlanner.Utilities.Locationwp.lng.SetValue(item,lng)   # sets longitude
    MissionPlanner.Utilities.Locationwp.alt.SetValue(item,alt)   # sets altitude
    print 'WP set'
    MAV.setGuidedModeWP(item)                                    # tells UAV "go to" the set lat/long @ alt
    print 'Going to WP'
    print 'Ready for bombing'                                    # StandBy
    bombe(n)                                                     # Launch bomb number n (n equal 1 or 2)
    print 'bombs away'                                           # Bombs away
   
   
    print 'set new WP'                                           # Go to next WP
    item2 = MissionPlanner.Utilities.Locationwp()                # creating waypoint
    cap_drone = cs.groundcourse                                  # cap du drone
    (lat2, lng2) = BibliLocalisation.coordsNextWaypoint(coords_croix, cap_drone, cap_drone)        # Calculating new latitude and longitude
    alt2 = cs.alt                                                # set Altitude
    MissionPlanner.Utilities.Locationwp.lat.SetValue(item2,lat2) # sets latitude
    MissionPlanner.Utilities.Locationwp.lng.SetValue(item2,lng2) # sets longitude
    MissionPlanner.Utilities.Locationwp.alt.SetValue(item2,alt2) # sets altitude
    print 'WP2 set'
    MAV.setGuidedModeWP(item2)                                   # tells UAV "go to" the set lat/long @ alt
    print 'Going to WP2'
    
    
    
def Fleche_detectee(coords_fleche, angle_fleche):
    """
    Crée un nouveau waypoint 15m plus loin que la flèche, dans la direction de la flèche et guide le drône vers celui ci.
    """   
    print 'set new WP'                                          # Go to next WP
    item = MissionPlanner.Utilities.Locationwp()                # creating waypoint
    cap_drone =  cs.groundcourse                                # cap du drone
    (lat, lng) = BibliLocalisation.coordsNextWaypoint(coords_fleche, angle_fleche, cap_drone) # Calculating new latitude and longitude                                               # Keep same altitude
    alt = cs.alt                                                # set Altitude
    MissionPlanner.Utilities.Locationwp.lat.SetValue(item,lat)  # sets latitude
    MissionPlanner.Utilities.Locationwp.lng.SetValue(item,lng)  # sets longitude
    MissionPlanner.Utilities.Locationwp.alt.SetValue(item,alt)  # sets altitude
    print 'WP set'
    MAV.setGuidedModeWP(item)                                   # tells UAV "go to" the set lat/long @ alt
    print 'Going to WP'
    
    
    
    