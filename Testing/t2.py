import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D

# Constants
L = 1.0
dx = 0.01
c = 1.0
dt = 0.7 * dx / c  # CFL condition
w = 0.05
xc = 0.5

# Initialize spatial grid
x = np.arange(0, L + dx, dx)
y = np.arange(0, L + dx, dx)
xx, yy = np.meshgrid(x, y)

npts = len(x)
nsteps = 199  # Number of time steps

# Initialize wave function
f = np.zeros((npts, npts, 3))
f[:, :, 0] = np.exp(-((xx - xc) ** 2 + (yy - xc) ** 2) / w**2)  # Initial Gaussian pulse

# First time step using Taylor expansion
f[1:-1, 1:-1, 1] = f[1:-1, 1:-1, 0] + 0.5 * c**2 * (
    (f[:-2, 1:-1, 0] + f[2:, 1:-1, 0] - 2 * f[1:-1, 1:-1, 0]) / dx**2
    + (f[1:-1, :-2, 0] + f[1:-1, 2:, 0] - 2 * f[1:-1, 1:-1, 0]) / dx**2
) * dt**2

# Set up 3D figure for animation
fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
ax.set_xlim(0, L)
ax.set_ylim(0, L)
ax.set_zlim(-1, 1)  # Fixed wave height range
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Wave Height")
ax.set_title("2D Wave Equation Simulation")

# Plot initial wave surface
surf = ax.plot_surface(xx, yy, f[:, :, 0], cmap="plasma", edgecolor="k", linewidth=0.5)

# Update function for animation
def update(frame):
    global f
    f[1:-1, 1:-1, 2] = (
        2 * f[1:-1, 1:-1, 1] - f[1:-1, 1:-1, 0] 
        + c**2 * (
            (f[:-2, 1:-1, 1] + f[2:, 1:-1, 1] - 2 * f[1:-1, 1:-1, 1]) / dx**2
            + (f[1:-1, :-2, 1] + f[1:-1, 2:, 1] - 2 * f[1:-1, 1:-1, 1]) / dx**2
        ) * dt**2
    )

    # Apply Neumann boundary conditions
    f[0, :, 2] = f[1, :, 2]  
    f[-1, :, 2] = f[-2, :, 2]  
    f[:, 0, 2] = f[:, 1, 2]  
    f[:, -1, 2] = f[:, -2, 2]  

    # Shift time steps
    f[:, :, 0], f[:, :, 1] = f[:, :, 1], f[:, :, 2]

    # Update plot
    ax.clear()
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)
    ax.set_zlim(-1, 1)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Wave Height")
    ax.set_title(f"2D Wave Simulation - Time: {frame * dt:.2f}")

    ax.plot_surface(xx, yy, f[:, :, 1], cmap="plasma", edgecolor="k", linewidth=0.3)

    return ax,

# Create animation
ani = animation.FuncAnimation(fig, update, frames=nsteps, interval=10, blit=False)

plt.show()
