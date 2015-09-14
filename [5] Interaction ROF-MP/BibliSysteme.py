# -*- coding: utf-8 -*-
"""
Created on Sat Sep 12 23:14:12 2015

@author: Charles

Bibliothèque d'interaction entre le script père (exécuté dans Mission Planner)
et le/les script(s) fils (ROF par exemple)

"""

import os
from os import system
import subprocess as sub
import sys


sep = ' '

# sans l'espace, qui est le séparateur
def coords_to_str(coords_tuple):
  
  str_coords = '(' + str(coords_tuple[0]) + ',' + str(coords_tuple[1]) + ')'
  return str_coords
  
def str_to_coords(str_coords):
  
  # enlève les parenthèses en début et fin des coords
  str_coords = str_coords.strip('(')
  str_coords = str_coords.strip(')')
  # sépare les deux coordonnées
  coords_str_tab = str_coords.split(',')
  # convertit en tuple
  coords = (float(coords_str_tab[0]), float(coords_str_tab[1]))
  
  return coords


def wrap_args_rof(coords_drone, alt_drone, cap_drone):
  
  str_coords = coords_to_str(coords_drone)
  str_alt = str(alt_drone)
  str_cap = str(cap_drone)
  
  str_args = str_coords + sep + str_alt + sep + str_cap
  return str_args
  

def unwrap_args_rof(str_args):
  
  args = str_args.split(sep)
  
  # coordonnées
  str_coords = args[0]
  coords = str_to_coords(str_coords)
  # altitude
  str_alt = args[1]
  alt = float(str_alt)
  # cap
  str_cap = args[2]
  cap = float(str_cap)
  
  return coords, alt, cap


# wrap_output_rof
def wrap_output_rof(type_objet, coords_objet, incertitude_coords_objet, cap_objet, incertitude_cap_objet):
  
  # transforme les arguments en chaines de caractères
  str_coords = coords_to_str(coords_objet)
  str_i_coords = str(incertitude_coords_objet)
  str_cap = str(cap_objet)
  str_i_cap = str(incertitude_cap_objet)
  
  # concatène le tout (avec le séparateur)
  str_output = type_objet + sep + str_coords + sep + str_i_coords + sep + str_cap + sep + str_i_cap
  
  return str_output


# unwrap_output_rof
def unwrap_output_rof(rof_out):
  
  out = rof_out.split(sep)
  
  type_objet = out[0]  
  coords_objet = str_to_coords(out[1])
  incertitude_coords = float(out[2])
  cap_obj = float(out[3])
  incertitude_cap = float(out[4])  

  return type_objet, coords_objet, incertitude_coords, cap_obj, incertitude_cap















