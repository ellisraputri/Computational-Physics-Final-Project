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
VS = np.ones((NX, NY)) * 1500.0  # Base shear wave velocity
RHO = np.ones((NX, NY)) * 2000.0  # Density
MU = RHO * VS**2  # Shear modulus (μ = ρ*vs²)

# Two-layer model example:
VS[NX//2:, :] = 2000.0  # Higher velocity layer
RHO[NX//2:, :] = 2500.0  # Higher density layer
MU = RHO * VS**2  # Recalculate shear modulus

# Initialize displacement fields for SV-waves
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

# Seismic source (vertical force for SV-waves)
source_x, source_y = NX//4, NY//2  # Source position
source_times = np.arange(NT) * DT
source_amp = ricker_wavelet(source_times - 0.1, f0=10.0) * 1e6  # Force amplitude

def update_wave(n):
    """Update the wave field for one time step for SV-waves"""
    global ux, uy, ux_prev, uy_prev
    
    # Add source (vertical force)
    if n < len(source_amp):
        uy[source_x, source_y] += source_amp[n] * DT**2 / RHO[source_x, source_y]
    
    # Calculate spatial derivatives
    dux_dx = np.zeros_like(ux)
    dux_dy = np.zeros_like(ux)
    duy_dx = np.zeros_like(uy)
    duy_dy = np.zeros_like(uy)
    
    # Central differences for derivatives
    dux_dx[1:-1, 1:-1] = (ux[2:, 1:-1] - ux[:-2, 1:-1]) / (2*DX)
    dux_dy[1:-1, 1:-1] = (ux[1:-1, 2:] - ux[1:-1, :-2]) / (2*DX)
    duy_dx[1:-1, 1:-1] = (uy[2:, 1:-1] - uy[:-2, 1:-1]) / (2*DX)
    duy_dy[1:-1, 1:-1] = (uy[1:-1, 2:] - uy[1:-1, :-2]) / (2*DX)
    
    # Calculate stresses (τ_xy = μ*(∂u_y/∂x + ∂u_x/∂y))
    tau_xy = MU * (duy_dx + dux_dy)
    
    # Update displacements using the wave equation for SV-waves
    ux_new = np.zeros_like(ux)
    uy_new = np.zeros_like(uy)
    
    # x-component
    ux_new[1:-1, 1:-1] = (
        2*ux[1:-1, 1:-1] - ux_prev[1:-1, 1:-1] +
        (DT**2 / RHO[1:-1, 1:-1]) * (
            (tau_xy[1:-1, 2:] - tau_xy[1:-1, :-2]) / (2*DX)  # ∂τ_xy/∂y
        )
    )
    
    # y-component
    uy_new[1:-1, 1:-1] = (
        2*uy[1:-1, 1:-1] - uy_prev[1:-1, 1:-1] +
        (DT**2 / RHO[1:-1, 1:-1]) * (
            (tau_xy[2:, 1:-1] - tau_xy[:-2, 1:-1]) / (2*DX)  # ∂τ_xy/∂x
        )
    )
    
    # Apply damping
    ux_new *= damping
    uy_new *= damping
    
    # Update fields
    ux_prev = ux.copy()
    uy_prev = uy.copy()
    ux = ux_new.copy()
    uy = uy_new.copy()

# Create figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Horizontal displacement plot
img1 = ax1.imshow(ux.T, extent=[XMIN, XMAX, YMAX, YMIN], 
                 cmap='seismic', vmin=-1e-6, vmax=1e-6)
plt.colorbar(img1, ax=ax1, label='Horizontal Displacement (m)')
ax1.set_title("Horizontal Displacement (SV-Wave)")
ax1.set_xlabel("Distance (m)")
ax1.set_ylabel("Depth (m)")

# Vertical displacement plot
img2 = ax2.imshow(uy.T, extent=[XMIN, XMAX, YMAX, YMIN], 
                 cmap='seismic', vmin=-1e-6, vmax=1e-6)
plt.colorbar(img2, ax=ax2, label='Vertical Displacement (m)')
ax2.set_title("Vertical Displacement (SV-Wave)")
ax2.set_xlabel("Distance (m)")
ax2.set_ylabel("Depth (m)")

# Add layer boundary
depth_separator = (YMAX - YMIN) * (NX // 2) / NX
for ax in [ax1, ax2]:
    ax.axhline(depth_separator, color='black', linestyle='--', 
              linewidth=1.5, label='Layer Boundary')
    ax.legend()

def update(frame):
    """Update function for animation"""
    for _ in range(PLOT_EVERY):
        update_wave(frame * PLOT_EVERY + _)
    
    # Update both plots
    current_max = max(np.max(np.abs(ux)), np.max(np.abs(uy)))
    vlimit = current_max if current_max > 0 else 1e-6
    
    img1.set_array(ux.T)
    img1.set_clim(vmin=-vlimit, vmax=vlimit)
    
    img2.set_array(uy.T)
    img2.set_clim(vmin=-vlimit, vmax=vlimit)
    
    return [img1, img2]

# Run animation
ani = FuncAnimation(fig, update, frames=NT//PLOT_EVERY, 
                   interval=50, blit=True)
plt.tight_layout()
plt.show()