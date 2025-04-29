import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.animation as animation
from scipy.ndimage import gaussian_filter

class SWave():
    def __init__(self, NX, NY, XMIN, XMAX, YMIN, YMAX, t_max, VEL_S):
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
        self.VS = VEL_S
        self.RHO = np.ones((NX, NY)) * 1000.0       #constant
        self.MU = self.RHO * self.VS**2  # Shear modulus

        self.ux = np.zeros((NX, NY))
        self.uy = np.zeros((NX, NY))
        self.ux_prev = np.zeros((NX, NY))
        self.uy_prev = np.zeros((NX, NY)) 
        self.tau_xy = np.zeros((NX, NY)) # shear stress

        ABL_WIDTH = 20 #grid point on simulation area's edge for absorbing
        self.damping = np.ones((NX, NY)) 
        self.damping[:ABL_WIDTH, :] = np.linspace(0.9, 1.0, ABL_WIDTH)[:, np.newaxis]
        self.damping[-ABL_WIDTH:, :] = np.linspace(1.0, 0.9, ABL_WIDTH)[:, np.newaxis]
        self.damping[:, :ABL_WIDTH] = np.minimum(self.damping[:, :ABL_WIDTH], np.linspace(0.9, 1.0, ABL_WIDTH))
        self.damping[:, -ABL_WIDTH:] = np.minimum(self.damping[:, -ABL_WIDTH:], np.linspace(1.0, 0.9, ABL_WIDTH))

    def ricker_wavelet(self,t, f0=15.0):
        return (1.0 - 2.0*(np.pi*f0*t)**2) * np.exp(-(np.pi*f0*t)**2)
    
    def run_wavelet_eq(self):
        self.source_x, self.source_y = self.NX//4, self.NY//2  # Source position
        source_times = np.arange(self.NT) * self.DT # Time values
        self.source_amp = self.ricker_wavelet(source_times - 0.1, f0=15.0) * 1e6  

    def update_wave(self,n):        
        # Add source (vertical force)
        if n < len(self.source_amp):
            self.uy[self.source_x, self.source_y] += self.source_amp[n] * self.DT**2 / self.RHO[self.source_x, self.source_y]
        
        # Calculate spatial derivatives
        dux_dx = np.zeros_like(self.ux)
        dux_dy = np.zeros_like(self.ux)
        duy_dx = np.zeros_like(self.uy)
        duy_dy = np.zeros_like(self.uy)
        
        # Central differences for derivatives
        dux_dx[1:-1, 1:-1] = (self.ux[2:, 1:-1] - self.ux[:-2, 1:-1]) / (2*self.DX)
        dux_dy[1:-1, 1:-1] = (self.ux[1:-1, 2:] - self.ux[1:-1, :-2]) / (2*self.DX)
        duy_dx[1:-1, 1:-1] = (self.uy[2:, 1:-1] - self.uy[:-2, 1:-1]) / (2*self.DX)
        duy_dy[1:-1, 1:-1] = (self.uy[1:-1, 2:] - self.uy[1:-1, :-2]) / (2*self.DX)
        
        tau_xy_now = self.MU * (duy_dx + dux_dy)
        self.tau_xy[:, :] = tau_xy_now
        
        ux_new = np.zeros_like(self.ux)
        uy_new = np.zeros_like(self.uy)
        
        # x-component
        ux_new[1:-1, 1:-1] = (
            2*self.ux[1:-1, 1:-1] - self.ux_prev[1:-1, 1:-1] +
            (self.DT**2 / self.RHO[1:-1, 1:-1]) * (
                (tau_xy_now[1:-1, 2:] - tau_xy_now[1:-1, :-2]) / (2*self.DX)  # ∂τ_xy/∂y
            )
        )
        
        # y-component
        uy_new[1:-1, 1:-1] = (
            2*self.uy[1:-1, 1:-1] - self.uy_prev[1:-1, 1:-1] +
            (self.DT**2 / self.RHO[1:-1, 1:-1]) * (
                (tau_xy_now[2:, 1:-1] - tau_xy_now[:-2, 1:-1]) / (2*self.DX)  # ∂τ_xy/∂x
            )
        )
        
        ux_new *= self.damping
        uy_new *= self.damping
        
        self.ux_prev = self.ux.copy()
        self.uy_prev = self.uy.copy()
        self.ux = ux_new.copy()
        self.uy = uy_new.copy()

    def create_figure_displacement(self):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        self.img1 = ax1.imshow(self.ux.T, extent=[self.XMIN, self.XMAX, self.YMAX, self.YMIN], cmap='seismic', vmin=-1e-6, vmax=1e-6)
        plt.colorbar(self.img1, ax=ax1, label='Horizontal Displacement (m)')
        ax1.set_title("Horizontal Displacement (SV-Wave)")
        ax1.set_xlabel("Distance (m)")
        ax1.set_ylabel("Depth (m)")

        # Vertical displacement plot
        self.img2 = ax2.imshow(self.uy.T, extent=[self.XMIN, self.XMAX, self.YMAX, self.YMIN], cmap='seismic', vmin=-1e-6, vmax=1e-6)
        plt.colorbar(self.img2, ax=ax2, label='Vertical Displacement (m)')
        ax2.set_title("Vertical Displacement (SV-Wave)")
        ax2.set_xlabel("Distance (m)")
        ax2.set_ylabel("Depth (m)")

        ani = FuncAnimation(fig, self.update, frames=self.NT//self.PLOT_EVERY, interval=50, blit=True)
        ffmpeg_writer = animation.FFMpegWriter(fps=20)
        ani.save('test_s_wave1.mp4', writer=ffmpeg_writer)


    def update(self,frame):
        """Update function for animation"""
        for _ in range(self.PLOT_EVERY):
            self.update_wave(frame * self.PLOT_EVERY + _)
        
        current_max = max(np.max(np.abs(self.ux)), np.max(np.abs(self.uy)))
        vlimit = current_max if current_max > 0 else 1e-6
        
        self.img1.set_array(self.ux.T)
        self.img1.set_clim(vmin=-vlimit, vmax=vlimit)
        
        self.img2.set_array(self.uy.T)
        self.img2.set_clim(vmin=-vlimit, vmax=vlimit)
        
        return [self.img1, self.img2]


    def create_figure_stress(self):
        fig, ax = plt.subplots(figsize=(10, 8))
        self.img = ax.imshow(self.tau_xy.T, extent=[self.XMIN, self.XMAX, self.YMAX, self.YMIN], 
                        cmap='seismic', vmin=-1e4, vmax=1e4)

        plt.colorbar(self.img, label='Shear Stress (Pa)', pad=0.01)
        ax.set_title("2D S-Wave Propagation (Shear Stress)", pad=20)
        ax.set_xlabel("Distance (m)")
        ax.set_ylabel("Depth (m)")
        ax.grid(False)

        ani_stress = FuncAnimation(fig, self.update_stress, frames=self.NT//self.PLOT_EVERY, interval=50, blit=True)
        ffmpeg_writer = animation.FFMpegWriter(fps=20)
        ani_stress.save('test_s_wave_stress_2.mp4', writer=ffmpeg_writer)

    def update_stress(self,frame):
        for _ in range(self.PLOT_EVERY):
            self.update_wave(frame * self.PLOT_EVERY + _)
        tau_smoothed = gaussian_filter(self.tau_xy, sigma=1.0)
        self.img.set_array(tau_smoothed.T)
        self.img.set_clim(-np.max(np.abs(tau_smoothed)), np.max(np.abs(tau_smoothed)))  # Auto-scale
        return [self.img]


