import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.signal import ricker

# Grid parameters
NX, NY = 200, 200  # Grid size
XMIN, XMAX = 0.0, 2000.0  # Meters
YMIN, YMAX = 0.0, 2000.0  # Meters
DX = (XMAX - XMIN) / NX  # Spatial step (m)
DT = 0.001  # Time step (s)
NT = 500  # Number of time steps
PLOT_EVERY = 5  # Plot every N steps

# Material properties - Shear wave velocity (m/s) and density (kg/m³)
VS = np.ones((NX, NY)) * 1500.0  # Base shear wave velocity (rock)
MU = np.ones((NX, NY)) * 2.25e9  # Shear modulus (μ = ρ*vs²)

# Two-layer model example:
# VS[NX//2:, :] = 2000.0  # Higher velocity layer
# MU[NX//2:, :] = 4.0e9    # Higher shear modulus layer

# Initialize displacement fields (S-waves involve particle motion)
ux = np.zeros((NX, NY))  # x-component of displacement
uy = np.zeros((NX, NY))  # y-component of displacement
ux_prev = np.zeros((NX, NY))  # Previous time step
uy_prev = np.zeros((NX, NY))  # Previous time step

# Absorbing boundary layer
ABL_WIDTH = 20
damping = np.ones((NX, NY))
damping[:ABL_WIDTH, :] = np.linspace(0.9, 1.0, ABL_WIDTH)[:, np.newaxis]
damping[-ABL_WIDTH:, :] = np.linspace(1.0, 0.9, ABL_WIDTH)[:, np.newaxis]
damping[:, :ABL_WIDTH] = np.minimum(damping[:, :ABL_WIDTH], np.linspace(0.9, 1.0, ABL_WIDTH))
damping[:, -ABL_WIDTH:] = np.minimum(damping[:, -ABL_WIDTH:], np.linspace(1.0, 0.9, ABL_WIDTH))

def ricker_wavelet(t, f0=10.0):
    """Ricker wavelet with peak frequency f0 (Hz)"""
    return (1.0 - 2.0*(np.pi*f0*t)**2) * np.exp(-(np.pi*f0*t)**2)

# Seismic source (horizontal force for SH-waves)
source_x, source_y = NX//4, NY//2  # Source position
source_times = np.arange(NT) * DT
source_amp = ricker_wavelet(source_times - 0.1, f0=10.0) * 1e6  # Force amplitude


def update_wave(n):
    """Update the wave field for one time step"""
    global ux, uy, ux_prev, uy_prev
    
    # Add source (horizontal force)
    if n < len(source_amp):
        ux[source_x, source_y] += source_amp[n] * DT**2 / MU[source_x, source_y]
    
    # Calculate stresses
    # τ_xy = μ*(∂u_y/∂x + ∂u_x/∂y)
    
    # Update x-displacement (SH-wave equation)
    ux_new = np.zeros_like(ux)
    ux_new[1:-1, 1:-1] = (
        2*ux[1:-1, 1:-1] - ux_prev[1:-1, 1:-1] +
        (VS[1:-1, 1:-1]**2 * DT**2 / DX**2) * (
            ux[2:, 1:-1] + ux[:-2, 1:-1] +
            ux[1:-1, 2:] + ux[1:-1, :-2] -
            4*ux[1:-1, 1:-1]
        )
    )
    
    # Apply damping
    ux_new *= damping
    
    # Update fields
    ux_prev = ux.copy()
    ux = ux_new.copy()

# Create figure
fig, ax = plt.subplots(figsize=(10, 8))
img = ax.imshow(ux.T, extent=[XMIN, XMAX, YMAX, YMIN], 
                cmap='seismic', vmin=-1e-6, vmax=1e-6)
plt.colorbar(img, label='Horizontal Displacement (m)')
ax.set_title("2D SH-Wave Propagation")
ax.set_xlabel("Distance (m)")
ax.set_ylabel("Depth (m)")

# Add layer boundary if using two-layer model
if np.any(VS != VS[0,0]):
    depth_separator = (YMAX - YMIN) * (NX // 2) / NX
    ax.axhline(depth_separator, color='black', linestyle='--', 
               linewidth=1.5, label='Layer Boundary')
    ax.legend()

def update(frame):
    """Update function for animation"""
    for _ in range(PLOT_EVERY):
        update_wave(frame * PLOT_EVERY + _)
    
    img.set_array(ux.T)
    img.set_clim(vmin=-np.max(np.abs(ux)), vmax=np.max(np.abs(ux)))
    return [img]

# Run animation
ani = FuncAnimation(fig, update, frames=NT//PLOT_EVERY, 
                    interval=50, blit=True)
plt.show()