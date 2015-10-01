# -*- coding: utf-8 -*-
"""
Created on Wed Apr 08 10:47:01 2015

@author: Charles

Bibliothèque de fonctions servant à la détection d'objets basée sur le tracking de couleurs,
des tests sur les contours des objets, et des tests de corrélation avec un "patron" (forme à détecter)

Sommaire des fonctions :

  - initVideoFlow
      -> lance l'acquisition vidéo sur la webcam ou la caméra du drone  
  
  - getImage
      -> récupère une image avec la même divergence de cas
      
  - endVideoFlow
      -> termine l'acquisition vidéo et ferme la/les fenêtres
      
  - trackeTeinte
      -> sélectionne une teinte de l'image
      
  - caracteristiques 
      -> donne les caractéristiques d'un contour spécifié
      
  - aireNonNulle 
      -> teste l'objet associé à un contour a une aire nulle (embêtant pour les calculs)
      
  - estPertinent 
      -> teste si un contour répond à des critères géométriques simples
      
  - trouveContoursPertinents 
      -> utilise les trois fonctions précédentes pour déterminer une liste de tous les contours pertinents dans une liste
         de contours donnée
      
  - trouveObjetsProbables
      -> même fonctionnalité mais à partir d'une image "trackée" (issue de la fonction tracke-teinte)
  
  - determineZoneATester
      -> détermine la zone (carrée) de l'image contenant le contour en argument.
  
  - creePatrons
      -> à partir d'un patron (de flèche par ex.) d'une orientation fixée, crée un tableau avec des patrons orientés selon les
         360°, par pas de N degrés (à donner en argument). Sert à tester si une zone contenant un contour (cf fonction précedente)
         contient la forme du patron
  
  - determineIndicesPatronsATester
      -> détermine une orientation probable de l'objet dans la zone et sélectionne les quelques patrons issus de la fonction
         précédente qui sont proches de cette orientation (pour ne pas devoir tester toutes les orientations)
  
  - matchePatrons
      -> Trouve le patron le mieux corrélé à l'objet dans la zone à tester, et le valide si la corrélation dépasse un seuil.
  
"""

import sys
import cv2
import numpy as np
from VideoCapture import Device

# Définition des variables ----------------------------------------------------

conf_path = 'D:/Charles/Documents/Sumo/Dassault UAV Challenge/Code/CodeUAVChallenge'
    
# Initialisation du programme -------------------------------------------------

# importe la configuration
sys.path.append(conf_path)
import conf_drone as cf

# Fonctions -------------------------------------------------------------------

def initVideoFlow(is_cam_embarquee):
    """
    initialise le flux vidéo selon si on veut utiliser la webcam ou la caméra du drone
    """
    cv2.namedWindow('frame')
        
    if is_cam_embarquee:
        print('caméra embarquée')
        try:
           cap = Device(devnum=cf.emb_cam_num, showVideoWindow=0)
        except Exception, e:
           print e
           cv2.destroyAllWindows()
    else:
        print('caméra interne')
        try:  
           cap = Device(devnum=cf.webcam_num, showVideoWindow=0)
        except Exception, e:
           print e
           cv2.destroyAllWindows()
    sys.stdout.flush()
    return cap
    

def getImage(is_cam_embarquee, cap):
    """
    Fait l'acquisition d'une image en différenciant le cas où on veut utiliser une cam embarquée ou la webcam du pc
    Rend une image au format BGR d'opencv
    """
#    if is_cam_embarquee:
    im = cap.getImage()
    arr = np.array(im)    
    frame = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
#    else:
#        _, frame = cap.read()
        
    return frame
    

def endVideoFlow(is_cam_embarquee, cap):
    """
    Arrête le flux vidéo et ferme la fenêtre d'affichage
    """
#    if not is_cam_embarquee:
#        cap.release()
#    else:
#        del cap
    del cap
    cv2.destroyAllWindows()
    

def trackeTeinte(frame, h_cible, marge_h, n_blur, kernel, s_min, v_min):
    """
    Extrait une couleur d'une image.
    Rend l'image trackée en double (une sera utilisée pour calculer les contours, opération qui se fait en place)
    
    image, teinte_cible, marge_teinte, taille_filtre_gaussien, noyau_opening -> image_trackee
    """
    frame_track = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)                    # convertit l'image de BGR à HSV 
    if (h_cible - marge_h) > 0 and (h_cible + marge_h < 180):                # si "pas de problème"
        lower_color = np.array([h_cible-marge_h, s_min, v_min])             # définit les couleurs limites à tracker
        upper_color = np.array([h_cible+marge_h, 255, 255])
        frame_track = cv2.inRange(frame_track, lower_color, upper_color)    # sélectionne les pixels dans l'intervalle de couleur 
    else:
        if h_cible < marge_h:                                    # si on est proche de 0, faire la congruence à 180 manuellement
            lower_color_1 = np.array([0, s_min, v_min])
            upper_color_1 = np.array([h_cible + marge_h, 255, 255])
            lower_color_2 = np.array([180 - abs(marge_h-h_cible), s_min, v_min])
            upper_color_2 = np.array([180, 255, 255])    
        else:
            lower_color_1 = np.array([0, s_min, v_min])          # idem si proche de 180
            upper_color_1 = np.array([marge_h - abs(180-h_cible), 255, 255])
            lower_color_2 = np.array([h_cible, s_min, v_min])
            upper_color_2 = np.array([180, 255, 255])     
        frame_track_1 = cv2.inRange(frame_track, lower_color_1, upper_color_1)
        frame_track_2 = cv2.inRange(frame_track, lower_color_2, upper_color_2)
        frame_track = cv2.add(frame_track_1, frame_track_2) 
    # test : filtre médian à la place du gaussien
    frame_track = cv2.medianBlur(frame_track, n_blur, 0)
