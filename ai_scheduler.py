# ai_scheduler.py
class AIScheduler:
    def predict_best_algorithm(self, processes):
        if not processes:
            return "FCFS"
        avg_burst = sum(p.burst_time for p in processes) / len(processes)
        return "SJF-P" if avg_burst <= 5 else "RR"