#!/usr/bin/env python3
"""
Pano Splitter GUI Application

A comprehensive GUI for all pano_splitter functionality including:
- Single image processing
- Batch image processing
- Performance benchmarking
- Real-time preview
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import time
import os
import sys
from pathlib import Path
from typing import List, Optional
import json
import queue

# Add the project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    import cv2
    import numpy as np
    from PIL import Image, ImageTk
    from pano_splitter.models import PanoramaImage, PerspectiveMetadata
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import multiprocessing
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install required dependencies:")
    print("pip install opencv-python pillow numpy")
    sys.exit(1)


def get_version():
    """Get version from pyproject.toml using simple text parsing"""
    try:
        pyproject_path = Path(__file__).parent / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('version = "') and line.endswith('"'):
                        # Extract version between quotes: version = "0.0.1"
                        return line.split('"')[1]
    except Exception:
        pass
    return "0.0.1"  # Fallback version


class PanoSplitterGUI:
    def __init__(self, root):
        self.root = root
        version = get_version()
        self.root.title(f"Pano Splitter v{version} - Panoramic Image Converter")
        self.root.geometry("1200x800")

        # Configure root grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Variables for processing
        self.processing = False
        self.cancel_processing = False
        self.log_queue = queue.Queue()

        # Default values
        self.default_pitch_list = [60, 90, 120]
        self.default_yaw_list = [0, 60, 120, 180, 240, 300]

        self.setup_gui()
        self.setup_styles()

        # Start log monitoring
        self.monitor_logs()

    def setup_styles(self):
        """Setup custom styles for the GUI"""
        style = ttk.Style()
        style.theme_use("clam")

        # Configure custom styles
        style.configure("Title.TLabel", font=("Arial", 16, "bold"))
        style.configure("Subtitle.TLabel", font=("Arial", 12, "bold"))
        style.configure("Success.TLabel", foreground="green")
        style.configure("Error.TLabel", foreground="red")

    def setup_gui(self):
        """Setup the main GUI layout"""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Create tabs
        self.setup_single_image_tab()
        self.setup_batch_processing_tab()
        self.setup_benchmark_tab()
        self.setup_settings_tab()

        # Status bar
        self.setup_status_bar()

    def setup_single_image_tab(self):
        """Setup the single image processing tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Single Image")

        # Configure grid
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # Title
        ttk.Label(frame, text="Single Image Processing", style="Title.TLabel").grid(
            row=0, column=0, columnspan=3, pady=(0, 20)
        )

        # Left panel - Controls
        left_frame = ttk.LabelFrame(frame, text="Settings", padding=10)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        # Input file selection
        ttk.Label(left_frame, text="Input Image:").grid(
            row=0, column=0, sticky="w", pady=2
        )
        self.single_input_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.single_input_var, width=40).grid(
            row=1, column=0, sticky="ew", pady=2
        )
        ttk.Button(left_frame, text="Browse", command=self.browse_single_input).grid(
            row=1, column=1, padx=(5, 0), pady=2
        )

        # Output directory
        ttk.Label(left_frame, text="Output Directory:").grid(
            row=2, column=0, sticky="w", pady=2
        )
        self.single_output_var = tk.StringVar(value="output_single")
        ttk.Entry(left_frame, textvariable=self.single_output_var, width=40).grid(
            row=3, column=0, sticky="ew", pady=2
        )
        ttk.Button(left_frame, text="Browse", command=self.browse_single_output).grid(
            row=3, column=1, padx=(5, 0), pady=2
        )

        # Image parameters frame
        params_frame = ttk.LabelFrame(left_frame, text="Image Parameters", padding=5)
        params_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)

        # FOV
        ttk.Label(params_frame, text="Field of View (°):").grid(
            row=0, column=0, sticky="w"
        )
        self.single_fov_var = tk.IntVar(value=100)
        ttk.Spinbox(
            params_frame, from_=30, to=180, textvariable=self.single_fov_var, width=15
        ).grid(row=0, column=1, sticky="w", padx=(5, 0))

        # Output dimensions
        ttk.Label(params_frame, text="Width:").grid(row=1, column=0, sticky="w")
        self.single_width_var = tk.IntVar(value=1000)
        ttk.Spinbox(
            params_frame,
            from_=100,
            to=4000,
            textvariable=self.single_width_var,
            width=15,
        ).grid(row=1, column=1, sticky="w", padx=(5, 0))

        ttk.Label(params_frame, text="Height:").grid(row=2, column=0, sticky="w")
        self.single_height_var = tk.IntVar(value=1500)
        ttk.Spinbox(
            params_frame,
            from_=100,
            to=4000,
            textvariable=self.single_height_var,
            width=15,
        ).grid(row=2, column=1, sticky="w", padx=(5, 0))

        # Output format
        ttk.Label(params_frame, text="Format:").grid(row=3, column=0, sticky="w")
        self.single_format_var = tk.StringVar(value="jpg")
        format_combo = ttk.Combobox(
            params_frame,
            textvariable=self.single_format_var,
            values=["jpg", "png", "jpeg"],
            width=12,
            state="readonly",
        )
        format_combo.grid(row=3, column=1, sticky="w", padx=(5, 0))

        # Angles frame
        angles_frame = ttk.LabelFrame(left_frame, text="Camera Angles", padding=5)
        angles_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=10)

        # Pitch angles
        ttk.Label(angles_frame, text="Pitch Angles (°):").grid(
            row=0, column=0, sticky="w"
        )
        self.single_pitch_var = tk.StringVar(value="60,90,120")
        ttk.Entry(angles_frame, textvariable=self.single_pitch_var, width=30).grid(
            row=1, column=0, sticky="ew", pady=2
        )

        # Yaw angles
        ttk.Label(angles_frame, text="Yaw Angles (°):").grid(
            row=2, column=0, sticky="w"
        )
        self.single_yaw_var = tk.StringVar(value="0,60,120,180,240,300")
        ttk.Entry(angles_frame, textvariable=self.single_yaw_var, width=30).grid(
            row=3, column=0, sticky="ew", pady=2
        )

        # Workers
        ttk.Label(angles_frame, text="Max Workers:").grid(row=4, column=0, sticky="w")
        self.single_workers_var = tk.IntVar(value=multiprocessing.cpu_count())
        ttk.Spinbox(
            angles_frame, from_=1, to=32, textvariable=self.single_workers_var, width=15
        ).grid(row=4, column=1, sticky="w", padx=(5, 0))

        # Process button
        self.single_process_btn = ttk.Button(
            left_frame,
            text="Process Image",
            command=self.process_single_image,
            style="Accent.TButton",
        )
        self.single_process_btn.grid(
            row=6, column=0, columnspan=2, pady=20, sticky="ew"
        )

        # Right panel - Preview and logs
        right_frame = ttk.Frame(frame)
        right_frame.grid(row=1, column=1, sticky="nsew")
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # Preview frame
        preview_frame = ttk.LabelFrame(right_frame, text="Preview", padding=10)
        preview_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.single_preview_label = ttk.Label(preview_frame, text="No image selected")
        self.single_preview_label.grid(row=0, column=0)

        # Log frame
        log_frame = ttk.LabelFrame(right_frame, text="Processing Log", padding=10)
        log_frame.grid(row=1, column=0, sticky="nsew")
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        self.single_log_text = scrolledtext.ScrolledText(log_frame, height=15, width=50)
        self.single_log_text.grid(row=0, column=0, sticky="nsew")

    def setup_batch_processing_tab(self):
        """Setup the batch processing tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Batch Processing")

        # Configure grid
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # Title
        ttk.Label(frame, text="Batch Image Processing", style="Title.TLabel").grid(
            row=0, column=0, columnspan=3, pady=(0, 20)
        )

        # Left panel - Controls
        left_frame = ttk.LabelFrame(frame, text="Settings", padding=10)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        # Input directory selection
        ttk.Label(left_frame, text="Input Directory:").grid(
            row=0, column=0, sticky="w", pady=2
        )
        self.batch_input_var = tk.StringVar()
        ttk.Entry(left_frame, textvariable=self.batch_input_var, width=40).grid(
            row=1, column=0, sticky="ew", pady=2
        )
        ttk.Button(left_frame, text="Browse", command=self.browse_batch_input).grid(
            row=1, column=1, padx=(5, 0), pady=2
        )

        # Output directory
        ttk.Label(left_frame, text="Output Directory:").grid(
            row=2, column=0, sticky="w", pady=2
        )
        self.batch_output_var = tk.StringVar(value="output_batch")
        ttk.Entry(left_frame, textvariable=self.batch_output_var, width=40).grid(
            row=3, column=0, sticky="ew", pady=2
        )
        ttk.Button(left_frame, text="Browse", command=self.browse_batch_output).grid(
            row=3, column=1, padx=(5, 0), pady=2
        )

        # Batch parameters (similar to single image but with additional options)
        batch_params_frame = ttk.LabelFrame(
            left_frame, text="Processing Parameters", padding=5
        )
        batch_params_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)

        # FOV
        ttk.Label(batch_params_frame, text="Field of View (°):").grid(
            row=0, column=0, sticky="w"
        )
        self.batch_fov_var = tk.IntVar(value=90)
        ttk.Spinbox(
            batch_params_frame,
            from_=30,
            to=180,
            textvariable=self.batch_fov_var,
            width=15,
        ).grid(row=0, column=1, sticky="w", padx=(5, 0))

        # Output dimensions
        ttk.Label(batch_params_frame, text="Width:").grid(row=1, column=0, sticky="w")
        self.batch_width_var = tk.IntVar(value=1000)
        ttk.Spinbox(
            batch_params_frame,
            from_=100,
            to=4000,
            textvariable=self.batch_width_var,
            width=15,
        ).grid(row=1, column=1, sticky="w", padx=(5, 0))

        ttk.Label(batch_params_frame, text="Height:").grid(row=2, column=0, sticky="w")
        self.batch_height_var = tk.IntVar(value=1500)
        ttk.Spinbox(
            batch_params_frame,
            from_=100,
            to=4000,
            textvariable=self.batch_height_var,
            width=15,
        ).grid(row=2, column=1, sticky="w", padx=(5, 0))

        # Output format
        ttk.Label(batch_params_frame, text="Format:").grid(row=3, column=0, sticky="w")
        self.batch_format_var = tk.StringVar(value="jpg")
        format_combo = ttk.Combobox(
            batch_params_frame,
            textvariable=self.batch_format_var,
            values=["jpg", "png", "jpeg", "auto"],
            width=12,
            state="readonly",
        )
        format_combo.grid(row=3, column=1, sticky="w", padx=(5, 0))

        # Angles
        ttk.Label(batch_params_frame, text="Pitch Angles (°):").grid(
            row=4, column=0, sticky="w"
        )
        self.batch_pitch_var = tk.StringVar(value="60,90,120")
        ttk.Entry(batch_params_frame, textvariable=self.batch_pitch_var, width=30).grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=2
        )

        ttk.Label(batch_params_frame, text="Yaw Angles (°):").grid(
            row=6, column=0, sticky="w"
        )
        self.batch_yaw_var = tk.StringVar(value="0,60,120,180,240,300")
        ttk.Entry(batch_params_frame, textvariable=self.batch_yaw_var, width=30).grid(
            row=7, column=0, columnspan=2, sticky="ew", pady=2
        )

        # Workers
        ttk.Label(batch_params_frame, text="Max Workers/Image:").grid(
            row=8, column=0, sticky="w"
        )
        self.batch_workers_var = tk.IntVar(value=multiprocessing.cpu_count() // 2)
        ttk.Spinbox(
            batch_params_frame,
            from_=1,
            to=32,
            textvariable=self.batch_workers_var,
            width=15,
        ).grid(row=8, column=1, sticky="w", padx=(5, 0))

        ttk.Label(batch_params_frame, text="Max Image Workers:").grid(
            row=9, column=0, sticky="w"
        )
        self.batch_image_workers_var = tk.IntVar(
            value=multiprocessing.cpu_count() // 4 or 1
        )
        ttk.Spinbox(
            batch_params_frame,
            from_=1,
            to=16,
            textvariable=self.batch_image_workers_var,
            width=15,
        ).grid(row=9, column=1, sticky="w", padx=(5, 0))

        # Process button
        self.batch_process_btn = ttk.Button(
            left_frame,
            text="Process All Images",
            command=self.process_batch_images,
            style="Accent.TButton",
        )
        self.batch_process_btn.grid(row=5, column=0, columnspan=2, pady=20, sticky="ew")

        # Right panel - Progress and logs
        right_frame = ttk.Frame(frame)
        right_frame.grid(row=1, column=1, sticky="nsew")
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # Progress frame
        progress_frame = ttk.LabelFrame(right_frame, text="Progress", padding=10)
        progress_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.batch_progress_var = tk.StringVar(value="Ready")
        ttk.Label(progress_frame, textvariable=self.batch_progress_var).grid(
            row=0, column=0, pady=5
        )

        self.batch_progress_bar = ttk.Progressbar(progress_frame, mode="determinate")
        self.batch_progress_bar.grid(row=1, column=0, sticky="ew", pady=5)

        # Log frame
        log_frame = ttk.LabelFrame(right_frame, text="Processing Log", padding=10)
        log_frame.grid(row=1, column=0, sticky="nsew")
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        self.batch_log_text = scrolledtext.ScrolledText(log_frame, height=15, width=50)
        self.batch_log_text.grid(row=0, column=0, sticky="nsew")

    def setup_benchmark_tab(self):
        """Setup the benchmark tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Benchmark")

        # Configure grid
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # Title
        ttk.Label(frame, text="Performance Benchmark", style="Title.TLabel").grid(
            row=0, column=0, columnspan=3, pady=(0, 20)
        )

        # Left panel - Controls
        left_frame = ttk.LabelFrame(frame, text="Benchmark Settings", padding=10)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        # Test image selection
        ttk.Label(left_frame, text="Test Image:").grid(
            row=0, column=0, sticky="w", pady=2
        )
        self.benchmark_input_var = tk.StringVar(value=str(Path("tests/test_pano.jpg")))
        ttk.Entry(left_frame, textvariable=self.benchmark_input_var, width=40).grid(
            row=1, column=0, sticky="ew", pady=2
        )
        ttk.Button(left_frame, text="Browse", command=self.browse_benchmark_input).grid(
            row=1, column=1, padx=(5, 0), pady=2
        )

        # Benchmark parameters
        bench_params_frame = ttk.LabelFrame(
            left_frame, text="Test Parameters", padding=5
        )
        bench_params_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)

        # Number of perspectives
        ttk.Label(bench_params_frame, text="Perspectives:").grid(
            row=0, column=0, sticky="w"
        )
        self.benchmark_perspectives_var = tk.IntVar(value=12)
        ttk.Spinbox(
            bench_params_frame,
            from_=1,
            to=50,
            textvariable=self.benchmark_perspectives_var,
            width=15,
        ).grid(row=0, column=1, sticky="w", padx=(5, 0))

        # Iterations
        ttk.Label(bench_params_frame, text="Iterations:").grid(
            row=1, column=0, sticky="w"
        )
        self.benchmark_iterations_var = tk.IntVar(value=3)
        ttk.Spinbox(
            bench_params_frame,
            from_=1,
            to=10,
            textvariable=self.benchmark_iterations_var,
            width=15,
        ).grid(row=1, column=1, sticky="w", padx=(5, 0))

        # Max workers
        ttk.Label(bench_params_frame, text="Max Workers:").grid(
            row=2, column=0, sticky="w"
        )
        self.benchmark_workers_var = tk.IntVar(value=multiprocessing.cpu_count())
        ttk.Spinbox(
            bench_params_frame,
            from_=1,
            to=32,
            textvariable=self.benchmark_workers_var,
            width=15,
        ).grid(row=2, column=1, sticky="w", padx=(5, 0))

        # Image dimensions
        ttk.Label(bench_params_frame, text="Width:").grid(row=3, column=0, sticky="w")
        self.benchmark_width_var = tk.IntVar(value=1000)
        ttk.Spinbox(
            bench_params_frame,
            from_=100,
            to=4000,
            textvariable=self.benchmark_width_var,
            width=15,
        ).grid(row=3, column=1, sticky="w", padx=(5, 0))

        ttk.Label(bench_params_frame, text="Height:").grid(row=4, column=0, sticky="w")
        self.benchmark_height_var = tk.IntVar(value=1500)
        ttk.Spinbox(
            bench_params_frame,
            from_=100,
            to=4000,
            textvariable=self.benchmark_height_var,
            width=15,
        ).grid(row=4, column=1, sticky="w", padx=(5, 0))

        # FOV
        ttk.Label(bench_params_frame, text="Field of View (°):").grid(
            row=5, column=0, sticky="w"
        )
        self.benchmark_fov_var = tk.IntVar(value=90)
        ttk.Spinbox(
            bench_params_frame,
            from_=30,
            to=180,
            textvariable=self.benchmark_fov_var,
            width=15,
        ).grid(row=5, column=1, sticky="w", padx=(5, 0))

        # Run benchmark button
        self.benchmark_btn = ttk.Button(
            left_frame,
            text="Run Benchmark",
            command=self.run_benchmark,
            style="Accent.TButton",
        )
        self.benchmark_btn.grid(row=3, column=0, columnspan=2, pady=20, sticky="ew")

        # Right panel - Results
        right_frame = ttk.Frame(frame)
        right_frame.grid(row=1, column=1, sticky="nsew")
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # Results frame
        results_frame = ttk.LabelFrame(
            right_frame, text="Benchmark Results", padding=10
        )
        results_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Create results display
        self.benchmark_results_text = tk.Text(results_frame, height=8, width=50)
        self.benchmark_results_text.grid(row=0, column=0, sticky="ew")

        # Log frame
        log_frame = ttk.LabelFrame(right_frame, text="Benchmark Log", padding=10)
        log_frame.grid(row=1, column=0, sticky="nsew")
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        self.benchmark_log_text = scrolledtext.ScrolledText(
            log_frame, height=15, width=50
        )
        self.benchmark_log_text.grid(row=0, column=0, sticky="nsew")

    def setup_settings_tab(self):
        """Setup the settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Settings")

        # Title
        ttk.Label(frame, text="Application Settings", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, pady=(0, 20)
        )

        # Settings frame
        settings_frame = ttk.LabelFrame(frame, text="Default Values", padding=10)
        settings_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        # Default angles
        ttk.Label(settings_frame, text="Default Pitch Angles:").grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.default_pitch_var = tk.StringVar(value="60,90,120")
        ttk.Entry(settings_frame, textvariable=self.default_pitch_var, width=50).grid(
            row=0, column=1, sticky="ew", pady=5, padx=(10, 0)
        )

        ttk.Label(settings_frame, text="Default Yaw Angles:").grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.default_yaw_var = tk.StringVar(value="0,60,120,180,240,300")
        ttk.Entry(settings_frame, textvariable=self.default_yaw_var, width=50).grid(
            row=1, column=1, sticky="ew", pady=5, padx=(10, 0)
        )

        # Apply button
        ttk.Button(
            settings_frame,
            text="Apply to All Tabs",
            command=self.apply_default_settings,
        ).grid(row=2, column=0, columnspan=2, pady=20)

        # About frame
        about_frame = ttk.LabelFrame(frame, text="About", padding=10)
        about_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)

        version = get_version()
        about_text = f"""Pano Splitter GUI v{version}
        
