import random
from copy import deepcopy

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.original_priority = priority
        self.remaining_time = burst_time
        self.start_time = None
        self.end_time = None
        self.waiting_time = 0
        self.turnaround_time = 0
        self.last_scheduled = 0

def calculate_metrics(processes):
    if not processes:
        return 0, 0, 0, 0
    total_wait = sum(p.waiting_time for p in processes)
    total_turn = sum(p.turnaround_time for p in processes)
    total_burst = sum(p.burst_time for p in processes)
    end_time = max(p.end_time for p in processes if p.end_time is not None)
    avg_wait = total_wait / len(processes)
    avg_turn = total_turn / len(processes)
    cpu_util = (total_burst / end_time) * 100 if end_time > 0 else 0
    throughput = len(processes) / end_time if end_time > 0 else 0
    return avg_wait, avg_turn, cpu_util, throughput

def priority_boost(processes, current_time, boost_interval=10):
    for p in processes:
        if current_time - p.last_scheduled > boost_interval and p.remaining_time > 0:
            p.priority = max(0, p.priority - 1)
            p.last_scheduled = current_time

def multi_core_scheduler(processes, num_cores, scheduler_func):
    if num_cores == 1:
        return scheduler_func(processes)
    processes = deepcopy(processes)
    processes.sort(key=lambda x: x.arrival_time)
    timelines = [[] for _ in range(num_cores)]
    current_times = [0] * num_cores
    completed = []
    ready_queue = []
    all_processes = processes.copy()
    max_iterations = 10000  # Safeguard against infinite loops
    iteration = 0

    while processes or ready_queue or any(p.remaining_time > 0 for p in all_processes if p not in completed):
        if iteration > max_iterations:
            print(f"Warning: Multi-core scheduler exceeded {max_iterations} iterations for {scheduler_func.__name__}, terminating.")
            break
        iteration += 1
        # Add newly arrived processes to ready queue
        while processes and processes[0].arrival_time <= min(current_times):
            ready_queue.append(processes.pop(0))
        priority_boost(ready_queue, min(current_times))

        # Process one job per core if available
        for core in range(num_cores):
            if not ready_queue:
                current_times[core] += 1
                continue
            # Use a copy of ready_queue for the scheduler
            sub_processes = [p for p in ready_queue if p.arrival_time <= current_times[core]]
            if not sub_processes:
                current_times[core] += 1
                continue
            sub_processes, algo_name, sub_timeline = scheduler_func(sub_processes)
            if not sub_timeline:
                current_times[core] += 1
                continue
            pid, start, end = sub_timeline[0]
            process = next(p for p in ready_queue if p.pid == pid and p in sub_processes)
            ready_queue.remove(process)
            if current_times[core] < process.arrival_time:
                current_times[core] = process.arrival_time
            start = current_times[core]
            execute_time = min(process.remaining_time, end - start)
            process.remaining_time -= execute_time
            if process.start_time is None:
                process.start_time = start
            timelines[core].append((f"{process.pid} (Core {core})", start, start + execute_time))
            current_times[core] += execute_time
            process.last_scheduled = current_times[core]
            if process.remaining_time == 0:
                process.end_time = current_times[core]
                process.turnaround_time = process.end_time - process.arrival_time
                process.waiting_time = process.turnaround_time - process.burst_time
                completed.append(process)
            else:
                ready_queue.append(process)

    # Merge timelines
    merged_timeline = []
    for core, timeline in enumerate(timelines):
        for entry in timeline:
            merged_timeline.append(entry)
    merged_timeline.sort(key=lambda x: x[1])
    return completed, f"{algo_name} (Multi-Core)", merged_timeline

def fcfs_scheduler(processes):
    processes.sort(key=lambda x: x.arrival_time)
    timeline = []
    current_time = 0
    for p in processes:
        if current_time < p.arrival_time:
            current_time = p.arrival_time
        p.start_time = current_time
        timeline.append((p.pid, current_time, current_time + p.burst_time))
        current_time += p.burst_time
        p.end_time = current_time
        p.turnaround_time = p.end_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time
    return processes, "FCFS", timeline

def sjf_non_preemptive(processes):
    processes.sort(key=lambda x: x.arrival_time)
    timeline = []
    current_time = 0
    completed = []
    while processes or any(p.arrival_time <= current_time for p in processes):
        available = [p for p in processes if p.arrival_time <= current_time]
        if not available:
            current_time += 1
            continue
        available.sort(key=lambda x: x.burst_time)
        p = available[0]
        processes.remove(p)
        p.start_time = current_time
        timeline.append((p.pid, current_time, current_time + p.burst_time))
        current_time += p.burst_time
        p.end_time = current_time
        p.turnaround_time = p.end_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time
        completed.append(p)
    return completed, "SJF (Non-Preemptive)", timeline

def sjf_preemptive(processes):
    processes.sort(key=lambda x: x.arrival_time)
    timeline = []
    current_time = 0
    completed = []
    current_process = None
    while processes or current_process:
        available = [p for p in processes if p.arrival_time <= current_time]
        if available:
            available.sort(key=lambda x: x.remaining_time)
            if current_process and current_process in processes:
                available.append(current_process)
            current_process = min(available, key=lambda x: x.remaining_time)
            if current_process in processes:
                processes.remove(current_process)
        if current_process and current_process not in completed:
            if current_process.start_time is None:
                current_process.start_time = current_time
            execute_time = 1  # Preemptive step by step
            timeline.append((current_process.pid, current_time, current_time + execute_time))
            current_process.remaining_time -= execute_time
            current_time += execute_time
            if current_process.remaining_time <= 0:
                current_process.end_time = current_time
                current_process.turnaround_time = current_process.end_time - current_process.arrival_time
                current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
                completed.append(current_process)
                current_process = None
        else:
            current_time += 1
    return completed, "SJF (Preemptive)", timeline

