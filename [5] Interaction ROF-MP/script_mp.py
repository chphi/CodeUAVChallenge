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


# Variables -------------------------------------------------------------------

# emplacement du code (pour donner le path à Mission Planner et en faire le répertoire de travail)
root = 'D:/Charles/Documents/Sumo/Dassault UAV Challenge/Code/CodeUAVChallenge'
script_dir = '[5] Interaction ROF-MP'

# emplacement du fichier de configuration
conf_path = 'D:/Charles/Documents/Sumo/Dassault UAV Challenge/Code/CodeUAVChallenge'

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
import BibliSysteme as bibsys

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


# Exécution sous-script --------------------------------------------------------

# lance le sous-processus et connecte ses entrées et sorties au présent script
p = sub.Popen('python script_rof.py', stdin = sub.PIPE, stdout=sub.PIPE)
print('reconnaissance d\'images lancée')

t0 = time.time()

while(True):
    
  # envoie des arguments à p
  args_rof = bibsys.wrap_args_rof(coords_drone, alt_drone, cap_drone)
  p.stdin.write(args_rof + "\n")   
  p.stdin.flush()
  
  # lit la sortie du script de reconnaissance de formes
  data = p.stdout.readline().strip()
  sys.stdout.flush()
  type_objet = 'none'

  # teste s'il y a eu une action de l'utilisateur
  if data == 'start':
     print(data) # lancer la mission
  elif data == 'abort':
     print(data) # lancer la procédure de "return to launch", quand terminé : arrêter la vidéo, l'automate etc...
  elif data == 'emergency':
     print(data) # extinction des moteurs (override l'ordre "abort" s'il a été donné avant)
  elif data == 'quit':
     print('ordre utilisateur : <quit>')
     ret = quit_subprocess(p, drone_status) # quitte le programme (si le drone est désarmé)
     if ret:
       print("fin du programme principal")
       break
  
  #☺ si pas d'action utilisateur :     
  else:
    type_objet, coords, incertitude_coords, cap, incertitude_cap = bibsys.unwrap_output_rof(data)    
    # si objet détecté : affiche les données
    if(type_objet != 'none'):
      print(data)
    else:
      print(str(time.time() - t0))
    
  # stop au bout de N secondes
  if (time.time() - t0 > cf.max_time):
    break


# Fin du script ---------------------------------------------------------------

# kill le sous-script
# attention le script n'a peut-être pas fini la boucle, il vaut mieux lui 
# envoyer un  signal lui disant de quitter : il peut alors fermer le flux vidéo
p.kill()

print('\nscript principal exécuté')
