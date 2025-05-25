import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from libcomcat.dataframes import get_summary_data_frame
from libcomcat.search import search, get_event_by_id
from datetime import datetime
import netCDF4 as nc
from P_wave_disp import PWaveDisplacement
from P_wave_pressure import PWavePressure
from S_wave import SWave
from seismogram import Seismogram
from show_video import VideoPlayer
from realdata_process import RealDataProcess

# ===== Main Application Class =====
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Main Menu")
        self.geometry("1200x800")

        # Create a container frame for the main layout
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        # Left: Canvas with scrollable frame
        self.canvas = tk.Canvas(container)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="left", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.scrollable_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Right: Info/Instruction frame
        self.right_frame = tk.Frame(container, width=350, bg="white")
        self.right_frame.pack(side="left", fill="y")

        self.info_label = tk.Label(
            self.right_frame,
            text="Welcome to the Seismic Simulation App!\n\n"
                 "Instructions:\n"
                 "- Fill in parameters and materials on the left.\n"
                 "- Use the buttons to run simulations and view results.\n"
                 "- Results and status will be shown here or in pop-up windows.",
            bg="white",
            font="Arial 16",
            wraplength=320,
            justify="left"
        )
        self.info_label.pack(padx=15, pady=15, anchor="n")

        # Initialize the application content
        self.input_window = None
        self.material_window = None
        self.NY_value = 400  # Default NY
        self.has_submit_input = False
        self.has_submit_material = False
        self.material_list = []

        self.create_widgets()

    def create_widgets(self):
        # Add widgets to the scrollable frame
        open_input_btn = tk.Button(self.scrollable_frame, text="Open Parameter Input", font="Arial 16", command=self.open_input_window)
        open_input_btn.pack(pady=10, padx=10, anchor="w")  # Align to the left

        self.input_status_label = tk.Label(self.scrollable_frame, text="Input Status: Not Submitted\n\n\n", font="Arial 14", fg="red", justify="left")
        self.input_status_label.pack(pady=10, padx=10, anchor="w")  # Align to the left

        open_material_btn = tk.Button(self.scrollable_frame, text="Open Material Layers", font="Arial 16", command=self.open_material_window)
        open_material_btn.pack(pady=10, padx=10, anchor="w")  # Align to the left

        self.material_status_label = tk.Label(self.scrollable_frame, text="Material Status: Not Submitted\n\n\n", font="Arial 14", fg="red", justify='left')
        self.material_status_label.pack(pady=10, padx=10, anchor="w")  # Align to the left

        open_pwave_dis_btn = tk.Button(self.scrollable_frame, text="P-wave Displacement Animation", font="Arial 16", command=self.open_Pwave_displacement)
        open_pwave_dis_btn.pack(pady=10, padx=10, anchor="w")  # Align to the left

        open_pwave_pres_btn = tk.Button(self.scrollable_frame, text="P-wave Pressure Animation", font="Arial 16", command=self.open_Pwave_pressure)
        open_pwave_pres_btn.pack(pady=10, padx=10, anchor="w")  # Align to the left

        open_swave_dis_btn = tk.Button(self.scrollable_frame, text="S-wave Displacement Animation", font="Arial 16", command=self.open_Swave_displacement)
        open_swave_dis_btn.pack(pady=10, padx=10, anchor="w")  # Align to the left

        open_swave_pres_btn = tk.Button(self.scrollable_frame, text="S-wave Pressure Animation", font="Arial 16", command=self.open_Swave_pressure)
        open_swave_pres_btn.pack(pady=10, padx=10, anchor="w")  # Align to the left

        open_seis_combined_btn = tk.Button(self.scrollable_frame, text="Seismogram Combined (P+S) Animation", font="Arial 16", command=self.open_seis_combined)
        open_seis_combined_btn.pack(pady=10, padx=10, anchor="w")  # Align to the left

        open_seis_separated_btn = tk.Button(self.scrollable_frame, text="Seismogram Separated (P,S) Animation", font="Arial 16", command=self.open_seis_separated)
        open_seis_separated_btn.pack(pady=10, padx=10, anchor="w")  # Align to the left

    def open_input_window(self):
        if self.has_submit_input: 
            messagebox.showerror("Error", "Input has been submitted")
            return
        
        if self.input_window is None or not self.input_window.winfo_exists():
            self.input_window = InputWindow(self)
        else:
            messagebox.showerror("Error", "Parameter Input Window is already open.")

    def open_material_window(self):
        if self.has_submit_material: 
            messagebox.showerror("Error", "Material parameter has been submitted")
            return

        if not self.has_submit_input:
            messagebox.showerror("Error", "Please fill in the input window first")
            return

        if self.material_window is None or not self.material_window.winfo_exists():
            self.material_window = MaterialWindow(self)
        else:
            messagebox.showerror("Error", "Material Window is already open.")

    def update_input_status(self):
        """Update the input submission status."""
        self.has_submit_input = True
        text = f"NX = {self.NX} \nNY = {self.NY} \nXMIN = {self.XMIN} \nXMAX = {self.XMAX} \nYMIN = {self.YMIN} \nYMAX = {self.YMAX} \nt_max = {self.t_max}"
        
        self.input_status_label.config(text=f"Input Status: Submitted \n {text} ", fg="green")

    def update_material_status(self):
        """Update the material submission status."""
        self.has_submit_material = True
        text = f"Location: {self.data_dict['location']} \nLatitude: {self.data_dict['latitude']} \nLongitude: {self.data_dict['longitude']} \nDepth: {self.data_dict['depth']} \nMagnitude: {self.data_dict['magnitude']}"
        self.material_status_label.config(text=f"Material Status: Submitted\n{text}", fg="green")

        real_data_processing = RealDataProcess(self.data_dict['latitude'], self.data_dict['longitude'], self.NX, self.NY, self.XMIN, self.XMAX, self.YMIN, self.YMAX)
        real_data_processing.process()
        real_data_processing.calculate()
        self.source_x = real_data_processing.source_x
        self.source_y = real_data_processing.source_y
        self.VEL_S = real_data_processing.VEL_S
        self.VEL_P = real_data_processing.VEL_P
        self.RHO = real_data_processing.RHO

    def open_Pwave_displacement(self):
        if not self.has_submit_input or not self.has_submit_material: 
            messagebox.showerror("Error", "Please submit the input and materials first.")
            return

        window = PWaveDisplacement(self.NX, self.NY, self.XMIN, self.XMAX, self.t_max, self.VEL_P, self.RHO, "real",self.source_x, self.source_y)
        window.run_wavelet_eq()
        window.create_figure()

        video_window = VideoPlayer(self, "real_test_disp_wave1.mp4")

    def open_Pwave_pressure(self):
        if not self.has_submit_input or not self.has_submit_material: 
            messagebox.showerror("Error", "Please submit the input and materials first.")
            return

        window = PWavePressure(self.NX, self.NY, self.XMIN, self.XMAX, self.YMIN, self.YMAX, self.t_max, self.VEL_P, self.RHO, "real",self.source_x, self.source_y)
        window.run_wavelet_eq()
        window.create_figure()

        video_window = VideoPlayer(self, "real_test_p_wave1.mp4")
    
    def open_Swave_displacement(self):
        if not self.has_submit_input or not self.has_submit_material: 
            messagebox.showerror("Error", "Please submit the input and materials first.")
            return

        window = SWave(self.NX, self.NY, self.XMIN, self.XMAX, self.YMIN, self.YMAX, self.t_max, self.VEL_S,self.RHO, "real",self.source_x, self.source_y)
        window.run_wavelet_eq()
        window.create_figure_displacement()

        seismic_moment = window.get_seismic_moment()
        magnitude = window.get_moment_magnitude_scale()
        energy = window.get_energy_released()
        self.info_label.config(text=f"Seismic moment = {seismic_moment} \nMagnitude = {magnitude} \nEnergy Released= {energy}")
        print(f"Seismic moment = {seismic_moment} \nMagnitude = {magnitude} \nEnergy Released= {energy}")

        video_window = VideoPlayer(self, "real_test_s_wave1.mp4")

    def open_Swave_pressure(self):
        if not self.has_submit_input or not self.has_submit_material: 
            messagebox.showerror("Error", "Please submit the input and materials first.")
            return

        window = SWave(self.NX, self.NY, self.XMIN, self.XMAX, self.YMIN, self.YMAX, self.t_max, self.VEL_S, self.RHO, "real",self.source_x, self.source_y)
        window.run_wavelet_eq()
        window.create_figure_stress()

        video_window = VideoPlayer(self, "real_test_s_wave_stress_2.mp4")

    def open_seis_combined(self):
        if not self.has_submit_input or not self.has_submit_material: 
            messagebox.showerror("Error", "Please submit the input and materials first.")
            return

        window = Seismogram(self.NX, self.NY, self.XMIN, self.XMAX, self.t_max, self.VEL_P, self.VEL_S, self.RHO, "real",self.source_x)
        window.compute()
        window.create_combined_figure()

        video_window = VideoPlayer(self, "real_combined_seismogram.mp4")

    def open_seis_separated(self):
        if not self.has_submit_input or not self.has_submit_material: 
            messagebox.showerror("Error", "Please submit the input and materials first.")
            return

        window = Seismogram(self.NX, self.NY, self.XMIN, self.XMAX, self.t_max, self.VEL_P, self.VEL_S,self.RHO, "real",self.source_x)
        window.compute()
        window.create_separated_figure()

        video_window = VideoPlayer(self, "real_separated_seismogram.mp4")

    def on_close(self):
        self.destroy()  # This will close all windows and end the mainloop

    



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

            print("NX =", self.master.master.NX)
            print("NY =", self.master.master.NY)
            print("XMIN =", self.master.master.XMIN)
            print("XMAX =", self.master.master.XMAX)
            print("YMIN =", self.master.master.YMIN)
            print("YMAX =", self.master.master.YMAX)
            print("t_max =", self.master.master.t_max)

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
class MaterialWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Material Window")
        self.geometry("800x600")
        self.dataframe = None  # To store the generated dataframe

        self.create_widgets()

    def create_widgets(self):
        # Start datetime input
        tk.Label(self, text="Start Datetime (YYYY-MM-DD HH:MM)").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.start_entry = tk.Entry(self, width=25)
        self.start_entry.grid(row=0, column=1, padx=10, pady=5)

        # End datetime input
        tk.Label(self, text="End Datetime (YYYY-MM-DD HH:MM)").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.end_entry = tk.Entry(self, width=25)
        self.end_entry.grid(row=1, column=1, padx=10, pady=5)

        # Generate button
        generate_btn = tk.Button(self, text="Generate Dataframe", command=self.generate_dataframe)
        generate_btn.grid(row=2, column=0, columnspan=2, pady=10)

        # Frame to hold the Treeview and scrollbars
        tree_frame = tk.Frame(self)
        tree_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Treeview to display the dataframe
        self.tree = ttk.Treeview(tree_frame, columns=("Index", "ID", "Latitude", "Longitude", "Location", "Magnitude"), show="headings")
        self.tree.heading("Index", text="Index")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Latitude", text="Latitude")
        self.tree.heading("Longitude", text="Longitude")
        self.tree.heading("Location", text="Location")
        self.tree.heading("Magnitude", text="Magnitude")
        self.tree.pack(side="left", fill="both", expand=True)

        # Add vertical scrollbar
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        v_scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=v_scrollbar.set)

        # Add horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        h_scrollbar.grid(row=4, column=0, columnspan=2, sticky="ew")
        self.tree.configure(xscrollcommand=h_scrollbar.set)

        # Row selection input
        tk.Label(self, text="Enter Row Index:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.row_entry = tk.Entry(self, width=10)
        self.row_entry.grid(row=5, column=1, padx=10, pady=5, sticky="w")

        # Select button
        select_btn = tk.Button(self, text="Select Row", command=self.select_row)
        select_btn.grid(row=6, column=0, columnspan=2, pady=10)

        # Configure grid weights
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def generate_dataframe(self):
        """Generate the dataframe based on the input datetimes."""
        try:
            # Parse the start and end datetimes
            start_datetime = datetime.strptime(self.start_entry.get(), "%Y-%m-%d %H:%M")
            end_datetime = datetime.strptime(self.end_entry.get(), "%Y-%m-%d %H:%M")

            # Generate the dataframe
            summary_events = search(starttime=start_datetime, endtime=end_datetime)
            self.dataframe = get_summary_data_frame(summary_events)

            # Clear the Treeview
            for row in self.tree.get_children():
                self.tree.delete(row)

            # Populate the Treeview with the dataframe
            for index, row in self.dataframe.iterrows():
                self.tree.insert("", "end", values=(index, row["id"], row["latitude"], row["longitude"], row["location"], row["magnitude"]))

        except ValueError:
            messagebox.showerror("Error", "Invalid datetime format. Please use YYYY-MM-DD HH:MM.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def select_row(self):
        """Handle row selection based on user input."""
        try:
            # Get the selected row index
            row_index = int(self.row_entry.get())
            if self.dataframe is None:
                raise ValueError("No dataframe generated yet.")

            # Get the row data
            selected_row = self.dataframe.iloc[row_index]
            self.master.data_dict = selected_row.to_dict()
            messagebox.showinfo("Row Selected", f"Selected Row:\n{selected_row.to_dict()}")
            self.master.update_material_status()
            self.destroy()

        except ValueError:
            messagebox.showerror("Error", "Invalid row index.")
        except IndexError:
            messagebox.showerror("Error", "Row index out of range.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")



if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
