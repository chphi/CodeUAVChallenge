# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 23:41:24 2015

@author: Jean-Christophe
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

Script.ChangeMode('Stabilize')

armeDrone(True)                                                                # armement du drone
time.sleep(2)
droneArme()

time.sleep(2)
print 'decollage'

Script.ChangeMode("Guided")                                                    # changes mode to "Guided"

# Décollage -------------------------------------------------------------------

takeOff(2)                                                                     # decollage
time.sleep(5)

# Waypoints -------------------------------------------------------------------
print 'Going to first WayPoint'
set_new_wp(48.7075515, 2.1599641, 5)                                           # premier WayPoint 
time.sleep(10)


print 'Going to next WayPoint'
set_new_wp(48.7077622, 2.1603101, 5)                                           # Second WayPoint
time.sleep(10)

# Atterrissage ----------------------------------------------------------------
print 'atterrissage'                                                           # atterrissage
land()


time.sleep(3)
print 'fin de la Mission'


print "fin"
