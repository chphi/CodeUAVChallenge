# -*- coding: utf-8 -*-
"""
Created on Sun Sep 13 17:01:25 2015

@author: Charles
"""

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
import BibliSysteme as bibsys


# Variables -------------------------------------------------------------------

root = 'D:/Charles/Documents/Sumo/Dassault UAV Challenge/Code/CodeUAVChallenge'
script_dir = '[5] Interaction ROF-MP'


# Initialisation --------------------------------------------------------------

path = root + '/' + script_dir
print(path + "\n")

system('cd ' + path) # modidie le répertoire de travail de cmd.exe
os.chdir(path) # modifie le répertoire de travail de MP

# infos sur le drone
coords_drone = (48.7077, 2.1602)
alt_drone = 10                           # altitude du drone en mètres
cap_drone = 0                            # cap du drone (en degrés)
orientation_cam = (0,0)                  # caméra à plat, devant = haut de l'image.

# Exécution sous-script -------------------------------------------------------

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
    type_objet, coords, incertitude_coords, cap, incertitude_cap = bibsys.unwrap_output_rof(data)    
    
    # affiche les données lues et le temps écoulé
    if(type_objet != 'none'):
        print("output ROF : " + data)
        print("temps écoulé : " + str(time.time() - t0))
    
    # stop au bout de 5 secondes
    if (time.time() - t0 > 30):
        break


# Fin du script ---------------------------------------------------------------

# kill le sous-script
# attention le script n'a peut-être pas fini la boucle, il vaut mieux lui 
# envoyer un  signal lui disant de quitter : il peut alors fermer le flux vidéo
p.kill()

print('\nscript principal exécuté')