#    frame_track = cv2.GaussianBlur(frame_track,(n_blur,n_blur),0)       # floute l'image (filtre gaussien)
    opening = cv2.morphologyEx(frame_track, cv2.MORPH_OPEN, kernel)     # fait une "ouverture" (réduit le bruit) 
    
    return opening
    
    
    
def caracteristiques(cnt):
    """
    Fonction calculant les caractéristiques d'un contour :
    - coordonnées du barycentre
    - longueur selon la plus grande dimension
    - orientation du contour
    - aire
    - solidité
    - rapport dimension min/dimension max
    
    contour -> centre_x, centre_y, L, orientation, aire, solidité, rapport
    """ 
    M = cv2.moments(cnt)
    area = M['m00']                                             # calcul de l'aire
    hull = cv2.convexHull(cnt)                                  # enveloppe convexe
    hull_area = cv2.contourArea(hull)                           # aire de l'enveloppe convexe
    solidity = float(area)/max(hull_area, 0.01)                 # calcul de la solidité (100 si contour d'aire nulle)
    box = cv2.minAreaRect(cnt)                                  # fitte un rectangle orienté
    L = max(box[1])                                             # calcule la plus grane longueur
    angle = box[2]                                              # calcule l'angle du rectangle
    aspect_ratio = min(box[1])/max(box[1])                      # ratio petite dimension/grande dimension    
    cx, cy = int(M['m10']/M['m00']) , int(M['m01']/M['m00'])    # barycentre du contour
    
    return cx, cy, L, angle, area, solidity, aspect_ratio
  
  

def aireNonNulle(cnt):
    """
    Vérifie qu'un contour a une aire non nulle. On vérifie que le contour fait plus de 5 points (sinon fitEllipse ne marche pas)
    Rend "True" si l'aire n'est pas nulle, "False" sinon
    
    contour -> bool
    """
    M = cv2.moments(cnt)
   
    return M['m00'] > 0 and len(cnt) > 5                        # on vérifie aussi qu'il y a plus de 5 points (sinon fitEllipse bug)
    
    

def estPertinent(caracs_contour, aire_min, aire_max, s_min, s_max, r_min, r_max):
   """
   détermine si un contour est pertinent ou non en fonction de certaines caractéristiques géométriques. Rend un booléen.
   "caracs" est déterminé à l'aide de la fonction "caracteristiques"
   
   caracs, aire_min, aire_max, solidité_max, ratio_min, ratio_max -> bool
   """
   cx, cy, L, angle, area, s, r = caracs_contour
   
   return (aire_min < area < aire_max)  and (s_min < s < s_max) and (r_min < r < r_max)     
   
   
def trouveContoursPertinents(contours, aire_min, aire_max, s_min, s_max, r_min, r_max):
    """
    Trouve les contours pertinents dans un jeu de contours d'après nos critères. Rend une liste de contours
    
    contours, aire_min, aire_max, solidité_min, solidité_max, ratio_min, ratio_max -> contours_pertinents
    """
    cnt_pertinents = []
    for i in range(0,len(contours)):            # balaie la liste de contours
        cnt = contours[i]                       # extrait le contour à l'indice i        
        if aireNonNulle(cnt) :                  # si l'aire n'est pas nulle on peut continuer les tests
            caracs = caracteristiques(cnt)      # détermine les caractéristiques du contour           
            if estPertinent(caracs, aire_min, aire_max, s_min, s_max, r_min, r_max): 
                cnt_pertinents.append( cnt )    # ajoute le contour à la liste des contours pertinent
    
    return cnt_pertinents
    
    
def trouveObjetsProbables(opening, aire_min, aire_max, s_min, s_max, r_min, r_max):   
    """
    Trouve des contours pertinents dans une image trackée, selon nos critères.
    Rend une liste de contours, qui sont les contours rentrant dans nos critères de sélection
    
    image, Amin, Amax, t, s_min, s_max, r_min, r_max -> contours pertinents
    """
    _, contours, _ = cv2.findContours(opening, cv2.RETR_EXTERNAL ,cv2.CHAIN_APPROX_SIMPLE)
    objets_probables = trouveContoursPertinents(contours, aire_min, aire_max, s_min, s_max, r_min, r_max)
    
    return objets_probables


