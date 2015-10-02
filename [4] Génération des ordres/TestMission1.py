# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 14:00:58 2015

@author: Jean-Christophe
"""

"""
Le but de cette mission est de mettre en place un circuit réalisé en autonomie par le drone, ou il devra faire un
petit tour, larguer deux bombes et atterir
"""


import os
from os import system
import sys
import clr
import time
import MissionPlanner #import *
clr.AddReference("MissionPlanner.Utilities") #includes the Utilities class
clr.AddReference("MAVLink")
import MAVLink

# Variables -------------------------------------------------------------------

# emplacement du code (pour donner le path à Mission Planner et en faire le répertoire de travail)
root = 'E:/Documents/Documents/Supelec/Drone/Developpement du drone/Software/CodeUAVChallenge'
script_dir = '[5] Interaction ROF-MP'

# emplacement du fichier de configuration
conf_path = root

# variable de debug
drone_status = 'disarmed'
lat1 = 48.7077622
lng1 = 2.1603329
lat2 = 48.7078179
lng2 = 2.1604027
alt = 3


# Initialisation --------------------------------------------------------------

# importe la configuration
sys.path.append(conf_path)
import conf_drone as cf

# change le path
path = root + '/' + script_dir
system('cd ' + path) # modidie le répertoire de travail de cmd.exe
os.chdir(path) # modifie le répertoire de travail de MP

# importe les biblis persos
sys.path.append(cf.libpath)
execfile(cf.libpath+'/'+'BibliAction.py')
#execfile(cf.libpath+'/'+'BibliAction.py')

# Début du script -------------------------------------------------------------

print 'Debut de la mission'

Script.ChangeMode("Stabilize")

droneArme()                                                                    # Indique l'état du drone
time.sleep(2)

armeDrone(True)                                                                # On arme le drone
time.sleep(4)
droneArme()                                                                    # On indique l'état du drone


# Décollage du drone ----------------------------------------------------------

print 'Décollage'


takeOff(3)                                                                     # On décolle verticalement à 3 mètres
time.sleep(5)


# Waypoints -------------------------------------------------------------------
print 'Création WayPoint 1'
set_new_wp(lat1, lng1, alt)                                                    # On ordonne au drone de se rendre au WayPoint
time.sleep(5)
print 'larguage Bombe 1'
bombe('1')                                                                     # On largue la Bombe 1
time.sleep(2)

print 'Création WayPoint 2'
set_new_wp(lat2, lng2, alt)                                                    # On ordonne au drone de se rendre au WayPoint
time.sleep(5)
print 'larguage Bombe 2'
bombe('2')                                                                     # On largue la bombe 2


# fin de la Mission -----------------------------------------------------------
print 'Retour à la maison'
Script.ChangeMode('RTL')                                                       # On rentre à la maison

time.sleep(10)
print 'Fin de la mission'