A comprehensive tool for converting panoramic images into perspective views.

Features:
• Single image processing
• Batch processing
• Performance benchmarking
• Parallel processing support
• Multiple output formats

Built with Python, OpenCV, and Tkinter."""

        ttk.Label(about_frame, text=about_text, justify="left").grid(
            row=0, column=0, sticky="w"
        )

    def setup_status_bar(self):
        """Setup the status bar"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var)
        self.status_label.grid(row=0, column=0, sticky="w")

        # Cancel button
        self.cancel_btn = ttk.Button(
            self.status_frame,
            text="Cancel",
            command=self.cancel_operation,
            state="disabled",
        )
        self.cancel_btn.grid(row=0, column=1, sticky="e")

        self.status_frame.grid_columnconfigure(0, weight=1)

    def monitor_logs(self):
        """Monitor the log queue and update GUI"""
        try:
            while True:
                log_entry = self.log_queue.get_nowait()
                tab_name = log_entry.get("tab", "single")
                message = log_entry.get("message", "")

                if tab_name == "single":
                    self.single_log_text.insert(tk.END, message + "\n")
                    self.single_log_text.see(tk.END)
                elif tab_name == "batch":
                    self.batch_log_text.insert(tk.END, message + "\n")
                    self.batch_log_text.see(tk.END)
                elif tab_name == "benchmark":
                    self.benchmark_log_text.insert(tk.END, message + "\n")
                    self.benchmark_log_text.see(tk.END)

        except queue.Empty:
            pass

        # Schedule next check
        self.root.after(100, self.monitor_logs)

    def log_message(self, message: str, tab: str = "single"):
        """Add message to log queue"""
        self.log_queue.put({"tab": tab, "message": message})

    def browse_single_input(self):
        """Browse for single input image"""
        filename = filedialog.askopenfilename(
            title="Select Panoramic Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")],
        )
        if filename:
            self.single_input_var.set(filename)
            self.load_preview(filename)

    def browse_single_output(self):
        """Browse for single output directory"""
        dirname = filedialog.askdirectory(title="Select Output Directory")
        if dirname:
            self.single_output_var.set(dirname)

    def browse_batch_input(self):
        """Browse for batch input directory"""
        dirname = filedialog.askdirectory(title="Select Input Directory")
        if dirname:
            self.batch_input_var.set(dirname)

    def browse_batch_output(self):
        """Browse for batch output directory"""
        dirname = filedialog.askdirectory(title="Select Output Directory")
        if dirname:
            self.batch_output_var.set(dirname)

    def browse_benchmark_input(self):
        """Browse for benchmark input image"""
        filename = filedialog.askopenfilename(
            title="Select Test Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")],
        )
        if filename:
            self.benchmark_input_var.set(filename)

    def load_preview(self, image_path: str):
        """Load and display image preview"""
        try:
            # Load image and create thumbnail
            image = Image.open(image_path)
            # Resize to fit preview area
            image.thumbnail((300, 200), Image.Resampling.LANCZOS)

            # Convert to PhotoImage and display
            photo = ImageTk.PhotoImage(image)
            self.single_preview_label.configure(image=photo, text="")
            self.single_preview_label.image = photo  # Keep a reference

        except Exception as e:
            self.single_preview_label.configure(
                image="", text=f"Error loading preview: {str(e)}"
            )

    def parse_angles(self, angle_string: str) -> List[int]:
        """Parse comma-separated angle string into list of integers"""
        try:
            angles = [int(x.strip()) for x in angle_string.split(",") if x.strip()]
            return angles
        except ValueError:
            raise ValueError(
                "Invalid angle format. Use comma-separated integers (e.g., '60,90,120')"
            )

    def validate_angles(self, pitch_angles: List[int], yaw_angles: List[int]):
        """Validate angle ranges"""
        for pitch in pitch_angles:
            if not (1 <= pitch <= 179):
                raise ValueError(
                    f"Pitch angle {pitch} must be between 1 and 179 degrees"
                )

        for yaw in yaw_angles:
            if not (0 <= yaw <= 360):
                raise ValueError(f"Yaw angle {yaw} must be between 0 and 360 degrees")

    def apply_default_settings(self):
        """Apply default settings to all tabs"""
        pitch_val = self.default_pitch_var.get()
        yaw_val = self.default_yaw_var.get()

        # Apply to single image tab
        self.single_pitch_var.set(pitch_val)
        self.single_yaw_var.set(yaw_val)

        # Apply to batch tab
        self.batch_pitch_var.set(pitch_val)
        self.batch_yaw_var.set(yaw_val)

        messagebox.showinfo("Settings Applied", "Default settings applied to all tabs.")

    def cancel_operation(self):
        """Cancel current processing operation"""
        self.cancel_processing = True
        self.status_var.set("Cancelling...")
        self.log_message("Processing cancelled by user", "single")
        self.log_message("Processing cancelled by user", "batch")
        self.log_message("Processing cancelled by user", "benchmark")

    def set_processing_state(self, processing: bool):
        """Set the processing state and update UI"""
        self.processing = processing
        self.cancel_processing = False

        # Update button states
        if processing:
            self.single_process_btn.config(state="disabled")
            self.batch_process_btn.config(state="disabled")
            self.benchmark_btn.config(state="disabled")
            self.cancel_btn.config(state="normal")
        else:
            self.single_process_btn.config(state="normal")
            self.batch_process_btn.config(state="normal")
            self.benchmark_btn.config(state="normal")
            self.cancel_btn.config(state="disabled")

    def process_single_image(self):
        """Process a single image"""
        if self.processing:
            return

        # Validate inputs
        input_path = self.single_input_var.get().strip()
        if not input_path or not Path(input_path).exists():
            messagebox.showerror("Error", "Please select a valid input image")
            return

        output_path = self.single_output_var.get().strip()
        if not output_path:
            messagebox.showerror("Error", "Please specify an output directory")
            return

        try:
            pitch_angles = self.parse_angles(self.single_pitch_var.get())
            yaw_angles = self.parse_angles(self.single_yaw_var.get())
            self.validate_angles(pitch_angles, yaw_angles)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        # Clear log
        self.single_log_text.delete(1.0, tk.END)

        # Start processing in background thread
        thread = threading.Thread(
            target=self._process_single_image_worker,
            args=(input_path, output_path, pitch_angles, yaw_angles),
        )
        thread.daemon = True
        thread.start()

    def _process_single_image_worker(
        self,
        input_path: str,
        output_path: str,
        pitch_angles: List[int],
        yaw_angles: List[int],
    ):
        """Worker thread for single image processing"""
        try:
            self.set_processing_state(True)
            self.status_var.set("Processing single image...")

            # Create output directory
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Get parameters
            fov = self.single_fov_var.get()
            width = self.single_width_var.get()
            height = self.single_height_var.get()
            output_format = self.single_format_var.get()
            max_workers = self.single_workers_var.get()

            self.log_message(f"Processing: {Path(input_path).name}", "single")
            self.log_message(f"Output directory: {output_path}", "single")
            self.log_message(f"Parameters: FOV={fov}, size={width}x{height}", "single")
            self.log_message(
                f"Angles: pitch={pitch_angles}, yaw={yaw_angles}", "single"
            )

            start_time = time.time()

            # Load panorama
            panorama = PanoramaImage(
                panorama_id=Path(input_path).stem, image=input_path
            )

            # Create perspective metadata list
            perspectives = []
            for pitch_angle in pitch_angles:
                for yaw_angle in yaw_angles:
                    if self.cancel_processing:
                        return

                    # Convert pitch (same as in CLI scripts)
                    adjusted_pitch = (180 - pitch_angle) - 90

                    perspective = PerspectiveMetadata(
                        pixel_width=width,
                        pixel_height=height,
                        horizontal_fov=fov,
                        vertical_fov=fov,
                        yaw_offset=yaw_angle,
                        pitch_offset=adjusted_pitch,
                    )
                    perspectives.append((perspective, pitch_angle, yaw_angle))

            # Generate perspectives in parallel
            processed_count = 0
            total_count = len(perspectives)

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for perspective, pitch_angle, yaw_angle in perspectives:
                    if self.cancel_processing:
                        break

                    future = executor.submit(
                        self._generate_perspective,
                        panorama,
                        perspective,
                        pitch_angle,
                        yaw_angle,
                        output_dir,
                        output_format,
                        fov,
                    )
                    futures.append(future)

                # Collect results
                for future in as_completed(futures):
                    if self.cancel_processing:
                        break

                    try:
                        success, filename = future.result()
                        if success:
                            self.log_message(f"✓ Saved: {filename}", "single")
                            processed_count += 1
                        else:
                            self.log_message(f"✗ Failed: {filename}", "single")
                    except Exception as e:
                        self.log_message(f"✗ Error: {str(e)}", "single")

            elapsed_time = time.time() - start_time

            if not self.cancel_processing:
                self.log_message(f"\n🎉 Processing complete!", "single")
                self.log_message(
                    f"📊 Generated {processed_count}/{total_count} images", "single"
                )
                self.log_message(f"⏱️ Total time: {elapsed_time:.2f} seconds", "single")
                self.log_message(
                    f"🚀 Average: {processed_count/elapsed_time:.2f} images/second",
                    "single",
                )
                self.status_var.set(
                    f"Completed: {processed_count}/{total_count} images"
                )
            else:
                self.log_message(f"\n❌ Processing cancelled", "single")
                self.status_var.set("Cancelled")

        except Exception as e:
            self.log_message(f"Error: {str(e)}", "single")
            self.status_var.set("Error occurred")
            messagebox.showerror("Error", f"Processing failed: {str(e)}")
        finally:
            self.set_processing_state(False)

    def _generate_perspective(
        self,
        panorama: PanoramaImage,
        perspective: PerspectiveMetadata,
        pitch_angle: int,
        yaw_angle: int,
        output_dir: Path,
        output_format: str,
        fov: int,
    ):
        """Generate a single perspective image"""
        try:
            # Generate perspective
            perspective_image = panorama.generate_perspective_image(perspective)
            output_array = perspective_image.get_perspective_image_array()

            # Create filename
            filename = f"{panorama.panorama_id}_pitch{pitch_angle}_yaw{yaw_angle}_fov{fov}.{output_format}"
            output_path = output_dir / filename

            # Save image
            output_bgr = cv2.cvtColor(output_array, cv2.COLOR_RGB2BGR)
            success = cv2.imwrite(str(output_path), output_bgr)

            return success, filename

        except Exception as e:
            return False, str(e)

    def process_batch_images(self):
        """Process multiple images in batch"""
        if self.processing:
            return

        # Validate inputs
        input_path = self.batch_input_var.get().strip()
        if not input_path or not Path(input_path).exists():
            messagebox.showerror("Error", "Please select a valid input directory")
            return

        output_path = self.batch_output_var.get().strip()
        if not output_path:
            messagebox.showerror("Error", "Please specify an output directory")
            return

        try:
            pitch_angles = self.parse_angles(self.batch_pitch_var.get())
            yaw_angles = self.parse_angles(self.batch_yaw_var.get())
            self.validate_angles(pitch_angles, yaw_angles)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        # Clear log
        self.batch_log_text.delete(1.0, tk.END)

        # Start processing in background thread
        thread = threading.Thread(
            target=self._process_batch_images_worker,
            args=(input_path, output_path, pitch_angles, yaw_angles),
        )
        thread.daemon = True
        thread.start()

    def _process_batch_images_worker(
        self,
        input_path: str,
        output_path: str,
        pitch_angles: List[int],
        yaw_angles: List[int],
    ):
        """Worker thread for batch image processing"""
        try:
            self.set_processing_state(True)
            self.status_var.set("Processing batch images...")

            # Create output directory
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Get parameters
            fov = self.batch_fov_var.get()
            width = self.batch_width_var.get()
            height = self.batch_height_var.get()
            output_format = self.batch_format_var.get()
            max_workers = self.batch_workers_var.get()
            max_image_workers = self.batch_image_workers_var.get()

            # Find all image files
            input_dir = Path(input_path)
            supported_extensions = [
                "*.jpg",
                "*.jpeg",
                "*.png",
                "*.JPG",
                "*.JPEG",
                "*.PNG",
            ]
            image_files = []
            for extension in supported_extensions:
                image_files.extend(input_dir.glob(extension))

            if not image_files:
                self.log_message("❌ No supported image files found", "batch")
                self.log_message("Supported formats: .jpg, .jpeg, .png", "batch")
                return

            self.log_message(
                f"📁 Found {len(image_files)} image(s) to process", "batch"
            )
            self.log_message(f"🎯 Processing from: {input_path}", "batch")
            self.log_message(f"📤 Output directory: {output_path}", "batch")
            self.log_message(f"⚙️ Parameters: FOV={fov}, size={width}x{height}", "batch")
            self.log_message(
                f"📐 Angles: pitch={pitch_angles}, yaw={yaw_angles}", "batch"
            )

            start_time = time.time()
            total_processed = 0
            total_perspectives = len(image_files) * len(pitch_angles) * len(yaw_angles)

            # Set up progress bar
            self.batch_progress_bar["maximum"] = len(image_files)
            self.batch_progress_bar["value"] = 0

            # Process each image
            for i, image_path in enumerate(image_files):
                if self.cancel_processing:
                    break

                # Update progress
                self.batch_progress_var.set(
                    f"Processing {i+1}/{len(image_files)}: {image_path.name}"
                )
                self.batch_progress_bar["value"] = i

                # Determine output format for this image
                if output_format == "auto":
                    current_format = image_path.suffix[1:].lower()
                else:
                    current_format = output_format

                # Process single image
                processed_count = self._process_single_image_sync(
                    image_path,
                    output_dir,
                    pitch_angles,
                    yaw_angles,
                    fov,
                    width,
                    height,
                    current_format,
                    max_workers,
                )
                total_processed += processed_count

                self.log_message(
                    f"  ✓ {image_path.name}: {processed_count} perspectives", "batch"
                )

            elapsed_time = time.time() - start_time

            if not self.cancel_processing:
                self.log_message(f"\n🎉 Batch processing complete!", "batch")
                self.log_message(
                    f"📊 Generated {total_processed}/{total_perspectives} images",
                    "batch",
                )
                self.log_message(f"⏱️ Total time: {elapsed_time:.2f} seconds", "batch")
                if elapsed_time > 0:
                    self.log_message(
                        f"🚀 Average: {total_processed/elapsed_time:.2f} images/second",
                        "batch",
                    )
                self.status_var.set(
                    f"Batch completed: {total_processed}/{total_perspectives} images"
                )
                self.batch_progress_var.set("Completed")
                self.batch_progress_bar["value"] = len(image_files)
            else:
                self.log_message(f"\n❌ Batch processing cancelled", "batch")
                self.status_var.set("Cancelled")
                self.batch_progress_var.set("Cancelled")

        except Exception as e:
            self.log_message(f"Error: {str(e)}", "batch")
            self.status_var.set("Error occurred")
            messagebox.showerror("Error", f"Batch processing failed: {str(e)}")
        finally:
            self.set_processing_state(False)

    def _process_single_image_sync(
        self,
        image_path: Path,
        output_dir: Path,
        pitch_angles: List[int],
        yaw_angles: List[int],
        fov: int,
        width: int,
        height: int,
        output_format: str,
        max_workers: int,
    ) -> int:
        """Process a single image synchronously and return count of generated images"""
        try:
            # Load panorama
            panorama = PanoramaImage(panorama_id=image_path.stem, image=str(image_path))

            # Create perspective metadata list
            perspectives = []
            for pitch_angle in pitch_angles:
                for yaw_angle in yaw_angles:
                    if self.cancel_processing:
                        return 0

                    # Convert pitch (same as in CLI scripts)
                    adjusted_pitch = (180 - pitch_angle) - 90

                    perspective = PerspectiveMetadata(
                        pixel_width=width,
                        pixel_height=height,
                        horizontal_fov=fov,
                        vertical_fov=fov,
                        yaw_offset=yaw_angle,
                        pitch_offset=adjusted_pitch,
                    )
                    perspectives.append((perspective, pitch_angle, yaw_angle))

            # Generate perspectives in parallel
            processed_count = 0

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for perspective, pitch_angle, yaw_angle in perspectives:
                    if self.cancel_processing:
                        break

                    future = executor.submit(
                        self._generate_perspective,
                        panorama,
                        perspective,
                        pitch_angle,
                        yaw_angle,
                        output_dir,
                        output_format,
                        fov,
                    )
                    futures.append(future)

                # Collect results
                for future in as_completed(futures):
                    if self.cancel_processing:
                        break

                    try:
                        success, filename = future.result()
                        if success:
                            processed_count += 1
                    except Exception:
                        pass  # Error already logged in _generate_perspective

            return processed_count

        except Exception as e:
            self.log_message(
                f"  ✗ Failed to process {image_path.name}: {str(e)}", "batch"
            )
            return 0

    def run_benchmark(self):
        """Run performance benchmark"""
        if self.processing:
            return

        # Validate test image
        test_image = self.benchmark_input_var.get().strip()
        if not test_image or not Path(test_image).exists():
            messagebox.showerror("Error", "Please select a valid test image")
            return

        # Clear log and results
        self.benchmark_log_text.delete(1.0, tk.END)
        self.benchmark_results_text.delete(1.0, tk.END)

        # Start benchmark in background thread
        thread = threading.Thread(target=self._run_benchmark_worker, args=(test_image,))
        thread.daemon = True
        thread.start()

    def _run_benchmark_worker(self, test_image: str):
        """Worker thread for benchmark"""
        try:
            self.set_processing_state(True)
            self.status_var.set("Running benchmark...")

            # Get parameters
            num_perspectives = self.benchmark_perspectives_var.get()
            iterations = self.benchmark_iterations_var.get()
            max_workers = self.benchmark_workers_var.get()
            width = self.benchmark_width_var.get()
            height = self.benchmark_height_var.get()
            fov = self.benchmark_fov_var.get()

            self.log_message(f"🎯 Benchmark Configuration:", "benchmark")
            self.log_message(f"   Input: {Path(test_image).name}", "benchmark")
            self.log_message(f"   Perspectives: {num_perspectives}", "benchmark")
            self.log_message(f"   Output size: {width}x{height}", "benchmark")
            self.log_message(f"   FOV: {fov}°", "benchmark")
            self.log_message(f"   Iterations: {iterations}", "benchmark")
            self.log_message(
                f"   CPU cores: {multiprocessing.cpu_count()}", "benchmark"
            )
            self.log_message(f"   Max workers: {max_workers}", "benchmark")
            self.log_message("", "benchmark")

            # Create test perspectives
            pitch_angles = [60, 120]  # 2 pitches
            yaw_angles = [0, 60, 120, 180, 240, 300]  # 6 yaws

            perspectives = []
            count = 0
            for pitch_angle in pitch_angles:
                for yaw_angle in yaw_angles:
                    if count >= num_perspectives:
                        break

                    adjusted_pitch = (180 - pitch_angle) - 90

                    perspective = PerspectiveMetadata(
                        pixel_width=width,
                        pixel_height=height,
                        horizontal_fov=fov,
                        vertical_fov=fov,
                        yaw_offset=yaw_angle,
                        pitch_offset=adjusted_pitch,
                    )
                    perspectives.append(perspective)
                    count += 1

                if count >= num_perspectives:
                    break

            # Run sequential benchmark
            seq_time, seq_rate = self._benchmark_sequential(
                test_image, perspectives, iterations
            )

            # Run parallel benchmark
            par_time, par_rate = self._benchmark_parallel(
                test_image, perspectives, max_workers, iterations
            )

            # Calculate results
            speedup = seq_time / par_time if par_time > 0 else 0
            throughput_improvement = par_rate / seq_rate if seq_rate > 0 else 0

            # Display results
            results = f"""🏁 Benchmark Results:
   Sequential: {seq_time:.2f}s ({seq_rate:.2f} imgs/sec)
   Parallel:   {par_time:.2f}s ({par_rate:.2f} imgs/sec)
   Speedup:    {speedup:.2f}x
   Throughput: {throughput_improvement:.2f}x improvement

"""

            if speedup > 1.5:
                results += f"🚀 Excellent speedup! Parallel processing is {speedup:.1f}x faster"
            elif speedup > 1.1:
                results += (
                    f"✅ Good speedup! Parallel processing is {speedup:.1f}x faster"
                )
            else:
                results += f"⚠️ Limited speedup. Consider fewer workers or check workload suitability"

            self.benchmark_results_text.insert(tk.END, results)
            self.log_message(results, "benchmark")
            self.status_var.set("Benchmark completed")

        except Exception as e:
            self.log_message(f"Benchmark error: {str(e)}", "benchmark")
            self.status_var.set("Benchmark failed")
            messagebox.showerror("Error", f"Benchmark failed: {str(e)}")
        finally:
            self.set_processing_state(False)

    def _benchmark_sequential(
        self, image_path: str, perspectives: List[PerspectiveMetadata], iterations: int
    ):
        """Run sequential benchmark"""
        self.log_message(
            f"🔄 Running sequential benchmark ({iterations} iteration(s))...",
            "benchmark",
        )

        total_time = 0
        total_images = 0

        for i in range(iterations):
            if self.cancel_processing:
                break

            start_time = time.time()

            for perspective_metadata in perspectives:
                if self.cancel_processing:
                    break

                panorama = PanoramaImage(panorama_id="benchmark", image=image_path)
                perspective_image = panorama.generate_perspective_image(
                    perspective_metadata
                )
                _ = (
                    perspective_image.get_perspective_image_array()
                )  # Simulate processing
                total_images += 1

            elapsed = time.time() - start_time
            total_time += elapsed
            rate = len(perspectives) / elapsed if elapsed > 0 else 0
            self.log_message(
                f"  Iteration {i+1}: {elapsed:.2f}s, {rate:.2f} imgs/sec", "benchmark"
            )

        avg_time = total_time / iterations if iterations > 0 else 0
        avg_rate = total_images / total_time if total_time > 0 else 0

        self.log_message(
            f"📊 Sequential Average: {avg_time:.2f}s, {avg_rate:.2f} imgs/sec",
            "benchmark",
        )
        return avg_time, avg_rate

    def _benchmark_parallel(
        self,
        image_path: str,
        perspectives: List[PerspectiveMetadata],
        max_workers: int,
        iterations: int,
    ):
        """Run parallel benchmark"""
        self.log_message(
            f"⚡ Running parallel benchmark with {max_workers} workers ({iterations} iteration(s))...",
            "benchmark",
        )

        total_time = 0
        total_images = 0

        for i in range(iterations):
            if self.cancel_processing:
                break

            start_time = time.time()

            # Load image once
            panorama = PanoramaImage(panorama_id="benchmark", image=image_path)

            # Generate perspectives in parallel using batch method
            perspective_images = panorama.generate_perspective_images_batch(
                perspectives, max_workers=max_workers
            )

            # Simulate saving
            for perspective_image in perspective_images:
                if self.cancel_processing:
                    break
                _ = perspective_image.get_perspective_image_array()
                total_images += 1

            elapsed = time.time() - start_time
            total_time += elapsed
            rate = len(perspectives) / elapsed if elapsed > 0 else 0
            self.log_message(
                f"  Iteration {i+1}: {elapsed:.2f}s, {rate:.2f} imgs/sec", "benchmark"
            )

        avg_time = total_time / iterations if iterations > 0 else 0
        avg_rate = total_images / total_time if total_time > 0 else 0

        self.log_message(
            f"📊 Parallel Average: {avg_time:.2f}s, {avg_rate:.2f} imgs/sec",
            "benchmark",
        )
        return avg_time, avg_rate


def main():
    """Main function to run the GUI application"""
    root = tk.Tk()
    app = PanoSplitterGUI(root)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
