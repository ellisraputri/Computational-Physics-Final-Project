from P_wave_disp import PWaveDisplacement
import numpy as np

layers = [
    (0, 400, 1200, 500),        # dry sands
]

NX,NY = 400,400
VEL_P = np.zeros((NX, NY))
VEL_S = np.zeros((NX, NY))
for y_start, y_end, vp, vs in layers:
    VEL_P[:, y_start:y_end] = vp
    VEL_S[:, y_start:y_end] = vs

app = PWaveDisplacement(400, 400, 0, 2000, 900, VEL_P)
app.run_wavelet_eq()
app.create_figure()