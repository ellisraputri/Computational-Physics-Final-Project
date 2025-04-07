import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D

def initialize_grid(L=1.0, dx=0.01):
    x = np.arange(0, L + dx, dx)
    y = np.arange(0, L + dx, dx)
    xx, yy = np.meshgrid(x, y)
    return x, y, xx, yy

def initialize_wave(xx, yy, epicenter=(0.5, 0.5), w=0.02):
    return np.exp(-((xx - epicenter[0]) ** 2 + (yy - epicenter[1]) ** 2) / w**2)

def apply_initial_taylor(f, c, dt, dx):
    f_next = f.copy()
    f_next[1:-1, 1:-1] = f[1:-1, 1:-1] + 0.5 * c**2 * (
        (f[:-2, 1:-1] + f[2:, 1:-1] - 2 * f[1:-1, 1:-1]) / dx**2 +
        (f[1:-1, :-2] + f[1:-1, 2:] - 2 * f[1:-1, 1:-1]) / dx**2
    ) * dt**2
    return f_next

def update_wave(f_prev, f_curr, c, dt, dx, damping=0.99):
    # Compute next time step using the wave equation finite difference update
    f_next = np.zeros_like(f_curr)
    f_next[1:-1, 1:-1] = (2 * f_curr[1:-1, 1:-1] - f_prev[1:-1, 1:-1] +
                          c**2 * (
                              (f_curr[:-2, 1:-1] + f_curr[2:, 1:-1] - 2 * f_curr[1:-1, 1:-1]) / dx**2 +
                              (f_curr[1:-1, :-2] + f_curr[1:-1, 2:] - 2 * f_curr[1:-1, 1:-1]) / dx**2
                          ) * dt**2)
    # Absorbing boundary: here a simple damping at edges; can be improved with PML
    f_next *= damping
    return f_next

# Simulation parameters
L = 1.0
dx = 0.01
c = 0.01
dt = 0.7 * dx / c
nsteps = 300

# Initialize grid and wave
x, y, xx, yy = initialize_grid(L, dx)
f0 = initialize_wave(xx, yy, epicenter=(0.5, 0.5), w=0.02)
f1 = apply_initial_taylor(f0, c, dt, dx)

# Set up figure for animation
fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
ax.set_xlim(0, L)
ax.set_ylim(0, L)
ax.set_zlim(-1, 1)
ax.set_xlabel("X (km)")
ax.set_ylabel("Y (km)")
ax.set_zlabel("Amplitude")
ax.set_title("Seismic Wave Propagation")

surf = ax.plot_surface(xx, yy, f0, cmap="plasma", edgecolor="k", linewidth=0.3)

# Time stepping for animation
def update(frame, f_prev, f_curr):
    global xx, yy, c, dt, dx
    f_next = update_wave(f_prev, f_curr, c, dt, dx)
    
    # Shift time steps for next update
    f_prev[:] = f_curr
    f_curr[:] = f_next
    
    # Update plot: clear and plot new surface
    ax.clear()
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)
    ax.set_zlim(-1, 1)
    ax.set_xlabel("X (km)")
    ax.set_ylabel("Y (km)")
    ax.set_zlabel("Amplitude")
    ax.set_title(f"Seismic Wave - Time: {frame * dt:.2f} sec")
    ax.plot_surface(xx, yy, f_curr, cmap="plasma", edgecolor="k", linewidth=0.3)
    return ax,

ani = animation.FuncAnimation(fig, update, frames=nsteps, fargs=(f0.copy(), f1.copy()), interval=10, blit=False)
plt.show()
