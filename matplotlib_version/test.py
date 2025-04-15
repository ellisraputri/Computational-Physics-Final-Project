from matplotlib.animation import FuncAnimation
import numpy as np
import matplotlib.pyplot as plt

# --- Grid and Sampling Parameters ---
NX, NY = 200, 200
XMIN, XMAX = 0.0, 2000.0
YMIN, YMAX = 0.0, 2000.0
DX = (XMAX - XMIN) / NX
DT = 0.001
t_max = 2.0
time = np.arange(0, t_max, DT)
NT = len(time)
PLOT_EVERY = 5  # Plot every N steps

# --- Define Velocity Models ---
VEL_P = np.ones((NX, NY)) * 2000.0
VEL_P[:, 70:120] = 2500.0
VEL_P[:, 120:160] = 3000.0

# S-wave velocity is typically Vp / 1.732
VEL_S = VEL_P / 1.732

# --- Constant Density Model ---
RHO = np.ones((NX, NY)) * 2200.0

# --- Extract 1D Profiles at Source ---
source_x = NX // 2
vp_profile = VEL_P[source_x, :]
vs_profile = VEL_S[source_x, :]
rho_profile = RHO[source_x, :]

# --- Reflection Coefficients ---
def compute_reflection_coeffs(vel_profile, rho_profile):
    rc = []
    for i in range(len(vel_profile) - 1):
        z1 = rho_profile[i] * vel_profile[i]
        z2 = rho_profile[i+1] * vel_profile[i+1]
        r = (z2 - z1) / (z2 + z1)
        rc.append(r)
    return np.array(rc)

rc_p = compute_reflection_coeffs(vp_profile, rho_profile)
rc_s = compute_reflection_coeffs(vs_profile, rho_profile)

# --- Two-way Travel Times ---
def compute_twt(vel_profile, dy):
    twt = [0.0]
    for i in range(1, len(vel_profile)):
        avg_v = (vel_profile[i-1] + vel_profile[i]) / 2
        dt_depth = 2 * dy / avg_v
        twt.append(twt[-1] + dt_depth)
    return np.array(twt)

twt_p = compute_twt(vp_profile, DX)
twt_s = compute_twt(vs_profile, DX)

# --- Reflectivity Series ---
def create_reflectivity_series(rc, twt, time, dt):
    series = np.zeros_like(time)
    for i, t in enumerate(twt[:-1]):
        idx = int(t / dt)
        if idx < len(series):
            series[idx] = rc[i]
    return series

reflectivity_p = create_reflectivity_series(rc_p, twt_p, time, DT)
reflectivity_s = create_reflectivity_series(rc_s, twt_s, time, DT)

# --- Ricker Wavelet ---
def ricker_wavelet(t, f0=20.0):
    return (1.0 - 2.0*(np.pi*f0*t)**2) * np.exp(-(np.pi*f0*t)**2)

f0 = 20.0
t_wavelet = np.linspace(-0.1, 0.1, int(0.2 / DT))
wavelet = ricker_wavelet(t_wavelet, f0)

# --- Convolution to Create Seismograms ---
seismogram_p = np.convolve(reflectivity_p, wavelet, mode='same')
seismogram_s = np.convolve(reflectivity_s, wavelet, mode='same')

# # --- Plot Both on One Chart ---
# plt.figure(figsize=(12, 5))
# plt.plot(time, seismogram_p, label="P-wave Seismogram", color='blue')
# plt.plot(time, seismogram_s, label="S-wave Seismogram", color='red', linestyle='--')
# plt.xlabel("Time (s)")
# plt.ylabel("Amplitude")
# plt.title("1D Synthetic Seismograms (P-wave and S-wave)")
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.show()


combined_seismogram = seismogram_p + seismogram_s

# Prepare figure and line object
fig, ax = plt.subplots(figsize=(10, 4))
line, = ax.plot([], [], color='purple', label='Combined Seismogram')
ax.set_xlim(0, time[-1])
ax.set_ylim(np.min(combined_seismogram) * 1.1, np.max(combined_seismogram) * 1.1)
ax.set_xlabel('Time (s)')
ax.set_ylabel('Amplitude')
ax.set_title('Seismogram Animation (P + S)')
ax.grid(True)
ax.legend()

# Total frames
frames = NT // PLOT_EVERY

# Initialization function
def init():
    line.set_data([], [])
    return line,

# Update function for each frame
def update(frame):
    idx = frame * PLOT_EVERY
    line.set_data(time[:idx], combined_seismogram[:idx])
    return line,

# Create animation
ani = FuncAnimation(fig, update, frames=frames, init_func=init, interval=50, blit=True)

plt.tight_layout()
plt.show()
