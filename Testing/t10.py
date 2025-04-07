import numpy as np
import matplotlib.pyplot as plt

# PARAMETERS
D = 100  # Distance from source to station (km)
Vp = 6.0  # P-wave velocity (km/s)
Vs = 3.5  # S-wave velocity (km/s)
freq_p = 2  # P-wave dominant frequency (Hz)
freq_s = 1  # S-wave dominant frequency (Hz)
attenuation = 0.02  # Attenuation factor
time = np.linspace(0, 50, 1000)  # Time axis (seconds)

# ARRIVAL TIMES
Tp = D / Vp  # P-wave arrival time
Ts = D / Vs  # S-wave arrival time

# SYNTHETIC WAVEFORMS
p_wave = np.exp(-attenuation * (time - Tp)) * np.sin(2 * np.pi * freq_p * (time - Tp)) * (time > Tp)
s_wave = np.exp(-attenuation * (time - Ts)) * np.sin(2 * np.pi * freq_s * (time - Ts)) * (time > Ts)

# PLOT SEISMOGRAM
plt.figure(figsize=(10, 4))
plt.plot(time, p_wave, label="P-wave", color='blue')
plt.plot(time, s_wave, label="S-wave", color='red')
plt.axvline(Tp, linestyle="--", color="blue", label="P-wave Arrival")
plt.axvline(Ts, linestyle="--", color="red", label="S-wave Arrival")
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")
plt.legend()
plt.title("Synthetic P-wave and S-wave Seismogram")
plt.grid()
plt.show()
