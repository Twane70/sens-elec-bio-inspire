# electric_sense.py
import numpy as np
from constants import *

class Sphere:
    """Représente une sphère dans la scène
    
    Attributes:
        position (np.array): Position [x,y,z] en m
        radius (float): Rayon en m
        chi (float): Contraste électrique χ = (γsphere - γeau)/(2γeau + γsphere)
                     χ > 0 conducteur, χ < 0 isolant
    """
    def __init__(self, position, radius, chi):
        self.position = np.array(position)
        self.radius = radius
        self.chi = chi

def compute_K_sphere(sphere, sensor_position, sensor_orientation):
    """Calcule la matrice K (5x5) pour une sphère selon l'équation:
    Kαβ = 1/(4πγ) * (rα.P.rβ)/(||rα||³||rβ||³)
    
    où:
    - P = χa³I est le tenseur de polarisation (I matrice identité 3x3)
    - rα est le vecteur position_electrode_α - position_sphere
    - rβ est le vecteur position_electrode_β - position_sphere
    """
    # Matrice K à calculer
    K = np.zeros((5,5))
    
    # Calcul tenseur de polarisation
    P = sphere.chi * sphere.radius**3 * np.eye(3)
    
    # Matrice de rotation du robot
    R = np.array([[np.cos(sensor_orientation), -np.sin(sensor_orientation), 0],
                  [np.sin(sensor_orientation), np.cos(sensor_orientation), 0],
                  [0, 0, 1]])
    
    # Pour chaque paire d'électrodes
    for alpha in range(5):
        # Position électrode alpha dans repère global
        pos_alpha = sensor_position + R @ np.array([X_ELECTRODES[alpha],
                                                  Y_ELECTRODES[alpha], 
                                                  Z_ELECTRODES[alpha]])
        # Vecteur rα
        r_alpha = pos_alpha - sphere.position
        
        for beta in range(5):
            # Position électrode beta dans repère global
            pos_beta = sensor_position + R @ np.array([X_ELECTRODES[beta],
                                                     Y_ELECTRODES[beta],
                                                     Z_ELECTRODES[beta]])
            # Vecteur rβ  
            r_beta = pos_beta - sphere.position
            
            # Calcul élément K_αβ
            K[alpha,beta] = 1/(4*np.pi*GAMMA) * \
                          (r_alpha @ P @ r_beta)/(np.linalg.norm(r_alpha)**3 * 
                                                np.linalg.norm(r_beta)**3)
    
    return K

def compute_electric_sense(spheres, sensor_position, sensor_orientation):
    """Calcule I_ax, I_lat et I_vert selon la méthodologie:
    1. Somme des matrices K de toutes les sphères
    2. Calcul courants perturbés δI = -C0KtotalC0U
    3. Extraction composantes axiale/latérale/verticale
    
    Indices des électrodes:
    0: queue (-0.2, 0, 0)
    1: gauche (0.2, 0.06, 0) 
    2: haut (0.2, 0, 0.06)
    3: droite (0.2, -0.06, 0)
    4: bas (0.2, 0, -0.06)
    """
    # 1. Somme des K
    K_total = np.zeros((5,5))
    for sphere in spheres:
        K_total += compute_K_sphere(sphere, sensor_position, sensor_orientation)
        
    # 2. Calcul courants perturbés
    delta_I = -C0 @ K_total @ C0 @ U
    
    # 3. Extraction composantes
    I_ax = (delta_I[1] + delta_I[2] + delta_I[3] + delta_I[4])/4  # moyenne des 4 électrodes avant
    I_lat = delta_I[1] - delta_I[3]  # gauche - droite 
    I_vert = delta_I[2] - delta_I[4]  # haut - bas
    
    return I_ax, I_lat, I_vert



