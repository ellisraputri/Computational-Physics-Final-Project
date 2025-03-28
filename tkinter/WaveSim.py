import tkinter as tk

class WaveSimulator(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.master = parent
        self.ground_level = 489
        self.submitted = False
        self.play = False
        self.create_widgets()
    
    def ground_click(self, event):
        if event.y > self.ground_level and not self.submitted:  
            self.x_entry.delete(0, tk.END)
            self.y_entry.delete(0, tk.END)
            self.x_entry.insert(0, str(event.x))
            self.y_entry.insert(0, str(event.y))

            self.canvas.delete("marker")
            self.canvas.create_oval(event.x - 8, event.y - 8, event.x + 8, event.y + 8, 
                                    fill="white", outline="white", tags='marker')

    def create_widgets(self):
        self.canvas = tk.Canvas(self, width=1000, height=768, bg="lightblue")
        self.canvas.place(x=0, y=0)
        self.canvas.create_rectangle(0, 489, 1000, 489+279, fill="saddlebrown", outline="")
        self.canvas.bind("<Button-1>", self.ground_click)

        self.right_panel = tk.Frame(self, width=360, height=781, bg="white")
        self.right_panel.place(x=1000, y=0)

        title_label = tk.Label(self.right_panel, text="User Input", font=("Poppins", 24, "bold"), bg="white")
        title_label.place(x=91, y=17)

        input_label = tk.Label(self.right_panel, text="Choose a hypocenter:", font=("Poppins", 14), bg="white")
        input_label.place(x=23, y=101)

        x_label = tk.Label(self.right_panel, text="x:", font=("Poppins", 14), bg="white")
        x_label.place(x=23, y=148)

        self.x_entry = tk.Entry(self.right_panel, width=5, font=("Poppins", 14),
                                bd=0, highlightbackground='grey',highlightthickness=1)
        self.x_entry.place(x=48, y=144)

        y_label = tk.Label(self.right_panel, text="y:", font=("Poppins", 14), bg="white")
        y_label.place(x=133, y=148)

        self.y_entry = tk.Entry(self.right_panel, width=5, font=("Poppins", 14),
                                bd=0, highlightbackground='grey',highlightthickness=1)
        self.y_entry.place(x=160, y=144)

        self.submit_button = tk.Button(self.right_panel, text="Save", font=("Poppins", 12),
                                       bd=0, command=self.toggle_submit)
        self.submit_button.place(x=253, y=144)


    def toggle_submit(self):
        if not self.submitted: 
            self.submitted = True
            self.submit_button.config(text="Cancel")

            self.x_label_value = tk.Label(self.right_panel, text=self.x_entry.get(), font=("Poppins", 14), bg="white")
            self.y_label_value = tk.Label(self.right_panel, text=self.y_entry.get(), font=("Poppins", 14), bg="white")

            self.x_label_value.place(x=48, y=144)
            self.y_label_value.place(x=160, y=144)

            self.x_entry.place_forget()
            self.y_entry.place_forget()

            self.canvas.delete("marker")
            x, y = int(self.x_label_value.cget("text")), int(self.y_label_value.cget("text"))
            self.canvas.create_line(x - 8, y - 8, x + 8, y + 8, fill="red", width=4, tags="marker")
            self.canvas.create_line(x + 8, y - 8, x - 8, y + 8, fill="red", width=4, tags="marker")

        else:  
            self.submitted = False
            self.submit_button.config(text="Submit")

            self.x_label_value.destroy()
            self.y_label_value.destroy()
            
            self.x_entry.place(x=48, y=144)
            self.y_entry.place(x=160, y=144)
            self.x_entry.delete(0, tk.END)
            self.y_entry.delete(0, tk.END)

            self.canvas.delete("marker")


    def toggle_play(self):
        if not self.play: 
            self.play = True
            self.submit_button.config(text="Cancel")

            self.x_label_value = tk.Label(self.right_panel, text=self.x_entry.get(), font=("Poppins", 14), bg="white")
            self.y_label_value = tk.Label(self.right_panel, text=self.y_entry.get(), font=("Poppins", 14), bg="white")

            self.x_label_value.place(x=48, y=144)
            self.y_label_value.place(x=160, y=144)

            self.x_entry.place_forget()
            self.y_entry.place_forget()

            self.canvas.delete("marker")
            x, y = int(self.x_label_value.cget("text")), int(self.y_label_value.cget("text"))
            self.canvas.create_line(x - 8, y - 8, x + 8, y + 8, fill="red", width=4, tags="marker")
            self.canvas.create_line(x + 8, y - 8, x - 8, y + 8, fill="red", width=4, tags="marker")

        else:  
            self.submitted = False
            self.submit_button.config(text="Submit")

            self.x_label_value.destroy()
            self.y_label_value.destroy()
            
            self.x_entry.place(x=48, y=144)
            self.y_entry.place(x=160, y=144)
            self.x_entry.delete(0, tk.END)
            self.y_entry.delete(0, tk.END)

            self.canvas.delete("marker")
    

       