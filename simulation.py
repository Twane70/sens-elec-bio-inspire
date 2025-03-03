# simulation.py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
import os
from pathlib import Path
from constants import *
from electric_sense import Sphere, compute_electric_sense
from command import ElectricBehavior
from draw_robot import draw_robot, draw_sphere

def setup_plot(ax, xlim=(-2.5, 2.5), ylim=(-2.5, 2.5), add_legend=False):
    """Configure les paramètres de l'axe"""
    ax.grid(True)
    ax.set_aspect('equal')
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    if add_legend:
        ax.legend(loc='upper right')

def create_random_scene(num_spheres=4, min_radius=0.1, max_radius=0.2, arena_size=2.0):
    """Crée une scène avec des sphères positionnées aléatoirement"""
    spheres = []
    
    for _ in range(num_spheres):
        # Position aléatoire (évite le centre où le robot démarre)
        while True:
            x = np.random.uniform(-arena_size, arena_size)
            y = np.random.uniform(-arena_size, arena_size)
            
            # Évite de placer trop près du robot (qui démarre à l'origine)
            if x*x + y*y > 0.5*0.5:
                break
        
        # Taille aléatoire
        radius = np.random.uniform(min_radius, max_radius)
        
        # Choix aléatoire: conducteur (chi>0) ou isolant (chi<0)
        chi = np.random.choice([1.0, -0.5])
        
        # Création de la sphère
        spheres.append(Sphere([x, y, 0], radius, chi))
    
    return spheres

def check_collision(robot_pos, spheres, collision_margin=0.05):
    """Vérifie si le robot est en collision avec une sphère"""
    for sphere in spheres:
        # Distance entre le robot et le centre de la sphère
        distance = np.linalg.norm(robot_pos[:2] - sphere.position[:2])
        
        # Collision si distance < rayon + marge
        if distance < (sphere.radius + collision_margin):
            return True
    
    return False

def is_out_of_bounds(position, bounds=2.5):
    """Vérifie si le robot est sorti des limites de la scène"""
    return abs(position[0]) > bounds or abs(position[1]) > bounds

def simulate_behavior(behavior, spheres, simulation_time=SIMULATION_TIME, dt=DT):
    """Simule le déplacement du robot avec un comportement spécifique"""
    # Position et orientation initiales du robot
    x, y, theta = 0.0, 0.0, 0.0
    
    # Historique des positions et orientations
    history = {
        'x': [x],
        'y': [y],
        'theta': [theta],
        'time': [0],
        'collision': False,
        'out_of_bounds': False
    }
    
    # Simulation
    t = 0
    while t < simulation_time:
        # Vérification de collision
        if check_collision(np.array([x, y, 0]), spheres):
            history['collision'] = True
            print(f"Collision détectée à t={t:.2f}s")
            break
        
        # Vérification si hors limites
        if is_out_of_bounds([x, y]):
            history['out_of_bounds'] = True
            print(f"Robot hors limites à t={t:.2f}s")
            break
        
        # Calcul des courants électriques
        I_ax, I_lat, I_vert = compute_electric_sense(spheres, np.array([x, y, 0]), theta)
        
        # Calcul des commandes
        v, w = behavior.compute_command(I_ax, I_lat)
        
        # Mise à jour de la position et orientation (intégration simple)
        theta += w * dt
        x += v * np.cos(theta) * dt
        y += v * np.sin(theta) * dt
        
        # Enregistrement dans l'historique
        history['x'].append(x)
        history['y'].append(y)
        history['theta'].append(theta)
        history['time'].append(t)
        
        # Incrémentation du temps
        t += dt
    
    return history

def run_simulation(seed, output_dir='simulations'):
    """Exécute la simulation pour les 4 comportements et visualise les résultats"""
    # Création du dossier de sortie s'il n'existe pas
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Création de la scène
    np.random.seed(seed)  # Pour la reproductibilité
    spheres = create_random_scene()
    
    # Simulation des 4 comportements
    behavior_types = [1, 2, 3, 4]
    histories = {}
    
    for bt in behavior_types:
        behavior = ElectricBehavior(behavior_type=bt)
        print(f"Simulation du comportement {bt}: {behavior.get_name()}")
        histories[bt] = simulate_behavior(behavior, spheres)
    
    # Visualisation des résultats
    fig, axs = plt.subplots(2, 2, figsize=(16, 12))
    axs = axs.flatten()
    
    # Préparation des éléments de légende communs
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    
    legend_elements = [
        Patch(facecolor='red', alpha=0.5, label='Conducteur (χ > 0)'),
        Patch(facecolor='blue', alpha=0.5, label='Isolant (χ < 0)'),
        Line2D([0], [0], color='b', linewidth=2, label='Trajectoire'),
        Line2D([0], [0], marker='o', color='r', markersize=10, linestyle='None', label='Collision')
    ]
    
    for i, bt in enumerate(behavior_types):
        ax = axs[i]
        history = histories[bt]
        behavior = ElectricBehavior(behavior_type=bt)
        
        # Dessin des sphères (en premier pour qu'elles soient en arrière-plan)
        for sphere in spheres:
            draw_sphere(ax, sphere)
        
        # Tracé de la trajectoire
        trajectory_line = ax.plot(history['x'], history['y'], 'b-', linewidth=2, label='Trajectoire')[0]
        
        # Dessin de la position initiale du robot
        draw_robot(ax, np.array([0, 0, 0]), 0, color='gray')
        
        # Dessin de la position finale du robot
        final_pos = np.array([history['x'][-1], history['y'][-1], 0])
        final_theta = history['theta'][-1]
        draw_robot(ax, final_pos, final_theta)
        
        # Marquage spécifique selon le résultat
        if history.get('collision', False):
            ax.plot(history['x'][-1], history['y'][-1], 'ro', markersize=10, label='Collision', alpha=0.5)
        elif history.get('out_of_bounds', False):
            ax.plot(history['x'][-1], history['y'][-1], 'yo', markersize=10, label='Hors limites', alpha=0.5)
        
        # Configuration de l'axe
        setup_plot(ax, xlim=(-2.5, 2.5), ylim=(-2.5, 2.5))
        ax.set_title(f"B{bt}: {behavior.get_name()}")
        
        # Ajout de la légende uniquement au premier graphique pour éviter la duplication
        if i == 0:
            ax.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    # Sauvegarde avec le numéro de seed dans le nom de fichier
    filename = os.path.join(output_dir, f'simulation_comportements_{seed:02d}.png')
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Sauvegarde de la simulation {seed} dans {filename}")
    plt.close(fig)  # Fermer la figure pour economiser la memoire

if __name__ == "__main__":
    # Nombre de simulations a executer
    num_simulations = 30
    
    for i in range(num_simulations):
        print(f"\nSimulation {i+1}/{num_simulations} (seed={i})...")
        run_simulation(i)
        print('\n'+'-'*24 )
    
    print(f"Toutes les simulations ont été enregistrées dans le dossier 'simulations/'")
