# debug.py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
import os
from constants import *
from electric_sense import Sphere, compute_electric_sense
from draw_robot import draw_robot, draw_sphere, draw_trajectory, setup_plot

def run_simulation(movement_type, sphere_type):
    """Fonction principale de simulation selon les paramètres choisis"""
    # Capteur fixe à l'origine
    sensor_pos = np.array([0, 0, 0])
    sensor_orientation = 0
    
    # Paramètres selon le type de mouvement
    if movement_type == 'front':
        # Sphère se déplaçant latéralement devant le capteur
        positions = []
        y_positions = np.linspace(-0.5, 0.5, 100)
        x_position = 0.3
        dimension = 'y'
        xlabel = 'Position Y de la sphère (m)'
        for y in y_positions:
            positions.append([x_position, y, 0])
    else:  # 'side'
        # Sphère se déplaçant d'avant en arrière à côté du capteur
        positions = []
        x_positions = np.linspace(0.7, -0.7, 100)
        y_position = 0.3
        dimension = 'x'
        xlabel = 'Position X de la sphère (m)'
        for x in x_positions:
            positions.append([x, y_position, 0])
    
    # Paramètres selon le type de sphère
    chi = 1.0 if sphere_type == 'conductrice' else -0.5
    
    # Création de la sphère
    sphere = Sphere(positions[0], 0.03, chi)
    
    # Stockage des mesures
    I_ax_values = []
    I_lat_values = []
    I_vert_values = []
    
    # Calcul pour chaque position
    for pos in positions:
        sphere.position = np.array(pos)
        I_ax, I_lat, I_vert = compute_electric_sense([sphere], sensor_pos, sensor_orientation)
        I_ax_values.append(I_ax)
        I_lat_values.append(I_lat)
        I_vert_values.append(I_vert)
    
    # Visualisation
    fig = plt.figure(figsize=(12, 8))
    
    # Plot de la scène
    ax_scene = plt.subplot(121)
    draw_robot(ax_scene, sensor_pos, sensor_orientation)
    draw_sphere(ax_scene, sphere)
    draw_trajectory(ax_scene, positions, dimension)
    setup_plot(ax_scene)
    plt.title(f'Vue de la scène - Sphère {sphere_type}')
    
    # Plot des mesures
    plt.subplot(122)
    x_axis = [pos[1] if dimension == 'y' else pos[0] for pos in positions]
    plt.plot(x_axis, I_ax_values, 'b-', label='I axial')
    plt.plot(x_axis, I_lat_values, 'r-', label='I latéral')
    plt.plot(x_axis, I_vert_values, 'g-', label='I vertical')
    plt.xlabel(xlabel)
    plt.ylabel('Intensité de champ (V/m)')
    plt.grid(True)
    plt.legend()
    
    plt.tight_layout()
    filename = f'mesures_sphere_{movement_type}_{sphere_type}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Figure enregistrée sous '{filename}'")
    plt.show()

def menu():
    """Affiche un menu pour choisir les paramètres de simulation"""
    print("\n=== TEST DU CAPTEUR ÉLECTRIQUE ===")
    print("Choisissez le type de mouvement de la sphère:")
    print("1. Mouvement frontal (gauche-droite)")
    print("2. Mouvement latéral (avant-arrière)")
    
    while True:
        choice = input("Votre choix (1/2): ")
        if choice in ['1', '2']:
            movement_type = 'front' if choice == '1' else 'side'
            break
        print("Choix invalide, veuillez réessayer.")
    
    print("\nChoisissez le type de sphère:")
    print("1. Conductrice (χ > 0)")
    print("2. Isolante (χ < 0)")
    
    while True:
        choice = input("Votre choix (1/2): ")
        if choice in ['1', '2']:
            sphere_type = 'conductrice' if choice == '1' else 'isolante'
            break
        print("Choix invalide, veuillez réessayer.")
    
    return movement_type, sphere_type

if __name__ == "__main__":
    movement_type, sphere_type = menu()
    run_simulation(movement_type, sphere_type)
