# -*- coding: cp1252 -*-
from transitions import Machine


direction_de_la_fleche = 0

class Drone(object):

    states = ['au sol','stationnaire','avance','largue la bombe','erreur']

    

    
    def __init__(self, donnees, coor_premier_point):

        # donnees contiendra ce dont on aura besoin
        # altitude, coordonnées ?

        self.donnees = donnees

        self.loadedCoordinates = coor_premier_point

        self.prochaineDirection = 0

        self.dernierPointConnu = 0

        self.distanceMax = 0

        self.machine = Machine(model=self, states=Drone.states, initial='au sol')

        self.machine.add_transition('envol', 'au sol', 'stationnaire', before='decolle', after='va_au_point(self.loadedCoord)')

        self.machine.add_transition('erreurFrom_au_sol', 'au sol', 'erreur', after='shutdown')

        self.machine.add_transition('atterrissage', 'stationnaire','au sol', before='atteris')

        self.machine.add_transition('lecture_flecheFrom_stationnaire', 'stationnaire', 'avance', before='maj _direction')

        self.machine.add_transition('erreurFrom_stationnaire', 'stationnaire', 'erreur', after='shutdown')

        self.machine.add_transition('lecture_flecheFrom_avance', 'avance', 'avance', before='maj_direction')

        self.machine.add_transition('perdu', 'avance', 'stationnaire', condition=['trop_loin'], after='va_au_dernier _point')

        self.machine.add_transition('lecture_croixFrom_avance', 'avance', 'largue la bombe', after='larguage')

        self.machine.add_transition('lecture_atterrissageFrom_avance', 'avance', 'au sol', before='atteris')

        self.machine.add_transition('erreurFrom_avance', 'avance', 'erreur', after='shutdown')

        self.machine.add_transition('larguee', 'largue la bombe', 'avance', condition=['bombe_larguee'])

        self.machine.add_transition('erreurFrom_largue_la_bombe', 'largue la bombe', 'erreur', after='shutdown')

    def va_au_point(self, coor) :
        print "Je vais aux coordonnées !"

    def shutdown(self)  :
        print "SHUTDOWN !!! Stay cover !"
        

    def decolle(self)   :
        print "Larguez les amarres !"

    def maj_direction(self) :
        print "Va là bas"
        self.direction = direction_de_la_fleche # mettre la direction de le fleche
        self.dernierPointConnu = 0 # remplacer 0 par la location actuelle

    def va_au_dernier_point(self)   :
        print "Je retourne là où je connais"
        self.va_au_point(self.dernierPointConnu)
        

    def trop_loin(self) :
        distance = 0 # remplacer 0 par la distance entre la location actuelle et la dernière connue
        return distance > self.distanceMax

    def bombe_larguee(self) :
        return True # remplacer true par une vérification que la bombe est larguée 
    


print "pouet"
        
