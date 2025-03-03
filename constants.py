# constants.py
import numpy as np

# Paramètres du capteur électrique
# Position des électrodes [m] (5 électrodes)
X_ELECTRODES = np.array([-0.2, 0.2, 0.2, 0.2, 0.2])  
Y_ELECTRODES = np.array([0, 0.06, 0, -0.06, 0])
Z_ELECTRODES = np.array([0, 0, 0.06, 0, -0.06])

# Conductivité eau [S/m]
GAMMA = 0.04

# Matrice de conductance de base (mesurée)
C0 = GAMMA * np.array([
    [0.2557, -0.0639, -0.0639, -0.0639, -0.0639],
    [-0.0639, 0.1218, -0.0203, -0.0173, -0.0203],
    [-0.0639, -0.0203, 0.1218, -0.0203, -0.0173],
    [-0.0639, -0.0173, -0.0203, 0.1218, -0.0203],
    [-0.0639, -0.0203, -0.0173, -0.0203, 0.1218]
])

# Tensions imposées [V]
U = np.array([1, 0, 0, 0, 0])  # Electrode 0 émettrice, autres réceptrices

# Paramètres du robot
ROBOT_LENGTH = 0.5  # Longueur [m]
ROBOT_WIDTH = 0.1   # Largeur [m]
ROBOT_HEIGHT = 0.2  # Hauteur [m]
ROBOT_MASS = 9.0    # Masse [kg]
ROBOT_SPEED = 0.1   # Vitesse constante [m/s]

# Paramètres de la scène
POOL_SIZE = 3.0     # Taille de l'aquarium carré [m]

# Paramètres de simulation
DT = 0.1           # Pas de temps [s]
SIMULATION_TIME = 60.0  # Durée simulation [s]

# Paramètre de commande
K_GAIN = 0.5  # Gain pour le calcul de la vitesse angulaire
