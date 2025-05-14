import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.animation as animation

class PWavePressure():
    def __init__(self, NX, NY, XMIN, XMAX, YMIN, YMAX, t_max, VEL_P, name):
        self.name = name
        self.NX = NX
        self.NY = NY
        self.XMIN = XMIN
        self.XMAX = XMAX
        self.YMIN = YMIN
        self.YMAX = YMAX
        self.PLOT_EVERY = 5

        self.DX = (XMAX - XMIN) / NX
        self.DT = 0.001
        time = np.arange(0, t_max, self.DT)
        self.NT = len(time)
        self.VEL = VEL_P
        self.RHO = np.ones((NX, NY)) * 1000.0       #constant

        self.phi = np.zeros((NX, NY))  # Pressure field (current)
        self.psi = np.zeros((NX, NY))  # Pressure field (previous)
        self.vx = np.zeros((NX, NY))  # x-component of particle velocity
        self.vy = np.zeros((NX, NY))  # y-component of particle velocity

        ABL_WIDTH = 20 #grid point on simulation area's edge for absorbing
        self.damping = np.ones((NX, NY)) 
        self.damping[:ABL_WIDTH, :] = np.linspace(0.9, 1.0, ABL_WIDTH)[:, np.newaxis]
        self.damping[-ABL_WIDTH:, :] = np.linspace(1.0, 0.9, ABL_WIDTH)[:, np.newaxis]

        # preserve the strongest self.damping when overlapping in left and right edge
        self.damping[:, :ABL_WIDTH] = np.minimum(self.damping[:, :ABL_WIDTH], np.linspace(0.9, 1.0, ABL_WIDTH))
        self.damping[:, -ABL_WIDTH:] = np.minimum(self.damping[:, -ABL_WIDTH:], np.linspace(1.0, 0.9, ABL_WIDTH))


    def ricker_wavelet(self, t, f0=20.0):
        return (1.0 - 2.0*(np.pi*f0*t)**2) * np.exp(-(np.pi*f0*t)**2)
    
    def run_wavelet_eq(self):
        self.source_x, self.source_y = self.NX//4, self.NY//2  # Source position
        source_times = np.arange(self.NT) * self.DT # Time values
        self.source_amp = self.ricker_wavelet(source_times - 0.1, f0=20.0) * 1e6  

    def update_wave(self,n):
        if n < len(self.source_amp):
            self.phi[self.source_x, self.source_y] += self.source_amp[n]
        
        # Update particle velocities (vx, vy)
        # vx[1:-1, 1:-1] -= (DT/RHO[1:-1, 1:-1]) * (phi[2:, 1:-1] - phi[:-2, 1:-1]) / (2*DX)
        # vy[1:-1, 1:-1] -= (DT/RHO[1:-1, 1:-1]) * (phi[1:-1, 2:] - phi[1:-1, :-2]) / (2*DX)
        
        # Update pressure field based on the final p_{i,j}^{n+1} formula
        phi_new = self.phi.copy()
        phi_new[1:-1, 1:-1] = (
            2*self.phi[1:-1, 1:-1] - self.psi[1:-1, 1:-1] +
            (self.VEL[1:-1, 1:-1]**2 * self.DT**2 / self.DX**2) * (
                
                self.phi[2:, 1:-1] + self.phi[:-2, 1:-1] +
                self.phi[1:-1, 2:] + self.phi[1:-1, :-2] -
                4*self.phi[1:-1, 1:-1]
            )
        )
        # apply damping
        phi_new *= self.damping

        # Update fields
        self.psi = self.phi.copy()
        self.phi = phi_new.copy()
    
    def update(self,frame):
        """Update function for animation"""
        for _ in range(self.PLOT_EVERY):
            self.update_wave(frame * self.PLOT_EVERY + _)
        
        self.img.set_array(self.phi.T)
        return [self.img]

    def create_figure(self):
        fig, ax = plt.subplots(figsize=(10, 8))
        self.img = ax.imshow(self.phi.T, extent=[self.XMIN, self.XMAX, self.YMAX, self.YMIN], cmap='seismic', vmin=-1e4, vmax=1e4)
        plt.colorbar(self.img, label='Pressure (Pa)')
        ax.set_title("2D Seismic Wave Propagation")
        ax.set_xlabel("Distance (m)")
        ax.set_ylabel("Depth (m)")

        ani = FuncAnimation(fig, self.update, frames=self.NT//self.PLOT_EVERY, interval=50, blit=True)
        ffmpeg_writer = animation.FFMpegWriter(fps=20)
        ani.save(self.name+'_test_p_wave1.mp4', writer=ffmpeg_writer)