def determineZoneATester(frame_trackee, cnt):
    """
    Détermine la région d'intérêt de l'image contenant le contour spécifié. Sert à faire du template matching sur cette région.
    Rend la zone à tester (sous forme d'image) et son centre
    
    image, contour -> zone_à_tester, centre_zone
    """
    (x,y),radius = cv2.minEnclosingCircle(cnt)        # fitte un cercle autour du contour
    x,y = (int(x),int(y))                             # centre probable
    radius = int(radius)                              
    x,y,w,h = x-radius, y-radius, 2*radius, 2*radius  # extrait la ROI 
    zone_a_tester = frame_trackee[y:(y+h), x:(x+w)]   # indices : lignes puis colonnes 
    centre_zone = (x+radius,y+radius)                 # détermine le centre de la zone
    
    return zone_a_tester, centre_zone
  

def creePatrons(patron, pas_angle, n_gauss):
    """
    Crée l'ensemble des patrons orientés pour faire du template matching sur une région d'intérêt où il y a une forme candidate
    Rend un tableau des patrons orientés de 0 à 360 degrés selon le pas spécifié.
    On fait un filtrage gaussien pour flouter le contour et le rendre moins spécifique (sinon template matching intolérant)
    
    patron, pas_angle, n_gauss -> patrons_orientés
    """        
    patron = cv2.cvtColor(patron, cv2.COLOR_BGR2GRAY)       # 
    patron = cv2.blur(patron,(n_gauss,n_gauss))
    all_angles = np.arange(0,360, pas_angle)
    h, w = np.shape(patron)
    patrons = np.zeros((h,w, 360/pas_angle), 'uint8')    
    for angle in all_angles:
        pas_angle = all_angles[1]-all_angles[0]
        indice = angle/pas_angle
        M = cv2.getRotationMatrix2D((h/2,w/2),-angle,1)     # signe négatif : rotation dans le sens horaire (comme une boussole)
        patron_oriente = cv2.warpAffine(patron,M,(h,w))     # rotation du patron d'origine
        patrons[:,:,indice] = patron_oriente                # stockage à la case correspondante dans le tableau des patrons
    
    return patrons
  
  
def determineIndicesPatronsATester(angle_probable, pas_angle):
    """
    Détermine un intervalle d'angles dans lequel peut être un objet en fonction d'un angle probable estimé. Détermine ensuite
    les indices des patrons orientés correspondants pour essayer le template matching
    
    angle_probable, pas_angle -> indices
    """    
    if angle_probable == -1:                            # si on ne donne pas d'angle probable -> on teste tous les angles
        range_angles = np.arange(0,360, pas_angle)
        angles_a_tester = range_angles
    else:
        range_angles = np.arange(-25,25+1,pas_angle)    # définit les orientations relatives à tester (/ angle probable)
        angles_a_tester_1 = np.mod(angle_probable + range_angles, 360) # orientations, sens direct
        angles_a_tester_2 = np.mod(180 + angle_probable + range_angles, 360) # orientations, sens opposé (+180°)
        angles_a_tester = np.int0(np.concatenate((angles_a_tester_1, angles_a_tester_2))) # les deux ensemble    
    indices_patrons_a_tester = np.int0((1./pas_angle) * angles_a_tester) # calcul des indices
    
    return indices_patrons_a_tester
    
    
def matchePatrons(zone_a_tester, indices_patrons_a_tester, patrons, seuil_certitude, n_gauss):    
    """
    détermine si l'objet dans une zone d'intérêt est bien celui que l'on cherche (utilise le template matching)
    Rend un booléen (vrai si objet détecté) et l'angle du patron qui a matché.
    
    Le template matching rend un coefficient de corrélation entre -1 et 1.
    
    zone_a_tester, indices_patrons, tableau_patrons_orientés, seuil_certitude -> bool, angle    
    """    
    coeff_max = 0                         # initialise le coeff max de corrélation    
    zone_a_tester = cv2.blur(zone_a_tester, (n_gauss, n_gauss))
    for i in indices_patrons_a_tester:    # balaie les patrons à tester
       coeff = cv2.matchTemplate(zone_a_tester,patrons[:,:,i],cv2.TM_CCOEFF_NORMED) # calcul le corr_coeff par template matching
       if coeff[0][0] > coeff_max:        # récupère le coeff max et son indice
           coeff_max = coeff[0][0]
           indice_max = i    
    if coeff_max > seuil_certitude:       # si on est suffisamment sûr on considère qu'on a détecté l'objet recherché
        objet_detecte = True
        angle_reel = 5*indice_max         # orientation du patron qui a matché
    else:
        objet_detecte = False
        angle_reel = 0
    
    return objet_detecte, angle_reel
    
    
    
    
    
