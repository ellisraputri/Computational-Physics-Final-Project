import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Constants
L = 1.0
dx = 0.01
c = 1.0
dt = 1.0 * dx / c  # CFL condition
w= 0.1

# Initialize x and y arrays
x = np.arange(0, L * (1 + dx), dx)
npts = len(x)
nsteps = 200

y = np.zeros((npts, 3))
y[:, 0] = np.sin(2 * np.pi * x / L)  # Initial condition
y[:, 0] = 0.5*np.sin(2 * np.pi * x / L) + 0.5*np.sin(3 * np.pi * x / L)  # Initial condition
y[:, 0] = np.exp(-(x-L/2)**2/w**2)  # Initial condition

y[1:-1, 1] = y[1:-1, 0] + 0.5 * c**2 * (dt / dx) ** 2 * (
    y[2:, 0] + y[:-2, 0] - 2 * y[1:-1, 0]
)

# Set up the figure and axis
fig, ax = plt.subplots()
line, = ax.plot(x, y[:, 0], "b-o")
ax.set_ylim(-1.2, 1.2)
ax.set_title("Wave Equation Simulation")

# Animation update function
def update(frame):
    global y
    y[1:-1, 2] = (
        2 * y[1:-1, 1]
        - y[1:-1, 0]
        + c**2 * (dt / dx) ** 2 * (y[2:, 1] + y[:-2, 1] - 2 * y[1:-1, 1])
    )

    # Shift time steps
    y[:, 0], y[:, 1] = y[:, 1], y[:, 2]

    # Update plot
    line.set_ydata(y[:, 1])
    ax.set_title(f"t={frame * dt:.2f}")
    return line,

# Create animation
ani = animation.FuncAnimation(fig, update, frames=nsteps, interval=10, blit=True)

plt.show()
