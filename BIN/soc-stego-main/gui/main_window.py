"""
Main Window Module for SOC Steganography Detection Tool.
Implements the primary CustomTkinter GUI interface.
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
import os
import sys
from datetime import datetime
import threading
import concurrent.futures

# Import project modules
from core.image_stego_engine import analyze_image
from core.stego_tool_engine import encode_message, decode_message
from reporting.logger import log_analysis_to_csv, log_batch_results
from reporting.report_generator import export_single_analysis_to_txt, export_batch_analysis_to_txt
from gui.file_dialog import select_image_file, select_folder
from core.vt_client import query_virustotal_hash, hash_payload_string
from config import (
    APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT,
    WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, COLOR_PRIMARY,
    COLOR_SUCCESS, COLOR_DANGER, HASH_DISPLAY_LENGTH,
    IMAGE_EXTENSIONS, BATCH_MAX_WORKERS, FONT_FAMILY,
    COLOR_BACKGROUND, COLOR_SECONDARY, COLOR_TEXT, COLOR_WARNING, COLOR_INFO
)

class SteganographyGUI:
    """Main GUI application for SOC Steganography Detection Tool."""
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        
        ctk.set_appearance_mode("dark")
        
        from tkinter import ttk
        style = ttk.Style()
        try:
            style.theme_use("default")
        except:
            pass
        style.configure("Stego.Horizontal.TProgressbar",
            troughcolor="#0a1f0a",
            background="#00e5cc",
            bordercolor="#1a3a2a",
            lightcolor="#00e5cc",
            darkcolor="#00e5cc",
            thickness=8)
        
        # Application state
        self.current_image_path = None
        self.current_analysis_result = None
        
        # Batch Application state
        self.batch_folder_path = None
        self.batch_results = []
        self.is_batch_running = False
        
        # Steganography state tracking
        self.current_stego_tab = None  # 'encode' or 'decode'
        self.stego_input_file = None
        self.stego_output_file = None
        self.stego_decode_file = None
        
        # Fonts
        self.font_main = ctk.CTkFont(family=FONT_FAMILY, size=12)
        self.font_bold = ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")
        self.font_h1 = ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold")
        self.font_h2 = ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold")
        
        # UI Setup
        self.create_menu_bar()
        self.create_main_interface()
        self.create_status_bar()
        
        self.update_status("Ready - System Initialized.")
    
    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0, bg=COLOR_PRIMARY, fg=COLOR_TEXT)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Select Image...", command=self.select_image)
        file_menu.add_separator()
        file_menu.add_command(label="Export to CSV...", command=self.export_to_csv, state=tk.DISABLED)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_application)
        self.file_menu = file_menu
        
        help_menu = tk.Menu(menubar, tearoff=0, bg=COLOR_PRIMARY, fg=COLOR_TEXT)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_main_interface(self):
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        # Top-level tabs: Steganography Tool | Steganalysis Tool
        self.main_tabs = ctk.CTkTabview(main_frame, segmented_button_selected_color=COLOR_SUCCESS, segmented_button_selected_hover_color="#00cc33", text_color="black")
        self.main_tabs.pack(fill=tk.BOTH, expand=True)

        self.stego_tab = self.main_tabs.add("Steganography Tool")
        analysis_container = self.main_tabs.add("Steganalysis Tool")

        # Under Steganography Tool: provide Encode / Decode subtabs
        self.stego_notebook = ctk.CTkTabview(self.stego_tab, segmented_button_selected_color=COLOR_SUCCESS, segmented_button_selected_hover_color="#00cc33", text_color="black")
        self.stego_notebook.pack(fill=tk.BOTH, expand=True)
        self.stego_encode_tab = self.stego_notebook.add("Encode")
        self.stego_decode_tab = self.stego_notebook.add("Decode")

        # Under Steganalysis: preserve existing analysis tabs (keeps backward compatibility)
        self.notebook = ctk.CTkTabview(analysis_container, segmented_button_selected_color=COLOR_SUCCESS, segmented_button_selected_hover_color="#00cc33", text_color="black")
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.single_tab = self.notebook.add("Single Image Analysis")
        self.batch_tab = self.notebook.add("Batch Directory Analysis")

        # Setup GUIs
        self.setup_steganography_encode_tab()
        self.setup_steganography_decode_tab()
        self.setup_single_analysis_tab()
        self.setup_batch_analysis_tab()

    def setup_single_analysis_tab(self):
        # File Selection
        file_frame = ctk.CTkFrame(self.single_tab, fg_color="transparent")
        file_frame.pack(fill=tk.X, pady=(10, 10))
        
        ctk.CTkLabel(file_frame, text="Selected Image:", font=self.font_bold).pack(side=tk.LEFT, padx=(0, 10))
        
        self.file_path_var = tk.StringVar(value="No image selected")
        self.file_path_label = ctk.CTkLabel(file_frame, textvariable=self.file_path_var, text_color="gray", font=self.font_main)
        self.file_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ctk.CTkButton(file_frame, text="Select Image", command=self.select_image, fg_color=COLOR_SECONDARY, hover_color=COLOR_PRIMARY, border_width=1, border_color=COLOR_SUCCESS, text_color=COLOR_SUCCESS).pack(side=tk.LEFT)
        
        # XOR Key
        key_frame = ctk.CTkFrame(self.single_tab, fg_color="transparent")
        key_frame.pack(fill=tk.X, pady=(0, 15))
        
        ctk.CTkLabel(key_frame, text="XOR Decryption Key:", font=self.font_bold).pack(side=tk.LEFT, padx=(0, 10))
        self.xor_key_var = tk.StringVar()
        ctk.CTkEntry(key_frame, textvariable=self.xor_key_var, width=250, font=self.font_main, border_color=COLOR_SUCCESS).pack(side=tk.LEFT, padx=(0, 10))
        ctk.CTkLabel(key_frame, text="(Optional)", text_color="gray", font=self.font_main).pack(side=tk.LEFT)
        
        # Action Buttons
        button_frame = ctk.CTkFrame(self.single_tab, fg_color="transparent")
        button_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.analyze_button = ctk.CTkButton(button_frame, text="Analyze Image", command=self.analyze_current_image, state=tk.DISABLED, fg_color=COLOR_SUCCESS, hover_color="#00cc33", text_color="black", font=self.font_bold)
        self.analyze_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_button = ctk.CTkButton(button_frame, text="Export CSV", command=self.export_to_csv, state=tk.DISABLED, fg_color=COLOR_SECONDARY, border_width=1, border_color=COLOR_INFO, text_color=COLOR_INFO)
        self.export_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_txt_button = ctk.CTkButton(button_frame, text="Export TXT", command=self.export_to_txt, state=tk.DISABLED, fg_color=COLOR_SECONDARY, border_width=1, border_color=COLOR_INFO, text_color=COLOR_INFO)
        self.export_txt_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.vt_button = ctk.CTkButton(button_frame, text="Threat Intel (VT)", command=self.launch_vt_scan, state=tk.DISABLED, fg_color=COLOR_SECONDARY, border_width=1, border_color=COLOR_WARNING, text_color=COLOR_WARNING)
        self.vt_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ctk.CTkButton(button_frame, text="Clear", command=self.clear_results, fg_color=COLOR_SECONDARY, hover_color=COLOR_DANGER).pack(side=tk.LEFT)
        
        # Results container (Scrollable)
        self.results_container = ctk.CTkScrollableFrame(self.single_tab, fg_color=COLOR_SECONDARY, corner_radius=10, border_width=1, border_color="#333333")
        self.results_container.pack(fill=tk.BOTH, expand=True, pady=(5, 5))
        
        self.display_welcome_message()

    def setup_batch_analysis_tab(self):
        folder_frame = ctk.CTkFrame(self.batch_tab, fg_color="transparent")
        folder_frame.pack(fill=tk.X, pady=(10, 10))
        
        ctk.CTkLabel(folder_frame, text="Target Folder:", font=self.font_bold).pack(side=tk.LEFT, padx=(0, 10))
        
        self.folder_path_var = tk.StringVar(value="No folder selected")
        ctk.CTkLabel(folder_frame, textvariable=self.folder_path_var, text_color="gray", font=self.font_main).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ctk.CTkButton(folder_frame, text="Select Folder", command=self.select_batch_folder, fg_color=COLOR_SECONDARY, border_width=1, border_color=COLOR_SUCCESS, text_color=COLOR_SUCCESS).pack(side=tk.LEFT)
        
        options_frame = ctk.CTkFrame(self.batch_tab, fg_color="transparent")
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        ctk.CTkLabel(options_frame, text="XOR Decryption Key:", font=self.font_bold).pack(side=tk.LEFT, padx=(0, 10))
        self.batch_xor_key_var = tk.StringVar()
        ctk.CTkEntry(options_frame, textvariable=self.batch_xor_key_var, width=250, border_color=COLOR_SUCCESS).pack(side=tk.LEFT, padx=(0, 10))
        
        btn_frame = ctk.CTkFrame(self.batch_tab, fg_color="transparent")
        btn_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.batch_scan_btn = ctk.CTkButton(btn_frame, text="Start Batch Scan", command=self.start_batch_scan, state=tk.DISABLED, fg_color=COLOR_SUCCESS, text_color="black", font=self.font_bold)
        self.batch_scan_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        
        self.batch_export_btn = ctk.CTkButton(btn_frame, text="Export CSV Report", command=self.export_batch_csv, state=tk.DISABLED, fg_color=COLOR_SECONDARY, border_width=1, border_color=COLOR_INFO, text_color=COLOR_INFO)
        self.batch_export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.batch_export_txt_btn = ctk.CTkButton(btn_frame, text="Export TXT Report", command=self.export_batch_txt, state=tk.DISABLED, fg_color=COLOR_SECONDARY, border_width=1, border_color=COLOR_INFO, text_color=COLOR_INFO)
        self.batch_export_txt_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ctk.CTkButton(btn_frame, text="Clear", command=self.clear_batch_results, fg_color=COLOR_SECONDARY).pack(side=tk.LEFT)
        
        progress_frame = ctk.CTkFrame(self.batch_tab, fg_color="transparent")
        progress_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.batch_progress_var = tk.DoubleVar(value=0)
        self.batch_progress = ctk.CTkProgressBar(progress_frame, variable=self.batch_progress_var, progress_color=COLOR_SUCCESS)
        self.batch_progress.pack(fill=tk.X, pady=(0, 5))
        self.batch_progress.set(0)
        
        self.batch_status_var = tk.StringVar(value="Ready.")
        ctk.CTkLabel(progress_frame, textvariable=self.batch_status_var, text_color=COLOR_SUCCESS, font=self.font_main).pack(anchor=tk.W)
        
        self.batch_results_container = ctk.CTkScrollableFrame(self.batch_tab, fg_color=COLOR_SECONDARY, corner_radius=10, border_width=1, border_color="#333333")
        self.batch_results_container.pack(fill=tk.BOTH, expand=True, pady=(5, 5))
        
        self.display_batch_welcome_message()

    def setup_steganography_encode_tab(self):
        frame = ctk.CTkFrame(self.stego_encode_tab, fg_color="#111811", border_color="#1a3a1a", border_width=2, corner_radius=10)
        frame.pack(fill=tk.X, expand=False, padx=15, pady=15)
        
        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.pack(fill=tk.X, padx=10, pady=10)

        self.stego_input_preview_frame = ctk.CTkFrame(top, width=40, height=40, fg_color="transparent", border_color="#2a6e4a", border_width=2)
        self.stego_input_preview_frame.pack_propagate(False)
        self.stego_input_preview_frame.pack(side=tk.LEFT, padx=(0,10))
        ctk.CTkLabel(self.stego_input_preview_frame, text="?", text_color="#2a6e4a", font=self.font_bold).pack(expand=True, fill=tk.BOTH)

        ctk.CTkLabel(top, text="Input Image:", font=self.font_bold).pack(side=tk.LEFT, padx=(0,10))
        self.stego_input_path_var = tk.StringVar(value="No image selected")
        self.stego_input_display_label = ctk.CTkLabel(top, text="No image selected", text_color="#2a6e4a", font=self.font_main)
        self.stego_input_display_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10))
        ctk.CTkButton(top, text="Select Image", command=self.select_stego_input_image, fg_color="#1a1a1a", border_width=2, border_color="#00e5cc", hover_color="#113333", text_color="#00e5cc", font=self.font_main).pack(side=tk.LEFT)

        # Message textbox header and byte counter
        msg_header = ctk.CTkFrame(frame, fg_color="transparent")
        msg_header.pack(fill=tk.X, padx=10, pady=(8,0))
        ctk.CTkLabel(msg_header, text="Secret Message / Script:", font=self.font_bold).pack(side=tk.LEFT)
        self.stego_byte_capacity_var = tk.StringVar(value="0 / ~0 bytes")
        self.stego_capacity_label = ctk.CTkLabel(msg_header, textvariable=self.stego_byte_capacity_var, text_color="#2a6e4a", font=self.font_main)
        self.stego_capacity_label.pack(side=tk.RIGHT)

        self.stego_message_tb = ctk.CTkTextbox(frame, height=160, font=self.font_main, fg_color="#05080E", border_color="#00c853", border_width=1)
        self.stego_message_tb.pack(fill=tk.BOTH, expand=False, padx=10, pady=(5,10))
        self.stego_message_tb.configure(padx=8, pady=8)
        self.stego_message_tb.insert("0.0", "// Enter secret message or paste script here...")
        self.stego_message_tb.configure(text_color="#2a6e4a")
        
        def _clear_enc_placeholder(e):
            if "// Enter secret message" in self.stego_message_tb.get("0.0", "end"):
                self.stego_message_tb.delete("0.0", "end")
                self.stego_message_tb.configure(text_color="white")
        
        def _on_key_release_enc(e):
            if hasattr(self, "_stego_cached_capacity") and self._stego_cached_capacity > 0:
                cap = self._stego_cached_capacity
                cur = len(self.stego_message_tb.get("0.0", "end")) - 1
                self.stego_byte_capacity_var.set(f"{cur} / ~{cap} bytes")
                if cur > cap:
                    self.stego_capacity_label.configure(text_color=COLOR_DANGER)
                else:
                    self.stego_capacity_label.configure(text_color="#2a6e4a")

        self.stego_message_tb.bind("<FocusIn>", _clear_enc_placeholder)
        self.stego_message_tb.bind("<KeyRelease>", _on_key_release_enc)

        # Password row
        pwd_frame = ctk.CTkFrame(frame, fg_color="transparent")
        pwd_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        ctk.CTkLabel(pwd_frame, text="Password (optional):", font=self.font_bold).pack(side=tk.LEFT, padx=(0,10))
        self.stego_pass_var = tk.StringVar()
        ctk.CTkEntry(pwd_frame, textvariable=self.stego_pass_var, width=300, show="*", border_color="#00c853").pack(side=tk.LEFT)

        # Output row
        out_frame = ctk.CTkFrame(frame, fg_color="transparent")
        out_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        ctk.CTkButton(out_frame, text="Choose Output...", command=self.select_stego_output_path, fg_color="#1a1a1a", border_width=2, border_color="#00e5cc", hover_color="#113333", text_color="#00e5cc", font=self.font_main).pack(side=tk.LEFT, padx=(0,10))
        self.stego_output_path_var = tk.StringVar(value="No output selected")
        self.stego_output_display_label = ctk.CTkLabel(out_frame, text="No output selected", text_color="#2a6e4a", font=self.font_main)
        self.stego_output_display_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Encode button and Progress bar
        btns = ctk.CTkFrame(frame, fg_color="transparent")
        btns.pack(fill=tk.X, padx=10, pady=(10,0))
        self.stego_encode_btn = ctk.CTkButton(btns, text="Encode", command=self.start_encode, fg_color="#39ff14", text_color="#000000", font=self.font_bold, state=tk.NORMAL, width=200, height=35)
        self.stego_encode_btn.pack(side=tk.LEFT)

        from tkinter import ttk
        self.stego_encode_pbar = ttk.Progressbar(frame, mode="indeterminate", style="Stego.Horizontal.TProgressbar")
        self.stego_encode_pbar.pack(fill=tk.X, padx=10, pady=(8,12))

    def setup_steganography_decode_tab(self):
        frame = ctk.CTkFrame(self.stego_decode_tab, fg_color="#111811", border_color="#1a3a1a", border_width=2, corner_radius=10)
        frame.pack(fill=tk.X, expand=False, padx=15, pady=15)
        
        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.pack(fill=tk.X, padx=10, pady=10)

        self.stego_decode_preview_frame = ctk.CTkFrame(top, width=40, height=40, fg_color="transparent", border_color="#2a6e4a", border_width=2)
        self.stego_decode_preview_frame.pack_propagate(False)
        self.stego_decode_preview_frame.pack(side=tk.LEFT, padx=(0,10))
        ctk.CTkLabel(self.stego_decode_preview_frame, text="?", text_color="#2a6e4a", font=self.font_bold).pack(expand=True, fill=tk.BOTH)

        ctk.CTkLabel(top, text="Stego Image:", font=self.font_bold).pack(side=tk.LEFT, padx=(0,10))
        self.stego_decode_path_var = tk.StringVar(value="No image selected")
        self.stego_decode_display_label = ctk.CTkLabel(top, text="No image selected", text_color="#2a6e4a", font=self.font_main)
        self.stego_decode_display_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10))
        ctk.CTkButton(top, text="Select Image", command=self.select_stego_decode_image, fg_color="#1a1a1a", border_width=2, border_color="#00e5cc", hover_color="#113333", text_color="#00e5cc", font=self.font_main).pack(side=tk.LEFT)

        # Password row
        pwd_frame = ctk.CTkFrame(frame, fg_color="transparent")
        pwd_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        ctk.CTkLabel(pwd_frame, text="Password (if used):", font=self.font_bold).pack(side=tk.LEFT, padx=(0,10))
        self.stego_decode_pass_var = tk.StringVar()
        ctk.CTkEntry(pwd_frame, textvariable=self.stego_decode_pass_var, width=300, show="*", border_color="#00c853").pack(side=tk.LEFT)

        # Decode button and Progress bar
        btns = ctk.CTkFrame(frame, fg_color="transparent")
        btns.pack(fill=tk.X, padx=10, pady=(10,0))
        self.stego_decode_btn = ctk.CTkButton(btns, text="Decode", command=self.start_decode, fg_color="#39ff14", text_color="#000000", font=self.font_bold, width=200, height=35)
        self.stego_decode_btn.pack(side=tk.LEFT)

        from tkinter import ttk
        self.stego_decode_pbar = ttk.Progressbar(frame, mode="indeterminate", style="Stego.Horizontal.TProgressbar")
        self.stego_decode_pbar.pack(fill=tk.X, padx=10, pady=(8,0))

        # Extracted message label and textbox with padding
        ctk.CTkLabel(frame, text="Extracted Message:", font=self.font_bold).pack(anchor=tk.W, padx=10, pady=(12,0))
        self.stego_decoded_tb = ctk.CTkTextbox(frame, height=200, font=self.font_main, fg_color="#05080E", border_color="#00c853", border_width=1)
        self.stego_decoded_tb.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5,12))
        # Add internal padding to textbox
        self.stego_decoded_tb.configure(padx=8, pady=8)
        self.stego_decoded_tb.insert("0.0", "// No message decoded yet. Run decode to extract.")
        self.stego_decoded_tb.configure(text_color="#2a6e4a")
        
        def _clear_dec_placeholder(e):
            if "// No message decoded yet. Run decode to extract." in self.stego_decoded_tb.get("0.0", "end"):
                self.stego_decoded_tb.delete("0.0", "end")
                self.stego_decoded_tb.configure(text_color="white")
        self.stego_decoded_tb.bind("<FocusIn>", _clear_dec_placeholder)

    # --- Steganography handlers ---
    def _truncate_path_for_display(self, path, max_width=60):
        """Truncate path for display while keeping full path in backend."""
        if len(path) <= max_width:
            return path
        return "..." + path[-max_width:]

    def select_stego_input_image(self):
        path = select_image_file()
        if path:
            self.stego_input_path_var.set(path)
            self.stego_input_file = path
            display_text = self._truncate_path_for_display(path)
            self.stego_input_display_label.configure(text=display_text)
            self.update_status(f"Input: {os.path.basename(path)}")
            # Cache capacity
            try:
                from PIL import Image
                with Image.open(path) as img:
                    self._stego_cached_capacity = (img.size[0] * img.size[1] * 3) // 8
                
                # trigger update
                cur = len(self.stego_message_tb.get("0.0", "end")) - 1
                if cur < 0: cur = 0
                self.stego_byte_capacity_var.set(f"{cur} / ~{self._stego_cached_capacity} bytes")
            except Exception:
                self._stego_cached_capacity = 0

    def select_stego_output_path(self):
        from config import LOGS_DIR
        default_name = f"stego_out_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        path = filedialog.asksaveasfilename(initialdir=LOGS_DIR, initialfile=default_name, defaultextension=".png", filetypes=[("PNG", "*.png"), ("BMP", "*.bmp"), ("All files", "*")])
        if path:
            self.stego_output_path_var.set(path)
            self.stego_output_file = path
            display_text = self._truncate_path_for_display(path)
            self.stego_output_display_label.configure(text=display_text)
            self.update_status(f"Output: {os.path.basename(path)}")

    def select_stego_decode_image(self):
        path = select_image_file()
        if path:
            self.stego_decode_path_var.set(path)
            self.stego_decode_file = path
            display_text = self._truncate_path_for_display(path)
            self.stego_decode_display_label.configure(text=display_text)
            self.update_status(f"Decoding: {os.path.basename(path)}")

    def start_encode(self):
        inp = self.stego_input_path_var.get()
        out = self.stego_output_path_var.get()
        msg = self.stego_message_tb.get("0.0", "end").strip()
        pwd = self.stego_pass_var.get().strip() or None
        if not inp or inp == "No image selected":
            messagebox.showwarning("No Input", "Please select an input image to encode into.")
            return
        if not out or out == "No output selected":
            messagebox.showwarning("No Output", "Please choose an output file to save the stego image.")
            return
        if not msg:
            messagebox.showwarning("No Message", "Please enter a secret message to embed.")
            return

        self.stego_encode_btn.configure(state=tk.DISABLED)
        self.update_status("Embedding payload...")
        try:
            self.stego_encode_pbar.start()
        except Exception:
            pass
        t = threading.Thread(target=self._run_encode_thread, args=(inp, msg, out, pwd))
        t.daemon = True
        t.start()

    def _run_encode_thread(self, inp, msg, out, pwd):
        try:
            encode_message(inp, msg, out, password=pwd)
            self.root.after(0, lambda: messagebox.showinfo("Encode Complete", f"Stego image saved:\n{out}"))
            self.root.after(0, lambda: self.update_status(f"Encode complete: {os.path.basename(out)}"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Encode Error", str(e)))
            self.root.after(0, lambda: self.update_status("Encode failed."))
        finally:
            self.root.after(0, lambda: self.stego_encode_btn.configure(state=tk.NORMAL))
            self.root.after(0, lambda: (self.stego_encode_pbar.stop() if hasattr(self, 'stego_encode_pbar') else None))

    def start_decode(self):
        inp = self.stego_decode_path_var.get()
        pwd = self.stego_decode_pass_var.get().strip() or None
        if not inp or inp == "No image selected":
            messagebox.showwarning("No Input", "Please select a stego image to decode.")
            return
        self.stego_decode_btn.configure(state=tk.DISABLED)
        self.update_status("Extracting payload...")
        try:
            self.stego_decode_pbar.start()
        except Exception:
            pass
        t = threading.Thread(target=self._run_decode_thread, args=(inp, pwd))
        t.daemon = True
        t.start()

    def _run_decode_thread(self, inp, pwd):
        try:
            res = decode_message(inp, password=pwd)
            self.root.after(0, lambda: self.stego_decoded_tb.delete("0.0", "end"))
            self.root.after(0, lambda: self.stego_decoded_tb.insert("0.0", res))
            self.root.after(0, lambda: self.stego_decoded_tb.configure(text_color="white"))
            self.root.after(0, lambda: self.update_status(f"Decode complete: extracted {len(res)} bytes"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Decode Error", str(e)))
            self.root.after(0, lambda: self.update_status("Decode failed."))
        finally:
            self.root.after(0, lambda: self.stego_decode_btn.configure(state=tk.NORMAL))
            self.root.after(0, lambda: (self.stego_decode_pbar.stop() if hasattr(self, 'stego_decode_pbar') else None))

    def create_status_bar(self):
        self.status_var = tk.StringVar()
        status_bar = ctk.CTkLabel(self.root, textvariable=self.status_var, anchor="w", fg_color=COLOR_SECONDARY, text_color=COLOR_SUCCESS, font=self.font_main, padx=10, pady=5)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def display_welcome_message(self):
        for widget in self.results_container.winfo_children():
            widget.destroy()
            
        header = ctk.CTkLabel(self.results_container, text=f"SYSTEM: {APP_NAME.upper()}", font=self.font_h1, text_color=COLOR_SUCCESS)
        header.pack(pady=(20, 10))
        
        text = "INITIATING STEGANOGRAPHY DETECTION PROTOCOLS...\n\n" \
               "Awaiting user input. Select a target image to begin deep LSB analysis.\n" \
               "Support for XOR decryption and global Threat Intel (VirusTotal) active.\n\n" \
               "// END OF MESSAGE"
        ctk.CTkLabel(self.results_container, text=text, font=self.font_main, justify=tk.LEFT).pack(anchor=tk.W, padx=20)

    def select_image(self):
        initial_dir = os.path.dirname(self.current_image_path) if self.current_image_path else None
        file_path = select_image_file(initial_dir)
        if file_path:
            if self.current_image_path != file_path:
                self.current_analysis_result = None
                self.export_button.configure(state=tk.DISABLED)
                self.export_txt_button.configure(state=tk.DISABLED)
                self.vt_button.configure(state=tk.DISABLED)
                self.display_welcome_message()
            
            self.current_image_path = file_path
            self.file_path_var.set(file_path)
            self.analyze_button.configure(state=tk.NORMAL)
            self.update_status(f"Target locked: {os.path.basename(file_path)}")

    def analyze_current_image(self):
        if not self.current_image_path:
            messagebox.showwarning("No Target", "Please select a target image first.")
            return
            
        self.show_loading_indicator()
        self.update_status("SCANNING TARGET...")
        self.analyze_button.configure(state=tk.DISABLED)
        self.export_button.configure(state=tk.DISABLED)
        self.export_txt_button.configure(state=tk.DISABLED)
        self.root.update_idletasks()
        
        xor_key = self.xor_key_var.get().strip()
        decode_key = xor_key if xor_key else None
        
        t = threading.Thread(target=self._run_analysis_thread, args=(self.current_image_path, decode_key))
        t.daemon = True
        t.start()

    def _run_analysis_thread(self, file_path, decode_key):
        try:
            result = analyze_image(file_path, decode_key)
            self.root.after(0, self._handle_analysis_complete, result)
        except Exception as e:
            self.root.after(0, self._handle_analysis_error, str(e))

    def _handle_analysis_complete(self, result):
        # Preserve VT results if we already scanned this file
        if self.current_analysis_result and self.current_analysis_result.get('file_path') == result.get('file_path'):
            if 'vt_results' in self.current_analysis_result:
                result['vt_results'] = self.current_analysis_result['vt_results']
                
        self.current_analysis_result = result
        self.display_analysis_results(result)
        
        self.export_button.configure(state=tk.NORMAL)
        self.export_txt_button.configure(state=tk.NORMAL)
        self.vt_button.configure(state=tk.NORMAL)
        self.file_menu.entryconfig("Export to CSV...", state=tk.NORMAL)
        
        if result.get('has_hidden_data', False):
            self.update_status("WARNING: HIDDEN PAYLOAD DETECTED.")
        else:
            self.update_status("SCAN COMPLETE: TARGET CLEAN.")
            
        self.analyze_button.configure(state=tk.NORMAL)

    def _handle_analysis_error(self, error_msg):
        messagebox.showerror("Analysis Error", f"System failure during scan:\n{error_msg}")
        self.update_status("SCAN FAILED.")
        self.display_welcome_message()
        self.analyze_button.configure(state=tk.NORMAL)

    def show_loading_indicator(self):
        for widget in self.results_container.winfo_children():
            widget.destroy()
            
        ctk.CTkLabel(self.results_container, text="EXECUTING DEEP SCAN...", font=self.font_h2, text_color=COLOR_SUCCESS).pack(pady=(50, 20))
        pbar = ctk.CTkProgressBar(self.results_container, mode="indeterminate", progress_color=COLOR_SUCCESS)
        pbar.pack(pady=10, padx=50, fill=tk.X)
        pbar.start()

    def display_analysis_results(self, result):
        for widget in self.results_container.winfo_children():
            widget.destroy()
            
        has_hidden_data = result.get('has_hidden_data', False)
        status = result.get('status', 'unknown')
        
        if status == 'error':
            status_text = "ERROR: ANALYSIS FAILED"
            status_color = COLOR_DANGER
        elif has_hidden_data:
            status_text = "THREAT DETECTED: HIDDEN PAYLOAD FOUND"
            status_color = COLOR_DANGER
        else:
            status_text = "CLEAN: NO STEGANOGRAPHY DETECTED"
            status_color = COLOR_SUCCESS
            
        # Status Header
        status_frame = ctk.CTkFrame(self.results_container, fg_color=status_color, corner_radius=5)
        status_frame.pack(fill=tk.X, pady=(0, 20), padx=10)
        ctk.CTkLabel(status_frame, text=status_text, font=self.font_h2, text_color="black", pady=10).pack()

        # 1. General File Information
        ctk.CTkLabel(self.results_container, text="General File Information", font=self.font_h2, text_color=COLOR_SUCCESS).pack(anchor=tk.W, padx=10, pady=(10, 5))
        info_frame = ctk.CTkFrame(self.results_container, fg_color="#0A0E17", border_width=1, border_color="#1F2937", corner_radius=5)
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        file_path = result.get('file_path', 'N/A')
        file_name = os.path.basename(file_path) if file_path != 'N/A' else 'N/A'
        self._add_row(info_frame, "File Name:", file_name)
        self._add_row(info_frame, "Target Path:", file_path)
        self._add_row(info_frame, "File Size:", f"{result.get('file_size', 0):,} bytes")
        self._add_row(info_frame, "SHA-256 Checksum:", result.get('file_hash', 'N/A'))
        self._add_row(info_frame, "Scan Timestamp:", result.get('timestamp', 'N/A'))

        # 2. Image Metadata
        ctk.CTkLabel(self.results_container, text="Image Metadata", font=self.font_h2, text_color=COLOR_SUCCESS).pack(anchor=tk.W, padx=10, pady=(0, 5))
        meta = result.get('metadata', {})
        meta_frame = ctk.CTkFrame(self.results_container, fg_color="#0A0E17", border_width=1, border_color="#1F2937", corner_radius=5)
        meta_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        self._add_row(meta_frame, "Format:", meta.get('format', 'N/A'))
        self._add_row(meta_frame, "Dimensions:", meta.get('dimensions', 'N/A'))
        self._add_row(meta_frame, "Color Mode:", meta.get('mode', 'N/A'))
        self._add_row(meta_frame, "Total Pixels:", f"{meta.get('total_pixels', 0):,}")
        self._add_row(meta_frame, "Max LSB Capacity:", f"{meta.get('max_capacity_bytes', 0):,} bytes")

        # 3. Steganography & Anomaly Detection
        ctk.CTkLabel(self.results_container, text="Steganography & Anomaly Detection", font=self.font_h2, text_color=COLOR_SUCCESS).pack(anchor=tk.W, padx=10, pady=(0, 5))
        det_frame = ctk.CTkFrame(self.results_container, fg_color="#0A0E17", border_width=1, border_color="#1F2937", corner_radius=5)
        det_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        self._add_row(det_frame, "Detection Status:", status_text, val_color=status_color)
        
        entropy = result.get('entropy_score', 0.0)
        from config import ENTROPY_THRESHOLD
        ent_color = COLOR_DANGER if entropy >= ENTROPY_THRESHOLD else COLOR_SUCCESS
        
        self._add_row(det_frame, "LSB Entropy:", f"{entropy:.4f}", val_color=ent_color)
        
        ent_assessment = f"High Randomness (Threshold: {ENTROPY_THRESHOLD})" if entropy >= ENTROPY_THRESHOLD else f"Normal Range (Threshold: {ENTROPY_THRESHOLD})"
        self._add_row(det_frame, "Entropy Assessment:", ent_assessment, val_color=ent_color)
        
        self._add_row(det_frame, "Hidden Payload:", "POSITIVE" if has_hidden_data else "NEGATIVE", val_color=COLOR_DANGER if has_hidden_data else COLOR_SUCCESS)
        self._add_row(det_frame, "Decryption Used:", "Yes" if result.get('decryption_key_used', False) else "No")
        
        if has_hidden_data:
            ctk.CTkLabel(det_frame, text="PAYLOAD PREVIEW", font=self.font_bold, text_color=COLOR_SUCCESS).pack(anchor=tk.W, padx=10, pady=(10, 5))
            
            tb = ctk.CTkTextbox(det_frame, height=120, font=self.font_main, fg_color="#05080E", border_color="#1F2937", border_width=1, text_color=COLOR_DANGER)
            tb.pack(fill=tk.X, padx=10, pady=(0, 10))
            tb.insert("0.0", result.get('hidden_message', ''))
            tb.configure(state=tk.DISABLED)

        # 4. Global Threat Intelligence
        ctk.CTkLabel(self.results_container, text="Global Threat Intelligence (VT)", font=self.font_h2, text_color=COLOR_SUCCESS).pack(anchor=tk.W, padx=10, pady=(0, 5))
        vt_frame = ctk.CTkFrame(self.results_container, fg_color="#0A0E17", border_width=1, border_color="#1F2937", corner_radius=5)
        vt_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        vt_results = result.get('vt_results', None)
        if vt_results:
            self._add_row(vt_frame, "Carrier Image:", vt_results.get('carrier_score', 'N/A'))
            payload_score = vt_results.get('payload_score', 'N/A')
            if payload_score != 'N/A':
                self._add_row(vt_frame, "Payload Data:", payload_score)
        else:
            self._add_row(vt_frame, "Status:", "Not Scanned", val_color="gray")

    def _add_row(self, parent, label, value, val_color=None):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill=tk.X, pady=(2, 0))
        
        # Key: Matrix Green, monospace
        ctk.CTkLabel(row, text=label, font=self.font_bold, text_color=COLOR_SUCCESS, width=200, anchor="w").pack(side=tk.LEFT, padx=(5, 10))
        
        # Value: Light grey or val_color
        v_color = val_color if val_color else "#E0E0E0"
        ctk.CTkLabel(row, text=value, font=self.font_main, text_color=v_color, anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Separator Line
        separator = ctk.CTkFrame(parent, height=1, fg_color="#1F2937")
        separator.pack(fill=tk.X, pady=(2, 0), padx=5)

    def display_batch_welcome_message(self):
        for widget in self.batch_results_container.winfo_children():
            widget.destroy()
        header = ctk.CTkLabel(self.batch_results_container, text=f"BATCH OPERATIONS", font=self.font_h1, text_color=COLOR_SUCCESS)
        header.pack(pady=(20, 10))
        ctk.CTkLabel(self.batch_results_container, text="Awaiting directory selection for mass steganography scan.", font=self.font_main).pack(anchor=tk.W, padx=20)

    def select_batch_folder(self):
        folder_path = select_folder()
        if folder_path:
            self.batch_folder_path = folder_path
            self.folder_path_var.set(folder_path)
            self.batch_scan_btn.configure(state=tk.NORMAL)
            self.update_status(f"Target directory locked: {os.path.basename(folder_path)}")

    def start_batch_scan(self):
        if not self.batch_folder_path: return
        self.is_batch_running = True
        self.batch_results = []
        self.batch_scan_btn.configure(state=tk.DISABLED)
        
        xor_key = self.batch_xor_key_var.get().strip()
        decode_key = xor_key if xor_key else None
        
        images = []
        for root, _, files in os.walk(self.batch_folder_path):
            for file in files:
                if os.path.splitext(file)[1].lower() in IMAGE_EXTENSIONS:
                    images.append(os.path.join(root, file))
                    
        total = len(images)
        if total == 0:
            messagebox.showinfo("Error", "No valid targets found in directory.")
            self.batch_scan_btn.configure(state=tk.NORMAL)
            return
            
        self.batch_progress_var.set(0)
        self.batch_status_var.set(f"Scanning {total} targets...")
        self._update_batch_dashboard(0, total, 0, 0, 0)
        
        t = threading.Thread(target=self._run_batch_thread, args=(images, decode_key, total))
        t.daemon = True
        t.start()


    def _run_batch_thread(self, images, decode_key, total):
        processed = flagged = clean = errors = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=BATCH_MAX_WORKERS) as executor:
            future_to_file = {executor.submit(analyze_image, path, decode_key): path for path in images}
            for future in concurrent.futures.as_completed(future_to_file):
                if not self.is_batch_running: break
                processed += 1
                try:
                    res = future.result()
                    self.batch_results.append(res)
                    if res.get('status') == 'error': errors += 1
                    elif res.get('has_hidden_data'): flagged += 1
                    else: clean += 1
                except: errors += 1
                self.root.after(0, self._update_batch_progress, processed, total, flagged, clean, errors)
                
        if self.is_batch_running:
            self.root.after(0, self._handle_batch_complete)
        else:
            self.root.after(0, self._handle_batch_cancelled)

    def _update_batch_progress(self, processed, total, flagged, clean, errors):
        prog = processed / total if total > 0 else 0
        self.batch_progress.set(prog)
        self.batch_status_var.set(f"Scanning... {processed}/{total}")
        self._update_batch_dashboard(processed, total, flagged, clean, errors)

    def _update_batch_dashboard(self, processed, total, flagged, clean, errors, complete=False, cancelled=False):
        for widget in self.batch_results_container.winfo_children(): widget.destroy()
        
        if complete:
            text = f"COMPLETE: {flagged} THREATS FOUND" if flagged else "COMPLETE: ALL CLEAN"
            color = COLOR_DANGER if flagged else COLOR_SUCCESS
        elif cancelled:
            text = "SCAN ABORTED"
            color = COLOR_WARNING
        else:
            text = "SCAN IN PROGRESS..."
            color = COLOR_INFO
            
        status_frame = ctk.CTkFrame(self.batch_results_container, fg_color=color, corner_radius=5)
        status_frame.pack(fill=tk.X, pady=(0, 20), padx=10)
        ctk.CTkLabel(status_frame, text=text, font=self.font_h2, text_color="black", pady=10).pack()

        grid = ctk.CTkFrame(self.batch_results_container, fg_color="transparent")
        grid.pack(fill=tk.X, padx=10)
        
        self._add_row(grid, "Targets Processed:", f"{processed} / {total}")
        self._add_row(grid, "Threats Detected:", str(flagged), val_color=COLOR_DANGER if flagged else COLOR_TEXT)
        self._add_row(grid, "Clean Targets:", str(clean), val_color=COLOR_SUCCESS)
        self._add_row(grid, "Scan Errors:", str(errors))

    def _handle_batch_complete(self):
        self.batch_status_var.set("SCAN COMPLETE. REPORT READY.")
        self.batch_scan_btn.configure(state=tk.NORMAL)
        self.batch_export_btn.configure(state=tk.NORMAL)
        self.batch_export_txt_btn.configure(state=tk.NORMAL)
        
        flagged = sum(1 for r in self.batch_results if r.get('has_hidden_data'))
        clean = sum(1 for r in self.batch_results if not r.get('has_hidden_data') and r.get('status')!='error')
        errors = sum(1 for r in self.batch_results if r.get('status')=='error')
        self._update_batch_dashboard(len(self.batch_results), len(self.batch_results), flagged, clean, errors, complete=True)

    def _handle_batch_cancelled(self):
        self.batch_status_var.set("SCAN ABORTED.")
        self.batch_scan_btn.configure(state=tk.NORMAL)
        self.batch_export_btn.configure(state=tk.NORMAL)
        self.batch_export_txt_btn.configure(state=tk.NORMAL)

    def export_batch_csv(self):
        if not self.batch_results: return
        try:
            res = log_batch_results(self.batch_results)
            if res.get('success'):
                messagebox.showinfo("Export Success", f"Report saved:\n{res['csv_path']}")
                self.update_status(f"Exported to: {res['csv_path']}")
            else:
                messagebox.showerror("Error", f"Failed: {res.get('error')}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_to_csv(self):
        if not self.current_analysis_result: return
        try:
            res = log_analysis_to_csv(self.current_analysis_result)
            if res['success']:
                messagebox.showinfo("Export Success", f"Report saved:\n{res['csv_path']}")
                self.update_status(f"Exported to: {res['csv_path']}")
            else:
                messagebox.showerror("Error", f"Failed: {res['error']}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_to_txt(self):
        if not self.current_analysis_result: return
        try:
            from config import LOGS_DIR
            default_name = f"stego_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            path = filedialog.asksaveasfilename(
                initialdir=LOGS_DIR,
                initialfile=default_name,
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if not path: return
            
            res = export_single_analysis_to_txt(self.current_analysis_result, path)
            if res.get('success'):
                messagebox.showinfo("Export Success", f"TXT Report saved:\n{res['txt_path']}")
                self.update_status(f"Exported TXT to: {res['txt_path']}")
            else:
                messagebox.showerror("Error", f"Failed: {res.get('error')}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_batch_txt(self):
        if not self.batch_results: return
        try:
            from config import LOGS_DIR
            default_name = f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            path = filedialog.asksaveasfilename(
                initialdir=LOGS_DIR,
                initialfile=default_name,
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if not path: return
            
            res = export_batch_analysis_to_txt(self.batch_results, path)
            if res.get('success'):
                messagebox.showinfo("Export Success", f"Batch TXT Report saved:\n{res['txt_path']}")
                self.update_status(f"Exported Batch TXT to: {res['txt_path']}")
            else:
                messagebox.showerror("Error", f"Failed: {res.get('error')}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_results(self):
        self.current_image_path = None
        self.current_analysis_result = None
        self.file_path_var.set("No image selected")
        self.xor_key_var.set("")
        self.analyze_button.configure(state=tk.DISABLED)
        self.export_button.configure(state=tk.DISABLED)
        self.export_txt_button.configure(state=tk.DISABLED)
        self.vt_button.configure(state=tk.DISABLED)
        self.display_welcome_message()
        self.update_status("System Reset.")

    def clear_batch_results(self):
        self.batch_folder_path = None
        self.batch_results = []
        self.folder_path_var.set("No folder selected")
        self.batch_xor_key_var.set("")
        self.batch_scan_btn.configure(state=tk.DISABLED)
        self.batch_export_btn.configure(state=tk.DISABLED)
        self.batch_export_txt_btn.configure(state=tk.DISABLED)
        self.batch_progress.set(0)
        self.batch_status_var.set("Ready.")
        self.display_batch_welcome_message()

    def update_status(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.status_var.set(f"  [{ts}] {msg}")

    def launch_vt_scan(self):
        if not self.current_analysis_result: return
        self.vt_button.configure(state=tk.DISABLED)
        
        vt_win = ctk.CTkToplevel(self.root)
        vt_win.title("Global Threat Intel")
        vt_win.geometry("500x400")
        vt_win.grab_set()
        
        ctk.CTkLabel(vt_win, text="QUERYING THREAT DATABASE...", font=self.font_h2, text_color=COLOR_INFO).pack(pady=20)
        pbar = ctk.CTkProgressBar(vt_win, mode="indeterminate", progress_color=COLOR_INFO)
        pbar.pack(pady=10, fill=tk.X, padx=50)
        pbar.start()
        
        sv = tk.StringVar(value="Establishing secure connection...")
        ctk.CTkLabel(vt_win, textvariable=sv, font=self.font_main).pack(pady=10)
        
        ihash = self.current_analysis_result.get('file_hash')
        phash = None
        if self.current_analysis_result.get('has_hidden_data'):
            phash = hash_payload_string(self.current_analysis_result.get('hidden_message', ''))
            
        t = threading.Thread(target=self._run_vt_thread, args=(ihash, phash, vt_win, sv))
        t.daemon = True
        t.start()

    def _run_vt_thread(self, ihash, phash, win, sv):
        try:
            sv.set("Scanning carrier hash...")
            i_res = query_virustotal_hash(ihash)
            p_res = None
            if phash:
                sv.set("Scanning payload hash...")
                p_res = query_virustotal_hash(phash)
            self.root.after(0, self._render_vt_results, win, i_res, p_res)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, win.destroy)
            self.root.after(0, lambda: self.vt_button.configure(state=tk.NORMAL))

    def _render_vt_results(self, win, i_res, p_res):
        for w in win.winfo_children(): w.destroy()
        
        f = ctk.CTkFrame(win, fg_color="transparent")
        f.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        vt_data = {}
        
        ctk.CTkLabel(f, text="CARRIER IMAGE SCAN", font=self.font_bold, text_color=COLOR_INFO).pack(anchor=tk.W)
        if i_res and i_res.get('success'):
            d = i_res['data']
            c = COLOR_DANGER if d['is_threat'] else COLOR_SUCCESS
            carrier_score = f"{d['malicious']}/{d['total']}"
            vt_data['carrier_score'] = carrier_score
            ctk.CTkLabel(f, text=f"{carrier_score} Malicious", font=self.font_h2, text_color=c).pack(anchor=tk.W, pady=5)
        else:
            ctk.CTkLabel(f, text="No Intel available.", text_color="gray").pack(anchor=tk.W)
            
        if p_res:
            ctk.CTkLabel(f, text="\nPAYLOAD SCAN", font=self.font_bold, text_color=COLOR_INFO).pack(anchor=tk.W, pady=(10,0))
            if p_res.get('success'):
                d = p_res['data']
                c = COLOR_DANGER if d['is_threat'] else COLOR_SUCCESS
                payload_score = f"{d['malicious']}/{d['total']}"
                vt_data['payload_score'] = payload_score
                ctk.CTkLabel(f, text=f"{payload_score} Malicious", font=self.font_h2, text_color=c).pack(anchor=tk.W, pady=5)
            else:
                ctk.CTkLabel(f, text="No Intel available.", text_color="gray").pack(anchor=tk.W)
                
        # Save VT data to current analysis so it appears in the report
        if self.current_analysis_result:
            self.current_analysis_result['vt_results'] = vt_data
            self.display_analysis_results(self.current_analysis_result)
                
        ctk.CTkButton(f, text="CLOSE", command=win.destroy, fg_color=COLOR_SECONDARY, border_width=1, border_color=COLOR_INFO).pack(side=tk.BOTTOM, pady=20)
        self.vt_button.configure(state=tk.NORMAL)

    def show_about(self):
        from config import ABOUT_TEXT
        messagebox.showinfo("System Info", ABOUT_TEXT)

    def exit_application(self):
        if messagebox.askokcancel("System Alert", "Terminate session?"):
            self.root.quit()

def launch_gui():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")
    root = ctk.CTk()
    app = SteganographyGUI(root)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()
