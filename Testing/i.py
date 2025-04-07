import numpy as np
import tkinter as tk
from PIL import Image, ImageTk

# Grid size and parameters
nx, ny = 100, 100
dx = dy = 1.0
dt = 0.01
nt = 200  # Number of time steps

# Elastic properties
rho = 1.0
mu = 1.0
lam = 2.0

# Compute wave velocities
vp = np.sqrt((lam + 2 * mu) / rho)
vs = np.sqrt(mu / rho)

# Initialize wave field
u = np.zeros((nx, ny))
v = np.zeros((nx, ny))

# Initialize Tkinter
root = tk.Tk()
root.title("Wave Propagation Simulation")

# Canvas for visualization
canvas = tk.Canvas(root, width=500, height=500, bg="white")
canvas.pack()

# Create an image object
img = tk.PhotoImage(width=nx, height=ny)
image_id = canvas.create_image(0, 0, anchor=tk.NW, image=img)

# Ground level definition
ground_level = 400
scaling_factor = 5  # Scale to fit Tkinter canvas


def update_wave():
    """Update wave propagation and redraw the image."""
    global u, v

    u_new = np.copy(u)

    # Apply wave equation update
    for i in range(1, nx - 1):
        for j in range(1, ny - 1):
            laplacian = (u[i+1, j] + u[i-1, j] + u[i, j+1] + u[i, j-1] - 4*u[i, j]) / (dx**2)
            v[i, j] += dt * laplacian * vp**2
            u_new[i, j] += dt * v[i, j]

    u[:] = u_new[:]

    # Convert wave field to grayscale image
    wave_img = Image.new("L", (nx, ny))
    pixels = wave_img.load()
    
    for i in range(nx):
        for j in range(ny):
            intensity = int(128 + u[i, j] * 255)  # Normalize wave values
            pixels[i, j] = max(0, min(255, intensity))

    # Convert to Tkinter image and update
    wave_img = wave_img.resize((500, 500))  # Scale to fit canvas
    img_tk = ImageTk.PhotoImage(wave_img)
    canvas.itemconfig(image_id, image=img_tk)
    canvas.image = img_tk  # Prevent garbage collection

    # Schedule next update
    root.after(50, update_wave)


def on_click(event):
    """Handle user click and set the wave source."""
    global u

    if event.y > ground_level:
        # Convert Tkinter click to wave grid coordinates
        grid_x = min(nx - 1, max(0, event.x // scaling_factor))
        grid_y = min(ny - 1, max(0, (event.y - ground_level) // scaling_factor))

        # Set wave disturbance at the clicked point
        u[grid_x, grid_y] = 1.0

        # Start the animation if not running
        update_wave()


# Draw ground and bind click event
canvas.create_rectangle(0, ground_level, 500, 500, fill="brown", outline="black")
canvas.bind("<Button-1>", on_click)

# Start Tkinter loop
root.mainloop()
