# command.py
import numpy as np
from constants import ROBOT_SPEED, K_GAIN

class ElectricBehavior:
    """Implémente les 4 comportements bio-inspirés décrits dans le papier de recherche
    
    Les comportements sont basés sur le tracking des lignes de champ électrique :
    B1: Attiré par tous les objets (K = k/I_ax, k > 0)
    B2: Repoussé par tous les objets (K = k/I_ax, k < 0)
    B3: Attiré par conducteurs, repoussé par isolants (K = k/|I_ax|, k > 0)
    B4: Attiré par isolants, repoussé par conducteurs (K = k/|I_ax|, k < 0)
    """
    
    def __init__(self, behavior_type=1, k_gain=K_GAIN, forward_speed=ROBOT_SPEED):
        """Initialise le comportement électrique
        
        Args:
            behavior_type: Type de comportement (1, 2, 3 ou 4)
            k_gain: Gain pour le calcul de la vitesse angulaire
            forward_speed: Vitesse linéaire constante du robot
        """
        self.behavior_type = behavior_type
        self.k_gain = k_gain
        self.forward_speed = forward_speed
        
        # Descriptions des comportements pour l'affichage
        self.behavior_names = {
            1: "Attiré par tous les objets",
            2: "Repoussé par tous les objets",
            3: "Attiré par conducteurs, repoussé par isolants",
            4: "Attiré par isolants, repoussé par conducteurs"
        }
    
    def compute_command(self, I_ax, I_lat):
        """Calcule la commande (v, ω) selon le comportement choisi
        
        Implémente la loi de commande V = C et Ω = K * I_lat
        où K varie selon le comportement:
        - B1: K = k/I_ax (k > 0)
        - B2: K = k/I_ax (k < 0)
        - B3: K = k/|I_ax| (k > 0)
        - B4: K = k/|I_ax| (k < 0)
        
        Args:
            I_ax: Courant axial mesuré
            I_lat: Courant latéral mesuré
            
        Returns:
            Tuple (v, ω) avec v la vitesse linéaire et ω la vitesse angulaire
        """
        # Vitesse linéaire constante
        v = self.forward_speed
        epsilon = 1e-10  # Valeur minimale pour eviter division par 0
        
        # Calcul de K selon le comportement
        if self.behavior_type == 1:
            # B1: Attiré par tous les objets
            K = self.k_gain / (I_ax + epsilon) if abs(I_ax) > epsilon else 0
            
        elif self.behavior_type == 2:
            # B2: Repoussé par tous les objets
            K = -self.k_gain / (I_ax + epsilon) if abs(I_ax) > epsilon else 0
            
        elif self.behavior_type == 3:
            # B3: Attiré par conducteurs, repoussé par isolants
            K = self.k_gain / abs(I_ax) if abs(I_ax) > epsilon else 0
            
        elif self.behavior_type == 4:
            # B4: Attiré par isolants, repoussé par conducteurs
            K = -self.k_gain / abs(I_ax) if abs(I_ax) > epsilon else 0
            
        else:
            raise ValueError(f"Comportement {self.behavior_type} non implémenté")
        
        # Calcul de la vitesse angulaire (selon l'équation Ω = K * I_lat)
        w = K * I_lat
        
        # Limitation de la vitesse angulaire pour éviter les mouvements trop brusques
        #w = np.clip(w, -np.pi, np.pi)
        
        return v, w
    
    def get_name(self):
        """Retourne le nom du comportement actuel"""
        return self.behavior_names.get(self.behavior_type, "Comportement inconnu")
