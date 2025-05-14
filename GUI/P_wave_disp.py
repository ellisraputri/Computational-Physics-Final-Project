import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.animation as animation

class PWaveDisplacement:
    def __init__(self, NX, NY, XMIN, XMAX, t_max, VEL_P, name):
        self.name = name
        self.NX = NX
        self.NY = NY
        self.XMIN = XMIN
        self.XMAX = XMAX
        self.PLOT_EVERY = 5

        self.DX = (XMAX - XMIN) / NX
        self.DT = 0.001
        time = np.arange(0, t_max, self.DT)
        self.NT = len(time)
        self.VEL = VEL_P
        self.RHO = np.ones((NX, NY)) * 1000.0       #constant

        self.K = np.ones((NX, NY)) * 5e9  # Higher K → faster P-wave
        self.ux = np.zeros((NX, NY))
        self.uy = np.zeros((NX, NY))
        self.ux_prev = np.zeros((NX, NY))
        self.uy_prev = np.zeros((NX, NY))

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

    def update_p_wave_only(self,n):
        if n < len(self.source_amp):
            self.ux[self.source_x, self.source_y] += self.source_amp[n] * self.DT**2 / self.RHO[self.source_x, self.source_y]

        # ∇·u
        div_u = np.zeros((self.NX, self.NY))
        div_u[1:-1, 1:-1] = (
            (self.ux[2:, 1:-1] - self.ux[:-2, 1:-1]) / (2 * self.DX) + (
            (self.uy[1:-1, 2:] - self.uy[1:-1, :-2]) / (2 * self.DX)
        ))

        # ∇(∇·u)
        grad_div_x = np.zeros((self.NX, self.NY))
        grad_div_y = np.zeros((self.NX, self.NY))
        grad_div_x[1:-1, 1:-1] = (div_u[2:, 1:-1] - div_u[:-2, 1:-1]) / (2 * self.DX)
        grad_div_y[1:-1, 1:-1] = (div_u[1:-1, 2:] - div_u[1:-1, :-2]) / (2 * self.DX)

        ux_new = (
            2 * self.ux - self.ux_prev + (self.DT**2 / self.RHO) * self.K * grad_div_x
        )
        uy_new = (
            2 * self.uy - self.uy_prev + (self.DT**2 / self.RHO) * self.K * grad_div_y
        )

        # Apply damping
        ux_new *= self.damping
        uy_new *= self.damping

        # Update fields
        self.ux_prev = self.ux.copy()
        self.uy_prev = self.uy.copy()
        self.ux = ux_new.copy()
        self.uy = uy_new.copy()
    
    def update(self, frame):
        for _ in range(self.PLOT_EVERY):
            self.update_p_wave_only(frame * self.PLOT_EVERY + _)
        
        self.img.set_array(np.sqrt(self.ux**2 + self.uy**2))
        return [self.img]

    def create_figure(self):
        fig, ax = plt.subplots(figsize=(10, 8))
        self.img = ax.imshow(np.sqrt(self.ux**2 + self.uy**2).T, cmap='seismic', vmin=-1e-5, vmax=1e-5)

        plt.colorbar(self.img, label='Displacement (m)')
        ax.set_title("P Wave Displacement Simulation")
        ax.set_xlabel("Distance (m)")
        ax.set_ylabel("Depth (m)")

        # Create animation
        ani = FuncAnimation(fig, self.update, frames=self.NT // self.PLOT_EVERY, interval=50, blit=True)
        ffmpeg_writer = animation.FFMpegWriter(fps=20)
        ani.save(self.name+'_test_disp_wave1.mp4', writer=ffmpeg_writer)




