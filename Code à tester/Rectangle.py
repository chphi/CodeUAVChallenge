# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 16:32:38 2015

@author: Charles
"""

import cv2
import BibliTracking as track

class Rectangle:
    
    def __init__(self, s_min, r_min, r_max, position, aire, est_detecte):
        self.sMin = s_min
        self.rMin = r_min
        self.rMax = r_max
        self.position = position
        self.aire = aire
        self.estDetecte = est_detecte
       
       
    def detecteRectangle(self, frame, n_blur, kernel, aire_min, aire_max, seuil_certitude, seuil_aire, n_zone, v_moy):
        """
        détecte tous les rectangles d'une image aux caractéristiques précisées dans le constructeur de classe.
        
        Si plusieurs rectangle repérés, met les attributs de l'objet rectangle sous forme de liste (liste des positions, 
        des aires)
        """                
        self.position = []
        self.aire = []
        self.estDetecte = False
        
        # Tracking du noir
        frame2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        th = cv2.adaptiveThreshold(frame2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, n_zone,v_moy)
        opening = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)
        
        # Calcul des contours
        _, contours, hierarchy = cv2.findContours(opening.copy(), cv2.RETR_EXTERNAL ,cv2.CHAIN_APPROX_SIMPLE)
        
        # filtrage des contours pertinents
        rect_probables = track.trouveObjetsProbables(opening, aire_min, aire_max, self.sMin, 1, self.rMin, self.rMax)
        
        for cnt in rect_probables:
            # fitte un rectangle
            rect = cv2.minAreaRect(cnt)
            # calcule l'aire du rectangle fitté
            aire_rect = rect[1][0] * rect[1][1]
            # calcule l'aire du contour trouvé
            M = cv2.moments(cnt)
            aire_cnt = M['m00'] 
            
            if aire_cnt/aire_rect > seuil_aire:    
            
                cv2.drawContours(frame, [cnt], -1, (255,255,255), 1)
                cx, cy = int(M['m10']/M['m00']) , int(M['m01']/M['m00'])
                cv2.circle(frame, (cx,cy), 1, (255,255,255), 3)
                
                self.position.append((cx, cy))
                self.aire.append(M['m00'])
                self.estDetecte = True
            
            