"""
Main Window Module for SOC Steganography Detection Tool.
Implements the primary CustomTkinter GUI interface with modern Cyber-SOC styling.
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
from PIL import Image
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
    COLOR_SUCCESS, COLOR_SUCCESS_HOVER, COLOR_DANGER, HASH_DISPLAY_LENGTH,
    IMAGE_EXTENSIONS, BATCH_MAX_WORKERS, FONT_FAMILY,
    COLOR_BACKGROUND, COLOR_SECONDARY, COLOR_BORDER, COLOR_TEXT,
    COLOR_TEXT_MUTED, COLOR_WARNING, COLOR_INFO, COLOR_ACCENT,
    ENTROPY_THRESHOLD, LOGS_DIR
)


class SteganographyGUI:
    """Main GUI application for SOC Steganography Detection Tool."""

    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} {APP_VERSION}")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.root.configure(fg_color=COLOR_BACKGROUND)

        ctk.set_appearance_mode("dark")

        # Application state
        self.current_image_path = None
        self.current_analysis_result = None

        # Batch Application state
        self.batch_folder_path = None
        self.batch_results = []
        self.is_batch_running = False

        # Stego state tracking
        self.stego_input_file = None
        self.stego_output_file = None
        self.stego_decode_file = None
        self._stego_cached_capacity = 0

        # Thumbnail cache references to prevent garbage collection
        self._preview_images = {}

        # Fonts
        self.font_mono_small = ctk.CTkFont(family=FONT_FAMILY, size=11)
        self.font_main = ctk.CTkFont(family=FONT_FAMILY, size=12)
        self.font_bold = ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")
        self.font_h2 = ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold")
        self.font_h1 = ctk.CTkFont(family=FONT_FAMILY, size=18, weight="bold")
        self.font_banner = ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold")

        # UI Setup
        self.create_menu_bar()
        self.create_main_interface()
        self.create_status_bar()

        self.update_status("SOC Steganography Studio & Forensic Engine Initialized.")

    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0, bg=COLOR_PRIMARY, fg=COLOR_TEXT)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Select Target Image...", command=self.select_image)
        file_menu.add_separator()
        file_menu.add_command(label="Export to CSV...", command=self.export_to_csv, state=tk.DISABLED)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_application)
        self.file_menu = file_menu

        help_menu = tk.Menu(menubar, tearoff=0, bg=COLOR_PRIMARY, fg=COLOR_TEXT)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About System", command=self.show_about)

    def create_main_interface(self):
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(10, 5))

        # Primary Tabs: Covert Studio vs SOC Forensic Analyzer
        self.main_tabs = ctk.CTkTabview(
            main_frame,
            fg_color=COLOR_PRIMARY,
            segmented_button_fg_color="#0F172A",
            segmented_button_selected_color=COLOR_SUCCESS,
            segmented_button_selected_hover_color=COLOR_SUCCESS_HOVER,
            segmented_button_unselected_color="#1E293B",
            segmented_button_unselected_hover_color="#334155",
            text_color="#000000",
            corner_radius=10,
            border_width=1,
            border_color=COLOR_BORDER
        )
        self.main_tabs.pack(fill=tk.BOTH, expand=True)

        self.stego_tab = self.main_tabs.add("Steganography (Hide / Extract)")
        self.analysis_tab = self.main_tabs.add("Stego Analyzer")

        # Sub-tabs for Steganography
        self.stego_subtabs = ctk.CTkTabview(
            self.stego_tab,
            fg_color="transparent",
            segmented_button_fg_color="#0B0F19",
            segmented_button_selected_color=COLOR_ACCENT,
            segmented_button_selected_hover_color="#2563EB",
            segmented_button_unselected_color="#1E293B",
            text_color="#FFFFFF",
            corner_radius=8
        )
        self.stego_subtabs.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.encode_subtab = self.stego_subtabs.add("Encode Payload")
        self.decode_subtab = self.stego_subtabs.add("Decode Payload")

        # Sub-tabs for Stego Analyzer
        self.analysis_subtabs = ctk.CTkTabview(
            self.analysis_tab,
            fg_color="transparent",
            segmented_button_fg_color="#0B0F19",
            segmented_button_selected_color=COLOR_ACCENT,
            segmented_button_selected_hover_color="#2563EB",
            segmented_button_unselected_color="#1E293B",
            text_color="#FFFFFF",
            corner_radius=8
        )
        self.analysis_subtabs.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.single_subtab = self.analysis_subtabs.add("Single Target Scan")
        self.batch_subtab = self.analysis_subtabs.add("Batch Directory Audit")

        # Setup Views
        self.setup_encode_view()
        self.setup_decode_view()
        self.setup_single_scan_view()
        self.setup_batch_scan_view()

    # =========================================================================
    # 1. COVERT STUDIO: ENCODE VIEW
    # =========================================================================
    def setup_encode_view(self):
        scroll_container = ctk.CTkScrollableFrame(self.encode_subtab, fg_color="transparent")
        scroll_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Card 1: Carrier Ingestion Card
        carrier_card = self._create_card(scroll_container, "Carrier Image Selection")
        
        c_body = ctk.CTkFrame(carrier_card, fg_color="transparent")
        c_body.pack(fill=tk.X, padx=15, pady=10)

        # Thumbnail Preview Container
        self.enc_preview_container = ctk.CTkFrame(
            c_body, width=90, height=90, fg_color="#0B0F19",
            border_width=1, border_color=COLOR_BORDER, corner_radius=8
        )
        self.enc_preview_container.pack_propagate(False)
        self.enc_preview_container.pack(side=tk.LEFT, padx=(0, 15))
        
        self.enc_preview_label = ctk.CTkLabel(
            self.enc_preview_container, text="[No Image]", font=self.font_mono_small, text_color=COLOR_TEXT_MUTED
        )
        self.enc_preview_label.pack(expand=True)

        # Info & Choose Button
        c_info = ctk.CTkFrame(c_body, fg_color="transparent")
        c_info.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.enc_path_var = tk.StringVar(value="No carrier image chosen")
        self.enc_path_lbl = ctk.CTkLabel(
            c_info, textvariable=self.enc_path_var, font=self.font_main, text_color=COLOR_TEXT_MUTED, anchor="w"
        )
        self.enc_path_lbl.pack(fill=tk.X, anchor="w")

        self.enc_specs_var = tk.StringVar(value="Dimensions: N/A | Capacity: ~0 bytes")
        self.enc_specs_lbl = ctk.CTkLabel(
            c_info, textvariable=self.enc_specs_var, font=self.font_mono_small, text_color=COLOR_INFO, anchor="w"
        )
        self.enc_specs_lbl.pack(fill=tk.X, anchor="w", pady=(4, 8))

        ctk.CTkButton(
            c_info, text="Select Carrier Image", command=self.select_stego_input_image,
            fg_color=COLOR_SECONDARY, hover_color="#374151", border_width=1,
            border_color=COLOR_BORDER, text_color=COLOR_TEXT, font=self.font_bold, width=170
        ).pack(anchor="w")

        # Card 2: Secret Payload Editor
        payload_card = self._create_card(scroll_container, "Secret Message / Script Payload")

        p_header = ctk.CTkFrame(payload_card, fg_color="transparent")
        p_header.pack(fill=tk.X, padx=15, pady=(10, 0))

        ctk.CTkLabel(p_header, text="Payload Content:", font=self.font_bold).pack(side=tk.LEFT)
        
        self.stego_byte_capacity_var = tk.StringVar(value="0 / 0 bytes (0%)")
        self.stego_capacity_label = ctk.CTkLabel(
            p_header, textvariable=self.stego_byte_capacity_var, font=self.font_mono_small, text_color=COLOR_SUCCESS
        )
        self.stego_capacity_label.pack(side=tk.RIGHT)

        self.stego_message_tb = ctk.CTkTextbox(
            payload_card, height=130, font=self.font_mono_small,
            fg_color="#0B0F19", border_color=COLOR_BORDER, border_width=1, corner_radius=8
        )
        self.stego_message_tb.pack(fill=tk.X, padx=15, pady=(8, 6))
        self.stego_message_tb.insert("0.0", "// Enter secret message, JSON data, or script to embed...")
        self.stego_message_tb.configure(text_color=COLOR_TEXT_MUTED)

        # Capacity Progress Bar Gauge
        self.enc_capacity_bar = ctk.CTkProgressBar(
            payload_card, progress_color=COLOR_SUCCESS, fg_color="#0B0F19", height=8, corner_radius=4
        )
        self.enc_capacity_bar.pack(fill=tk.X, padx=15, pady=(0, 10))
        self.enc_capacity_bar.set(0)

        # Textbox Bindings
        def _clear_enc_placeholder(e):
            if "// Enter secret message" in self.stego_message_tb.get("0.0", "end"):
                self.stego_message_tb.delete("0.0", "end")
                self.stego_message_tb.configure(text_color=COLOR_TEXT)

        def _on_key_release_enc(e):
            self._update_encode_capacity_gauge()

        self.stego_message_tb.bind("<FocusIn>", _clear_enc_placeholder)
        self.stego_message_tb.bind("<KeyRelease>", _on_key_release_enc)

        # Card 3: Security & Output Settings
        opts_card = self._create_card(scroll_container, "Encryption & Output Destination")

        # Password row
        sec_row = ctk.CTkFrame(opts_card, fg_color="transparent")
        sec_row.pack(fill=tk.X, padx=15, pady=(10, 8))

        ctk.CTkLabel(sec_row, text="AES Encryption Passphrase (Optional):", font=self.font_bold).pack(side=tk.LEFT, padx=(0, 10))
        self.stego_pass_var = tk.StringVar()
        self.enc_pass_entry = ctk.CTkEntry(
            sec_row, textvariable=self.stego_pass_var, width=280, show="*",
            border_color=COLOR_BORDER, fg_color="#0B0F19"
        )
        self.enc_pass_entry.pack(side=tk.LEFT, padx=(0, 10))

        self.enc_show_pass_var = tk.BooleanVar(value=False)
        def _toggle_enc_pass():
            self.enc_pass_entry.configure(show="" if self.enc_show_pass_var.get() else "*")
        ctk.CTkCheckBox(sec_row, text="Show", variable=self.enc_show_pass_var, command=_toggle_enc_pass, width=60, font=self.font_mono_small).pack(side=tk.LEFT)

        # Output row
        out_row = ctk.CTkFrame(opts_card, fg_color="transparent")
        out_row.pack(fill=tk.X, padx=15, pady=(0, 12))

        ctk.CTkButton(
            out_row, text="Choose Output Path...", command=self.select_stego_output_path,
            fg_color=COLOR_SECONDARY, hover_color="#374151", border_width=1, border_color=COLOR_BORDER,
            text_color=COLOR_INFO, font=self.font_main, width=170
        ).pack(side=tk.LEFT, padx=(0, 12))

        self.stego_output_path_var = tk.StringVar(value="Default auto-generated name will be used")
        self.stego_output_display_label = ctk.CTkLabel(
            out_row, textvariable=self.stego_output_path_var, font=self.font_mono_small, text_color=COLOR_TEXT_MUTED, anchor="w"
        )
        self.stego_output_display_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Action Buttons & Execution
        act_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        act_frame.pack(fill=tk.X, pady=(10, 15))

        self.stego_encode_btn = ctk.CTkButton(
            act_frame, text="Encode & Embed Payload", command=self.start_encode,
            fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS_HOVER, text_color="#000000",
            font=self.font_h2, height=42, width=240, corner_radius=8
        )
        self.stego_encode_btn.pack(side=tk.LEFT, padx=(5, 15))

        self.stego_encode_pbar = ctk.CTkProgressBar(
            act_frame, mode="indeterminate", progress_color=COLOR_SUCCESS, height=10
        )
        self.stego_encode_pbar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.stego_encode_pbar.set(0)

    def _update_encode_capacity_gauge(self):
        if not hasattr(self, "_stego_cached_capacity") or self._stego_cached_capacity <= 0:
            self.stego_byte_capacity_var.set("0 / ~0 bytes (0%)")
            self.enc_capacity_bar.set(0)
            return

        cap = self._stego_cached_capacity
        raw_text = self.stego_message_tb.get("0.0", "end")
        if "// Enter secret message" in raw_text:
            cur = 0
        else:
            cur = len(raw_text.encode('utf-8')) - 1
            if cur < 0: cur = 0

        pct = (cur / cap) if cap > 0 else 0
        self.stego_byte_capacity_var.set(f"{cur:,} / ~{cap:,} bytes ({pct*100:.1f}%)")
        self.enc_capacity_bar.set(min(pct, 1.0))

        if pct > 1.0:
            self.stego_capacity_label.configure(text_color=COLOR_DANGER)
            self.enc_capacity_bar.configure(progress_color=COLOR_DANGER)
            self.stego_encode_btn.configure(state=tk.DISABLED)
        elif pct > 0.85:
            self.stego_capacity_label.configure(text_color=COLOR_WARNING)
            self.enc_capacity_bar.configure(progress_color=COLOR_WARNING)
            self.stego_encode_btn.configure(state=tk.NORMAL)
        else:
            self.stego_capacity_label.configure(text_color=COLOR_SUCCESS)
            self.enc_capacity_bar.configure(progress_color=COLOR_SUCCESS)
            self.stego_encode_btn.configure(state=tk.NORMAL)

    # =========================================================================
    # 2. COVERT STUDIO: DECODE VIEW
    # =========================================================================
    def setup_decode_view(self):
        scroll_container = ctk.CTkScrollableFrame(self.decode_subtab, fg_color="transparent")
        scroll_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Card 1: Stego Image Selection
        dec_card = self._create_card(scroll_container, "Stego Image Ingestion")

        d_body = ctk.CTkFrame(dec_card, fg_color="transparent")
        d_body.pack(fill=tk.X, padx=15, pady=10)

        self.dec_preview_container = ctk.CTkFrame(
            d_body, width=90, height=90, fg_color="#0B0F19",
            border_width=1, border_color=COLOR_BORDER, corner_radius=8
        )
        self.dec_preview_container.pack_propagate(False)
        self.dec_preview_container.pack(side=tk.LEFT, padx=(0, 15))

        self.dec_preview_label = ctk.CTkLabel(
            self.dec_preview_container, text="[No Image]", font=self.font_mono_small, text_color=COLOR_TEXT_MUTED
        )
        self.dec_preview_label.pack(expand=True)

        d_info = ctk.CTkFrame(d_body, fg_color="transparent")
        d_info.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.stego_decode_path_var = tk.StringVar(value="No stego image chosen")
        self.dec_path_lbl = ctk.CTkLabel(
            d_info, textvariable=self.stego_decode_path_var, font=self.font_main, text_color=COLOR_TEXT_MUTED, anchor="w"
        )
        self.dec_path_lbl.pack(fill=tk.X, anchor="w")

        self.dec_specs_var = tk.StringVar(value="Dimensions: N/A | Format: N/A")
        self.dec_specs_lbl = ctk.CTkLabel(
            d_info, textvariable=self.dec_specs_var, font=self.font_mono_small, text_color=COLOR_INFO, anchor="w"
        )
        self.dec_specs_lbl.pack(fill=tk.X, anchor="w", pady=(4, 8))

        ctk.CTkButton(
            d_info, text="Select Stego Image", command=self.select_stego_decode_image,
            fg_color=COLOR_SECONDARY, hover_color="#374151", border_width=1,
            border_color=COLOR_BORDER, text_color=COLOR_TEXT, font=self.font_bold, width=170
        ).pack(anchor="w")

        # Card 2: Password Authentication
        pass_card = self._create_card(scroll_container, "Decryption Credentials")

        pwd_row = ctk.CTkFrame(pass_card, fg_color="transparent")
        pwd_row.pack(fill=tk.X, padx=15, pady=10)

        ctk.CTkLabel(pwd_row, text="AES Passphrase (If encrypted):", font=self.font_bold).pack(side=tk.LEFT, padx=(0, 10))
        self.stego_decode_pass_var = tk.StringVar()
        self.dec_pass_entry = ctk.CTkEntry(
            pwd_row, textvariable=self.stego_decode_pass_var, width=280, show="*",
            border_color=COLOR_BORDER, fg_color="#0B0F19"
        )
        self.dec_pass_entry.pack(side=tk.LEFT, padx=(0, 10))

        self.dec_show_pass_var = tk.BooleanVar(value=False)
        def _toggle_dec_pass():
            self.dec_pass_entry.configure(show="" if self.dec_show_pass_var.get() else "*")
        ctk.CTkCheckBox(pwd_row, text="Show", variable=self.dec_show_pass_var, command=_toggle_dec_pass, width=60, font=self.font_mono_small).pack(side=tk.LEFT)

        # Action Button & Progress
        act_row = ctk.CTkFrame(scroll_container, fg_color="transparent")
        act_row.pack(fill=tk.X, pady=(10, 10))

        self.stego_decode_btn = ctk.CTkButton(
            act_row, text="Extract Hidden Message", command=self.start_decode,
            fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS_HOVER, text_color="#000000",
            font=self.font_h2, height=42, width=240, corner_radius=8
        )
        self.stego_decode_btn.pack(side=tk.LEFT, padx=(5, 15))

        self.stego_decode_pbar = ctk.CTkProgressBar(
            act_row, mode="indeterminate", progress_color=COLOR_SUCCESS, height=10
        )
        self.stego_decode_pbar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.stego_decode_pbar.set(0)

        # Card 3: Extracted Output
        out_card = self._create_card(scroll_container, "Extracted Payload")

        out_header = ctk.CTkFrame(out_card, fg_color="transparent")
        out_header.pack(fill=tk.X, padx=15, pady=(10, 0))

        self.dec_char_count_var = tk.StringVar(value="Length: 0 characters")
        ctk.CTkLabel(out_header, textvariable=self.dec_char_count_var, font=self.font_mono_small, text_color=COLOR_INFO).pack(side=tk.LEFT)

        def _copy_dec_to_clipboard():
            msg = self.stego_decoded_tb.get("0.0", "end").strip()
            if msg and "// No message decoded yet" not in msg:
                self.root.clipboard_clear()
                self.root.clipboard_append(msg)
                self.update_status("Extracted message copied to clipboard!")
                messagebox.showinfo("Clipboard", "Message copied to clipboard.")

        ctk.CTkButton(
            out_header, text="Copy to Clipboard", command=_copy_dec_to_clipboard,
            fg_color=COLOR_SECONDARY, hover_color="#374151", border_width=1, border_color=COLOR_BORDER,
            text_color=COLOR_TEXT, font=self.font_mono_small, width=130, height=26
        ).pack(side=tk.RIGHT)

        self.stego_decoded_tb = ctk.CTkTextbox(
            out_card, height=150, font=self.font_mono_small,
            fg_color="#0B0F19", border_color=COLOR_BORDER, border_width=1, corner_radius=8
        )
        self.stego_decoded_tb.pack(fill=tk.BOTH, expand=True, padx=15, pady=(8, 12))
        self.stego_decoded_tb.insert("0.0", "// No message decoded yet. Run extraction to view contents.")
        self.stego_decoded_tb.configure(text_color=COLOR_TEXT_MUTED)

    # =========================================================================
    # 3. SOC FORENSIC ANALYZER: SINGLE TARGET SCAN VIEW
    # =========================================================================
    def setup_single_scan_view(self):
        # Target Selection & Key Toolbar Card
        top_card = ctk.CTkFrame(self.single_subtab, fg_color=COLOR_PRIMARY, border_width=1, border_color=COLOR_BORDER, corner_radius=10)
        top_card.pack(fill=tk.X, padx=5, pady=(5, 8))

        top_inner = ctk.CTkFrame(top_card, fg_color="transparent")
        top_inner.pack(fill=tk.X, padx=12, pady=10)

        # Image thumbnail preview
        self.scan_preview_container = ctk.CTkFrame(
            top_inner, width=70, height=70, fg_color="#0B0F19",
            border_width=1, border_color=COLOR_BORDER, corner_radius=8
        )
        self.scan_preview_container.pack_propagate(False)
        self.scan_preview_container.pack(side=tk.LEFT, padx=(0, 12))

        self.scan_preview_label = ctk.CTkLabel(
            self.scan_preview_container, text="[Target]", font=self.font_mono_small, text_color=COLOR_TEXT_MUTED
        )
        self.scan_preview_label.pack(expand=True)

        # Target Path & Passphrase Info
        info_col = ctk.CTkFrame(top_inner, fg_color="transparent")
        info_col.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.file_path_var = tk.StringVar(value="No target image selected")
        ctk.CTkLabel(info_col, textvariable=self.file_path_var, font=self.font_bold, text_color=COLOR_TEXT, anchor="w").pack(fill=tk.X)

        key_row = ctk.CTkFrame(info_col, fg_color="transparent")
        key_row.pack(fill=tk.X, pady=(6, 0))

        ctk.CTkLabel(key_row, text="Decryption Passphrase (Optional):", font=self.font_mono_small, text_color=COLOR_TEXT_MUTED).pack(side=tk.LEFT, padx=(0, 8))
        self.xor_key_var = tk.StringVar()
        ctk.CTkEntry(
            key_row, textvariable=self.xor_key_var, width=200, height=28,
            font=self.font_mono_small, border_color=COLOR_BORDER, fg_color="#0B0F19"
        ).pack(side=tk.LEFT, padx=(0, 10))

        ctk.CTkButton(
            top_inner, text="Select Target Image", command=self.select_image,
            fg_color=COLOR_SECONDARY, hover_color="#374151", border_width=1,
            border_color=COLOR_SUCCESS, text_color=COLOR_SUCCESS, font=self.font_bold, width=160, height=36
        ).pack(side=tk.RIGHT, padx=(10, 0))

        # Action Toolbar
        action_bar = ctk.CTkFrame(self.single_subtab, fg_color="transparent")
        action_bar.pack(fill=tk.X, padx=5, pady=(0, 8))

        self.analyze_button = ctk.CTkButton(
            action_bar, text="Scan Target", command=self.analyze_current_image,
            state=tk.DISABLED, fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS_HOVER,
            text_color="#000000", font=self.font_bold, width=130, height=32, corner_radius=6
        )
        self.analyze_button.pack(side=tk.LEFT, padx=(0, 8))

        self.export_button = ctk.CTkButton(
            action_bar, text="Export CSV", command=self.export_to_csv,
            state=tk.DISABLED, fg_color=COLOR_SECONDARY, hover_color="#374151",
            border_width=1, border_color=COLOR_INFO, text_color=COLOR_INFO, font=self.font_main, width=110, height=32
        )
        self.export_button.pack(side=tk.LEFT, padx=(0, 8))

        self.export_txt_button = ctk.CTkButton(
            action_bar, text="Export TXT", command=self.export_to_txt,
            state=tk.DISABLED, fg_color=COLOR_SECONDARY, hover_color="#374151",
            border_width=1, border_color=COLOR_INFO, text_color=COLOR_INFO, font=self.font_main, width=110, height=32
        )
        self.export_txt_button.pack(side=tk.LEFT, padx=(0, 8))

        self.vt_button = ctk.CTkButton(
            action_bar, text="VirusTotal Threat Scan", command=self.launch_vt_scan,
            state=tk.DISABLED, fg_color=COLOR_SECONDARY, hover_color="#374151",
            border_width=1, border_color=COLOR_WARNING, text_color=COLOR_WARNING, font=self.font_main, width=180, height=32
        )
        self.vt_button.pack(side=tk.LEFT, padx=(0, 8))

        ctk.CTkButton(
            action_bar, text="Reset", command=self.clear_results,
            fg_color=COLOR_SECONDARY, hover_color=COLOR_DANGER, font=self.font_main, width=80, height=32
        ).pack(side=tk.RIGHT)

        # Forensic Results Container (Scrollable)
        self.results_container = ctk.CTkScrollableFrame(
            self.single_subtab, fg_color=COLOR_PRIMARY, corner_radius=10,
            border_width=1, border_color=COLOR_BORDER
        )
        self.results_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        self.display_welcome_message()

    # =========================================================================
    # 4. SOC FORENSIC ANALYZER: BATCH DIRECTORY AUDIT VIEW
    # =========================================================================
    def setup_batch_scan_view(self):
        # Folder Ingestion Card
        folder_card = ctk.CTkFrame(self.batch_subtab, fg_color=COLOR_PRIMARY, border_width=1, border_color=COLOR_BORDER, corner_radius=10)
        folder_card.pack(fill=tk.X, padx=5, pady=(5, 8))

        f_inner = ctk.CTkFrame(folder_card, fg_color="transparent")
        f_inner.pack(fill=tk.X, padx=15, pady=12)

        ctk.CTkLabel(f_inner, text="Target Directory:", font=self.font_bold).pack(side=tk.LEFT, padx=(0, 10))

        self.folder_path_var = tk.StringVar(value="No directory selected for audit")
        ctk.CTkLabel(
            f_inner, textvariable=self.folder_path_var, text_color=COLOR_TEXT_MUTED,
            font=self.font_mono_small, anchor="w"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        ctk.CTkButton(
            f_inner, text="Select Directory", command=self.select_batch_folder,
            fg_color=COLOR_SECONDARY, hover_color="#374151", border_width=1,
            border_color=COLOR_SUCCESS, text_color=COLOR_SUCCESS, font=self.font_bold, width=160
        ).pack(side=tk.RIGHT)

        # Batch Options & Action Bar
        opt_card = ctk.CTkFrame(self.batch_subtab, fg_color="transparent")
        opt_card.pack(fill=tk.X, padx=5, pady=(0, 8))

        self.batch_scan_btn = ctk.CTkButton(
            opt_card, text="Start Batch Audit", command=self.start_batch_scan,
            state=tk.DISABLED, fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS_HOVER,
            text_color="#000000", font=self.font_bold, width=170, height=34
        )
        self.batch_scan_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.batch_export_btn = ctk.CTkButton(
            opt_card, text="Export CSV Audit Report", command=self.export_batch_csv,
            state=tk.DISABLED, fg_color=COLOR_SECONDARY, hover_color="#374151",
            border_width=1, border_color=COLOR_INFO, text_color=COLOR_INFO, font=self.font_main
        )
        self.batch_export_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.batch_export_txt_btn = ctk.CTkButton(
            opt_card, text="Export TXT Report", command=self.export_batch_txt,
            state=tk.DISABLED, fg_color=COLOR_SECONDARY, hover_color="#374151",
            border_width=1, border_color=COLOR_INFO, text_color=COLOR_INFO, font=self.font_main
        )
        self.batch_export_txt_btn.pack(side=tk.LEFT, padx=(0, 10))

        ctk.CTkButton(
            opt_card, text="Reset Audit", command=self.clear_batch_results,
            fg_color=COLOR_SECONDARY, hover_color=COLOR_DANGER, font=self.font_main, width=100
        ).pack(side=tk.RIGHT)

        # Progress Bar Card
        prog_card = ctk.CTkFrame(self.batch_subtab, fg_color=COLOR_PRIMARY, border_width=1, border_color=COLOR_BORDER, corner_radius=8)
        prog_card.pack(fill=tk.X, padx=5, pady=(0, 8))

        p_inner = ctk.CTkFrame(prog_card, fg_color="transparent")
        p_inner.pack(fill=tk.X, padx=15, pady=8)

        self.batch_progress_var = tk.DoubleVar(value=0)
        self.batch_progress = ctk.CTkProgressBar(p_inner, variable=self.batch_progress_var, progress_color=COLOR_SUCCESS, height=8)
        self.batch_progress.pack(fill=tk.X, pady=(0, 4))
        self.batch_progress.set(0)

        self.batch_status_var = tk.StringVar(value="Audit Ready.")
        ctk.CTkLabel(p_inner, textvariable=self.batch_status_var, text_color=COLOR_SUCCESS, font=self.font_mono_small).pack(anchor=tk.W)

        # Batch Results Dashboard Frame
        self.batch_results_container = ctk.CTkScrollableFrame(
            self.batch_subtab, fg_color=COLOR_PRIMARY, corner_radius=10,
            border_width=1, border_color=COLOR_BORDER
        )
        self.batch_results_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        self.display_batch_welcome_message()

    # =========================================================================
    # UI HELPER: CARD CREATOR & THUMBNAIL RENDERING
    # =========================================================================
    def _create_card(self, parent, title):
        card = ctk.CTkFrame(parent, fg_color=COLOR_PRIMARY, border_width=1, border_color=COLOR_BORDER, corner_radius=10)
        card.pack(fill=tk.X, pady=(0, 10))
        
        header = ctk.CTkFrame(card, fg_color="#1E293B", corner_radius=8)
        header.pack(fill=tk.X, padx=5, pady=(5, 0))
        ctk.CTkLabel(header, text=f" {title.upper()}", font=self.font_bold, text_color=COLOR_TEXT).pack(anchor=tk.W, padx=8, pady=4)
        return card

    def _render_thumbnail(self, image_path, container, label_widget, max_size=(80, 80)):
        """Renders an image thumbnail smoothly into the target preview container."""
        try:
            pil_img = Image.open(image_path)
            orig_w, orig_h = pil_img.size
            
            # Calculate thumbnail size maintaining aspect ratio
            pil_img.thumbnail(max_size, Image.Resampling.LANCZOS)
            thumb_w, thumb_h = pil_img.size
            
            ctk_thumb = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(thumb_w, thumb_h))
            self._preview_images[container] = ctk_thumb  # Prevent GC
            
            label_widget.configure(image=ctk_thumb, text="")
            return orig_w, orig_h, pil_img.format
        except Exception:
            label_widget.configure(image=None, text="[Preview N/A]")
            return None, None, None

    # =========================================================================
    # EVENT HANDLERS & STEGANOGRAPHY LOGIC
    # =========================================================================
    def _truncate_path(self, path, max_len=55):
        if len(path) <= max_len: return path
        return "..." + path[-(max_len - 3):]

    def select_stego_input_image(self):
        path = select_image_file()
        if path:
            self.stego_input_file = path
            self.enc_path_var.set(self._truncate_path(path))
            w, h, fmt = self._render_thumbnail(path, self.enc_preview_container, self.enc_preview_label)
            if w and h:
                cap = (w * h * 3) // 8
                self._stego_cached_capacity = cap
                self.enc_specs_var.set(f"Dimensions: {w}x{h} | Format: {fmt} | Max Capacity: ~{cap:,} bytes")
            else:
                self._stego_cached_capacity = 0
                self.enc_specs_var.set("Dimensions: N/A | Capacity: ~0 bytes")
            self._update_encode_capacity_gauge()
            self.update_status(f"Loaded carrier: {os.path.basename(path)}")

    def select_stego_output_path(self):
        default_name = f"stego_out_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        path = filedialog.asksaveasfilename(
            initialdir=LOGS_DIR, initialfile=default_name, defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("BMP files", "*.bmp"), ("All files", "*.*")]
        )
        if path:
            self.stego_output_file = path
            self.stego_output_path_var.set(self._truncate_path(path))
            self.update_status(f"Output destination: {os.path.basename(path)}")

    def select_stego_decode_image(self):
        path = select_image_file()
        if path:
            self.stego_decode_file = path
            self.stego_decode_path_var.set(self._truncate_path(path))
            w, h, fmt = self._render_thumbnail(path, self.dec_preview_container, self.dec_preview_label)
            if w and h:
                self.dec_specs_var.set(f"Dimensions: {w}x{h} | Format: {fmt}")
            self.update_status(f"Loaded stego target: {os.path.basename(path)}")

    def start_encode(self):
        inp = self.stego_input_file
        out = self.stego_output_file
        if not out:
            out = os.path.join(LOGS_DIR, f"stego_out_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            self.stego_output_file = out

        msg = self.stego_message_tb.get("0.0", "end").strip()
        pwd = self.stego_pass_var.get().strip() or None

        if not inp or not os.path.exists(inp):
            messagebox.showwarning("Missing Carrier", "Please select a valid carrier image to embed data into.")
            return
        if not msg or "// Enter secret message" in msg:
            messagebox.showwarning("Missing Payload", "Please enter a message or script to embed.")
            return

        self.stego_encode_btn.configure(state=tk.DISABLED)
        self.update_status("Embedding secret payload into carrier image...")
        try: self.stego_encode_pbar.start()
        except: pass

        t = threading.Thread(target=self._run_encode_thread, args=(inp, msg, out, pwd))
        t.daemon = True
        t.start()

    def _run_encode_thread(self, inp, msg, out, pwd):
        try:
            encode_message(inp, msg, out, password=pwd)
            self.root.after(0, lambda: messagebox.showinfo("Encoding Complete", f"Stego image successfully created:\n\n{out}"))
            self.root.after(0, lambda: self.update_status(f"Successfully created stego image: {os.path.basename(out)}"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Encoding Error", f"Failed to encode payload:\n{str(e)}"))
            self.root.after(0, lambda: self.update_status("Encoding failed."))
        finally:
            self.root.after(0, lambda: self.stego_encode_btn.configure(state=tk.NORMAL))
            self.root.after(0, lambda: self.stego_encode_pbar.stop())

    def start_decode(self):
        inp = self.stego_decode_file
        pwd = self.stego_decode_pass_var.get().strip() or None

        if not inp or not os.path.exists(inp):
            messagebox.showwarning("Missing Target", "Please select a stego image to extract payload from.")
            return

        self.stego_decode_btn.configure(state=tk.DISABLED)
        self.update_status("Extracting and decrypting payload...")
        try: self.stego_decode_pbar.start()
        except: pass

        t = threading.Thread(target=self._run_decode_thread, args=(inp, pwd))
        t.daemon = True
        t.start()

    def _run_decode_thread(self, inp, pwd):
        try:
            res = decode_message(inp, password=pwd)
            self.root.after(0, lambda: self.stego_decoded_tb.delete("0.0", "end"))
            self.root.after(0, lambda: self.stego_decoded_tb.insert("0.0", res))
            self.root.after(0, lambda: self.stego_decoded_tb.configure(text_color=COLOR_TEXT))
            self.root.after(0, lambda: self.dec_char_count_var.set(f"Extracted Payload: {len(res):,} characters ({len(res.encode()):,} bytes)"))
            self.root.after(0, lambda: self.update_status(f"Extraction successful ({len(res)} characters)."))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Extraction Error", f"Extraction failed:\n{str(e)}"))
            self.root.after(0, lambda: self.update_status("Extraction failed."))
        finally:
            self.root.after(0, lambda: self.stego_decode_btn.configure(state=tk.NORMAL))
            self.root.after(0, lambda: self.stego_decode_pbar.stop())

    # =========================================================================
    # STEGANALYSIS SINGLE TARGET SCAN
    # =========================================================================
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
            self.file_path_var.set(self._truncate_path(file_path))
            self._render_thumbnail(file_path, self.scan_preview_container, self.scan_preview_label)
            self.analyze_button.configure(state=tk.NORMAL)
            self.update_status(f"Target selected: {os.path.basename(file_path)}")

    def analyze_current_image(self):
        if not self.current_image_path:
            messagebox.showwarning("No Target", "Please select a target image to scan.")
            return

        self.show_loading_indicator()
        self.update_status("Executing deep steganographic analysis...")
        self.analyze_button.configure(state=tk.DISABLED)
        self.export_button.configure(state=tk.DISABLED)
        self.export_txt_button.configure(state=tk.DISABLED)
        self.root.update_idletasks()

        xor_key = self.xor_key_var.get().strip() or None
        t = threading.Thread(target=self._run_analysis_thread, args=(self.current_image_path, xor_key))
        t.daemon = True
        t.start()

    def _run_analysis_thread(self, file_path, decode_key):
        try:
            result = analyze_image(file_path, decode_key)
            self.root.after(0, self._handle_analysis_complete, result)
        except Exception as e:
            self.root.after(0, self._handle_analysis_error, str(e))

    def _handle_analysis_complete(self, result):
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
            self.update_status("CRITICAL: Covert payload signature detected in target!")
        else:
            self.update_status("Scan Complete: No covert payload detected.")

        self.analyze_button.configure(state=tk.NORMAL)

    def _handle_analysis_error(self, error_msg):
        messagebox.showerror("Scan Error", f"Analysis failed:\n{error_msg}")
        self.update_status("Scan failed.")
        self.display_welcome_message()
        self.analyze_button.configure(state=tk.NORMAL)

    def show_loading_indicator(self):
        for widget in self.results_container.winfo_children(): widget.destroy()

        load_frame = ctk.CTkFrame(self.results_container, fg_color="transparent")
        load_frame.pack(expand=True, fill=tk.BOTH, pady=40)

        ctk.CTkLabel(load_frame, text="SCANNING TARGET LSB & CALCULATING ENTROPY...", font=self.font_h2, text_color=COLOR_INFO).pack(pady=(10, 15))
        pbar = ctk.CTkProgressBar(load_frame, mode="indeterminate", progress_color=COLOR_INFO, width=350)
        pbar.pack(pady=10)
        pbar.start()

    def display_welcome_message(self):
        for widget in self.results_container.winfo_children(): widget.destroy()

        welcome_card = ctk.CTkFrame(self.results_container, fg_color="#0F172A", border_width=1, border_color=COLOR_BORDER, corner_radius=10)
        welcome_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=15)

        ctk.CTkLabel(welcome_card, text="STEGO ANALYZER FORENSIC DASHBOARD", font=self.font_h1, text_color=COLOR_SUCCESS).pack(pady=(25, 10))
        
        intro = (
            "Select a target carrier image to begin deep forensic examination.\n\n"
            "Forensic Engine Capabilities:\n"
            "• Header & Signature Extraction (V2 SOC Protocol)\n"
            "• Sliding-Window Bitstream EOF Pattern Matching\n"
            "• 7-Layer Heuristic Garbage Filtering\n"
            "• LSB Shannon Entropy Distribution (Randomness Gauge)\n"
            "• Global Threat Intelligence Cross-Referencing (VirusTotal v3 API)"
        )
        ctk.CTkLabel(welcome_card, text=intro, font=self.font_main, justify=tk.LEFT, text_color=COLOR_TEXT_MUTED).pack(padx=25, pady=(0, 20), anchor=tk.W)

    def display_analysis_results(self, result):
        for widget in self.results_container.winfo_children(): widget.destroy()

        has_hidden_data = result.get('has_hidden_data', False)
        status = result.get('status', 'unknown')
        entropy = result.get('entropy_score', 0.0)

        # Verdict Determination
        if status == 'error':
            verdict_text = "ERROR: FORENSIC ANALYSIS FAILED"
            verdict_color = COLOR_DANGER
        elif has_hidden_data:
            verdict_text = "CRITICAL: COVERT PAYLOAD SIGNATURE DETECTED"
            verdict_color = COLOR_DANGER
        elif entropy >= ENTROPY_THRESHOLD:
            verdict_text = f"SUSPICIOUS: HIGH ENTROPY ANOMALY DETECTED ({entropy:.4f})"
            verdict_color = COLOR_WARNING
        else:
            verdict_text = "CLEAN: NO STEGANOGRAPHY SIGNATURES DETECTED"
            verdict_color = COLOR_SUCCESS

        # 1. Verdict Banner
        banner = ctk.CTkFrame(self.results_container, fg_color=verdict_color, corner_radius=8)
        banner.pack(fill=tk.X, padx=8, pady=(5, 12))
        ctk.CTkLabel(banner, text=verdict_text, font=self.font_banner, text_color="#000000", pady=8).pack()

        # 2. File & Metadata Card
        file_card = self._create_card(self.results_container, "Target File Telemetry")
        f_grid = ctk.CTkFrame(file_card, fg_color="transparent")
        f_grid.pack(fill=tk.X, padx=12, pady=8)

        file_path = result.get('file_path', 'N/A')
        meta = result.get('metadata', {})

        self._add_metric_row(f_grid, "File Name:", os.path.basename(file_path))
        self._add_metric_row(f_grid, "Full Path:", file_path)
        self._add_metric_row(f_grid, "File Size:", f"{result.get('file_size', 0):,} bytes")
        self._add_metric_row(f_grid, "SHA-256 Checksum:", result.get('file_hash', 'N/A'), val_color=COLOR_INFO)
        self._add_metric_row(f_grid, "Image Specs:", f"{meta.get('dimensions', 'N/A')} ({meta.get('mode', 'N/A')}) | Max Capacity: {meta.get('max_capacity_bytes', 0):,} bytes")

        # 3. Stego Engine & Entropy Analysis Card
        engine_card = self._create_card(self.results_container, "Steganalysis & Randomness Metrics")
        e_grid = ctk.CTkFrame(engine_card, fg_color="transparent")
        e_grid.pack(fill=tk.X, padx=12, pady=8)

        ent_color = COLOR_DANGER if entropy >= ENTROPY_THRESHOLD else COLOR_SUCCESS
        self._add_metric_row(e_grid, "Detection Verdict:", "POSITIVE (Threat Found)" if has_hidden_data else "NEGATIVE (Clean)", val_color=verdict_color)
        self._add_metric_row(e_grid, "LSB Shannon Entropy:", f"{entropy:.4f} / 8.0000 (Anomaly Threshold: {ENTROPY_THRESHOLD})", val_color=ent_color)

        # Visual Entropy Bar
        ent_bar_frame = ctk.CTkFrame(engine_card, fg_color="transparent")
        ent_bar_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        ent_prog = ctk.CTkProgressBar(ent_bar_frame, progress_color=ent_color, height=8)
        ent_prog.pack(fill=tk.X)
        ent_prog.set(entropy / 8.0)

        # 4. Extracted Payload Preview Card (if payload found)
        if has_hidden_data:
            payload_card = self._create_card(self.results_container, "Extracted Payload Content")
            
            p_top = ctk.CTkFrame(payload_card, fg_color="transparent")
            p_top.pack(fill=tk.X, padx=12, pady=(6, 0))

            def _copy_payload():
                msg = result.get('hidden_message', '')
                if msg:
                    self.root.clipboard_clear()
                    self.root.clipboard_append(msg)
                    self.update_status("Payload copied to clipboard!")
                    messagebox.showinfo("Clipboard", "Payload copied to clipboard.")

            ctk.CTkButton(
                p_top, text="Copy Payload", command=_copy_payload,
                fg_color=COLOR_SECONDARY, hover_color="#374151", border_width=1,
                border_color=COLOR_BORDER, text_color=COLOR_TEXT, font=self.font_mono_small, width=110, height=24
            ).pack(side=tk.RIGHT)

            tb = ctk.CTkTextbox(
                payload_card, height=100, font=self.font_mono_small,
                fg_color="#0B0F19", border_color=COLOR_BORDER, border_width=1, text_color=COLOR_DANGER
            )
            tb.pack(fill=tk.X, padx=12, pady=(6, 10))
            tb.insert("0.0", result.get('hidden_message', ''))
            tb.configure(state=tk.DISABLED)

        # 5. Global Threat Intelligence (VirusTotal) Card
        vt_card = self._create_card(self.results_container, "Global Threat Intelligence (VirusTotal)")
        v_grid = ctk.CTkFrame(vt_card, fg_color="transparent")
        v_grid.pack(fill=tk.X, padx=12, pady=8)

        vt_results = result.get('vt_results')
        if vt_results:
            carrier_score = vt_results.get('carrier_score', 'N/A')
            c_color = COLOR_DANGER if "0/" not in carrier_score and carrier_score != "N/A" else COLOR_SUCCESS
            self._add_metric_row(v_grid, "Carrier Image Threat Score:", carrier_score, val_color=c_color)

            payload_score = vt_results.get('payload_score', 'N/A')
            if payload_score != 'N/A':
                p_color = COLOR_DANGER if "0/" not in payload_score else COLOR_SUCCESS
                self._add_metric_row(v_grid, "Payload Hash Threat Score:", payload_score, val_color=p_color)
        else:
            self._add_metric_row(v_grid, "VirusTotal Status:", "Threat Scan Not Performed Yet (Click 'VirusTotal Threat Scan' above)", val_color=COLOR_TEXT_MUTED)

    def _add_metric_row(self, parent, label, value, val_color=None):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill=tk.X, pady=2)
        ctk.CTkLabel(row, text=label, font=self.font_bold, text_color=COLOR_SUCCESS, width=220, anchor="w").pack(side=tk.LEFT, padx=(4, 8))
        v_col = val_color if val_color else COLOR_TEXT
        ctk.CTkLabel(row, text=str(value), font=self.font_mono_small, text_color=v_col, anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)

    # =========================================================================
    # BATCH SCAN ENGINE
    # =========================================================================
    def display_batch_welcome_message(self):
        for widget in self.batch_results_container.winfo_children(): widget.destroy()
        card = ctk.CTkFrame(self.batch_results_container, fg_color="#0F172A", border_width=1, border_color=COLOR_BORDER, corner_radius=10)
        card.pack(fill=tk.BOTH, expand=True, padx=10, pady=15)
        ctk.CTkLabel(card, text="MASS DIRECTORY FORENSIC AUDIT", font=self.font_h1, text_color=COLOR_SUCCESS).pack(pady=(20, 8))
        ctk.CTkLabel(card, text="Select a target directory above to run parallel multithreaded steganography detection across all images.", font=self.font_main, text_color=COLOR_TEXT_MUTED).pack(padx=20, pady=(0, 20))

    def select_batch_folder(self):
        folder_path = select_folder()
        if folder_path:
            self.batch_folder_path = folder_path
            self.folder_path_var.set(self._truncate_path(folder_path, 65))
            self.batch_scan_btn.configure(state=tk.NORMAL)
            self.update_status(f"Target directory locked: {os.path.basename(folder_path)}")

    def start_batch_scan(self):
        if not self.batch_folder_path: return
        self.is_batch_running = True
        self.batch_results = []
        self.batch_scan_btn.configure(state=tk.DISABLED)

        images = []
        for root, _, files in os.walk(self.batch_folder_path):
            for file in files:
                if os.path.splitext(file)[1].lower() in IMAGE_EXTENSIONS:
                    images.append(os.path.join(root, file))

        total = len(images)
        if total == 0:
            messagebox.showinfo("Empty Directory", "No supported image files found in selected directory.")
            self.batch_scan_btn.configure(state=tk.NORMAL)
            return

        self.batch_progress_var.set(0)
        self.batch_status_var.set(f"Auditing {total} targets in parallel...")
        self._update_batch_dashboard(0, total, 0, 0, 0)

        t = threading.Thread(target=self._run_batch_thread, args=(images, total))
        t.daemon = True
        t.start()

    def _run_batch_thread(self, images, total):
        processed = flagged = clean = errors = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=BATCH_MAX_WORKERS) as executor:
            future_to_file = {executor.submit(analyze_image, path, None): path for path in images}
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

    def _update_batch_progress(self, processed, total, flagged, clean, errors):
        prog = processed / total if total > 0 else 0
        self.batch_progress.set(prog)
        self.batch_status_var.set(f"Auditing... {processed}/{total} images processed")
        self._update_batch_dashboard(processed, total, flagged, clean, errors)

    def _update_batch_dashboard(self, processed, total, flagged, clean, errors, complete=False):
        for widget in self.batch_results_container.winfo_children(): widget.destroy()

        if complete:
            b_text = f"AUDIT COMPLETE: {flagged} THREATS IDENTIFIED" if flagged else "AUDIT COMPLETE: ALL TARGETS CLEAN"
            b_color = COLOR_DANGER if flagged else COLOR_SUCCESS
        else:
            b_text = f"AUDIT IN PROGRESS: {processed} / {total} SCANNED"
            b_color = COLOR_INFO

        banner = ctk.CTkFrame(self.batch_results_container, fg_color=b_color, corner_radius=8)
        banner.pack(fill=tk.X, padx=8, pady=(5, 12))
        ctk.CTkLabel(banner, text=b_text, font=self.font_banner, text_color="#000000", pady=8).pack()

        stat_card = self._create_card(self.batch_results_container, "Audit Statistics")
        s_grid = ctk.CTkFrame(stat_card, fg_color="transparent")
        s_grid.pack(fill=tk.X, padx=12, pady=8)

        self._add_metric_row(s_grid, "Total Images Ingested:", f"{processed} / {total}")
        self._add_metric_row(s_grid, "Threats Flagged:", str(flagged), val_color=COLOR_DANGER if flagged else COLOR_TEXT)
        self._add_metric_row(s_grid, "Clean Targets:", str(clean), val_color=COLOR_SUCCESS)
        self._add_metric_row(s_grid, "Processing Errors:", str(errors), val_color=COLOR_WARNING if errors else COLOR_TEXT_MUTED)

    def _handle_batch_complete(self):
        self.batch_status_var.set("AUDIT COMPLETED. Reports ready for export.")
        self.batch_scan_btn.configure(state=tk.NORMAL)
        self.batch_export_btn.configure(state=tk.NORMAL)
        self.batch_export_txt_btn.configure(state=tk.NORMAL)

        flagged = sum(1 for r in self.batch_results if r.get('has_hidden_data'))
        clean = sum(1 for r in self.batch_results if not r.get('has_hidden_data') and r.get('status') != 'error')
        errors = sum(1 for r in self.batch_results if r.get('status') == 'error')
        self._update_batch_dashboard(len(self.batch_results), len(self.batch_results), flagged, clean, errors, complete=True)

    def clear_batch_results(self):
        self.batch_folder_path = None
        self.batch_results = []
        self.folder_path_var.set("No directory selected for audit")
        self.batch_scan_btn.configure(state=tk.DISABLED)
        self.batch_export_btn.configure(state=tk.DISABLED)
        self.batch_export_txt_btn.configure(state=tk.DISABLED)
        self.batch_progress.set(0)
        self.batch_status_var.set("Audit Ready.")
        self.display_batch_welcome_message()

    # =========================================================================
    # VIRUSTOTAL THREAT INTEL MODAL
    # =========================================================================
    def launch_vt_scan(self):
        if not self.current_analysis_result: return
        self.vt_button.configure(state=tk.DISABLED)

        vt_win = ctk.CTkToplevel(self.root)
        vt_win.title("VirusTotal Global Threat Intelligence")
        vt_win.geometry("520x420")
        vt_win.configure(fg_color=COLOR_BACKGROUND)
        vt_win.grab_set()

        ctk.CTkLabel(vt_win, text="QUERYING VIRUSTOTAL DATABASE...", font=self.font_h2, text_color=COLOR_INFO).pack(pady=(20, 10))
        pbar = ctk.CTkProgressBar(vt_win, mode="indeterminate", progress_color=COLOR_INFO, width=380)
        pbar.pack(pady=10)
        pbar.start()

        sv = tk.StringVar(value="Establishing secure API connection...")
        ctk.CTkLabel(vt_win, textvariable=sv, font=self.font_mono_small, text_color=COLOR_TEXT_MUTED).pack(pady=10)

        ihash = self.current_analysis_result.get('file_hash')
        phash = None
        if self.current_analysis_result.get('has_hidden_data'):
            payload_to_hash = self.current_analysis_result.get('raw_payload', self.current_analysis_result.get('hidden_message', ''))
            phash = hash_payload_string(payload_to_hash)

        t = threading.Thread(target=self._run_vt_thread, args=(ihash, phash, vt_win, sv))
        t.daemon = True
        t.start()

    def _run_vt_thread(self, ihash, phash, win, sv):
        try:
            sv.set("Scanning carrier image hash...")
            i_res = query_virustotal_hash(ihash)
            p_res = None
            if phash:
                sv.set("Scanning extracted payload hash...")
                p_res = query_virustotal_hash(phash)
            self.root.after(0, self._render_vt_results, win, i_res, p_res)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("API Error", str(e)))
            self.root.after(0, win.destroy)
            self.root.after(0, lambda: self.vt_button.configure(state=tk.NORMAL))

    def _render_vt_results(self, win, i_res, p_res):
        for w in win.winfo_children(): w.destroy()

        f = ctk.CTkFrame(win, fg_color="transparent")
        f.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        vt_data = {}

        # Carrier section
        c_card = self._create_card(f, "Carrier Image Scan")
        c_body = ctk.CTkFrame(c_card, fg_color="transparent")
        c_body.pack(fill=tk.X, padx=12, pady=10)

        if i_res and i_res.get('success'):
            d = i_res['data']
            col = COLOR_DANGER if d['is_threat'] else COLOR_SUCCESS
            carrier_score = f"{d['malicious']}/{d['total']} Vendors Flagged"
            vt_data['carrier_score'] = carrier_score
            ctk.CTkLabel(c_body, text=carrier_score, font=self.font_h2, text_color=col).pack(anchor=tk.W)
        else:
            err = i_res.get('error', 'No intel available in database.') if i_res else 'Not queried.'
            ctk.CTkLabel(c_body, text=err, font=self.font_mono_small, text_color=COLOR_TEXT_MUTED).pack(anchor=tk.W)

        # Payload section
        if p_res:
            p_card = self._create_card(f, "Extracted Payload Scan")
            p_body = ctk.CTkFrame(p_card, fg_color="transparent")
            p_body.pack(fill=tk.X, padx=12, pady=10)

            if p_res.get('success'):
                d = p_res['data']
                col = COLOR_DANGER if d['is_threat'] else COLOR_SUCCESS
                payload_score = f"{d['malicious']}/{d['total']} Vendors Flagged"
                vt_data['payload_score'] = payload_score
                ctk.CTkLabel(p_body, text=payload_score, font=self.font_h2, text_color=col).pack(anchor=tk.W)
            else:
                err = p_res.get('error', 'No intel available in database.') if p_res else 'Not queried.'
                ctk.CTkLabel(p_body, text=err, font=self.font_mono_small, text_color=COLOR_TEXT_MUTED).pack(anchor=tk.W)

        if self.current_analysis_result:
            self.current_analysis_result['vt_results'] = vt_data
            self.display_analysis_results(self.current_analysis_result)

        ctk.CTkButton(
            f, text="Close", command=win.destroy, fg_color=COLOR_SECONDARY,
            hover_color="#374151", border_width=1, border_color=COLOR_BORDER, width=120, height=32
        ).pack(side=tk.BOTTOM, pady=(15, 0))
        self.vt_button.configure(state=tk.NORMAL)

    # =========================================================================
    # EXPORT & UTILITY HANDLERS
    # =========================================================================
    def export_to_csv(self):
        if not self.current_analysis_result: return
        try:
            res = log_analysis_to_csv(self.current_analysis_result)
            if res['success']:
                messagebox.showinfo("Export Complete", f"Scan logged to CSV audit record:\n{res['csv_path']}")
                self.update_status(f"Exported to: {os.path.basename(res['csv_path'])}")
            else:
                messagebox.showerror("Export Failed", str(res.get('error')))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_to_txt(self):
        if not self.current_analysis_result: return
        try:
            default_name = f"stego_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            path = filedialog.asksaveasfilename(
                initialdir=LOGS_DIR, initialfile=default_name, defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if not path: return
            res = export_single_analysis_to_txt(self.current_analysis_result, path)
            if res.get('success'):
                messagebox.showinfo("Export Complete", f"Report saved:\n{res['txt_path']}")
                self.update_status(f"Exported TXT report: {os.path.basename(res['txt_path'])}")
            else:
                messagebox.showerror("Export Failed", str(res.get('error')))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_batch_csv(self):
        if not self.batch_results: return
        try:
            res = log_batch_results(self.batch_results)
            if res.get('success'):
                messagebox.showinfo("Export Complete", f"Batch audit saved:\n{res['csv_path']}")
                self.update_status(f"Exported batch CSV: {os.path.basename(res['csv_path'])}")
            else:
                messagebox.showerror("Export Failed", str(res.get('error')))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_batch_txt(self):
        if not self.batch_results: return
        try:
            default_name = f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            path = filedialog.asksaveasfilename(
                initialdir=LOGS_DIR, initialfile=default_name, defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if not path: return
            res = export_batch_analysis_to_txt(self.batch_results, path)
            if res.get('success'):
                messagebox.showinfo("Export Complete", f"Batch report saved:\n{res['txt_path']}")
                self.update_status(f"Exported batch TXT: {os.path.basename(res['txt_path'])}")
            else:
                messagebox.showerror("Export Failed", str(res.get('error')))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_results(self):
        self.current_image_path = None
        self.current_analysis_result = None
        self.file_path_var.set("No target image selected")
        self.xor_key_var.set("")
        self.scan_preview_label.configure(image=None, text="[Target]")
        self.analyze_button.configure(state=tk.DISABLED)
        self.export_button.configure(state=tk.DISABLED)
        self.export_txt_button.configure(state=tk.DISABLED)
        self.vt_button.configure(state=tk.DISABLED)
        self.display_welcome_message()
        self.update_status("Target state cleared. Ready for next scan.")

    def create_status_bar(self):
        self.status_var = tk.StringVar()
        status_bar = ctk.CTkLabel(
            self.root, textvariable=self.status_var, anchor="w",
            fg_color=COLOR_PRIMARY, text_color=COLOR_SUCCESS, font=self.font_mono_small,
            padx=12, pady=6
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.status_var.set(f" [{ts}] {msg}")

    def show_about(self):
        from config import ABOUT_TEXT
        messagebox.showinfo("System Info", ABOUT_TEXT)

    def exit_application(self):
        if messagebox.askokcancel("System Alert", "Terminate current session?"):
            self.root.quit()


def launch_gui():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")
    root = ctk.CTk()
    app = SteganographyGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
