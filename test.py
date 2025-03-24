import tkinter as tk

def on_click(event):
    if event.y > ground_level: 
        label.config(text=f"Underground Click: x={event.x}, y={event.y}")
        canvas.delete("dot")
        canvas.create_oval(event.x - 8, event.y - 8, event.x + 8, event.y + 8, fill="red", outline="red", tags='dot')


root = tk.Tk()
root.title("Above and Underground Click Detector")
root.geometry("800x780")

ground_level = 400  

canvas = tk.Canvas(root, width=800, height=700, bg="skyblue")
canvas.pack()

canvas.create_rectangle(0, ground_level, 800, 700, fill="brown", outline="black")
canvas.create_line(0, ground_level, 800, ground_level, width=3)

label = tk.Label(root, text="Click in the underground area", font=("Arial", 12))
label.pack()
canvas.bind("<Button-1>", on_click)


root.mainloop()
