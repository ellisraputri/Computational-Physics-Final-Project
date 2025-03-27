import tkinter as tk
from WaveSim import WaveSimulator

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry('1360x768')
        self.title('Earthquake Simulator')
        self.configure(bg='white')

        self.center_window()
        self.wave_simulator_page = WaveSimulator(self)

        self.show_frame(self.wave_simulator_page)


    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width // 2) - (1360 // 2)
        y = (screen_height // 2) - (768 // 2)
        self.geometry(f'1360x768+{x}+{y}')
    

    def show_frame(self, frame):
        for widget in self.winfo_children():  
            widget.pack_forget()
        frame.pack(fill='both', expand=True)        


if __name__ == "__main__":
    app = App()
    app.resizable(False,False)
    app.mainloop()