# -*- coding: cp1252 -*-
from transitions import Machine

class Drone(object):

    states = ['au sol','stationnaire','avance','largue la bombe','explore','erreur']

    
    def __init__(self, donnees):

        # donnees contiendra ce dont on aura besoin
        # altitude, coordonnées ?

        self.donnees = donnees

        self.prochaineDirection = 0

        self.machine = Machine(model=self, states=Drone.states, initial='au sol')

        self.machine.add_transition('envol', 'au sol', 'stationnaire', before='decolle')

        self.machine.add_transition('erreur1', 'au sol', 'erreur', after='shutdown')

        self.machine.add_transition('atterrissage', 'stationnaire','au sol', before='atteris')

        self.machine.add_transition('sans_but', 'stationnaire', 'explore')

        self.machine.add_transition('lecture_fleche1', 'stationnaire', 'avance', before='maj _direction')

        self.machine.add_transition('erreur2', 'stationnaire', 'erreur', after='shutdown')

        self.machine.add_transition('lecture_fleche2', 'avance', 'avance', before='maj_direction')

        self.machine.add_transition('perdu', 'avance', 'stationnaire', condition=['trop_loin'])

        self.machine.add_transition('lecture_croix1', 'avance', 'largue la bombe', after='larguage')

        self.machine.add_transition('lecture_atterrissage1', 'avance', 'au sol', before='atteris')

        self.machine.add_transition('erreur3', 'avance', 'erreur', after='shutdown')

        self.machine.add_transition('larguee', 'largue la bombe', 'avance', condition=['bombe_larguee'])

        self.machine.add_transition('erreur4', 'au sol', 'erreur', after='shutdown')

        self.machine.add_transition('lecture_croix2', 'explore', 'largue la bombe', after='larguage')

        self.machine.add_transition('lecture_fleche3', 'explore', 'avance', before='maj_direction')

        self.machine.add_transition('lecture_atterrissage2', 'explore', 'au sol', before='atteris')

        
