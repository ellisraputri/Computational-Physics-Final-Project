import tkinter as tk
from tkinter import Label, Button, Canvas, Scrollbar
import cv2
from PIL import Image, ImageTk

# ...existing imports...

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

        # Thresholds for switching layout
        width_threshold = 1200
        height_threshold = 800

        self.is_playing = False

        # Main container
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        if self.video_width > width_threshold or self.video_height > height_threshold:
            # --- LARGE VIDEO: video and controls scroll together ---
            # Set window size to show a portion of the video (with scrollbars)
            window_width = min(self.video_width, 1000)
            window_height = min(self.video_height, 800)
            self.geometry(f"{window_width + 50}x{window_height + 150}")

            # Create a canvas with scrollbars
            video_canvas = Canvas(main_frame)
            h_scrollbar = Scrollbar(main_frame, orient="horizontal", command=video_canvas.xview)
            v_scrollbar = Scrollbar(main_frame, orient="vertical", command=video_canvas.yview)
            video_canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

            # Pack everything
            h_scrollbar.pack(side="bottom", fill="x")
            v_scrollbar.pack(side="right", fill="y")
            video_canvas.pack(side="left", fill="both", expand=True)

            # Create a frame inside the canvas
            scrollable_frame = tk.Frame(video_canvas)
            video_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

            # Video label
            self.label = Label(scrollable_frame)
            self.label.pack(pady=10)

            # Control buttons (inside the scrollable frame)
            control_frame = tk.Frame(scrollable_frame)
            control_frame.pack(pady=10)

            # Configure the scrollable frame to be the size of the video
            scrollable_frame.update_idletasks()  # Update geometry information
            video_canvas.config(scrollregion=(
                0, 0, 
                max(self.video_width, scrollable_frame.winfo_reqwidth()), 
                max(self.video_height, scrollable_frame.winfo_reqheight())
            ))

            # Bind the configure event to update scrollregion
            def on_frame_configure(event):
                video_canvas.configure(scrollregion=video_canvas.bbox("all"))
            
            scrollable_frame.bind("<Configure>", on_frame_configure)


        else:
            # --- SMALL VIDEO: video and controls in separate frames ---
            # Left: video only
            self.geometry(f"{self.video_width + 180}x{self.video_height + 150}")
            video_frame = tk.Frame(main_frame)
            video_frame.pack(side="left", fill="both", expand=True)

            self.label = Label(video_frame)
            self.label.pack(pady=10)

            # Right: controls only
            control_frame = tk.Frame(main_frame)
            control_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Control buttons (shared code)
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