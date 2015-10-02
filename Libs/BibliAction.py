# -*- coding: utf-8 -*-
"""
Created on Wed Aug 05 18:05:46 2015

@author: Jean-Christophe
"""

                ####################################################
                #                                                  #
                #              Bibliothèque des actions            #
                #                                                  #
                ####################################################

"""

Ce script est une bibliothèque de fonctions servant à executer les action sur le drone

Sommaire des fonctions :

  - droneArme
      -> Indique si le drone est armé ou pas

  - armeDrone
      -> Arme le drone

  - warmUp
      -> Arme le drone et essaie pendant timeOut secondes    
          
  - bombe
      -> Largue la bombe
        
  - set_new_wp
      -> Défini un new Waypoint et supprime les autres

  - takeOff
      -> Le drone décolle

  - land
      -> Le drone atterrit
      
  - fonction1
      -> Arme le drone puis le désarme, rend le contrôle au pilote (mode stabilize).

  - fonction2
      -> Arme le drone, décolle à la verticale, attend N secondes (loiter) et atterrit.
      
  - fonction3
      -> Arme le drone, décolle à la verticale, va vers un point GPS et atterrit.

"""

import os
import clr
import time
import sys
clr.AddReference("MAVLink")
import MAVLink

sys.path.append(os.getcwd())

import MissionPlanner
clr.AddReference("MissionPlanner.Utilities")                                   # includes the Utilities class



def droneArme():
    """
    Indique si le drone est armé
    """
    if (cs.armed == True): 
        print "drone armé"                                                     # Indique si le drone est armé
        return True
    else:
        print "drone desarmé"                                                  # Indique si le drone est désarmé
        return False


def armeDrone(bool):
    Script.ChangeMode("stabilize")
    if bool == True:
        MAV.doARM("true")
    else:
        MAV.doARM("false")


def warmUp(warmup_time):
    """
    Tente d'armer le drone pendant max_warmup_time secondes
    """
    t0 = time.time()
    time.sleep(1)
    print 'début de la procédure d\'armement des moteurs'
    time.sleep(1)
    
    while time.time() - t0 < warmup_time:
        MAV.doARM("true")
        time.sleep(2)
        if droneArme():
            return True
    
    print "Error : Drone non armé"
    return False
        


def bombe(n):
    """
    Largue la bombe n (1 ou 2).
    """
    if (n == '1'):
        MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, 11 ,2000, 0, 0, 0, 0, 0)   # On libère la bombe 1
        time.sleep(3)
        MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, 11 ,1500, 0, 0, 0, 0, 0)   # On revient au centre
        print 'Bomb1 away'
    if (n == '2'):
        MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, 11 ,1000, 0, 0, 0, 0, 0)   # On libère la bombe 2
        time.sleep(3)
        MAV.doCommand(MAVLink.MAV_CMD.DO_SET_SERVO, 11 ,1500, 0, 0, 0, 0, 0)   # On revient au centre
        print 'Bomb2 away'


def set_new_wp(lat, lng, alt):
    """
    Définit un nouveau WayPoint et s'y rend
    """
    
    item = MissionPlanner.Utilities.Locationwp()                               # Création du waypoint

    MissionPlanner.Utilities.Locationwp.lat.SetValue(item,lat)                 # Sets latitude
    MissionPlanner.Utilities.Locationwp.lng.SetValue(item,lng)                 # Sets longitude
    MissionPlanner.Utilities.Locationwp.alt.SetValue(item,alt)                 # Sets altitude
    print 'WP set'
    MAV.setGuidedModeWP(item)                                                  # On se rend au waypoint
    print 'Going to WP'

 
def takeOff(alt):
    """
    Le drone décolle à la vertical et se met à l'altitude demandée
    """
    Script.ChangeMode("Guided")                                                # On passe en mode "Guided"

    MAV.doCommand(MAVLink.MAV_CMD.TAKEOFF, 0, 0, 0, 0, 0, 0, alt)              # Decolle à l'altitude voulue    


   
def land():
    """
    Atterrit à l'endroit demandé
    """
    lat = cs.lat
    lng = cs.lng    
    
    MAV.doCommand(MAVLink.MAV_CMD.LAND, 0, 0, 0, 0, lat, lng, 0)               # On atterrit
  
  
def do_return_to_launch():
    Script.ChangeMode('RTL') 
  
  
def fonction1():
    """
    Arme le drone puis le désarme, rend le contrôle au pilote (mode stabilize).
    """
    # Armement des moteurs ----------------------------------------------------    
    print "début du script"

    time.sleep(1)                                                              # On attend 10s
    armeDrone(True)                                                            # On arme les moteurs
    time.sleep(3)
    droneArme()                                                                # On indique l'état du drone
    time.sleep(5)
    
    # Desarmements des moteurs ------------------------------------------------
    armeDrone(False)                                                           # On désarme les moteurs
    time.sleep(12)
    droneArme()                                                                # On indique l'état du drone
    time.sleep(1)
    
    Script.ChangeMode("stabilize")                                             # On rend la main au pilote
    time.sleep(10)
    print "script terminé"  

  
def fonction2(n, inputAlt):
    """
    Arme le drone, décolle à la verticale, attend N secondes (loiter) et atterrit.
    """
    time.sleep(1)                                                              
    print 'Starting Mission'

    # Décollage ---------------------------------------------------------------
    armeDrone()                                                                # On arme les moteurs
    time.sleep(2)
    droneArme()                                                                # Indique si le drone est armé 
    Script.Sleep(3)
    
    decollage(inpuAlt)
    
    # Attente -----------------------------------------------------------------
    time.sleep(n*1000)
    
    print 'Mission Complete'
    
    # Atterrissage ------------------------------------------------------------
    Script.ChangeMode("RTL")                                                   # Return to Launch point
    print 'Returning to Launch'
    time.sleep(2)
    print 'Fin de la Mission'
    
    
def fonction3(lat, lng, alt):
    """
    Arme le drone, décolle à la verticale, va vers un point GPS et atterrit.
    """
    time.sleep(10)                                                             
    print 'Starting Mission'


    #Décollage ----------------------------------------------------------------
    armeDrone()                                                                # On arme les moteurs
    time.sleep(3)
    droneArme()                                                                # Indique si le drone est armé 
    #Nouveau Waypoint ---------------------------------------------------------
    set_new_wp(lat, lng, alt)                                                  # Nouveau WayPoint
    time.sleep(1)
       
    #Atterrissage -------------------------------------------------------------
    if (cs.wp_dist < 1):
        Script.ChangeMode("LAND")                                              # On passe au mode "LAND"
        print 'LAND'
    


    
    
    
    
    