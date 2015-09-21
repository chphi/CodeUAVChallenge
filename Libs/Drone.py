# -*- coding: utf-8 -*-
"""
@author: Christian

Classe implémentant un automate à états pour le drone
"""

# TODO : quand on a vu un objet, on va dessus et on se remet à l'altitude optimale


import time
import sys
from transitions import Machine

# Variables --------------------------------------------------------------------

conf_path = 'D:/Charles/Documents/Sumo/Dassault UAV Challenge/Code/CodeUAVChallenge'


# Initialisation du programme --------------------------------------------------

# importe le fichier de configuration des scripts
sys.path.append(conf_path)
import conf_drone as cf

# importe les biblis persos
sys.path.append(cf.libpath)
import BibliLocalisation as loc


# Définition de la classe ------------------------------------------------------

class Drone(object):

# les états de states (à  part l'état 'erreur'), sont respectivement
# les états D, A, C, F, E du schéma automate de la présentation chez Dassault
  states = ['standby', 'landed', 'dropping_load', 'avance', 'perdu', 'erreur']
  
  
  def __init__(self, donnees, initial_coords):
    
    # analyse des données
    (coords_drone, cap_drone, alt_drone) = donnees
    
    # cap actuel du drone
    self.cap = cap_drone
    # coordonnées du drone
    self.coords = coords_drone
    # altitude courante du drone
    self.alti = alt_drone
    # altitude demandée
    self.alt_consigne = 0    
    # coordonnées de la zone de décollage ou de la dernière flèche vue
    self.last_known_location = initial_coords
    # destination en cours (coords cibles initiales ou point dans l'alignement de la dernière flèche vue)
    self.destination = initial_coords
    
    # initialise la machine à états
    self.machine = Machine(model=self, states=Drone.states, initial='standby', ignore_invalid_triggers=True)

    # add transition :           trigger               source                          dest
    self.machine.add_transition('erreur'            , '*'                           , 'erreur'       , after='shutdown')
    self.machine.add_transition('take_off_order'    , 'standby'                     , 'avance'       , before='decolle')
    self.machine.add_transition('landing_detected'  , ['avance', 'dropping_load']   , 'landed'       , before='land')
    self.machine.add_transition('landing_detected'  , 'perdu'                       , 'landed'       , before='land')
    self.machine.add_transition('arrow_detected'    , ['standby', 'perdu', 'avance'], 'avance'       , after='follow_arrow')
    self.machine.add_transition('is_lost'           , ['standby', 'avance']         , 'perdu'        , after='recover')    
    self.machine.add_transition('cross_detected'    , ['standby', 'avance']         , 'dropping_load', after='drop_load')
    self.machine.add_transition('load_down'         , 'dropping_load'               , 'avance'       , after='back_to_dest')


  # change l'altitude consigne en prenant en compte le max
  def set_alt_consigne(self, new_alt_consigne):
    self.alt_consigne = min(new_alt_consigne, cf.max_alt)


  # change l'altitude consigne et y emmène le drone
  def set_altitude(self, target_alti):
    self.set_alt_consigne(target_alti)
    print('je monte/descends verticalement à ' + str(self.alt_consigne) + 'm d\'altitude')


  def follow_arrow(self, arrow_coords, arrow_heading) :
    print( 'j\'enregistre la position de la flèche vue' )
    self.destination = arrow_coords
    print( 'je vais à l\'emplacement de la flèche:' )
    self.go_to(self.destination, cf.nav_alt)
    print('j\'y suis, j\'enregistre cette position comme étant la dernière connue')
    self.last_known_location = arrow_coords
    print( 'je calcule ma prochaine destination...' )
    self.destination = loc.coordsNextWaypoint(arrow_coords, arrow_heading)
    print( 'je me dirige vers cette destination :' )
    self.go_to(self.destination, self.alt_consigne)


  def drop_load(self, cross_coords):
    print( 'je vais au dessus de la croix : ' + str(cross_coords) )
    self.go_to(cross_coords, cf.dropping_alt)
    print('je largue la charge')
    # attend le largage de la charge
    time.sleep(cf.dropping_time)
    print('charge larguée, je reprends ma route')
    self.load_down()


  def back_to_dest(self):
    self.go_to(self.destination, cf.nav_alt)


  def shutdown(self):
    # atterrit sans délai, désarme les moteurs
    print "shutdown!"
        
  
  def decolle(self):
    # monte à la verticale
    self.set_altitude(cf.takeoff_alt)
    # monte en avançant vers les 1ères coordonnées
    print('je me dirige maintenant vers les 1ères coordonnées cibles :')
    self.go_to(self.destination, cf.nav_alt)


  def go_to(self, coords_cible, alt_cible) :
    # TODO : ne pas oublier de supprimer l'ancien WP cible avant d'en créer un autre
    # va aux coordonnées et à l'altitude indiquées en ligne droite
    print( "go_to( " + str(coords_cible) + ", " + str(alt_cible) + " )" )
    # mémorise l'altitude d'arrivée demandée comme nouvelle altitude consigne
    self.set_alt_consigne(alt_cible)
    

  def recover(self) :
    # retourne au dernier point connu
    print('je retourne au dernier point connu : ' + str(self.last_known_location))
    self.go_to(self.last_known_location, cf.nav_alt)
    # éventuellement : vérifier direction de la flèche (pour ça il faut l'enlever du parcours...)
    print('j\'y suis, maintenant je repars avec une altitude supérieure')
    self.set_altitude(self.alt_consigne + 5)
    self.go_to(self.destination, self.alt_consigne)


  def land(self, landing_coords):
    # va à la zone d'atterrissage et atterrit à la verticale  
    print('je vais aux coords d\'atterrissage : ' + str(landing_coords) )
    # éventuellement: commence déjà à descendre :
    self.go_to(landing_coords, cf.landing_alt)
    print('j\'y suis, j\'atterris à la verticale')
    
    
#   def update_status()
#     effectue la transition appropriée à la situation, en fonction des données à disposition.
        
#   def warm_up()
#     initialise le drone, arme les moteurs quand il est prêt, stocke les coordonnées de départ




