import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Grid size and time parameters
nx, ny = 100, 100  # Grid size
dx = dy = 1.0  # Grid spacing
dt = 0.01  # Time step
nt = 200  # Number of time steps

# Elastic constants (Lamé parameters) and density
rho = 1.0  # Density
mu = 1.0  # Shear modulus (Lamé parameter)
lam = 2.0  # Second Lamé parameter

# Wave velocity calculations
vp = np.sqrt((lam + 2 * mu) / rho)  # P-wave velocity
vs = np.sqrt(mu / rho)  # S-wave velocity

# Initialize displacement and velocity arrays
u = np.zeros((nx, ny))
v = np.zeros((nx, ny))  # Velocity field

# Source parameters
source_x, source_y = nx // 2, ny // 2  # Source location
u[source_x, source_y] = 1.0  # Initial disturbance

# Initialize figure for animation
fig, ax = plt.subplots()
cax = ax.imshow(u, cmap='seismic', vmin=-0.1, vmax=0.1)
fig.colorbar(cax)

# Finite Difference Time Domain (FDTD) solver
def update(frame):
    global u, v
    u_new = np.copy(u)

    # Apply 2D wave equation update
    for i in range(1, nx - 1):
        for j in range(1, ny - 1):
            laplacian = (u[i+1, j] + u[i-1, j] + u[i, j+1] + u[i, j-1] - 4*u[i, j]) / (dx**2)
            v[i, j] += dt * laplacian * vp**2
            u_new[i, j] += dt * v[i, j]

    u[:] = u_new[:]  # Update displacement field
    cax.set_array(u)
    return [cax]

# Animate wave propagation
ani = animation.FuncAnimation(fig, update, frames=nt, interval=50, blit=False)
plt.show()
