from matplotlib import animation
from matplotlib.animation import FuncAnimation
import numpy as np
import matplotlib.pyplot as plt

class Seismogram():
    def __init__(self, NX, NY, XMIN, XMAX, t_max, VEL_P, VEL_S, name):
        self.name =name
        self.NX = NX
        self.NY = NY
        self.XMIN = XMIN
        self.XMAX = XMAX
        self.PLOT_EVERY = 5

        self.DX = (XMAX - XMIN) / NX
        self.DT = 0.001
        self.time = np.arange(0, t_max, self.DT)
        self.NT = len(self.time)
        self.frames = len(self.time) // self.PLOT_EVERY
        self.VEL_P = VEL_P
        self.VEL_S = VEL_S
        self.RHO = np.ones((NX, NY)) * 1000.0

        self.source_x = NX // 4
        self.vp_profile = self.VEL_P[self.source_x, :]
        self.vs_profile = self.VEL_S[self.source_x, :]
        self.rho_profile = self.RHO[self.source_x, :]

    def compute_reflection_coeffs(self, vel_profile, rho_profile):
        rc = []
        for i in range(len(vel_profile) - 1):
            # Skip if either current or next layer has Vs=0 (air/water)
            if vel_profile[i] == 0 or vel_profile[i+1] == 0:
                rc.append(0)  # No reflection
                continue
                
            z1 = rho_profile[i] * vel_profile[i]
            z2 = rho_profile[i+1] * vel_profile[i+1]
            r = (z2 - z1) / (z2 + z1)
            rc.append(r)
        return np.array(rc)
    
    def compute_twt(self, vel_profile, dy):
        twt = [0.0]
        for i in range(1, len(vel_profile)):
            if vel_profile[i] == 0:  # Skip S-wave in air/water
                twt.append(np.inf)   # Infinite travel time (never arrives)
                continue
            avg_v = (vel_profile[i-1] + vel_profile[i]) / 2
            dt_depth = 2 * dy / avg_v
            twt.append(twt[-1] + dt_depth)
        return np.array(twt)
    
    def create_reflectivity_series(self, rc, twt, time, dt):
        series = np.zeros_like(time)
        for i, t in enumerate(twt[:-1]):
            if np.isinf(t):  # Skip if travel time is infinite
                continue
            idx = int(t / dt)
            if 0 <= idx < len(series):
                series[idx] = rc[i]
        return series
    
    def ricker_wavelet(self, t, f0=20.0):
        return (1.0 - 2.0*(np.pi*f0*t)**2) * np.exp(-(np.pi*f0*t)**2)
    
    def compute(self):
        rc_p = self.compute_reflection_coeffs(self.vp_profile, self.rho_profile)
        rc_s = self.compute_reflection_coeffs(self.vs_profile, self.rho_profile)

        twt_p = self.compute_twt(self.vp_profile, self.DX)
        twt_s = self.compute_twt(self.vs_profile, self.DX)

        reflectivity_p = self.create_reflectivity_series(rc_p, twt_p, self.time, self.DT)
        reflectivity_s = self.create_reflectivity_series(rc_s, twt_s, self.time, self.DT)

        f0_p = 20.0
        f0_s = 15.0
        t_wavelet = np.linspace(-0.1, 0.1, int(0.2 / self.DT))
        wavelet_p = self.ricker_wavelet(t_wavelet, f0_p)
        wavelet_s = self.ricker_wavelet(t_wavelet, f0_s)

        self.seismogram_p = np.convolve(reflectivity_p, wavelet_p, mode='same')
        self.seismogram_s = np.convolve(reflectivity_s, wavelet_s, mode='same')
        self.seismogram_s *= 1.5  # Amplify S-wave
        self.seismogram_s = np.roll(self.seismogram_s, int(0.2 / self.DT))  # Phase shift

        self.combined_seismogram = self.seismogram_p + self.seismogram_s
    
    def create_combined_figure(self):
        fig, ax = plt.subplots(figsize=(10, 4))
        self.line, = ax.plot([], [], color='purple', label='Combined Seismogram')
        ax.set_xlim(0, self.time[-1])
        ax.set_ylim(np.min(self.combined_seismogram) * 1.1, np.max(self.combined_seismogram) * 1.1)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        ax.set_title('Seismogram Animation (P + S)')
        ax.grid(True)
        ax.legend()

        ani = FuncAnimation(fig, self.update_combined, frames=self.frames, init_func=self.init_combined, interval=20, blit=True)
        ffmpeg_writer = animation.FFMpegWriter(fps=20)
        ani.save(self.name+'_combined_seismogram.mp4', writer=ffmpeg_writer)

    def init_combined(self):
        self.line.set_data([], [])
        return self.line,

    def update_combined(self,frame):
        idx = min(frame * self.PLOT_EVERY, len(self.time) - 1)  # Ensure we don't exceed array bounds
        self.line.set_data(self.time[:idx], self.combined_seismogram[:idx])
        return self.line,

    def create_separated_figure(self):
        fig, ax = plt.subplots(figsize=(10, 4))
        self.line_p, = ax.plot([], [], color='blue', label='P-wave')
        self.line_s, = ax.plot([], [], color='red', label='S-wave', linestyle='--')

        ax.set_xlim(0, self.time[-1])
        min_val = min(self.seismogram_p.min(), self.seismogram_s.min()) * 1.1
        max_val = max(self.seismogram_p.max(), self.seismogram_s.max()) * 1.1
        ax.set_ylim(min_val, max_val)

        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        ax.set_title('Seismogram Animation (P-wave and S-wave)')
        ax.grid(True)
        ax.legend(loc='lower left')

        ani = FuncAnimation(fig, self.update_separated, frames=self.frames, init_func=self.init_separated, interval=20, blit=True)
        ffmpeg_writer = animation.FFMpegWriter(fps=20)
        ani.save(self.name+'_separated_seismogram.mp4', writer=ffmpeg_writer)

    def init_separated(self):
        self.line_p.set_data([], [])
        self.line_s.set_data([], [])
        return self.line_p, self.line_s

    def update_separated(self,frame):
        idx = min(frame * self.PLOT_EVERY, len(self.time) - 1)
        self.line_p.set_data(self.time[:idx], self.seismogram_p[:idx])
        self.line_s.set_data(self.time[:idx], self.seismogram_s[:idx])
        return self.line_p, self.line_s





