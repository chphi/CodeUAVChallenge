# -*- coding: utf-8 -*-


from transitions import Machine


direction_de_la_fleche = 0

class Drone(object):

    states = ['etatInitial','etatFinal','larguageDeBombe','avance','perdu','erreur']

    ######
    # 
    #   les états de states (à  part l'état 'erreur'), sont respectivement
    #   les états D, A, C, F, E du schéma automate de la présentation chez Dassault
    #

    # TODO : créer une structure pour les données
    
    def __init__(self, donnees, coor_premier_point):

        # donnees contiendra ce dont on aura besoin
        # altitude, coordonnées ?

        self.donnees = donnees

        self.loadedCoordinates = coor_premier_point

        self.prochaineDirection = 0

        self.dernierPointConnu = coor_premier_point

        self.distanceMax = 0

        self.machine = Machine(model=self, states=Drone.states, initial='etatInitial')

        self.machine.add_transition('erreurFrom_etatInitial', 'etatInitial', 'erreur', after='shutdown')
        
        self.machine.add_transition('erreurFrom_avance', 'avance', 'erreur', after='shutdown')
        
        self.machine.add_transition('erreurFrom_perdu', 'perdu', 'erreur', after='shutdown')
        
        self.machine.add_transition('erreurFrom_larguageDeBombe', 'larguageDeBombe', 'erreur', after='shutdown')
        
        self.machine.add_transition('erreurFrom_atterissage', 'atterissage', 'erreur', after='shutdown')

        self.machine.add_transition('lecture_atterissageFrom_avance', 'avance','etatFinal', before='atteris')
        
        self.machine.add_transition('lecture_atterissageFrom_larguageDeBombe', 'larguageDeBombe','etatFinal', before='atteris')

        self.machine.add_transition('lecture_flecheFrom_etatInitial', 'etatInitial', 'avance', before='maj _direction')
        
        self.machine.add_transition('lecture_flecheFrom_perdu', 'perdu', 'avance', before='maj _direction')

        self.machine.add_transition('lecture_flecheFrom_avance', 'avance', 'avance', before='maj_direction')

        self.machine.add_transition('deriveFrom_avance', 'avance', 'perdu', condition=['trop_loin'])
        
        self.machine.add_transition('deriveFrom_etatInitial', 'etatInitial', 'perdu', condition=['trop_loin'])

        self.machine.add_transition('lecture_croixFrom_avance', 'avance', 'larguageDeBombe', after='larguage')
        
        self.machine.add_transition('lecture_croixFrom_etatInitial', 'etatInitial', 'larguageDeBombe', after='larguage')

        self.machine.add_transition('larguee', 'larguageDeBombe', 'avance', condition=['bombe_larguee'])



    def va_au_point(self, coor) :
        print "Je vais aux coordonnÃ©es !"

    def shutdown(self)  :
        print "SHUTDOWN !!! Stay cover !"
        

    def decolle(self)   :
        print "Larguez les amarres !"

    def maj_direction(self) :
        print "Va lÃ  bas"
        self.direction = direction_de_la_fleche # mettre la direction de le fleche
        self.dernierPointConnu = 0 # remplacer 0 par la localisation actuelle

    def va_au_dernier_point(self)   :
        print "Je retourne lÃ  oÃ¹ je connais"
        self.va_au_point(self.dernierPointConnu)
        

    def trop_loin(self) :
        distance = 0 # remplacer 0 par la distance entre la localisation actuelle et la dernière connue
        return distance > self.distanceMax

    def bombe_larguee(self) :
        return True # remplacer true par une vÃ©rification que la bombe est larguÃ©e 
    


print "pouet"
        