def rr_scheduler(processes, quantum):
    processes.sort(key=lambda x: x.arrival_time)
    timeline = []
    current_time = 0
    queue = []
    completed = []
    while processes or queue:
        while processes and processes[0].arrival_time <= current_time:
            queue.append(processes.pop(0))
        if not queue:
            current_time += 1
            continue
        p = queue.pop(0)
        if p.start_time is None:
            p.start_time = current_time
        time_slice = min(quantum, p.remaining_time)
        timeline.append((p.pid, current_time, current_time + time_slice))
        current_time += time_slice
        p.remaining_time -= time_slice
        if p.remaining_time == 0:
            p.end_time = current_time
            p.turnaround_time = p.end_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            completed.append(p)
        else:
            queue.append(p)
    return completed, "Round Robin", timeline

def priority_non_preemptive(processes):
    processes.sort(key=lambda x: x.arrival_time)
    timeline = []
    current_time = 0
    completed = []
    while processes or any(p.arrival_time <= current_time for p in processes):
        available = [p for p in processes if p.arrival_time <= current_time]
        if not available:
            current_time += 1
            continue
        available.sort(key=lambda x: x.priority)
        p = available[0]
        processes.remove(p)
        p.start_time = current_time
        timeline.append((p.pid, current_time, current_time + p.burst_time))
        current_time += p.burst_time
        p.end_time = current_time
        p.turnaround_time = p.end_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time
        completed.append(p)
    return completed, "Priority (Non-Preemptive)", timeline

def priority_preemptive(processes):
    processes.sort(key=lambda x: x.arrival_time)
    timeline = []
    current_time = 0
    completed = []
    current_process = None
    while processes or current_process:
        available = [p for p in processes if p.arrival_time <= current_time]
        if available:
            available.sort(key=lambda x: x.priority)
            if current_process and current_process in processes and current_process.priority < min(p.priority for p in available):
                available.append(current_process)
            current_process = min(available, key=lambda x: x.priority)
            if current_process in processes:
                processes.remove(current_process)
        if current_process and current_process not in completed:
            if current_process.start_time is None:
                current_process.start_time = current_time
            execute_time = 1  # Preemptive step by step
            timeline.append((current_process.pid, current_time, current_time + execute_time))
            current_process.remaining_time -= execute_time
            current_time += execute_time
            if current_process.remaining_time <= 0:
                current_process.end_time = current_time
                current_process.turnaround_time = current_process.end_time - current_process.arrival_time
                current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
                completed.append(current_process)
                current_process = None
        else:
            current_time += 1
    return completed, "Priority (Preemptive)", timeline

def mlfq_scheduler(processes, quanta):
    processes.sort(key=lambda x: x.arrival_time)
    timeline = []
    current_time = 0
    queues = [[] for _ in range(len(quanta))]
    completed = []
    queues[0].extend(processes)
    processes.clear()
    max_iterations = 10000  # Safeguard against infinite loops
    iteration = 0

    while any(queues):
        if iteration > max_iterations:
            print(f"Warning: MLFQ scheduler exceeded {max_iterations} iterations, terminating.")
            break
        iteration += 1
        # Find the highest non-empty queue
        current_queue = next((i for i, q in enumerate(queues) if q), len(queues))
        if current_queue >= len(queues) and not queues[current_queue - 1]:
            current_time += 1
            continue
        if current_queue < len(queues) and queues[current_queue]:
            print(f"Processing queue {current_queue} at time {current_time}, queue sizes: {[len(q) for q in queues]}")
            current_process = queues[current_queue].pop(0)
            if current_process.start_time is None:
                current_process.start_time = current_time
            quantum = quanta[current_queue]
            time_slice = min(quantum, current_process.remaining_time)
            timeline.append((current_process.pid, current_time, current_time + time_slice))
            current_time += time_slice
            current_process.remaining_time -= time_slice
            if current_process.remaining_time == 0:
                current_process.end_time = current_time
                current_process.turnaround_time = current_process.end_time - current_process.arrival_time
                current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
                completed.append(current_process)
            else:
                next_queue = min(current_queue + 1, len(queues) - 1)
                current_process.priority = next_queue
                queues[next_queue].append(current_process)
        # Handle new arrivals
        new_arrivals = [p for p in processes if p.arrival_time <= current_time]
        for p in new_arrivals:
            processes.remove(p)
            p.priority = 0
            queues[0].append(p)
    return completed, "MLFQ", timeline

def intelligent_scheduler(processes, quantum):
    total_priority = sum(p.priority for p in processes)
    avg_priority = total_priority / len(processes) if processes else 0
    total_burst = sum(p.burst_time for p in processes)
    avg_burst = total_burst / len(processes) if processes else 0
    if avg_priority <= 2 and avg_burst <= 5:
        return sjf_preemptive(processes)
    elif avg_priority > 2 and avg_burst > 5:
        return priority_preemptive(processes)
    else:
        return rr_scheduler(processes, quantum)