import tkinter as tk
from tkinter import ttk, messagebox

# List of materials
materials = [
    "Air", "Water", "Ice", "Oil", "Vegetal Soil", "Dry Sands", "Wet Sands",
    "Saturated Shales and Clays", "Porous and Saturated Sandstones", "Marls",
    "Chalk", "Coal", "Salt", "Anhydrites", "Limestones", "Dolomites",
    "Granite", "Basalt", "Gneiss"
]

opened_material_window =False

# Main submit function
def submit():
    global opened_material_window

    if(opened_material_window):
        messagebox.showerror("Error", "Material window is already opened")
        return

    try:
        global NY
        NX = int(entry_nx.get())
        NY = int(entry_ny.get())
        XMIN = float(entry_xmin.get())
        XMAX = float(entry_xmax.get())
        YMIN = float(entry_ymin.get())
        YMAX = float(entry_ymax.get())
        t_max = float(entry_tmax.get())
        density = float(entry_density.get())

        print("NX =", NX)
        print("NY =", NY)
        print("XMIN =", XMIN)
        print("XMAX =", XMAX)
        print("YMIN =", YMIN)
        print("YMAX =", YMAX)
        print("t_max =", t_max)
        print("density =", density)

        messagebox.showinfo("Success", "Parameters submitted successfully!")
        opened_material_window = True

        open_material_window()

    except ValueError:
        messagebox.showerror("Error", "Please enter valid numeric values.")

# Function to open a new window for materials
def open_material_window():
    material_window = tk.Toplevel(root)
    material_window.title("Define Material Layers")
    material_window.geometry("650x500")

    # ===== Scrollable Canvas Setup =====
    container = tk.Frame(material_window)
    canvas = tk.Canvas(container, height=400)
    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    container.pack(fill="both", expand=True)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ===== Title and Headers =====
    tk.Label(scrollable_frame, text="Velocity Input", font="Arial 16 bold").grid(row=0, column=0, columnspan=3, pady=10)

    tk.Label(scrollable_frame, text="From", font="Arial 14 bold").grid(row=1, column=0, padx=30, pady=10)
    tk.Label(scrollable_frame, text="To", font="Arial 14 bold").grid(row=1, column=1, padx=30, pady=10)
    tk.Label(scrollable_frame, text="Material", font="Arial 14 bold").grid(row=1, column=2, padx=30, pady=10)

    rows = []

    def add_row():
        row = len(rows) + 2

        from_entry = tk.Entry(scrollable_frame, width=10, font="Arial 14")
        from_entry.grid(row=row, column=0, padx=5, pady=5)

        to_entry = tk.Entry(scrollable_frame, width=10, font="Arial 14")
        to_entry.grid(row=row, column=1, padx=5, pady=5)

        material_var = tk.StringVar()
        material_dropdown = ttk.Combobox(scrollable_frame, textvariable=material_var, values=materials, state="readonly", font="Arial 14")
        material_dropdown.set(materials[0])
        material_dropdown.grid(row=row, column=2, padx=5, pady=5)

        rows.append((from_entry, to_entry, material_dropdown))

    def validate_and_print():
        try:
            for i, (from_entry, to_entry, dropdown) in enumerate(rows):
                from_val = int(from_entry.get())
                to_val = int(to_entry.get())

                if to_val > NY:
                    raise ValueError(f"Row {i+1}: 'To' height ({to_val}) exceeds NY ({NY})")

                material = dropdown.get()
                print(f"Layer {i+1}: From {from_val} To {to_val} - {material}")

            messagebox.showinfo("Success", "All layers are valid and printed to console.")
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))

    # Initial row
    add_row()

    # Buttons (outside scrollable area)
    button_frame = tk.Frame(material_window)
    button_frame.pack(pady=10)

    add_btn = tk.Button(button_frame, text="Add Layer", command=add_row, font="Arial 14")
    add_btn.grid(row=0, column=0, padx=10)

    submit_layers_btn = tk.Button(button_frame, text="Validate Layers", command=validate_and_print, font="Arial 14")
    submit_layers_btn.grid(row=0, column=1, padx=10)

    def on_close():
        global opened_material_window
        opened_material_window = False
        material_window.destroy()

    material_window.protocol("WM_DELETE_WINDOW", on_close)

# ==== MAIN GUI ====
root = tk.Tk()
root.title("Seismic Simulation Parameters")
root.geometry("500x500")

tk.Label(root, text="Insert Parameter", font="Arial 20 bold").grid(row=0, column=0, columnspan=2, pady=20)

# Define labels and entries
fields = [
    ("NX:", "200"),
    ("NY:", "400"),
    ("XMIN:", "0.0"),
    ("XMAX:", "2000.0"),
    ("YMIN:", "0.0"),
    ("YMAX:", "4000.0"),
    ("t_max:", "4.0"),
    ("Density:", "2200"),
]

entries = {}

for i, (label_text, default_value) in enumerate(fields):
    tk.Label(root, text=label_text, font="Arial 14").grid(row=i+1, column=0, padx=10, pady=5, sticky="e")
    entry = tk.Entry(root, font="Arial 14")
    entry.insert(0, default_value)
    entry.grid(row=i+1, column=1, padx=10, pady=5, sticky="w")
    entries[label_text.strip(":").lower()] = entry

# Access entries
entry_nx = entries["nx"]
entry_ny = entries["ny"]
entry_xmin = entries["xmin"]
entry_xmax = entries["xmax"]
entry_ymin = entries["ymin"]
entry_ymax = entries["ymax"]
entry_tmax = entries["t_max"]
entry_density = entries["density"]

# Submit button
submit_btn = tk.Button(root, text="Submit", font="Arial 14", command=submit)
submit_btn.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)

root.mainloop()
