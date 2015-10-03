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
import BibliNav as nav
execfile(cf.libpath + '/' + 'BibliAction.py')


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
    self.coords = coords_drone    # (lat, lng)
    # altitude courante du drone
    self.alti = alt_drone
    # altitude demandée
    self.alt_consigne = 0    
    # coordonnées de la zone de décollage ou de la dernière flèche vue
    self.last_known_location = initial_coords
    # destination en cours (coords cibles initiales ou point dans l'alignement de la dernière flèche vue)
    self.destination = initial_coords
    # slot de largage actif
    self.active_bomb = 1
    
    # initialise la machine à états
    self.machine = Machine(model=self, states=Drone.states, initial='standby', ignore_invalid_triggers=cf.ignore_invalid_triggers)

    # add transition :           trigger               source                          dest
    self.machine.add_transition('erreur'            , '*'                           , 'erreur'       , after='shutdown')
    self.machine.add_transition('take_off_order'    , 'standby'                     , 'avance'       , after='decolle')
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
    self.go_to(self.coords, target_alti)
    sys.stdout.flush()


  def follow_arrow(self, arrow_coords, arrow_heading) :
    print( 'j\'enregistre la position de la flèche vue' )
    self.destination = arrow_coords
    print( 'je vais à l\'emplacement de la flèche:' )
    self.go_to(self.destination, cf.nav_alt)
    time_start = time.time()
    while (cs.wp_dist > cf.wp_radius):
        time.sleep(0.01)
        if time_start - time.time() > 5:
            break
    print('j\'y suis, j\'enregistre cette position comme étant la dernière connue')
    self.last_known_location = arrow_coords
    print( 'je calcule ma prochaine destination...' )
    self.destination = nav.coordsNextWaypoint(arrow_coords, arrow_heading)
    print( 'je me dirige vers cette destination :' )
    self.go_to(self.destination, self.alt_consigne)
    sys.stdout.flush()

  def drop_load(self, cross_coords):
    print( 'je vais au dessus de la croix : ' + str(cross_coords) )
    self.go_to(cross_coords, cf.dropping_alt)
    # attend qu'on se soit approché suffisamment du point GPS
    while (cs.wp_dist > cf.wp_radius):
        time.sleep(0.01)
        if time_start - time.time() > 5:
            break
    print('je largue la charge')
    sys.stdout.flush()
    bomb(self.active_bomb)
    # attend le largage de la charge
    time.sleep(cf.dropping_time)
    print('charge larguée')
    sys.stdout.flush()
    self.active_bomb = 2 # on passe sur la bombe 2
    # remonte quand la charge est larguée
    self.set_altitude(cf.takeoff_alt)
    # repart vers la précédente destination  
    self.load_down()

  def back_to_dest(self):
    # reprend la route vers la dernière destination
    print('je reprends la route vers ma dernière destination')
    self.go_to(self.destination, cf.nav_alt)
    sys.stdout.flush()

  def shutdown(self):
    # arrête les moteurs puis les désarme
    print "shutdown! (NOT IMPLEMENTED, RTL IN REPLACEMENT)"
    sys.stdout.flush()
    do_return_to_launch()
  
  def decolle(self):
    # monte à la verticale
    self.set_altitude(cf.takeoff_alt)
    
    # finit la montée en avançant vers les 1ères coordonnées
    print('je me dirige maintenant vers les 1ères coordonnées cibles :')
    self.go_to(self.destination, cf.nav_alt)
    sys.stdout.flush()

  def go_to(self, coords_cible, alt_cible) :
    # va aux coordonnées et à l'altitude indiquées, en ligne droite
    print( "go_to( " + str(coords_cible) + ", " + str(alt_cible) + " )" )
    lat = coords_cible[0]
    lng = coords_cible[1]
    set_new_wp(lat, lng, alt_cible)
    # mémorise l'altitude d'arrivée demandée comme nouvelle altitude consigne
    self.set_alt_consigne(alt_cible)
    sys.stdout.flush()

  def recover(self) :
    # retourne au dernier point connu (flèche)
    print('je retourne au dernier point connu : ' + str(self.last_known_location))
    self.go_to(self.last_known_location, cf.nav_alt)
    # éventuellement : revérifier direction de la flèche (pour ça il faut l'enlever du parcours...)
    print('j\'y suis, maintenant je repars avec une altitude supérieure')
    self.set_altitude(self.alt_consigne + 5)
    self.go_to(self.destination, self.alt_consigne)
    sys.stdout.flush()

  def land(self, landing_coords):
    # va à la zone d'atterrissage et atterrit à la verticale  
    print('je vais aux coords d\'atterrissage : ' + str(landing_coords) )
    # éventuellement: commence déjà à descendre :
    self.go_to(landing_coords, cf.landing_alt)
    while (cs.wp_dist > cf.wp_radius):
        time.sleep(0.01)
        if time_start - time.time() > 5:
            break
    print('j\'y suis, j\'atterris à la verticale')
    sys.stdout.flush()
    land()
  
  def return_to_launch(self):
    print('je retourne à la zone de décollage')
    sys.stdout.flush()
    do_return_to_launch()   
    
  def update_status(self, coords_drone, cap_drone, alt_drone, rof_data):
#     effectue la transition appropriée à la situation, en fonction des données à disposition.
    type_objet, coords, incertitude_coords, cap, incertitude_cap = rof_data
    if ( type_objet == 'none'):
      d = nav.distance(coords_drone, self.last_known_location)
      if ( d > cf.dist_max ):
        self.is_lost()
    if ( type_objet == 'fleche'):
      self.arrow_detected(coords, cap)
    if ( type_objet == 'croix' ):
      self.cross_detected(coords)
    if ( type_objet == 'rectangle' ):      
      self.landing_detected(coords)
     




