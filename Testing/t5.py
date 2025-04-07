import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# 🌍 Grid and Physical Constants
L = 1.0       # Grid size (1 km)
dx = 0.01     # Spatial step (10 m)
c = 3.5       # Wave speed (~3.5 km/s for rock)
dt = 0.5 * dx / (np.sqrt(2) * c)  # CFL condition for stability
npts = int(L / dx) + 1
nsteps = 300  # Simulation steps

# 🌍 Initialize 2D Grid
x = np.linspace(0, L, npts)
y = np.linspace(0, L, npts)
xx, yy = np.meshgrid(x, y)

# 🌋 Seismic Source (Ricker Wavelet)
def ricker_wavelet(t, f0=10.0):
    """ Ricker wavelet (commonly used for seismic sources) """
    t0 = 1.0 / f0
    term = (np.pi * f0 * (t - t0))**2
    return (1 - 2 * term) * np.exp(-term)

# 🌋 Epicenter location (center of grid)
epicenter_x, epicenter_y = L / 2, L / 2
epicenter_idx_x = int(epicenter_x / dx)
epicenter_idx_y = int(epicenter_y / dx)

# 🌍 Initialize wave field
u = np.zeros((npts, npts, 3))  # u[:,:,0] = prev, u[:,:,1] = current, u[:,:,2] = next

# 🎥 Set up the figure
fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
ax.set_xlim(0, L)
ax.set_ylim(0, L)
ax.set_zlim(-1, 1)
ax.set_xlabel("X (km)")
ax.set_ylabel("Y (km)")
ax.set_zlabel("Amplitude")
ax.set_title("Seismic Wave Propagation")

# 🌊 Initial 3D wave plot
surf = ax.plot_surface(xx, yy, u[:, :, 0], cmap="plasma", edgecolor="k", linewidth=0.3)

# 🎬 Update function for animation
def update(frame):
    global u

    # Apply wave equation (Finite Difference)
    u[1:-1, 1:-1, 2] = (
        2 * u[1:-1, 1:-1, 1] - u[1:-1, 1:-1, 0]  # Time evolution
        + (c**2 * dt**2 / dx**2) * (
            (u[:-2, 1:-1, 1] + u[2:, 1:-1, 1] - 2 * u[1:-1, 1:-1, 1])  # d²u/dx²
            + (u[1:-1, :-2, 1] + u[1:-1, 2:, 1] - 2 * u[1:-1, 1:-1, 1])  # d²u/dy²
        )
    )

    # Add source term
    u[epicenter_idx_x, epicenter_idx_y, 2] += ricker_wavelet(frame * dt, f0=5.0)

    # Absorbing boundary conditions (damping)
    damping = 0.99
    u[:, :, 2] *= damping

    # Shift time steps
    u[:, :, 0], u[:, :, 1] = u[:, :, 1], u[:, :, 2]

    # Update plot
    ax.clear()
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)
    ax.set_zlim(-1, 1)
    ax.set_xlabel("X (km)")
    ax.set_ylabel("Y (km)")
    ax.set_zlabel("Amplitude")
    ax.set_title(f"Seismic Wave - Time: {frame * dt:.2f} sec")

    ax.plot_surface(xx, yy, u[:, :, 1], cmap="plasma", edgecolor="k", linewidth=0.3)

    return ax,

# Create animation
ani = animation.FuncAnimation(fig, update, frames=nsteps, interval=10, blit=False)
plt.show()
