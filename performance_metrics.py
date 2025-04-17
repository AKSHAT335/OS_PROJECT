# performance_metrics.py
import tkinter as tk
from tkinter import ttk
from cpu_scheduler_algorithms import calculate_metrics

class PerformanceMetrics:
    def __init__(self, processes, frame):
        if not processes:
            ttk.Label(frame, text="No metrics available. Run a simulation first.").pack(pady=20)
            return

        # Calculate metrics
        avg_wait, avg_turn, cpu_util, throughput = calculate_metrics(processes)

        # Create a frame for metrics display
        metrics_frame = ttk.LabelFrame(frame, text="Performance Metrics", padding=10)
        metrics_frame.pack(fill="both", expand=True, pady=10)

        # Display metrics
        ttk.Label(metrics_frame, text=f"Average Waiting Time: {avg_wait:.2f}").pack(anchor="w", padx=10, pady=5)
        ttk.Label(metrics_frame, text=f"Average Turnaround Time: {avg_turn:.2f}").pack(anchor="w", padx=10, pady=5)
        ttk.Label(metrics_frame, text=f"CPU Utilization: {cpu_util:.2f}%").pack(anchor="w", padx=10, pady=5)
        ttk.Label(metrics_frame, text=f"Throughput: {throughput:.4f}").pack(anchor="w", padx=10, pady=5)