import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

"""
Simulation d'un capteur électrique capacitif et de sa réponse à des objets perturbateurs.

Principes physiques :
1. Électrocinétique quasi-stationnaire : les champs sont considérés instantanés (∇·j = 0)
2. Le capteur crée un champ électrique E0 de type dipôle (j = γE)
3. Les objets se polarisent sous l'effet de E0 selon leur nature :
   - Conducteurs : les charges se réorganisent pour annuler E interne (χ > 0)
   - Isolants : les dipôles s'orientent en opposition à E0 (χ < 0)
4. Cette polarisation P crée un champ perturbateur E1
5. La mesure du capteur (ΔI) résulte du potentiel créé par E1 à sa position
"""

class ElectricSensor:
    def __init__(self, objects, params=None):
        # Paramètres physiques par défaut
        self.params = {
            'gamma': 1.0,     # conductivité du milieu (S/m)
            'C0': 1.0,        # conductance à vide du capteur (S)
            'U': 1.0,         # tension appliquée (V)
            'a': 0.3,         # rayon des sphères (m)
            'chi_cond': 20.0, # contraste conducteur (>0)
            'chi_isol': -20.0 # contraste isolant (<0)
        }
        if params:
            self.params.update(params)
        
        # Courant initial I = γ·U·C0
        self.I = self.params['C0'] * self.params['U']
        self.objects = objects
        self.capteur_pos = np.array([0, 0])
        
        # Grille de calcul
        self.n = 50
        x = np.linspace(-2, 2, self.n)
        y = np.linspace(-2, 2, self.n)
        self.X, self.Y = np.meshgrid(x, y)

    def compute_E0(self, x, y):
        """Calcul du champ électrique initial E0 créé par le capteur.
        
        E0 suit la loi d'un dipôle électrique :
        E0(r) = I·r/(4πγr³) où r est le vecteur position depuis le capteur
        """
        r = np.array([x - self.capteur_pos[0], y - self.capteur_pos[1]])
        r_norm = np.sqrt(r[0]**2 + r[1]**2)
        E = np.zeros((2, x.shape[0], x.shape[1]))
        # Masque pour éviter la singularité au centre
        mask = r_norm > 0.3
        # Composantes du champ E0
        E[0][mask] = self.I * r[0][mask] / (4*np.pi*self.params['gamma']*r_norm[mask]**3)
        E[1][mask] = self.I * r[1][mask] / (4*np.pi*self.params['gamma']*r_norm[mask]**3)
        return E

    def compute_E1(self, x, y, obj):
        """Calcul du champ de perturbation E1 créé par un objet.
        
        1. L'objet se polarise sous l'effet de E0 : P = χ·a³·E0
        2. Cette polarisation crée un champ dipôlaire :
           E1(r) = [3(P·r)r - r²P]/(4πγr⁵)
        """
        pos = np.array(obj[:2])
        # Contraste selon la nature de l'objet
        chi = self.params['chi_cond'] if obj[2] else self.params['chi_isol']
        
        # Calcul de E0 à la position de l'objet
        r_to_obj = pos - self.capteur_pos
        r_norm_obj = np.sqrt(np.sum(r_to_obj**2))
        E0_at_obj = self.I * r_to_obj / (4*np.pi*self.params['gamma']*r_norm_obj**3)
        
        # Moment dipolaire induit P = χa³E0
        P = chi * self.params['a']**3 * E0_at_obj
        
        # Calcul du champ dipôlaire E1
        r = np.array([x - pos[0], y - pos[1]])
        r_norm = np.sqrt(r[0]**2 + r[1]**2)
        E = np.zeros((2, x.shape[0], x.shape[1]))
        mask = r_norm > 0.3
        
        # Produit scalaire P·r
        P_dot_r = P[0]*r[0] + P[1]*r[1]
        # Formule du champ dipôlaire
        for i in range(2):
            E[i][mask] = (3*P_dot_r[mask]*r[i][mask] - r_norm[mask]**2*P[i]) / \
                         (4*np.pi*self.params['gamma']*r_norm[mask]**5)
        return E

    def compute_delta_I(self, angle):
        """Calcul de la variation de courant ΔI pour une orientation donnée.
        
        ΔI est proportionnel au potentiel créé par E1 :
        ΔI = -C0·ΔV = -C0·∫E1·dl
        L'intégrale est évaluée le long de la direction du capteur.
        """
        direction = np.array([np.cos(angle), np.sin(angle)])
        phi_total = 0
        
        for obj in self.objects:
            pos = np.array(obj[:2])
            chi = self.params['chi_cond'] if obj[2] else self.params['chi_isol']
            r = pos - self.capteur_pos
            r_norm = np.sqrt(np.sum(r**2))
            # E0 à la position de l'objet
            E0_at_obj = self.I * r / (4*np.pi*self.params['gamma']*r_norm**3)
            # Polarisation induite
            P = chi * self.params['a']**3 * E0_at_obj
            # Contribution au potentiel
            phi = np.sum(P * direction) / (4*np.pi*self.params['gamma']*r_norm**2)
            phi_total += phi
        
        return -self.params['C0'] * phi_total

    def plot_fields(self):
        """Visualisation des champs et de la réponse du capteur"""
        fig = plt.figure(figsize=(15, 10))

        # Calcul des champs
        E0 = self.compute_E0(self.X, self.Y)
        E1_total = sum(self.compute_E1(self.X, self.Y, obj) for obj in self.objects)
        E_total = E0 + E1_total

        # Calcul de ΔI pour toutes les orientations
        angles = np.linspace(0, 2*np.pi, 360)
        delta_I = np.array([self.compute_delta_I(angle) for angle in angles])

        def add_objects(ax):
            for obj in self.objects:
                color = 'green' if obj[2] else 'red'
                ax.add_patch(Circle((obj[0], obj[1]), self.params['a'], 
                                  color=color, alpha=0.3))
            ax.plot(self.capteur_pos[0], self.capteur_pos[1], 'ko')

        # Visualisation des champs E0, E1 et E_total
        fields = [(E0, 'Champ initial E0', 'blue'),
                 (E1_total, 'Champ de perturbation E1', 'red'),
                 (E_total, 'Champ total', 'purple')]
        
        for i, (field, title, color) in enumerate(fields, 1):
            ax = plt.subplot(2, 2, i)
            plt.streamplot(self.X, self.Y, field[0], field[1], 
                         density=2, color=color, linewidth=0.5)
            add_objects(ax)
            plt.title(title)
            plt.axis('equal')
            plt.grid(True)

        # Diagramme polaire de la réponse ΔI
        ax = plt.subplot(224, projection='polar')
        ax.plot(angles, delta_I)
        ax.set_title('ΔI selon l\'orientation du capteur')
        ax.set_theta_zero_location('E')  # 0° aligné avec l'axe x

        # Marquage des positions des objets
        for obj in self.objects:
            x, y = obj[:2]
            theta = np.arctan2(y, x)
            color = 'green' if obj[2] else 'red'
            r_max = max(abs(delta_I)) * 1.1
            ax.plot(theta, r_max, 'o', color=color, markersize=10, alpha=0.5)

        plt.figtext(0.02, 0.02, 'Vert: conducteur\nRouge: isolant', 
                   bbox=dict(facecolor='white', alpha=0.8))
        plt.tight_layout()
        return fig

# Configuration et exécution
objects = [
    [1.0,  0.2, True],   # [x, y, is_conductor]
    [1.6, -1.3, False],
    [-0.6, 1.1, True],
    [-1.0, 0.2, False],
]

sensor = ElectricSensor(objects)
fig = sensor.plot_fields()
fig.savefig('champs_et_delta_I.png', dpi=300, bbox_inches='tight')
plt.close()
