import tkinter as tk
from tkinter import Label, Button
import cv2
from PIL import Image, ImageTk

class VideoPlayer(tk.Toplevel):
    def __init__(self, parent, video_path):
        super().__init__(parent)
        self.title("Tkinter Video Player")
        self.video_path = video_path
        self.cap = cv2.VideoCapture(self.video_path)

        if not self.cap.isOpened():
            print("Error: Cannot open video.")
            self.destroy()
            return

        self.video_width  = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.video_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.geometry(f"{self.video_width + 180}x{self.video_height + 90}")
        self.is_playing = False

        # Main container (horizontal layout)
        main_frame = tk.Frame(self)
        main_frame.pack()

        # Left: Video Display
        self.label = Label(main_frame)
        self.label.pack(side="left")

        # Right: Control Buttons
        control_frame = tk.Frame(main_frame)
        control_frame.pack(side="left", padx=10)

        self.play_btn = Button(control_frame, text="Play", command=self.play_video, font="Arial 14", width=10)
        self.play_btn.pack(pady=5)

        self.pause_btn = Button(control_frame, text="Pause", command=self.pause_video, font="Arial 14", width=10)
        self.pause_btn.pack(pady=5)

        self.reset_btn = Button(control_frame, text="Reset", command=self.reset_video, font="Arial 14", width=10)
        self.reset_btn.pack(pady=5)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def play_video(self):
        if not self.is_playing:
            self.is_playing = True
            self.update_video()

    def pause_video(self):
        self.is_playing = False

    def reset_video(self):
        self.is_playing = False
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to frame 0
        self.update_frame()  # Show first frame

    def update_video(self):
        if self.is_playing:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)

                self.label.imgtk = imgtk
                self.label.configure(image=imgtk)

                self.after(30, self.update_video)  # ~33 FPS
            else:
                print("Video ended.")
                self.is_playing = False

    def update_frame(self):
        # Display a single frame (for reset)
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)

    def on_closing(self):
        self.is_playing = False
        if self.cap.isOpened():
            self.cap.release()
        self.destroy()




    

