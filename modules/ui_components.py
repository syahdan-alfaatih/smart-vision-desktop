import customtkinter as ctk
from tkinter import filedialog
import os

# 1. SIDEBAR FRAME
class SidebarFrame(ctk.CTkFrame):
    def __init__(self, master, start_callback, db_callback, width=300, height=None):
        super().__init__(master, width=width, corner_radius=0, fg_color="#1f1f1f")
        self.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")

        self.start_callback = start_callback
        self.db_callback = db_callback

        self.logo_label = ctk.CTkLabel(self, text="VISION DASHBOARD", font=("Roboto Medium", 20, "bold"))
        self.logo_label.place(x=20, y=30)

        # Buttons
        self.btn_start = ctk.CTkButton(self, text="INITIATE SYSTEM", font=("Arial", 16, "bold"),
                                       height=50, fg_color="#0066cc", hover_color="#0052a3",
                                       command=self.on_start_click)
        self.btn_start.place(x=20, y=100, relwidth=0.85)

        self.btn_mode = ctk.CTkButton(self, text="Select Mode", height=40, fg_color="#333333", state="disabled")
        self.btn_mode.place(x=20, y=180, relwidth=0.85)

        self.btn_db = ctk.CTkButton(self, text="Database Management", height=40, fg_color="#333333",
                                    hover_color="#555555", command=self.on_db_click)
        self.btn_db.place(x=20, y=230, relwidth=0.85)

    def on_start_click(self):
        if self.start_callback:
            self.start_callback()
        self.hide_menu()

    def on_db_click(self):
        if self.db_callback:
            self.db_callback()

    def hide_menu(self):
        self.place_forget()

    def show_menu(self):
        self.lift()
        self.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")


# 2. DATABASE WINDOW (POP-UP)
class DatabaseWindow(ctk.CTkToplevel):
    def __init__(self, parent, data_manager):
        super().__init__(parent)
        self.data_manager = data_manager
        self.title("Face Database Manager")
        self.geometry("700x500")
        self.resizable(False, False)
        
        # Window Behavior (Fixed: Not topmost so file explorer works)
        self.attributes("-topmost", False)
        self.transient(parent) 
        self.grab_set() 
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT PANEL: LIST ---
        self.left_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(self.left_frame, text="REGISTERED FACES", font=("Arial", 14, "bold")).pack(pady=10)
        
        self.scroll_list = ctk.CTkScrollableFrame(self.left_frame, fg_color="#1f1f1f")
        self.scroll_list.pack(expand=True, fill="both", padx=10, pady=5)
        
        self.selected_name = None
        self.list_buttons = []

        self.btn_delete = ctk.CTkButton(self.left_frame, text="DELETE SELECTED", fg_color="#cc0000",
                                        hover_color="#990000", state="disabled", command=self.delete_action)
        self.btn_delete.pack(pady=10, padx=10, fill="x")

        # --- RIGHT PANEL: INPUT ---
        self.right_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.right_frame, text="ADD NEW FACE", font=("Arial", 14, "bold")).pack(pady=10)

        self.entry_name = ctk.CTkEntry(self.right_frame, placeholder_text="Enter Name (e.g., SYAHDAN)")
        self.entry_name.pack(pady=10, padx=20, fill="x")

        self.btn_browse = ctk.CTkButton(self.right_frame, text="Choose Image File...", command=self.browse_file)
        self.btn_browse.pack(pady=5, padx=20, fill="x")
        
        self.lbl_file_path = ctk.CTkLabel(self.right_frame, text="No file selected", text_color="gray")
        self.lbl_file_path.pack(pady=5)
        self.selected_image_path = None

        self.btn_save = ctk.CTkButton(self.right_frame, text="PROCESS & SAVE", fg_color="#0066cc",
                                      height=40, command=self.save_action)
        self.btn_save.pack(pady=20, padx=20, fill="x")

        self.lbl_status = ctk.CTkLabel(self.right_frame, text="", text_color="yellow")
        self.lbl_status.pack(pady=10)

        self.refresh_list()

    def refresh_list(self):
        for btn in self.list_buttons:
            btn.destroy()
        self.list_buttons.clear()
        
        names = self.data_manager.get_face_list()
        
        for name in names:
            btn = ctk.CTkButton(self.scroll_list, text=name, fg_color="#333333", hover_color="#444444",
                                anchor="w", command=lambda n=name: self.select_name(n))
            btn.pack(fill="x", pady=2)
            self.list_buttons.append(btn)

    def select_name(self, name):
        self.selected_name = name
        self.btn_delete.configure(state="normal", text=f"DELETE '{name}'")

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.selected_image_path = file_path
            self.lbl_file_path.configure(text=os.path.basename(file_path))

    def save_action(self):
        name = self.entry_name.get().strip()
        if not name:
            self.lbl_status.configure(text="Error: Name required!", text_color="red")
            return
        if not self.selected_image_path:
            self.lbl_status.configure(text="Error: Image required!", text_color="red")
            return

        self.lbl_status.configure(text="Processing AI...", text_color="yellow")
        self.update()

        success, msg = self.data_manager.add_face(name, self.selected_image_path)

        if success:
            self.lbl_status.configure(text=msg, text_color="#00ff00")
            self.entry_name.delete(0, "end")
            self.selected_image_path = None
            self.lbl_file_path.configure(text="No file selected")
            self.refresh_list()
        else:
            self.lbl_status.configure(text=msg, text_color="red")

    def delete_action(self):
        if self.selected_name:
            success, msg = self.data_manager.delete_face(self.selected_name)
            if success:
                self.selected_name = None
                self.btn_delete.configure(state="disabled", text="DELETE SELECTED")
                self.refresh_list()
                self.lbl_status.configure(text=msg, text_color="#00ff00")