import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Grid size and time parameters
nx, ny = 100, 100  # Grid resolution
dx = dy = 1.0  # Grid spacing
dt = 0.005  # Time step
nt = 200  # Number of time steps

# Elastic properties
rho = 1.0
mu = 1.0   # Shear modulus (S-wave)
lam = 2.0  # First Lamé parameter (P-wave)

# Compute P-wave and S-wave speeds
vp = np.sqrt((lam + 2 * mu) / rho)
vs = np.sqrt(mu / rho)

# Initialize displacement and velocity fields
u_x = np.zeros((nx, ny))  # X-displacement
u_y = np.zeros((nx, ny))  # Y-displacement
v_x = np.zeros((nx, ny))  # X-velocity
v_y = np.zeros((nx, ny))  # Y-velocity

# Define source location (epicenter)
source_x, source_y = nx // 2, ny // 2
u_x[source_x, source_y] = 1.0
u_y[source_x, source_y] = 1.0

# Define seismometer location (e.g., at bottom-right corner)
seismo_x, seismo_y = 48, 48
seismogram = []

# Initialize figure for wave animation
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 8))

# Wave propagation plot
cax = ax1.imshow(np.sqrt(u_x**2 + u_y**2), cmap='seismic', vmin=-0.1, vmax=0.1)
ax1.set_title("Wave Propagation")
fig.colorbar(cax, ax=ax1)

# Seismogram plot
seismo_line, = ax2.plot([], [], color='black')
ax2.set_xlim(0, nt)
ax2.set_ylim(-0.1, 0.1)
ax2.set_title("Seismogram at ({} , {})".format(seismo_x, seismo_y))
ax2.set_xlabel("Time Step")
ax2.set_ylabel("Displacement")

# Finite Difference Method update function
def update(frame):
    global u_x, u_y, v_x, v_y

    u_x_new = np.copy(u_x)
    u_y_new = np.copy(u_y)

    # Loop over grid (ignoring boundaries)
    for i in range(1, nx - 1):
        for j in range(1, ny - 1):
            laplacian_x = (u_x[i+1, j] + u_x[i-1, j] + u_x[i, j+1] + u_x[i, j-1] - 4*u_x[i, j]) / dx**2
            laplacian_y = (u_y[i+1, j] + u_y[i-1, j] + u_y[i, j+1] + u_y[i, j-1] - 4*u_y[i, j]) / dy**2

            # Update velocity fields
            v_x[i, j] += dt * (vp**2 * laplacian_x + vs**2 * laplacian_y)
            v_y[i, j] += dt * (vs**2 * laplacian_x + vp**2 * laplacian_y)

            # Update displacement fields
            u_x_new[i, j] += dt * v_x[i, j]
            u_y_new[i, j] += dt * v_y[i, j]

    u_x[:] = u_x_new[:]
    u_y[:] = u_y_new[:]

    # Record seismogram data
    seismogram.append(u_x[seismo_x, seismo_y])

    # Update wave visualization
    cax.set_array(np.sqrt(u_x**2 + u_y**2))

    # Update seismogram plot
    seismo_line.set_data(range(len(seismogram)), seismogram)

    return [cax, seismo_line]

# Animate simulation
ani = animation.FuncAnimation(fig, update, frames=nt, interval=50, blit=False)
plt.show()
