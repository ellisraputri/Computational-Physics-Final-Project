import numpy as np

class WaveSimulation:
    def __init__(self, grid_size=(100, 100), dx=5.0, dt=0.05):
        self.nx, self.ny = grid_size
        self.dx, self.dy = dx, dx  # Grid spacing (matches pixel size)
        self.dt = dt  # Time step
        
        # Material properties (adjust these for different wave behaviors)
        self.rho = 1.0  # Density
        self.mu = 1.0   # Shear modulus
        self.lam = 2.0  # Second Lamé parameter
        
        # Wave velocities
        self.vp = np.sqrt((self.lam + 2 * self.mu) / self.rho)  # P-wave velocity
        self.vs = np.sqrt(self.mu / self.rho)  # S-wave velocity
        
        # Wave field arrays
        self.u = np.zeros((self.nx, self.ny))  # Displacement
        self.v = np.zeros((self.nx, self.ny))  # Velocity
        self.a = np.zeros((self.nx, self.ny))  # Acceleration
        
        # Damping coefficient (for wave energy dissipation)
        self.damping = 0.01
        
        # Source parameters
        self.source_x = None
        self.source_y = None
        self.source_active = False

    def set_source(self, x, y):
        """Set the source location in pixel coordinates"""
        # Convert pixel coordinates to grid coordinates
        i = int(x / self.dx)
        j = int(y / self.dx)
        
        if 0 <= i < self.nx and 0 <= j < self.ny:
            self.source_x = i
            self.source_y = j
            self.source_active = True
            
            # Add initial disturbance (Gaussian pulse)
            for di in range(-3, 4):
                for dj in range(-3, 4):
                    ni, nj = i + di, j + dj
                    if 0 <= ni < self.nx and 0 <= nj < self.ny:
                        dist = np.sqrt(di**2 + dj**2)
                        self.u[ni, nj] += 10 * np.exp(-dist**2 / 2.0)

    def update_wave(self):
        """Update the wave simulation using finite differences"""
        if not self.source_active:
            return
            
        # Calculate acceleration (wave equation)
        u = self.u
        a = self.a
        
        # Central difference for Laplacian
        a[1:-1, 1:-1] = (self.vp**2) * (
            (u[2:, 1:-1] + u[:-2, 1:-1] - 2*u[1:-1, 1:-1]) / (self.dx**2) +
            (u[1:-1, 2:] + u[1:-1, :-2] - 2*u[1:-1, 1:-1]) / (self.dy**2)
        )
        
        # Update velocity and displacement
        self.v += self.dt * a
        self.u += self.dt * self.v
        
        # Apply damping
        self.v *= (1 - self.damping)
        
        # Apply boundary conditions (simple absorbing boundaries)
        self.u[0, :] = 0
        self.u[-1, :] = 0
        self.u[:, 0] = 0
        self.u[:, -1] = 0