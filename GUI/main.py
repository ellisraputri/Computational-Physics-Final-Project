import tkinter as tk
from tkinter import ttk, messagebox

# ===== Materials List =====
materials = [
    "Air", "Water", "Ice", "Oil", "Vegetal Soil", "Dry Sands", "Wet Sands",
    "Saturated Shales and Clays", "Porous and Saturated Sandstones", "Marls",
    "Chalk", "Coal", "Salt", "Anhydrites", "Limestones", "Dolomites",
    "Granite", "Basalt", "Gneiss"
]

# ===== Main Application Class =====
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Main Menu")
        self.geometry("1200x800")
        self.input_window = None
        self.material_window = None
        self.NY_value = 400  # Default NY
        self.has_submit_input = False
        self.has_submit_material = False
        self.material_list =[]

        self.create_widgets()

    def create_widgets(self):
        # Button to open the input window
        open_input_btn = tk.Button(self, text="Open Parameter Input", font="Arial 16", command=self.open_input_window)
        open_input_btn.pack(pady=10)

        # Label to show input submission status
        self.input_status_label = tk.Label(self, text="Input Status: Not Submitted", font="Arial 14", fg="red")
        self.input_status_label.pack(pady=10)

        # Button to open the material window
        open_material_btn = tk.Button(self, text="Open Material Layers", font="Arial 16", command=self.open_material_window)
        open_material_btn.pack(pady=10)

        # Label to show material submission status
        self.material_status_label = tk.Label(self, text="Material Status: Not Submitted", font="Arial 14", fg="red")
        self.material_status_label.pack(pady=10)

    def open_input_window(self):
        if self.input_window is None or not self.input_window.winfo_exists():
            self.input_window = InputWindow(self)
        else:
            messagebox.showerror("Error", "Parameter Input Window is already open.")

    def open_material_window(self):
        # Update NY if InputWindow is opened and submitted
        if self.has_submit_input:
            self.NY_value = self.NY
        else:
            messagebox.showerror("Error", "Please fill in the input window first")
            return

        if self.material_window is None or not self.material_window.winfo_exists():
            self.material_window = MaterialWindow(self, self.NY_value)
        else:
            messagebox.showerror("Error", "Material Window is already open.")

    def update_input_status(self):
        """Update the input submission status."""
        self.has_submit_input = True
        text = f"NX = {self.NX} \nNY = {self.NY} \nXMIN = {self.XMIN} \nXMAX = {self.XMAX} \nYMIN = {self.YMIN} \nYMAX = {self.YMAX} \nt_max = {self.t_max} \ndensity = {self.density}"
        
        self.input_status_label.config(text=f"Input Status: Submitted \n {text} ", fg="green")

    def update_material_status(self):
        """Update the material submission status."""
        self.has_submit_material = True
        text = ""
        print(self.material_list)
        for (fromval, toval, material) in self.material_list:
            text += f"Layer ({fromval} to {toval}): {material}\n"

        self.material_status_label.config(text=f"Material Status: Submitted\n{text}", fg="green")


# ===== Input Window Class =====
class InputFrame(tk.Frame):
    def __init__(self, master, on_submit):
        super().__init__(master)
        self.master = master
        self.on_submit = on_submit
        self.entries = {}
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Insert Parameter", font="Arial 20 bold").grid(row=0, column=0, columnspan=2, pady=20)

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

        for i, (label_text, default_value) in enumerate(fields):
            tk.Label(self, text=label_text, font="Arial 14").grid(row=i+1, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(self, font="Arial 14")
            entry.insert(0, default_value)
            entry.grid(row=i+1, column=1, padx=10, pady=5, sticky="w")
            self.entries[label_text.strip(":").lower()] = entry

        submit_btn = tk.Button(self, text="Submit", font="Arial 14", command=self.submit)
        submit_btn.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)

    def submit(self):
        try:
            self.master.master.NX = int(self.entries["nx"].get())
            self.master.master.NY = int(self.entries["ny"].get())
            self.master.master.XMIN = float(self.entries["xmin"].get())
            self.master.master.XMAX = float(self.entries["xmax"].get())
            self.master.master.YMIN = float(self.entries["ymin"].get())
            self.master.master.YMAX = float(self.entries["ymax"].get())
            self.master.master.t_max = float(self.entries["t_max"].get())
            self.master.master.density = float(self.entries["density"].get())

            print("NX =", self.master.master.NX)
            print("NY =", self.master.master.NY)
            print("XMIN =", self.master.master.XMIN)
            print("XMAX =", self.master.master.XMAX)
            print("YMIN =", self.master.master.YMIN)
            print("YMAX =", self.master.master.YMAX)
            print("t_max =", self.master.master.t_max)
            print("density =", self.master.master.density)

            messagebox.showinfo("Success", "Parameters submitted successfully!")
            self.master.master.update_input_status()  # Update the status in the main app
            self.master.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values.")


class InputWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Seismic Simulation Parameters")
        self.geometry("500x500")
        self.master = master  # Reference to MainApp
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Create the input frame
        self.input_frame = InputFrame(self, self.submit_parameters)
        self.input_frame.pack(fill="both", expand=True)

    def submit_parameters(self, data):
        self.master.NX = data['nx']
        self.master.NY = data['ny']
        self.master.XMIN = data['xmin']
        self.master.XMAX = data['xmax']
        self.master.YMIN = data['ymin']
        self.master.YMAX = data['ymax']
        self.master.t_max = data['t_max']
        self.master.density = data['density']

        self.master.update_input_status()
        self.master.destroy()

    def on_close(self):
        self.destroy()


# ===== Material Window Class =====
class MaterialFrame(tk.Frame):
    def __init__(self, master, NY, on_validate):
        super().__init__(master)
        self.master = master
        self.NY = NY
        self.on_validate = on_validate
        self.rows = []
        self.create_widgets()

    def create_widgets(self):
        container = tk.Frame(self)
        canvas = tk.Canvas(container, height=400)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        container.pack(fill="both", expand=True)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(self.scrollable_frame, text="Velocity Input", font="Arial 16 bold").grid(row=0, column=0, columnspan=3, pady=10)
        tk.Label(self.scrollable_frame, text="From", font="Arial 14 bold").grid(row=1, column=0, padx=30, pady=10)
        tk.Label(self.scrollable_frame, text="To", font="Arial 14 bold").grid(row=1, column=1, padx=30, pady=10)
        tk.Label(self.scrollable_frame, text="Material", font="Arial 14 bold").grid(row=1, column=2, padx=30, pady=10)

        self.add_row()

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        add_btn = tk.Button(button_frame, text="Add Layer", command=self.add_row, font="Arial 14")
        add_btn.grid(row=0, column=0, padx=10)

        validate_btn = tk.Button(button_frame, text="Validate Layers", command=self.validate_and_send, font="Arial 14")
        validate_btn.grid(row=0, column=1, padx=10)

    def validate_and_send(self):
        try:
            maximum_layer = 0
            minimum_layer = self.NY

            for i, (from_entry, to_entry, dropdown) in enumerate(self.rows):
                from_val = int(from_entry.get())
                to_val = int(to_entry.get())
                maximum_layer = max(to_val, maximum_layer)
                minimum_layer = min(from_val, minimum_layer)

                if to_val > self.NY:
                    raise ValueError(f"Row {i+1}: 'To' height ({to_val}) exceeds NY ({self.NY})")

                material = dropdown.get()
                print(f"Layer {i+1}: From {from_val} To {to_val} - {material}")
                self.master.master.material_list.append((from_val, to_val, material))

            if maximum_layer < self.NY or minimum_layer > 0:
                raise ValueError(f"All vertical layer height up to NY must have material specification.")

            messagebox.showinfo("Success", "All layers are valid and printed to console.")
            self.master.master.update_material_status()  # Update the status in the main app
            self.master.destroy()
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
            self.master.master.material_list.clear()

    def add_row(self):
        row = len(self.rows) + 2

        from_entry = tk.Entry(self.scrollable_frame, width=10, font="Arial 14")
        from_entry.grid(row=row, column=0, padx=5, pady=5)

        to_entry = tk.Entry(self.scrollable_frame, width=10, font="Arial 14")
        to_entry.grid(row=row, column=1, padx=5, pady=5)

        material_var = tk.StringVar()
        material_dropdown = ttk.Combobox(self.scrollable_frame, textvariable=material_var, values=materials, state="readonly", font="Arial 14")
        material_dropdown.set(materials[0])
        material_dropdown.grid(row=row, column=2, padx=5, pady=5)

        self.rows.append((from_entry, to_entry, material_dropdown))


class MaterialWindow(tk.Toplevel):
    def __init__(self, master, NY):
        super().__init__(master)
        self.title("Define Material Layers")
        self.geometry("650x500")
        self.master = master  # Reference to MainApp
        self.NY = NY
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Create the material frame
        self.material_frame = MaterialFrame(self, self.NY, self.submit_layers)
        self.material_frame.pack(fill="both", expand=True)

    def submit_layers(self, data):
        self.master.update_material_status()
        self.destroy()

    def on_close(self):
        self.destroy()


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
