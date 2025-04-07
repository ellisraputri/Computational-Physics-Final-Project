import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Simulation parameters
NX, NY = 200, 200  # Grid size
XMIN, XMAX = -1.0, 1.0
YMIN, YMAX = -1.0, 1.0
COURANT = 0.1       # Wave speed
KAPPA = 0.0         # Damping
NSTEPS = 500        # Number of time steps
PLOT_EVERY = 5      # Plot every N steps

# Initialize wave fields
phi = np.zeros((NX, NY))  # Current wave field
psi = np.zeros((NX, NY))  # Previous wave field

# Initialize with a circular wave at center
def init_circular_wave():
    x = np.linspace(XMIN, XMAX, NX)
    y = np.linspace(YMIN, YMAX, NY)
    X, Y = np.meshgrid(x, y, indexing='ij')
    r = np.sqrt((X-0.5)**2 + Y**2)
    phi[:, :] = np.exp(-(r*10)**2)

init_circular_wave()

# Create figure for animation
fig, ax = plt.subplots()
img = ax.imshow(phi.T, extent=[XMIN, XMAX, YMIN, YMAX], 
               origin='lower', cmap='seismic', vmin=-0.1, vmax=0.1)
plt.colorbar(img)

def update_wave():
    """Update the wave field for one time step"""
    global phi, psi
    
    # Laplacian (second derivative)
    laplacian = (np.roll(phi, 1, axis=0) + np.roll(phi, -1, axis=0) +
                 np.roll(phi, 1, axis=1) + np.roll(phi, -1, axis=1) - 4*phi)
    
    # New wave field
    phi_new = 2*phi - psi + COURANT**2 * laplacian - KAPPA*phi
    
    # Update fields
    psi = phi.copy()
    phi = phi_new.copy()
    
    # Boundary conditions (fixed ends)
    phi[0, :] = 0
    phi[-1, :] = 0
    phi[:, 0] = 0
    phi[:, -1] = 0

def update(frame):
    """Update function for animation"""
    for _ in range(PLOT_EVERY):
        update_wave()
    
    img.set_array(phi.T)
    return [img]

# Create animation
ani = FuncAnimation(fig, update, frames=NSTEPS//PLOT_EVERY, 
                   interval=50, blit=True)

plt.title("2D Wave Equation Simulation")
plt.xlabel("X")
plt.ylabel("Y")
plt.show()