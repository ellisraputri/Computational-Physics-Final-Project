import numpy as np
import matplotlib.pyplot as plt

# Earthquake parameters
Depth = 85  # Depth in km
Vp, Vs = 6.5, 3.5  # P-wave & S-wave velocities (km/s)
D = 500  # Approximate source-to-station distance (km)

# Compute travel times
Tp, Ts = np.hypot(D, Depth) / Vp, np.hypot(D, Depth) / Vs

# Time axis (faster computation)
time = np.linspace(0, 60, 1000)  # 60 seconds, 1000 points

# Generate simple P-wave and S-wave
p_wave = np.sin(10 * (time - Tp)) * (time > Tp)
s_wave = np.sin(5 * (time - Ts)) * (time > Ts)

# Plot
plt.plot(time, p_wave, label="P-wave", color='blue')
plt.plot(time, s_wave, label="S-wave", color='red')
plt.axvline(Tp, linestyle="--", color="blue", label=f"P-wave {Tp:.1f}s")
plt.axvline(Ts, linestyle="--", color="red", label=f"S-wave {Ts:.1f}s")
plt.legend()
plt.show()
