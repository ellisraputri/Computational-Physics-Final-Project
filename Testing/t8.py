import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Grid size and time parameters
nx, ny = 100, 100  # Grid resolution
dx = dy = 1.0  # Grid spacing
dt = 0.005  # Time step
nt = 200  # Number of time steps

# Elastic properties (density and Lamé parameters)
rho = 1.0
mu = 1.0   # Shear modulus (controls S-wave speed)
lam = 2.0  # First Lamé parameter (affects P-wave speed)

# Compute P-wave and S-wave velocities
vp = np.sqrt((lam + 2 * mu) / rho)  # P-wave speed
vs = np.sqrt(mu / rho)  # S-wave speed

# Initialize displacement and velocity fields (u_x and u_y for vector waves)
u_x = np.zeros((nx, ny))  # X-component of displacement
u_y = np.zeros((nx, ny))  # Y-component of displacement
v_x = np.zeros((nx, ny))  # X-component of velocity
v_y = np.zeros((nx, ny))  # Y-component of velocity

# Source position (epicenter)
source_x, source_y = nx // 2, ny // 2
u_x[source_x, source_y] = 1.0  # Initial disturbance in x
u_y[source_x, source_y] = 1.0  # Initial disturbance in y

# Initialize figure for animation
fig, ax = plt.subplots()
cax = ax.imshow(np.sqrt(u_x**2 + u_y**2), cmap='seismic', vmin=-0.1, vmax=0.1)
fig.colorbar(cax)

# Finite Difference Method update function
def update(frame):
    global u_x, u_y, v_x, v_y
    u_x_new = np.copy(u_x)
    u_y_new = np.copy(u_y)

    # Loop over grid (ignoring boundaries)
    for i in range(1, nx - 1):
        for j in range(1, ny - 1):
            # Laplacians for u_x and u_y
            laplacian_x = (u_x[i+1, j] + u_x[i-1, j] + u_x[i, j+1] + u_x[i, j-1] - 4*u_x[i, j]) / dx**2
            laplacian_y = (u_y[i+1, j] + u_y[i-1, j] + u_y[i, j+1] + u_y[i, j-1] - 4*u_y[i, j]) / dy**2

            # Update velocity fields using both P-wave and S-wave speeds
            v_x[i, j] += dt * (vp**2 * laplacian_x + vs**2 * laplacian_y)
            v_y[i, j] += dt * (vs**2 * laplacian_x + vp**2 * laplacian_y)

            # Update displacement fields
            u_x_new[i, j] += dt * v_x[i, j]
            u_y_new[i, j] += dt * v_y[i, j]

    # Update arrays
    u_x[:] = u_x_new[:]
    u_y[:] = u_y_new[:]

    # Update visualization (display total wave magnitude)
    cax.set_array(np.sqrt(u_x**2 + u_y**2))
    return [cax]

# Animate wave propagation
ani = animation.FuncAnimation(fig, update, frames=nt, interval=50, blit=False)
plt.show()
