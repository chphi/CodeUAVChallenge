# -*- coding: utf-8 -*-
"""
Created on Wed Apr 08 10:30:18 2015

@author: Charles
"""

import cv2
import numpy as np
import BibliTracking as track

class Fleche:
    
    def __init__(self, patron, teinte, s_max, r_min, r_max, angle, position, taille, est_detectee):
        self.teinte = teinte
        self.patron = patron
        self.sMax = s_max
        self.rMin = r_min
        self.rMax = r_max
        self.angle = angle
        self.position = position
        self.taille = taille
        self.estDetectee = est_detectee
       
       
    def detecteFleche(self, frame, marge_h, n_blur, kernel, aire_min, aire_max, patrons, pas_angle, seuil_certitude, s_min, v_min, n_gauss):
        """
        détecte toutes les flèches d'une image aux caractéristiques précisées dans le constructeur de classe.
        
        Si plusieurs flèches repérées, met les attributs de l'objet flèche sous forme de liste (liste des positions, 
        des tailles, des angles)
        """
        
        t, S, rm, rM = self.teinte, self.sMax, self.rMin, self.rMax
        fleche_detectee = False     
        self.angle = []
        self.position = []
        self.taille = []
        self.estDetectee = False
        
        frame_trackee = track.trackeTeinte(frame, t, marge_h, n_blur, kernel, s_min, v_min)
        fleches_probables = track.trouveObjetsProbables(frame_trackee.copy(), aire_min, aire_max, 0, S, rm, rM)
        
        for cnt in fleches_probables:
            
            _, (w,l), angle_probable = cv2.fitEllipse(cnt)        # orientation probable (à 180° près)
            taille_approx = max(w,l)                              # taille probable
            zone_a_tester, centre_zone = track.determineZoneATester(frame_trackee, cnt)
    
            if np.int0(min(np.shape(zone_a_tester))) > 1:         # vérifie que la zone est bien en 2D (si bord de l'image : ligne)
                
                zat_normalisee = cv2.resize(zone_a_tester, (50, 50))  # met la zone à la taille du patron
                indices_patrons_a_tester = track.determineIndicesPatronsATester(angle_probable, pas_angle) # détermine les orientations du patron à tester
                fleche_detectee, angle_objet = track.matchePatrons(zat_normalisee, indices_patrons_a_tester, patrons, seuil_certitude, n_gauss)            
                
                if fleche_detectee:
                    cv2.drawContours(frame, [cnt], -1, (0,0,255), 2)
                    cv2.circle(frame,centre_zone, 3, (0,0,255), -1)
                    self.angle.append(angle_objet)
                    self.position.append(centre_zone)
                    self.taille.append(taille_approx)
                    self.estDetectee = True











