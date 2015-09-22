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
       
       
    def detecteRectangle(self, frame, n_blur, kernel, aire_min, aire_max, seuil_aire, n_zone, v_moy, epsi_ratio):
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
        
        # 1ère passe : filtrage des contours pertinents (aire, solidité, ratio de longueurs)
        cnt_pertinents = track.trouveObjetsProbables(opening, aire_min, aire_max, self.sMin, 1, self.rMin, self.rMax)
        
        # 2ème passe : fittage de rectangle (si on le fait après l'approx tout ressemble à un rectangle)        
        rect_probables = []
        for cnt in cnt_pertinents:
           # fitte un rectangle
            rect = cv2.minAreaRect(cnt)
            # calcule l'aire du rectangle fitté
            aire_rect = rect[1][0] * rect[1][1]
            # calcule l'aire du contour trouvé
            M = cv2.moments(cnt)
            aire_cnt = M['m00'] 
            if aire_cnt/aire_rect > seuil_aire:
               rect_probables.append(cnt)
#               cv2.drawContours(frame, [cnt], -1, (255, 0, 0), 1)        
      
        # 3ème passe : on approxime les contours restants et on ne garde que ceux à 4 coins
        for cnt in rect_probables:
          epsilon = epsi_ratio*cv2.arcLength(cnt,True)
          approx = cv2.approxPolyDP(cnt,epsilon,True)
          if len(approx) == 4:   
                M = cv2.moments(approx)
                cv2.drawContours(frame, [approx], -1, (255,255,255), 2)
                cx, cy = int(M['m10']/M['m00']) , int(M['m01']/M['m00'])
                cv2.circle(frame, (cx,cy), 1, (255,255,255), 3)
                self.position.append((cx, cy))
                self.aire.append(M['m00'])
                self.estDetecte = True
            
            
