import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import json
import logging
import threading
from cpu_scheduler_algorithms import *
from cpu_scheduler_visualization import SchedulerVisualizer
from performance_metrics import PerformanceMetrics
from ai_scheduler import AIScheduler
import time

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ]
)

class SchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced CPU Scheduler Simulator")
        self.root.geometry("1400x900")

        self.main_frame = ttk.Frame(self.root, padding=0)
        self.main_frame.pack(fill="both", expand=True)

        # Header frame to simulate the glossy header
        self.header_frame = ttk.Frame(self.main_frame, height=60, style="Header.TFrame")
        self.header_frame.pack(fill="x")

        self.sidebar = ttk.Frame(self.main_frame, width=200, style="Sidebar.TFrame")
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)

        self.content_frame = ttk.Frame(self.main_frame, style="Content.TFrame")
        self.content_frame.pack(side="left", fill="both", expand=True, padx=0, pady=0)

        self.canvas = tk.Canvas(self.content_frame, bg="#1A2A44", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, anchor="w", padding=2, style="Status.TLabel")
        self.status_bar.pack(side="bottom", fill="x")

        # Enhanced modern theme with gradients and styled widgets
        self.setup_modern_theme()

        self.processes = []
        self.process_entries = []
        self.step_mode = False
        self.current_step = 0
        self.step_timeline = []
        self.current_processes = []
        self.current_algo_name = "N/A"
        self.timeline = []
        self.num_cores = 1
        self.ai_scheduler = AIScheduler()
        self.comparison_results = {}
        self.process_listbox = None
        self.comparison_thread = None

        nav_items = [
            ("Process Management", self.show_process_management),
            ("Scheduling", self.show_scheduling),
            ("Results", self.show_results),
            ("Metrics", self.show_metrics),
            ("Comparison", self.show_comparison),
            ("About", self.show_about)
        ]
        self.nav_buttons = []
        for text, cmd in nav_items:
            btn = ttk.Button(self.sidebar, text=text, command=cmd, style="Nav.TButton")
            btn.pack(fill="x", pady=2, padx=2)
            self.nav_buttons.append(btn)

        # Dark Mode toggle
        self.dark_mode_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.sidebar, text="Dark Mode", variable=self.dark_mode_var, style="Modern.TCheckbutton", command=self.toggle_theme).pack(pady=2)

        self.process_management_frame = ttk.Frame(self.content_frame)
        self.scheduling_frame = ttk.Frame(self.content_frame)
        self.results_frame = ttk.Frame(self.content_frame)
        self.metrics_frame = ttk.Frame(self.content_frame)
        self.comparison_frame = ttk.Frame(self.content_frame)
        self.about_frame = ttk.Frame(self.content_frame)

        self._resize_canvas()  # Initial canvas resize
        self.show_process_management()

    def setup_modern_theme(self):
        style = ttk.Style()
        style.theme_use('default')

        # Custom styles with enhanced modern design
        style.configure("Sidebar.TFrame", background="#1A2A44", relief="flat")
        style.configure("Content.TFrame", background="#2E4057", relief="flat")
        style.configure("Header.TFrame", background="#2A4066", relief="flat")
        style.configure("Nav.TButton", background="#34495E", foreground="#E6E6FA", font=("Segoe UI", 10, "bold"), padding=6)
        style.map("Nav.TButton",
                  background=[("active", "#465C71")],
                  foreground=[("active", "#B0B0FF")])
        style.configure("Modern.TLabel", background="#2E4057", foreground="#E6E6FA", font=("Segoe UI", 11, "bold"))
        style.configure("Modern.TButton", background="#34495E", foreground="#E6E6FA", font=("Segoe UI", 10), padding=6, borderwidth=1)
        style.map("Modern.TButton",
                  background=[("active", "#465C71")],
                  foreground=[("active", "#B0B0FF")],
                  relief=[("active", "flat"), ("!active", "raised")])
        style.configure("Modern.TCheckbutton", background="#1A2A44", foreground="#E6E6FA", font=("Segoe UI", 10), indicatorcolor="#34495E")
        style.configure("TLabel", background="#2E4057", foreground="#E6E6FA", font=("Segoe UI", 10))
        style.configure("TButton", background="#34495E", foreground="#E6E6FA", font=("Segoe UI", 10), padding=6)
        style.map("TButton",
                  background=[("active", "#465C71")],
                  foreground=[("active", "#B0B0FF")])
        style.configure("TRadiobutton", background="#2E4057", foreground="#E6E6FA", font=("Segoe UI", 10))
        style.configure("TNotebook", background="#2E4057")
        style.configure("TNotebook.Tab", background="#34495E", foreground="#E6E6FA", padding=[10, 4], borderwidth=1)
        style.map("TNotebook.Tab",
                  background=[("selected", "#4A6B9A")],
                  foreground=[("selected", "#FFFFFF")])
        style.configure("Treeview", background="#34495E", fieldbackground="#34495E", foreground="#E6E6FA", font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#4A6B9A", foreground="#E6E6FA", font=("Segoe UI", 10, "bold"))
        style.configure("TEntry", fieldbackground="#4A6B9A", foreground="#E6E6FA", insertbackground="#B0B0FF")
        style.configure("Status.TLabel", background="#1A2A44", foreground="#E6E6FA", font=("Segoe UI", 10))

        # Custom button styles with vibrant accents
        style.configure("Run.TButton", background="#00C4B6", foreground="#1A2A44", font=("Segoe UI", 10, "bold"))
        style.map("Run.TButton",
                  background=[("active", "#00A899")],
                  foreground=[("active", "#FFFFFF")])
        style.configure("Step.TButton", background="#6B46C1", foreground="#E6E6FA")
        style.map("Step.TButton",
                  background=[("active", "#553C9A")],
                  foreground=[("active", "#FFFFFF")])
        style.configure("Gantt.TButton", background="#3498DB", foreground="#1A2A44")
        style.map("Gantt.TButton",
                  background=[("active", "#2980B9")],
                  foreground=[("active", "#FFFFFF")])
        style.configure("Compare.TButton", background="#E67E22", foreground="#1A2A44")
        style.map("Compare.TButton",
                  background=[("active", "#D35400")],
                  foreground=[("active", "#FFFFFF")])
        style.configure("Test.TButton", background="#E67E22", foreground="#1A2A44")
        style.map("Test.TButton",
                  background=[("active", "#D35400")],
                  foreground=[("active", "#FFFFFF")])

        # Draw gradient on canvas
        self._create_diagonal_gradient(0, 0, self.canvas.winfo_width(), self.canvas.winfo_height(), ["#1A2A44", "#2A4066", "#3A5577"])

    def setup_light_theme(self):
        style = ttk.Style()
        style.theme_use('default')
        self.canvas.configure(bg="#F0F4F8")
        self._create_diagonal_gradient(0, 0, self.canvas.winfo_width(), self.canvas.winfo_height(), ["#F0F4F8", "#DDE3F0", "#B0C4DE"])
        self.header_frame.configure(style="Header.TFrame")
        style.configure("Header.TFrame", background="#B0C4DE", relief="flat")

        style.configure("Sidebar.TFrame", background="#B0C4DE")
        style.configure("Content.TFrame", background="#FFFFFF")
        style.configure("Nav.TButton", background="#87CEEB", foreground="#333333", font=("Segoe UI", 10, "bold"), padding=6)
        style.map("Nav.TButton",
                  background=[("active", "#63B8FF")],
                  foreground=[("active", "#FFFFFF")])
        style.configure("Modern.TLabel", background="#F0F4F8", foreground="#333333", font=("Segoe UI", 11, "bold"))
        style.configure("Modern.TButton", background="#87CEEB", foreground="#333333", font=("Segoe UI", 10), padding=6, borderwidth=1)
        style.map("Modern.TButton",
                  background=[("active", "#63B8FF")],
                  foreground=[("active", "#FFFFFF")],
                  relief=[("active", "flat"), ("!active", "raised")])
        style.configure("Modern.TCheckbutton", background="#B0C4DE", foreground="#333333", font=("Segoe UI", 10), indicatorcolor="#87CEEB")
        style.configure("TLabel", background="#FFFFFF", foreground="#333333", font=("Segoe UI", 10))
        style.configure("TButton", background="#B0C4DE", foreground="#333333", font=("Segoe UI", 10), padding=6)
        style.map("TButton",
                  background=[("active", "#90A4AE")],
                  foreground=[("active", "#FFFFFF")])
        style.configure("TRadiobutton", background="#FFFFFF", foreground="#333333", font=("Segoe UI", 10))
        style.configure("TNotebook", background="#FFFFFF")
        style.configure("TNotebook.Tab", background="#DDE3F0", foreground="#333333", padding=[10, 4], borderwidth=1)
        style.map("TNotebook.Tab",
                  background=[("selected", "#87CEEB")],
                  foreground=[("selected", "#FFFFFF")])
        style.configure("Treeview", background="#DDE3F0", fieldbackground="#DDE3F0", foreground="#333333", font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#B0C4DE", foreground="#333333", font=("Segoe UI", 10, "bold"))
        style.configure("TEntry", fieldbackground="#DDE3F0", foreground="#333333", insertbackground="black")
        style.configure("Status.TLabel", background="#F0F4F8", foreground="#333333", font=("Segoe UI", 10))

        style.configure("Run.TButton", background="#2ECC71", foreground="#333333")
        style.map("Run.TButton", background=[("active", "#27AE60")], foreground=[("active", "#FFFFFF")])
        style.configure("Step.TButton", background="#F1C40F", foreground="#333333")
        style.map("Step.TButton", background=[("active", "#D4AC0D")], foreground=[("active", "#FFFFFF")])
        style.configure("Gantt.TButton", background="#3498DB", foreground="#333333")
        style.map("Gantt.TButton", background=[("active", "#2980B9")], foreground=[("active", "#FFFFFF")])
        style.configure("Compare.TButton", background="#E67E22", foreground="#333333")
        style.map("Compare.TButton", background=[("active", "#D35400")], foreground=[("active", "#FFFFFF")])
        style.configure("Test.TButton", background="#E67E22", foreground="#333333")
        style.map("Test.TButton", background=[("active", "#D35400")], foreground=[("active", "#FFFFFF")])

    def toggle_theme(self):
        if self.dark_mode_var.get():
            self.setup_modern_theme()
        else:
            self.setup_light_theme()
        self.update_styles()
        self._resize_canvas()
        self.status_var.set(f"Switched to {'Dark' if self.dark_mode_var.get() else 'Light'} Mode")

    def update_styles(self):
        for frame in [self.process_management_frame, self.scheduling_frame, self.results_frame,
                     self.metrics_frame, self.comparison_frame, self.about_frame]:
            for widget in frame.winfo_children():
                if isinstance(widget, ttk.Label):
                    widget.configure(style="Modern.TLabel")
                elif isinstance(widget, ttk.Button):
                    widget.configure(style="Modern.TButton")
                elif isinstance(widget, ttk.Radiobutton):
                    widget.configure(style="TRadiobutton")
                elif isinstance(widget, ttk.Entry):
                    widget.configure(style="TEntry")
                elif isinstance(widget, ttk.Treeview):
                    widget.configure(style="Treeview")
        for btn in self.nav_buttons:
            btn.configure(style="Nav.TButton")

    def _create_diagonal_gradient(self, x0, y0, x1, y1, colors):
        if not hasattr(self, 'canvas'):
            return
        steps = 100
        for i in range(steps):
            r1, g1, b1 = self.root.winfo_rgb(colors[0])[:3]
            r2, g2, b2 = self.root.winfo_rgb(colors[-1])[:3]
            r = int(r1 + (r2 - r1) * i / (steps - 1))
            g = int(g1 + (g2 - g1) * i / (steps - 1))
            b = int(b1 + (b2 - b1) * i / (steps - 1))
            color = f'#{r:04x}{g:04x}{b:04x}'
            self.canvas.create_line(x0, y0 + (y1 - y0) * i / steps, x1, y0 + (y1 - y0) * (i + 1) / steps, fill=color, width=2)

    def _resize_canvas(self):
        if hasattr(self, 'canvas'):
            content_height = self.root.winfo_height() - self.header_frame.winfo_height() - self.status_bar.winfo_height()
            self.canvas.config(width=self.root.winfo_width() - self.sidebar.winfo_width(), height=content_height)
            self.canvas.place(x=self.sidebar.winfo_width(), y=self.header_frame.winfo_height())
            self._create_diagonal_gradient(0, 0, self.canvas.winfo_width(), self.canvas.winfo_height(), ["#1A2A44", "#2A4066", "#3A5577"])

    def clear_content(self):
        for frame in [self.process_management_frame, self.scheduling_frame, self.results_frame,
                     self.metrics_frame, self.comparison_frame, self.about_frame]:
            for widget in frame.winfo_children():
                widget.destroy()
            frame.pack_forget()
        self._resize_canvas()

    def show_process_management(self):
        self.clear_content()
        self.process_management_frame.pack(fill="both", expand=True)
        self.build_process_management()
        self.status_var.set("Process Management section loaded")
        self._resize_canvas()

    def show_scheduling(self):
        self.clear_content()
        self.scheduling_frame.pack(fill="both", expand=True)
        self.build_scheduling()
        self.status_var.set("Scheduling section loaded")
        self._resize_canvas()

    def show_results(self):
        self.clear_content()
        self.results_frame.pack(fill="both", expand=True)
        self.build_results()
        self.status_var.set("Results section loaded")
        self._resize_canvas()

    def show_metrics(self):
        self.clear_content()
        self.metrics_frame.pack(fill="both", expand=True)
        self.build_metrics()
        self.status_var.set("Metrics section loaded")
        self._resize_canvas()

    def show_comparison(self):
        self.clear_content()
        self.comparison_frame.pack(fill="both", expand=True)
        self.build_comparison()
        self.status_var.set("Comparison completed")
        self._resize_canvas()

    def show_about(self):
        self.clear_content()
        self.about_frame.pack(fill="both", expand=True)
        self.build_about()
        self.status_var.set("About section loaded")
        self._resize_canvas()

    def build_process_management(self):
        for widget in self.process_management_frame.winfo_children():
            widget.destroy()
        input_frame = ttk.LabelFrame(self.process_management_frame, text="Process Configuration", padding=5, style="Modern.TFrame")
        input_frame.pack(fill="x", pady=0)

        listbox_frame = ttk.Frame(input_frame)
        listbox_frame.pack(fill="both", expand=True, pady=2)
        if self.process_listbox is None or not self.process_listbox.winfo_exists():
            self.process_listbox = tk.Listbox(listbox_frame, height=10, bg="#4A6B9A", fg="#E6E6FA")
        self.process_listbox.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.process_listbox.yview, style="Vertical.TScrollbar")
        scrollbar.pack(side="right", fill="y")
        self.process_listbox.configure(yscrollcommand=scrollbar.set)

        input_subframe = ttk.Frame(input_frame)
        input_subframe.pack(fill="x", pady=2)

        headers = ["PID", "Arrival", "Burst", "Priority"]
        self.new_process_entries = []
        for i, header in enumerate(headers):
            ttk.Label(input_subframe, text=header, style="Modern.TLabel").grid(row=0, column=i, padx=5, pady=2, sticky="e")
            entry = ttk.Entry(input_subframe, width=10, style="TEntry")
            entry.grid(row=1, column=i, padx=5, pady=2)
            entry.insert(0, "0" if header != "PID" else f"P{len(self.processes) + 1}")
            self.new_process_entries.append(entry)

        button_frame = ttk.Frame(input_frame)
        button_frame.pack(pady=5)
        btn_configs = [
            ("Add Process", self.add_process),
            ("Random Processes", self.add_random_processes),
            ("Clear All", self.clear_all),
            ("Save Config", self.save_config),
            ("Load Config", self.load_config)
        ]
        for text, cmd in btn_configs:
            btn = ttk.Button(button_frame, text=text, command=cmd, style="Modern.TButton")
            btn.pack(side="left", padx=2)

    def update_process_listbox(self):
        if self.process_listbox is None or not self.process_listbox.winfo_exists():
            self.status_var.set("Error: Process listbox not initialized or destroyed")
            return
        self.process_listbox.delete(0, tk.END)
        for p in self.processes:
            self.process_listbox.insert(tk.END, f"{p.pid}: Arrival={p.arrival_time}, Burst={p.burst_time}, Priority={p.priority}")
        self.status_var.set(f"Updated process list: {len(self.processes)} processes")

    def add_process(self):
        try:
            pid = self.new_process_entries[0].get()
            arrival = int(self.new_process_entries[1].get())
            burst = int(self.new_process_entries[2].get())
            priority = int(self.new_process_entries[3].get())
            if arrival < 0 or burst <= 0:
                raise ValueError("Arrival must be >= 0, Burst must be > 0")
            process = Process(pid, arrival, burst, priority)
            self.processes.append(process)
            self.update_process_listbox()
            self.new_process_entries[0].delete(0, tk.END)
            self.new_process_entries[0].insert(0, f"P{len(self.processes) + 1}")
            self.status_var.set(f"Added process {pid}")
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self.root)
            self.status_var.set("Error adding process")

    def add_random_processes(self):
        num_processes = random.randint(3, 10)
        for _ in range(num_processes):
            pid = f"P{len(self.processes) + 1}"
            arrival = random.randint(0, 10)
            burst = random.randint(1, 10)
            priority = random.randint(0, 5)
            self.processes.append(Process(pid, arrival, burst, priority))
        self.update_process_listbox()
        self.status_var.set(f"Added {num_processes} random processes")

    def clear_all(self):
        self.processes.clear()
        self.update_process_listbox()
        self.status_var.set("Cleared all processes")

    def save_config(self):
        config = [{"pid": p.pid, "arrival": p.arrival_time, "burst": p.burst_time, "priority": p.priority} 
                  for p in self.processes]
        file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file:
            with open(file, "w") as f:
                json.dump(config, f)
            self.status_var.set(f"Saved configuration to {file}")

    def load_config(self):
        file = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file:
            with open(file, "r") as f:
                config = json.load(f)
            self.processes.clear()
            for proc in config:
                self.processes.append(Process(proc["pid"], proc["arrival"], proc["burst"], proc["priority"]))
            self.update_process_listbox()
            self.status_var.set(f"Loaded configuration from {file}")

    def build_scheduling(self):
        for widget in self.scheduling_frame.winfo_children():
            widget.destroy()
        algo_frame = ttk.LabelFrame(self.scheduling_frame, text="Algorithm & Settings", padding=5, style="Modern.TFrame")
        algo_frame.pack(fill="both", expand=True, pady=0)

        self.algo_var = tk.StringVar(value="Intelligent")
        algos = [
            ("FCFS", "FCFS"), ("SJF (NP)", "SJF-NP"), ("SJF (P)", "SJF-P"),
            ("Round Robin", "RR"), ("Priority (NP)", "PR-NP"), ("Priority (P)", "PR-P"),
            ("MLFQ", "MLFQ"), ("Intelligent", "Intelligent"), ("Custom", "Custom")
        ]
        algo_subframe = ttk.Frame(algo_frame)
        algo_subframe.pack(fill="x", pady=2)
        for i, (text, value) in enumerate(algos):
            btn = ttk.Radiobutton(algo_subframe, text=text, variable=self.algo_var, value=value, style="TRadiobutton")
            btn.grid(row=0, column=i, padx=5, pady=2)

        settings_frame = ttk.Frame(algo_frame)
        settings_frame.pack(fill="x", pady=2)

        ttk.Label(settings_frame, text="Quantum:", style="Modern.TLabel").grid(row=0, column=0, padx=5, sticky="e")
        self.quantum_var = tk.StringVar(value="2")
        ttk.Entry(settings_frame, textvariable=self.quantum_var, width=5, style="TEntry").grid(row=0, column=1, padx=5)

        ttk.Label(settings_frame, text="Number of Cores:", style="Modern.TLabel").grid(row=0, column=2, padx=5, sticky="e")
        self.cores_var = tk.StringVar(value="1")
        ttk.Entry(settings_frame, textvariable=self.cores_var, width=5, style="TEntry").grid(row=0, column=3, padx=5)

        self.custom_algo_frame = ttk.Frame(algo_frame)
        self.custom_algo_frame.pack(fill="both", expand=True, pady=2)
        ttk.Label(self.custom_algo_frame, text="Custom Algorithm (Python Code):", style="Modern.TLabel").pack(anchor="w")
        self.custom_algo_text = tk.Text(self.custom_algo_frame, height=5, width=50, bg="#4A6B9A", fg="#E6E6FA", insertbackground="#B0B0FF")
        self.custom_algo_text.pack(fill="both", expand=True, pady=2)
        self.custom_algo_text.insert(tk.END, "# Define your custom scheduling algorithm here\ndef custom_scheduler(processes, quantum):\n    return processes, 'Custom', []")

        control_frame = ttk.Frame(algo_frame)
        control_frame.pack(pady=5)
        btn_configs = [
            ("Run Simulation", self.run_simulation, "Run.TButton"),
            ("Step Simulation", self.start_step_mode, "Step.TButton"),
            ("View Gantt", self.view_gantt, "Gantt.TButton"),
            ("Compare All", self.run_comparison, "Compare.TButton")
        ]
        for text, cmd, style_name in btn_configs:
            btn = ttk.Button(control_frame, text=text, command=cmd, style=style_name)
            btn.pack(side="left", padx=2)

        test_btn = ttk.Button(algo_frame, text="Test Code", command=self.test_custom_code, style="Test.TButton")
        test_btn.pack(pady=5)

    def test_custom_code(self):
        custom_code = self.custom_algo_text.get("1.0", tk.END)
        try:
            local_vars = {"processes": [], "quantum": 2}
            exec(custom_code, globals(), local_vars)
            result = local_vars.get("custom_scheduler", lambda p, q: (p, "Custom", []))(local_vars["processes"], local_vars["quantum"])
            messagebox.showinfo("Test Result", f"Custom code executed: {result}", parent=self.root)
            self.status_var.set("Custom code tested successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Test failed: {str(e)}", parent=self.root)
            self.status_var.set("Custom code test failed")

    def run_simulation(self):
        if not self.processes:
            if not messagebox.askyesno("Warning", "No processes added. Add random processes?", parent=self.root):
                self.status_var.set("Simulation cancelled: No processes")
                return
            self.add_random_processes()
        try:
            self.status_var.set("Running simulation...")
            self.num_cores = int(self.cores_var.get())
            algo = self.algo_var.get()
            quantum = int(self.quantum_var.get())
            if algo == "Custom":
                custom_code = self.custom_algo_text.get("1.0", tk.END)
                processes, algo_name, timeline = self.run_custom_algorithm(custom_code, self.processes[:], quantum)
            elif algo == "Intelligent":
                predicted_algo = self.ai_scheduler.predict_best_algorithm(self.processes)
                processes, algo_name, timeline = self.run_algorithm(predicted_algo, self.processes[:], quantum)
                algo_name = f"Intelligent ({predicted_algo})"
            else:
                processes, algo_name, timeline = self.run_algorithm(algo, self.processes[:], quantum)
            self.current_processes = processes
            self.current_algo_name = algo_name
            self.timeline = timeline
            self.show_results()
            self.display_results(processes, algo_name, *calculate_metrics(processes))
            self.status_var.set("Simulation completed")
        except Exception as e:
            messagebox.showerror("Error", f"Simulation failed: {str(e)}", parent=self.root)
            self.status_var.set("Simulation failed")

    def run_algorithm(self, algo, processes, quantum):
        if algo == "FCFS":
            return multi_core_scheduler(processes, self.num_cores, fcfs_scheduler)
        elif algo == "SJF-NP":
            return multi_core_scheduler(processes, self.num_cores, sjf_non_preemptive)
        elif algo == "SJF-P":
            return multi_core_scheduler(processes, self.num_cores, sjf_preemptive)
        elif algo == "RR":
            return multi_core_scheduler(processes, self.num_cores, lambda p: rr_scheduler(p, quantum))
        elif algo == "PR-NP":
            return multi_core_scheduler(processes, self.num_cores, priority_non_preemptive)
        elif algo == "PR-P":
            return multi_core_scheduler(processes, self.num_cores, priority_preemptive)
        elif algo == "MLFQ":
            return multi_core_scheduler(processes, self.num_cores, lambda p: mlfq_scheduler(p, [quantum, quantum * 2, quantum * 4]))
        elif algo == "Intelligent":
            return multi_core_scheduler(processes, self.num_cores, lambda p: intelligent_scheduler(p, quantum))
        else:
            raise ValueError(f"Unknown algorithm: {algo}")

    def run_custom_algorithm(self, code, processes, quantum):
        local_vars = {"processes": processes, "quantum": quantum}
        exec(code, globals(), local_vars)
        return local_vars.get("custom_scheduler", lambda p, q: (p, "Custom", []))(processes, quantum)

    def start_step_mode(self):
        if not self.processes:
            if not messagebox.askyesno("Warning", "No processes added. Add random processes?", parent=self.root):
                self.status_var.set("Step mode cancelled: No processes")
                return
            self.add_random_processes()
        try:
            self.status_var.set("Starting step mode...")
            self.num_cores = int(self.cores_var.get())
            algo = self.algo_var.get()
            quantum = int(self.quantum_var.get())
            if algo == "Custom":
                custom_code = self.custom_algo_text.get("1.0", tk.END)
                self.step_processes, self.current_algo_name, self.step_timeline = self.run_custom_algorithm(custom_code, self.processes[:], quantum)
            elif algo == "Intelligent":
                predicted_algo = self.ai_scheduler.predict_best_algorithm(self.processes)
                self.step_processes, self.current_algo_name, self.step_timeline = self.run_algorithm(predicted_algo, self.processes[:], quantum)
                self.current_algo_name = f"Intelligent ({predicted_algo})"
            else:
                self.step_processes, self.current_algo_name, self.step_timeline = self.run_algorithm(algo, self.processes[:], quantum)
            self.step_mode = True
            self.current_step = 0
            self.timeline = self.step_timeline
            self.show_results()
            self.step_simulation()
            self.status_var.set("Step mode started")
        except Exception as e:
            messagebox.showerror("Error", f"Step mode failed: {str(e)}", parent=self.root)
            self.status_var.set("Step mode failed")

    def step_simulation(self):
        if not self.step_mode or self.current_step >= len(self.step_timeline):
            self.step_mode = False
            self.display_results(self.step_processes, self.current_algo_name, *calculate_metrics(self.step_processes))
            self.status_var.set("Step mode completed")
            return
        self.current_step += 1
        self.timeline = self.step_timeline[:self.current_step]
        self.display_results(self.step_processes, self.current_algo_name, *calculate_metrics(self.step_processes))
        self.status_var.set(f"Step {self.current_step} of {len(self.step_timeline)}")

    def build_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        result_frame = ttk.LabelFrame(self.results_frame, text="Simulation Results", padding=5, style="Modern.TFrame")
        result_frame.pack(fill="both", expand=True, pady=0)

        self.algo_label = ttk.Label(result_frame, text="Algorithm: N/A", style="Modern.TLabel")
        self.algo_label.pack(anchor="w", pady=2)
        self.wait_label = ttk.Label(result_frame, text="Avg Waiting Time: N/A", style="Modern.TLabel")
        self.wait_label.pack(anchor="w", padx=5, pady=2)
        self.turn_label = ttk.Label(result_frame, text="Avg Turnaround Time: N/A", style="Modern.TLabel")
        self.turn_label.pack(anchor="w", padx=5, pady=2)
        self.cpu_label = ttk.Label(result_frame, text="CPU Utilization: N/A", style="Modern.TLabel")
        self.cpu_label.pack(anchor="w", padx=5, pady=2)
        self.throughput_label = ttk.Label(result_frame, text="Throughput: N/A", style="Modern.TLabel")
        self.throughput_label.pack(anchor="w", padx=5, pady=2)

        self.result_tree = ttk.Treeview(result_frame, columns=("PID", "Start", "End", "Waiting", "Turnaround"), show="headings", height=10, style="Treeview")
        for col in ("PID", "Start", "End", "Waiting", "Turnaround"):
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=120, anchor="center")
        self.result_tree.pack(fill="both", expand=True, padx=5, pady=2)

    def display_results(self, processes, algo_name, avg_wait, avg_turn, cpu_util, throughput):
        if not hasattr(self, 'algo_label'):
            self.show_results()
        self.algo_label.config(text=f"Algorithm: {algo_name}")
        self.wait_label.config(text=f"Avg Waiting Time: {avg_wait:.2f}")
        self.turn_label.config(text=f"Avg Turnaround Time: {avg_turn:.2f}")
        self.cpu_label.config(text=f"CPU Utilization: {cpu_util:.2f}%")
        self.throughput_label.config(text=f"Throughput: {throughput:.4f}")
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        for p in processes:
            start = p.start_time if p.start_time is not None else "N/A"
            self.result_tree.insert("", "end", values=(p.pid, start, p.end_time, p.waiting_time, p.turnaround_time))
        self.status_var.set("Results updated")

    def view_gantt(self):
        if not self.timeline:
            messagebox.showwarning("Warning", "No timeline available. Run a simulation first.", parent=self.root)
            self.status_var.set("No timeline available")
            return
        print(f"Opening Gantt chart with timeline: {self.timeline}")
        visualizer = SchedulerVisualizer()
        visualizer.display_gantt_chart(self.current_algo_name, self.current_processes, self.timeline)
        self.status_var.set("Gantt chart opened")

    def run_comparison(self):
        if not self.processes:
            if not messagebox.askyesno("Warning", "No processes added. Add random processes?", parent=self.root):
                self.status_var.set("Comparison cancelled: No processes")
                return
            self.add_random_processes()

        if self.comparison_thread and self.comparison_thread.is_alive():
            self.status_var.set("Comparison already in progress...")
            return

        self.status_var.set("Starting comparison...")
        self.comparison_results.clear()
        self.comparison_thread = threading.Thread(target=self._run_comparison_task, daemon=True)
        self.comparison_thread.start()
        self.root.after(100, self._check_comparison_completion)

    def _run_comparison_task(self):
        try:
            quantum = int(self.quantum_var.get())
            self.num_cores = int(self.cores_var.get())
            algorithms = ["FCFS", "SJF-NP", "SJF-P", "RR", "PR-NP", "PR-P", "MLFQ", "Intelligent"]
            logging.info(f"Starting comparison with {len(self.processes)} processes, quantum={quantum}, cores={self.num_cores}")
            for i, algo in enumerate(algorithms, 1):
                logging.info(f"Starting {algo} at {time.time()}")
                processes_copy = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in self.processes]
                try:
                    if algo == "Intelligent":
                        predicted_algo = self.ai_scheduler.predict_best_algorithm(processes_copy)
                        processes, algo_name, timeline = self.run_algorithm(predicted_algo, processes_copy, quantum)
                        algo_name = f"Intelligent ({predicted_algo})"
                    else:
                        processes, algo_name, timeline = self.run_algorithm(algo, processes_copy, quantum)
                    avg_wait, avg_turn, cpu_util, throughput = calculate_metrics(processes)
                    self.comparison_results[algo_name] = {
                        "processes": processes,
                        "timeline": timeline,
                        "avg_wait": avg_wait,
                        "avg_turn": avg_turn,
                        "cpu_util": cpu_util,
                        "throughput": throughput
                    }
                    logging.info(f"Completed {algo_name}: Avg Wait={avg_wait:.2f}, Avg Turn={avg_turn:.2f}, CPU Util={cpu_util:.2f}%, Throughput={throughput:.4f} at {time.time()}")
                    self.root.after(0, lambda: self.status_var.set(f"Processing {algo} ({i}/{len(algorithms)})"))
                except Exception as e:
                    logging.error(f"Error running {algo} at {time.time()}: {str(e)}")
                logging.info(f"Finished {algo} at {time.time()}")
            logging.info(f"Comparison results: {list(self.comparison_results.keys())}")
            if not self.comparison_results:
                logging.warning("No results generated in comparison. Check algorithm implementations.")
        except Exception as e:
            logging.error(f"General error in comparison at {time.time()}: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Comparison failed: {str(e)}", parent=self.root))

    def _check_comparison_completion(self):
        if self.comparison_thread and not self.comparison_thread.is_alive():
            if self.comparison_results:
                self.show_comparison()
                self.status_var.set("Comparison completed")
            else:
                self.status_var.set("Comparison failed: No results generated")
        else:
            self.root.after(100, self._check_comparison_completion)

    def build_comparison(self):
        for widget in self.comparison_frame.winfo_children():
            if isinstance(widget, tk.Canvas):
                widget.destroy()
            else:
                widget.destroy()
        
        self.comparison_frame.pack_forget()
        self.comparison_frame.pack(fill="both", expand=True)

        comp_frame = ttk.LabelFrame(self.comparison_frame, text="Algorithm Comparison", padding=2, style="Modern.TFrame")
        comp_frame.pack(fill="both", expand=True, padx=5, pady=0)

        if not self.comparison_results:
            ttk.Label(comp_frame, text="Run comparison first or check console for errors.", style="Modern.TLabel").pack(pady=2)
            return

        table_frame = ttk.Frame(comp_frame)
        table_frame.pack(fill="both", expand=True, padx=5, pady=0)

        self.comp_tree = ttk.Treeview(table_frame, columns=("Algorithm", "Avg Wait", "Avg Turn", 
                            "CPU Util", "Throughput"), show="headings", height=10, style="Treeview")
        for col in ("Algorithm", "Avg Wait", "Avg Turn", "CPU Util", "Throughput"):
            self.comp_tree.heading(col, text=col)
            self.comp_tree.column(col, width=150, anchor="center")
        self.comp_tree.pack(fill="both", expand=True, padx=5, pady=2)

        btn_frame = ttk.Frame(table_frame)
        btn_frame.pack(pady=2)
        ttk.Button(btn_frame, text="Export Results", command=self.export_comparison, style="Modern.TButton").pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Update Charts", command=self.display_comparison, style="Modern.TButton").pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Show Best Algorithm", command=self.show_best_algorithm, style="Modern.TButton").pack(side="left", padx=2)
        ttk.Button(btn_frame, text="View Chart", command=self.view_comparison_chart, style="Modern.TButton").pack(side="left", padx=2)

        self.display_comparison()

    def draw_bar_chart(self, tab, data, title, ylabel, colors):
        for widget in tab.winfo_children():
            widget.destroy()

        logging.debug(f"Drawing bar chart with data: {data}")
        num_algorithms = len(data)
        canvas_width = max(800, num_algorithms * 120)
        canvas_height = 700
        canvas = tk.Canvas(tab, width=canvas_width, height=canvas_height, bg="#4A6B9A", highlightthickness=2, highlightbackground="#34495E")
        canvas.pack(fill="both", expand=True)

        if not data or not self.comparison_results:
            canvas.create_text(canvas_width // 2, canvas_height // 2, text="No data available", font=("Segoe UI", 12), fill="#E6E6FA")
            logging.warning("No data available for chart")
            return

        canvas.create_rectangle(10, 10, canvas_width - 10, 50, fill="#4A6B9A", outline="")
        self._create_diagonal_gradient(10, 10, canvas_width - 10, 50, ["#5A7B9A", "#34495E"])
        canvas.create_text(canvas_width // 2, 30, text=title, font=("Segoe UI", 14, "bold"), fill="#E6E6FA")
        canvas.create_text(canvas_width // 2 + 1, 31, text=title, font=("Segoe UI", 14, "bold"), fill="#B0B0FF")

        canvas.create_text(30, canvas_height // 2, text=ylabel, font=("Segoe UI", 10), angle=90, fill="#E6E6FA")
        canvas.create_text(31, canvas_height // 2 + 1, text=ylabel, font=("Segoe UI", 10), angle=90, fill="#B0B0FF")

        max_value = max(data) if max(data) > 0 else 1
        bar_width = 70
        spacing = 30
        total_width = num_algorithms * (bar_width + spacing)
        start_x = max(50, (canvas_width - total_width) // 2)

        for i, (value, algo) in enumerate(zip(data, self.comparison_results.keys())):
            x0 = start_x + i * (bar_width + spacing)
            height = (value / max_value) * (canvas_height - 200) if max_value > 0 else 0
            y0 = canvas_height - 150 - height

            rect_id = canvas.create_rectangle(x0, canvas_height - 150, x0 + bar_width, canvas_height - 150, fill=colors[i % len(colors)], outline="#E6E6FA", width=1)
            self._create_diagonal_gradient(x0, y0, x0 + bar_width, y0 + 10, [colors[i % len(colors)], "#5A7B9A"])
            canvas.create_rectangle(x0 + 2, y0 + 2, x0 + bar_width + 2, canvas_height - 150 + 2, fill="#333333", outline="", stipple="gray25")

            def animate_bar(i, height, rect_id):
                if height < (value / max_value) * (canvas_height - 200):
                    height += 5
                    canvas.coords(rect_id, x0, canvas_height - 150 - height, x0 + bar_width, canvas_height - 150)
                    self.root.after(10, lambda: animate_bar(i, height, rect_id))
            animate_bar(i, 0, rect_id)

            text_y = max(60, y0 - 20)
            canvas.create_text(x0 + bar_width // 2, text_y, text=f"{value:.2f}", font=("Segoe UI", 10, "bold"), fill="#E6E6FA")
            canvas.create_text(x0 + bar_width // 2 + 1, text_y + 1, text=f"{value:.2f}", font=("Segoe UI", 10, "bold"), fill="#B0B0FF")

            algo_short = algo.split()[0] if " " in algo else algo[:4]
            canvas.create_text(x0 + bar_width // 2, canvas_height - 100, text=algo_short, font=("Segoe UI", 10), angle=45, fill="#E6E6FA")

        canvas.create_line(50, canvas_height - 150, canvas_width - 50, canvas_height - 150, fill="#E6E6FA", width=2)
        canvas.create_line(50, 50, 50, canvas_height - 150, fill="#E6E6FA", width=2)
        canvas.create_line(51, 51, 51, canvas_height - 149, fill="#34495E", width=1, dash=(4, 4))

        for i in range(0, int(max_value) + 1, max(1, int(max_value) // 5)):
            y = canvas_height - 150 - (i / max_value) * (canvas_height - 200)
            canvas.create_line(50, y, canvas_width - 50, y, fill="#34495E", dash=(4, 4))
            canvas.create_text(40, y, text=str(i), font=("Segoe UI", 10), fill="#E6E6FA", anchor="e")

        logging.debug("Bar chart drawn successfully")

    def display_comparison(self):
        for item in self.comp_tree.get_children():
            self.comp_tree.delete(item)
        
        algorithms = list(self.comparison_results.keys())
        if not algorithms:
            self.status_var.set("No comparison results to display")
            return
        
        wait_times = [self.comparison_results[algo]["avg_wait"] for algo in algorithms]
        turn_times = [self.comparison_results[algo]["avg_turn"] for algo in algorithms]
        cpu_utils = [self.comparison_results[algo]["cpu_util"] for algo in algorithms]
        throughputs = [self.comparison_results[algo]["throughput"] for algo in algorithms]

        for algo, data in self.comparison_results.items():
            self.comp_tree.insert("", "end", values=(algo, f"{data['avg_wait']:.2f}", 
                            f"{data['avg_turn']:.2f}", f"{data['cpu_util']:.2f}%", 
                            f"{data['throughput']:.4f}"))

        self.status_var.set(f"Comparison displayed with {len(algorithms)} algorithms")

    def view_comparison_chart(self):
        if not self.comparison_results:
            messagebox.showwarning("Warning", "Run comparison first.", parent=self.root)
            self.status_var.set("No comparison results to display")
            return

        chart_window = tk.Toplevel(self.root)
        chart_window.title("Comparison Charts")
        chart_window.geometry("1200x700")
        chart_window.configure(bg="#1A2A44")

        chart_notebook = ttk.Notebook(chart_window)
        chart_notebook.pack(fill="both", expand=True, padx=10, pady=10)

        algorithms = list(self.comparison_results.keys())
        wait_times = [self.comparison_results[algo]["avg_wait"] for algo in algorithms]
        turn_times = [self.comparison_results[algo]["avg_turn"] for algo in algorithms]
        cpu_utils = [self.comparison_results[algo]["cpu_util"] for algo in algorithms]
        throughputs = [self.comparison_results[algo]["throughput"] for algo in algorithms]
        colors = ["#4CAF50", "#2196F3", "#FF9800", "#F44336", "#9C27B0", "#3F51B5", "#FF5722", "#009688"]

        wait_chart_tab = ttk.Frame(chart_notebook)
        turn_chart_tab = ttk.Frame(chart_notebook)
        cpu_chart_tab = ttk.Frame(chart_notebook)
        throughput_chart_tab = ttk.Frame(chart_notebook)

        chart_notebook.add(wait_chart_tab, text="Average Waiting Time")
        chart_notebook.add(turn_chart_tab, text="Average Turnaround Time")
        chart_notebook.add(cpu_chart_tab, text="CPU Utilization")
        chart_notebook.add(throughput_chart_tab, text="Throughput")

        self.draw_bar_chart(wait_chart_tab, wait_times, "Average Waiting Time Comparison", "Time (units)", colors)
        self.draw_bar_chart(turn_chart_tab, turn_times, "Average Turnaround Time Comparison", "Time (units)", colors)
        self.draw_bar_chart(cpu_chart_tab, cpu_utils, "CPU Utilization Comparison", "Percentage (%)", colors)
        self.draw_bar_chart(throughput_chart_tab, throughputs, "Throughput Comparison", "Processes/Unit Time", colors)

        self.status_var.set("Comparison charts opened in new window")

    def show_best_algorithm(self):
        if not self.comparison_results:
            messagebox.showwarning("Warning", "Run comparison first.", parent=self.root)
            return
        
        metrics = {
            "Lowest Avg Waiting Time": lambda x: min(x, key=lambda k: self.comparison_results[k]["avg_wait"]),
            "Lowest Avg Turnaround Time": lambda x: min(x, key=lambda k: self.comparison_results[k]["avg_turn"]),
            "Highest CPU Utilization": lambda x: max(x, key=lambda k: self.comparison_results[k]["cpu_util"]),
            "Highest Throughput": lambda x: max(x, key=lambda k: self.comparison_results[k]["throughput"])
        }
        
        metric_var = tk.StringVar(value=list(metrics.keys())[0])
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Best Metric")
        dialog.geometry("320x200")
        dialog.configure(bg="#1A2A44")
        
        ttk.Label(dialog, text="Choose metric to determine the best algorithm:", style="Modern.TLabel").pack(pady=5)
        for metric in metrics.keys():
            ttk.Radiobutton(dialog, text=metric, variable=metric_var, value=metric, style="TRadiobutton").pack(anchor="w", padx=10, pady=2)
        
        def on_submit():
            selected_metric = metric_var.get()
            best_algo = metrics[selected_metric](self.comparison_results.keys())
            best_values = self.comparison_results[best_algo]
            message = (f"Best Algorithm: {best_algo}\n"
                      f"Avg Waiting Time: {best_values['avg_wait']:.2f}\n"
                      f"Avg Turnaround Time: {best_values['avg_turn']:.2f}\n"
                      f"CPU Utilization: {best_values['cpu_util']:.2f}%\n"
                      f"Throughput: {best_values['throughput']:.4f}")
            messagebox.showinfo("Best Algorithm", message, parent=self.root)
            dialog.destroy()
        
        ttk.Button(dialog, text="Submit", command=on_submit, style="Modern.TButton").pack(pady=10)
        dialog.transient(self.root)
        dialog.grab_set()

    def export_comparison(self):
        file = filedialog.asksaveasfilename(defaultextension=".csv", 
                                          filetypes=[("CSV files", "*.csv")])
        if file:
            with open(file, "w") as f:
                f.write("Algorithm,Avg Wait,Avg Turn,CPU Util,Throughput\n")
                for algo, data in self.comparison_results.items():
                    f.write(f"{algo},{data['avg_wait']:.2f},{data['avg_turn']:.2f},"
                           f"{data['cpu_util']:.2f},{data['throughput']:.4f}\n")
            self.status_var.set(f"Comparison exported to {file}")

    def build_metrics(self):
        for widget in self.metrics_frame.winfo_children():
            widget.destroy()
        metrics_frame = ttk.LabelFrame(self.metrics_frame, text="Performance Metrics", padding=5, style="Modern.TFrame")
        metrics_frame.pack(fill="both", expand=True, pady=0)
        if self.current_processes:
            PerformanceMetrics(self.current_processes, metrics_frame)
            self.status_var.set("Metrics displayed")
        else:
            ttk.Label(metrics_frame, text="No metrics available. Run a simulation first.", style="Modern.TLabel").pack(pady=2)
            self.status_var.set("No metrics available")

    def build_about(self):
        for widget in self.about_frame.winfo_children():
            widget.destroy()
        about_frame = ttk.LabelFrame(self.about_frame, text="About", padding=5, style="Modern.TFrame")
        about_frame.pack(fill="both", expand=True, pady=0)

        # Project Title
        ttk.Label(about_frame, text="Project Title: CPU Scheduler Simulator", style="Modern.TLabel").pack(pady=2)

        # Description
        ttk.Label(about_frame, text="Description: A GUI-based tool to simulate various CPU scheduling algorithms with visualization and performance metrics.", style="Modern.TLabel").pack(pady=2)

        # Installation Instructions
        ttk.Label(about_frame, text="Installation Instructions:", style="Modern.TLabel", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=2)
        ttk.Label(about_frame, text="Clone the repository: git clone https://github.com/gauravtiwarrii/cpu-scheduler-simulator.git", style="Modern.TLabel").pack(anchor="w", pady=1)
        ttk.Label(about_frame, text="cd cpu-scheduler-simulator", style="Modern.TLabel").pack(anchor="w", pady=1)
        ttk.Label(about_frame, text="Install dependencies: pip install -r requirements.txt", style="Modern.TLabel").pack(anchor="w", pady=1)
        ttk.Label(about_frame, text="Run the application: python main.py", style="Modern.TLabel").pack(anchor="w", pady=2)

        # Features
        ttk.Label(about_frame, text="Features:", style="Modern.TLabel", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=2)
        features = [
            "Supports FCFS, SJF (Non-Preemptive/Preemptive), Round Robin, Priority (Non-Preemptive/Preemptive), and Intelligent scheduling.",
            "Interactive GUI for process configuration.",
            "Gantt chart visualization (static and animated).",
            "Performance comparison of all algorithms.",
            "Export results to CSV."
        ]
        for feature in features:
            ttk.Label(about_frame, text=feature, style="Modern.TLabel", wraplength=600).pack(anchor="w", pady=1)

        # Usage
        ttk.Label(about_frame, text="Usage:", style="Modern.TLabel", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=2)
        usage = [
            "Add processes with PID, arrival time, burst time, and priority.",
            "Select an algorithm and run the simulation.",
            "View metrics and Gantt chart.",
            "Export results as needed."
        ]
        for use in usage:
            ttk.Label(about_frame, text=use, style="Modern.TLabel").pack(anchor="w", pady=1)

        # Contributors
        ttk.Label(about_frame, text="Contributors:", style="Modern.TLabel", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=2)
        contributors = [
            "Gaurav Tiwari: Implemented scheduling algorithms",
            "Kundan kr Ray: Developed the GUI frontend",
            "Harshit Kumar Verma: Created visualization and utilities"
        ]
        for contributor in contributors:
            ttk.Label(about_frame, text=contributor, style="Modern.TLabel").pack(anchor="w", pady=1)

        # Additional Info
        ttk.Label(about_frame, text="Date: April 10, 2025", style="Modern.TLabel").pack(pady=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerGUI(root)
    root.mainloop()