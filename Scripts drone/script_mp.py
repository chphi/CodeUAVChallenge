# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 21:51:26 2015

@author: Charles

Script à exécuter dans Mission Planner

Mettre le sous-script "script_test.py" dans le même dossier que celui-ci et 
changer les variables "root" et "script_dir" pour que ça corresponde. Attention
les accents ne sont pas bien gérés dans les adresses.
"""

import os
from os import system
import subprocess as sub
import sys
import time
import clr
import sys
clr.AddReference("MAVLink")
import MAVLink
import MissionPlanner
clr.AddReference("MissionPlanner.Utilities")                                   # includes the Utilities class

print('début du script d\'exécution de mission')

# Variables -------------------------------------------------------------------

# emplacement du code (pour donner le path à Mission Planner et en faire le répertoire de travail)
root = 'D:/Charles/Documents/Sumo/Dassault UAV Challenge/Code/CodeUAVChallenge'
script_dir = 'Scripts drone'

# emplacement du fichier de configuration
conf_path = 'D:/Charles/Documents/Sumo/Dassault UAV Challenge/Code/CodeUAVChallenge'

# variable de debug
drone_status = 'disarmed'

# variables de mission
mission_running = False


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
import BibliSysteme as bibsys
#import BibliNav as nav
execfile(cf.libpath + '/' + 'Drone.py')
execfile(cf.libpath + '/' + 'BibliAction.py')

# infos sur le drone
coords_drone = (48.7077, 2.1602)
alt_drone = 10                           # altitude du drone en mètres
cap_drone = 0                            # cap du drone (en degrés)
orientation_cam = (0,0)                  # caméra à plat, devant = haut de l'image.


# Fonctions --------------------------------------------------------------------

def quit_subprocess(p, drone_status):
  if drone_status == 'disarmed':
    p.kill()
    return 1
  else:
    print('impossible de quitter : drone pas désarmé')
    return 0

#def drone_startup():
#  # attend que le drone soit prêt et arme les moteurs
#  print('startup : attend que le drone doit prêt et arme les moteurs...')
#  sys.stdout.flush()
#  time.sleep(5)
#  print('moteurs armés')
#  drone_status = 'armed'
#  print('drone_status : ' + str(drone_status))
#  print('set_mode(guided)')
#  print('prêt à commencer la mission')
#  sys.stdout.flush()
#  return 1
  

# Démarre le drone -------------------------------------------------------------

#à la fin de la fonction, le drone est prêt à décoller
print('lance la procédure d\'armement des moteurs')
sys.stdout.flush()
#warmUp(30)


# Lance la ROF -----------------------------------------------------------------

# lance le sous-processus et connecte ses entrées et sorties au présent script
p = sub.Popen('python script_rof.py', stdin = sub.PIPE, stdout=sub.PIPE)
print('reconnaissance d\'images lancée')

t0 = time.time()


# Initialise l'automate --------------------------------------------------------

drone = Drone((coords_drone, cap_drone, alt_drone), cf.initial_target)


# Boucle principale ------------------------------------------------------------
while(True):

  # TODO : actualiser coords, altitude et cap drone

  # envoie des arguments à p
  args_rof = bibsys.wrap_args_rof(coords_drone, alt_drone, cap_drone)
  p.stdin.write(args_rof + "\n")   
  p.stdin.flush()
  
  # lit la sortie du script de reconnaissance de formes
  data_str = p.stdout.readline().strip()
  sys.stdout.flush()
  type_objet = 'none'

  # teste s'il y a eu une action de l'utilisateur
  if data_str == 'start':
#    print('\n')
    print('ordre utilisateur : <start>')
    mission_running = True
    print('je démarre la mission')
    t0 = time.time()
    drone.take_off_order()
    
  elif data_str == 'abort':
    # lancer la procédure de "return to launch"
#    print('\n')    
    print('ordre utilisateur : <abort>')
    print('j\'arrête la mission')
    mission_running = False  # avec ça ne prend plus en compte les formes au sol
    drone.return_to_launch()
    
  elif data_str == 'manuel':
#    print('\n')
    print('ordre utilisateur : <manuel>')
    print('je me mets en loiter et j\'arrête la mission')
    mission_running = False
    print('vous avez les commandes')
    
  elif data_str == 'emergency':
    # extinction sans délai des moteurs
#    print('\n')
    print('ordre utilisateur : <emergency>')
    drone.shutdown()
    print('drone au sol, fin du programme')
    break
  
  # touche "q" pour quitter, quand la mission est terminée
  elif data_str == 'quit':
#    print('\n')
    print('ordre utilisateur : <quit>')
    drone_status = 'disarmed' # pour les tests en simu on force le désarmement des moteurs
    ret = quit_subprocess(p, drone_status) # quitte le programme (si le drone est désarmé)
    if ret:
      print("fin du programme principal")
      break
  
  
  # si pas d'action utilisateur :
  else:
    # les données reçues sont alors bien celles de la reconnaissance d'images
    rof_data = bibsys.unwrap_output_rof(data_str)
    # si on est à une altitude suffisante et en mission, on analyse le résultat de la ROF
    if( alt_drone > cf.min_rof_alt and mission_running ):
      # affiche quand on a vu un objet
      if ( rof_data[0] != 'none' ):
        print('\n')
        print(data_str)
        sys.stdout.flush()
#      print(str(time.time() - t0))
      # envoie les infos à l'automate, déclenche la transition appropriée
      drone.update_status(coords_drone, cap_drone, alt_drone, rof_data)

  # stoppe si la mission s'éternise
  if (time.time() - t0 > cf.max_time):
    print('time out, je retourne à la zone de décollage')
    break


# Fin du script ---------------------------------------------------------------

# kill le sous-script
# attention le script n'a peut-être pas fini la boucle, il vaut mieux lui 
# envoyer un  signal lui disant de quitter : il peut alors fermer le flux vidéo
p.kill()

print('\nscript principal exécuté')
