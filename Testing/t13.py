import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.signal import ricker

# Simulation parameters
NX, NY = 200, 200  # Grid size
XMIN, XMAX = 0.0, 2000.0  # Meters
YMIN, YMAX = 0.0, 2000.0  # Meters
DX = (XMAX - XMIN) / NX  # Spatial step (m)
DT = 0.001  # Time step (s)
NT = 500  # Number of time steps
PLOT_EVERY = 5  # Plot every N steps

# Wave speed model (m/s) - Simple two-layer model
VEL = np.ones((NX, NY)) * 3000.0  # Base velocity (water)
# VEL[NX//2:, :] = 3000.0  # Higher velocity layer (rock)

# Density model (kg/m³) - Constant for simplicity
RHO = np.ones((NX, NY)) * 1000.0

# Initialize wave fields
phi = np.zeros((NX, NY))  # Pressure field (current)
psi = np.zeros((NX, NY))  # Pressure field (previous)
vx = np.zeros((NX, NY))  # x-component of particle velocity
vy = np.zeros((NX, NY))  # y-component of particle velocity

# Absorbing boundary layer width
ABL_WIDTH = 20
damping = np.ones((NX, NY))
damping[:ABL_WIDTH, :] = np.linspace(0.9, 1.0, ABL_WIDTH)[:, np.newaxis]
damping[-ABL_WIDTH:, :] = np.linspace(1.0, 0.9, ABL_WIDTH)[:, np.newaxis]
damping[:, :ABL_WIDTH] = np.minimum(damping[:, :ABL_WIDTH], np.linspace(0.9, 1.0, ABL_WIDTH))
damping[:, -ABL_WIDTH:] = np.minimum(damping[:, -ABL_WIDTH:], np.linspace(1.0, 0.9, ABL_WIDTH))

# Seismic source (Ricker wavelet at center)
def ricker_wavelet(t, f0=20.0):
    """Ricker wavelet with peak frequency f0 (Hz)"""
    return (1.0 - 2.0*(np.pi*f0*t)**2) * np.exp(-(np.pi*f0*t)**2)

source_x, source_y = NX//4, NY//2  # Source position
source_times = np.arange(NT) * DT
source_amp = ricker_wavelet(source_times - 0.1, f0=20.0) * 1e6  # Pressure amplitude

def update_wave(n):
    """Update the wave field for one time step"""
    global phi, psi, vx, vy
    
    # Add source (pressure injection)
    if n < len(source_amp):
        phi[source_x, source_y] += source_amp[n]
    
    # Update particle velocities (vx, vy)
    vx[1:-1, 1:-1] -= (DT/RHO[1:-1, 1:-1]) * (phi[2:, 1:-1] - phi[:-2, 1:-1]) / (2*DX)
    vy[1:-1, 1:-1] -= (DT/RHO[1:-1, 1:-1]) * (phi[1:-1, 2:] - phi[1:-1, :-2]) / (2*DX)
    
    # Update pressure field
    phi_new = phi.copy()
    phi_new[1:-1, 1:-1] = (
        2*phi[1:-1, 1:-1] - psi[1:-1, 1:-1] +
        (VEL[1:-1, 1:-1]**2 * DT**2 / DX**2) * (
            phi[2:, 1:-1] + phi[:-2, 1:-1] +
            phi[1:-1, 2:] + phi[1:-1, :-2] -
            4*phi[1:-1, 1:-1]
        )
    )
    phi_new *= damping

    
    # Update fields
    psi = phi.copy()
    phi = phi_new.copy()
    
    # Boundary conditions (already handled by damping)

# Create figure
fig, ax = plt.subplots(figsize=(10, 8))
img = ax.imshow(phi.T, extent=[XMIN, XMAX, YMAX, YMIN], 
                cmap='seismic', vmin=-1e4, vmax=1e4)
plt.colorbar(img, label='Pressure (Pa)')
ax.set_title("2D Seismic Wave Propagation")
ax.set_xlabel("Distance (m)")
ax.set_ylabel("Depth (m)")

depth_separator = (YMAX - YMIN) * (NX // 2) / NX  # halfway down the Y axis
ax.axhline(depth_separator, color='black', linestyle='--', linewidth=1.5, label='Water-Ground Boundary')
ax.legend()

def update(frame):
    """Update function for animation"""
    for _ in range(PLOT_EVERY):
        update_wave(frame * PLOT_EVERY + _)
    
    img.set_array(phi.T)
    return [img]

# Run animation
ani = FuncAnimation(fig, update, frames=NT//PLOT_EVERY, 
                    interval=50, blit=True)
plt.show()