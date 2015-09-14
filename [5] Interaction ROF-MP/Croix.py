# -*- coding: utf-8 -*-
"""
Created on Wed Apr 08 10:30:18 2015

@author: Charles
"""

import cv2
import numpy as np
import BibliTracking as track

class Croix:
    
    def __init__(self, patron, teinte, s_max, r_min, r_max, position, taille, est_detecte):
       
        self.teinte = teinte
        self.patron = patron
        self.sMax = s_max
        self.rMin = r_min
        self.rMax = r_max
        self.position = position
        self.taille = taille
        self.estDetecte = est_detecte
       
       
       
    def detecteCroix(self, frame, marge_h, n_blur, kernel, aire_min, aire_max, patrons, pas_angle, seuil_certitude, s_min, v_min, n_gauss):
        """
        détecte toutes les croix d'une image aux caractéristiques précisées dans le constructeur de classe.
        
        Si plusieurs croix repérées met leurs attributs sous forme de liste (liste des positions, des tailles)
        """
    
        t, S, rm, rM = self.teinte, self.sMax, self.rMin, self.rMax
        croix_detecte = False     
        self.angle = -1
        self.position = []
        self.taille = []
        self.estDetecte = False
        
        frame_trackee = track.trackeTeinte(frame, t, marge_h, n_blur, kernel, s_min, v_min)
        croix_probables = track.trouveObjetsProbables(frame_trackee.copy(), aire_min, aire_max, 0, S, rm, rM)
        
        for cnt in croix_probables:
            
            (x,y),radius = cv2.minEnclosingCircle(cnt)            # position et rayon de la forme  
            x,y = (int(x),int(y))
            taille_approx = 2*int(radius)                             # taille probable
            zone_a_tester, _ = track.determineZoneATester(frame_trackee, cnt)
    
            if np.int0(min(np.shape(zone_a_tester))) > 1:   
                
                zat_normalisee = cv2.resize(zone_a_tester, (50, 50))
                indices_patrons_a_tester = track.determineIndicesPatronsATester(-1, pas_angle)
                croix_detecte, _ = track.matchePatrons(zat_normalisee, indices_patrons_a_tester, patrons, seuil_certitude, n_gauss)            
                
                if croix_detecte:
                    cv2.drawContours(frame, [cnt], -1, (0,255,255), 1)
                    cv2.circle(frame,(x,y), 3, (0,255,255), -1)
                    self.position.append((x,y))
                    self.taille.append(taille_approx)
                    self.estDetecte = True











