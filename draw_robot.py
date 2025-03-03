# draw_robot.py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon
from constants import X_ELECTRODES, Y_ELECTRODES, Z_ELECTRODES

def draw_robot(ax, sensor_pos, sensor_orientation, robot_size=0.1, color='black'):
    """Dessine le robot avec ses électrodes sur l'axe donné"""
    # Robot (triangle pour montrer l'orientation)
    angle = sensor_orientation
    triangle_points = np.array([
        [sensor_pos[0] + robot_size*np.cos(angle), sensor_pos[1] + robot_size*np.sin(angle)],  # pointe
        [sensor_pos[0] - robot_size*np.cos(angle) + robot_size/2*np.sin(angle), 
         sensor_pos[1] - robot_size*np.sin(angle) - robot_size/2*np.cos(angle)],  # coin droit
        [sensor_pos[0] - robot_size*np.cos(angle) - robot_size/2*np.sin(angle),
         sensor_pos[1] - robot_size*np.sin(angle) + robot_size/2*np.cos(angle)]   # coin gauche
    ])
    triangle = Polygon(triangle_points, color=color)
    ax.add_patch(triangle)
    
    # Électrodes
    electrodes = []
    for i in range(5):
        # Rotation des coordonnées des électrodes
        R = np.array([[np.cos(angle), -np.sin(angle), 0],
                     [np.sin(angle), np.cos(angle), 0],
                     [0, 0, 1]])
        pos = sensor_pos + R @ np.array([X_ELECTRODES[i], Y_ELECTRODES[i], Z_ELECTRODES[i]])
        electrode = ax.plot(pos[0], pos[1], 'ko', markersize=5)[0]
        electrodes.append(electrode)
    
    return triangle, electrodes

def draw_sphere(ax, sphere):
    """Dessine une sphère sur l'axe donné"""
    sphere_plot = Circle((sphere.position[0], sphere.position[1]), 
                        sphere.radius, 
                        color='red' if sphere.chi > 0 else 'blue',
                        alpha=0.5)
    ax.add_patch(sphere_plot)
    return sphere_plot

def draw_trajectory(ax, positions, dimension='y'):
    """Dessine la trajectoire de la sphère"""
    if dimension == 'y':
        # Trajectoire horizontale (y varie)
        x_val = positions[0][0]
        y_vals = [pos[1] for pos in positions]
        ax.plot([x_val] * len(positions), y_vals, 'b--', alpha=0.3, label='Trajectoire sphère')
    else:
        # Trajectoire verticale (x varie)
        y_val = positions[0][1]
        x_vals = [pos[0] for pos in positions]
        ax.plot(x_vals, [y_val] * len(positions), 'b--', alpha=0.3, label='Trajectoire sphère')
    
def setup_plot(ax, xlim=(-1.0, 1.0), ylim=(-1.0, 1.0)):
    """Configure les paramètres de l'axe"""
    ax.grid(True)
    ax.set_aspect('equal')
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.legend()
