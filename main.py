# main.py
import tkinter as tk
import traceback

if __name__ == "__main__":
    try:
        root = tk.Tk()
        from cpu_scheduler_gui import SchedulerGUI
        app = SchedulerGUI(root)
        root.mainloop()
    except Exception as e:
        print("An error occurred:")
        print(traceback.format_exc())