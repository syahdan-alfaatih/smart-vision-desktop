import customtkinter as ctk
from modules.ui_components import SidebarFrame, DatabaseWindow # <--- Import DatabaseWindow
from modules.camera_thread import CameraThread
from modules.data_manager import DataManager 
from PIL import Image
import os

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class SmartVisionApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Smart Vision Desktop")
        
        self.geometry("960x600")
        self.resizable(False, False)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.bind("<Escape>", lambda event: self.destroy())

        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color="black")
        self.main_area.grid(row=0, column=0, sticky="nsew")
        
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(0, weight=1)

        self.camera_label = ctk.CTkLabel(self.main_area, text="", fg_color="black")
        self.camera_label.grid(row=0, column=0, sticky="nsew")

        self.status_label = ctk.CTkLabel(
            self.main_area, 
            text="SYSTEM READY.\nWAITING FOR INPUT.", 
            font=("Consolas", 30, "bold"),
            text_color="white"
        )
        self.status_label.place(relx=0.5, rely=0.5, anchor="center")

        self.btn_stop = ctk.CTkButton(
            self,
            text="TERMINATE / STOP",
            font=("Arial", 14, "bold"),
            fg_color="#cc0000",
            hover_color="#990000",
            corner_radius=0,
            width=180,
            height=40,
            command=self.stop_process
        )

        self.update_idletasks()
        
        self.data_manager = DataManager()
        
        self.sidebar = SidebarFrame(
            self, 
            start_callback=self.start_process,
            db_callback=self.open_database_menu 
        )

        self.camera_engine = CameraThread(video_source=0)
        self.last_size = (0, 0)
        self.db_window = None

    def resize_with_aspect_ratio(self, image, max_w, max_h):
        img_w, img_h = image.size
        if img_w == 0 or img_h == 0: return image
        ratio = min(max_w / img_w, max_h / img_h)
        new_w = int(img_w * ratio)
        new_h = int(img_h * ratio)
        return image.resize((new_w, new_h), Image.BICUBIC)

    def open_database_menu(self):
        if self.db_window is None or not self.db_window.winfo_exists():
            self.db_window = DatabaseWindow(self, self.data_manager)
            
            self.db_window.protocol("WM_DELETE_WINDOW", self.on_db_close)
        else:
            self.db_window.focus()

    def on_db_close(self):
        if self.camera_engine:
            new_data = self.data_manager.load_database()
            self.camera_engine.update_database(new_data)
        
        self.db_window.destroy()

    def start_process(self):
        print(">> System Started.")
        self.status_label.configure(text="LOADING DATABASE...")
        self.status_label.lift()
        self.update_idletasks()
        
        loaded_data = self.data_manager.load_database()
        
        self.camera_engine.update_database(loaded_data)
        
        self.status_label.configure(text="INITIALIZING CAMERA...")
        self.btn_stop.place(relx=0.98, rely=0.95, anchor="se")
        self.lift()
        self.focus_force()

        self.camera_engine.start_camera()
        self.update_camera_loop()

    def stop_process(self):
        print(">> System Stopped.")
        self.camera_engine.stop_camera()
        self.camera_label.configure(image=None) 
        self.camera_label.image = None
        self.sidebar.show_menu()
        self.btn_stop.place_forget()
        self.status_label.configure(text="WHAT DO YOU THINK?\nSYSTEM IDLE.")
        self.status_label.place(relx=0.5, rely=0.5, anchor="center")

    def update_camera_loop(self):
        if self.camera_engine.is_running:
            frame = self.camera_engine.latest_frame
            
            if frame is not None:
                win_w = self.main_area.winfo_width()
                win_h = self.main_area.winfo_height()

                if win_w > 10 and win_h > 10:
                    resized_frame = self.resize_with_aspect_ratio(
                        frame, win_w, win_h
                    )

                    ctk_img = ctk.CTkImage(
                        light_image=resized_frame,
                        dark_image=resized_frame,
                        size=resized_frame.size
                    )

                    self.camera_label.configure(image=ctk_img)
                    self.camera_label.image = ctk_img 

                    if self.status_label.winfo_ismapped():
                        self.status_label.place_forget()

            self.after(1000 // 30, self.update_camera_loop)

if __name__ == "__main__":
    app = SmartVisionApp()
    app.mainloop()
