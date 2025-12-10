#!/usr/bin/env python3

import sys

# ====== COLORS ======
RESET = "\033[0m"
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"

# ========== INPUT PARSER ==========
def parse_input(file_path):
    with open(file_path, "r") as f:
        lines = f.read().splitlines()

    processes = lines[0].split("=")[1].strip().replace(" ", "").split(",")
    arrival = list(map(int, lines[1].split("=")[1].strip().split(",")))
    burst   = list(map(int, lines[2].split("=")[1].strip().split(",")))

    return processes, arrival, burst


# ========== TABLE PRINTER ==========
def print_table(title, processes, arrival, burst, ct, waiting, turnaround):
    print(f"\n{MAGENTA}=== {title} ==={RESET}")
    print(f"{YELLOW}{'PID':<8}{'Arrival':<10}{'Burst':<10}{'CT':<10}{'WT':<10}{'TAT':<12}{RESET}")
    print("-" * 65)

    for i in range(len(processes)):
        print(f"{BLUE}{processes[i]:<8}{arrival[i]:<10}{burst[i]:<10}{ct[i]:<10}{waiting[i]:<10}{turnaround[i]:<12}{RESET}")

    print("-" * 65)
    print(f"{GREEN}Average WT:  {sum(waiting)/len(waiting):.2f}{RESET}")
    print(f"{GREEN}Average TAT: {sum(turnaround)/len(turnaround):.2f}{RESET}\n")


# ========== GANTT CHART ==========
def print_gantt_chart(gantt):
    print(f"{GREEN}\nGantt Chart:{RESET}")
    print(" ", end="")
    for p, t in gantt:
        print(f"{GREEN}|  {p}  |{RESET}", end="")
    print()

    print("0", end="")
    for p, t in gantt:
        print(f"{GREEN}    {t}{RESET}", end="")
    print("\n")


# ======================================
#               FCFS
# ======================================
def fcfs(processes, arrival, burst):
    n = len(processes)
    waiting = [0] * n
    turnaround = [0] * n
    ct = [0] * n

    time = 0
    ready_queue = []
    gantt = []

    print(f"{MAGENTA}\n--- FCFS READY QUEUE ---{RESET}")

    for i in range(n):
        if time < arrival[i]:
            time = arrival[i]

        ready_queue.append(processes[i])
        print(f"{CYAN}Time {time}: Ready Queue → {ready_queue}{RESET}")

        waiting[i] = time - arrival[i]
        time += burst[i]
        ct[i] = time
        turnaround[i] = ct[i] - arrival[i]

        gantt.append((processes[i], time))
        ready_queue.remove(processes[i])

    print_table("FCFS Scheduling", processes, arrival, burst, ct, waiting, turnaround)
    print_gantt_chart(gantt)


# ======================================
#         SJF (NON-PREEMPTIVE)
# ======================================
def sjf(processes, arrival, burst):
    n = len(processes)
    waiting = [0] * n
    turnaround = [0] * n
    ct = [0] * n

    completed = [False] * n
    time = 0
    done = 0

    gantt = []
    ready_queue = []

    print(f"{MAGENTA}\n--- SJF READY QUEUE ---{RESET}")

    while done < n:

        for i in range(n):
            if arrival[i] <= time and not completed[i] and processes[i] not in ready_queue:
                ready_queue.append(processes[i])

        if ready_queue:
            print(f"{CYAN}Time {time}: Ready Queue → {ready_queue}{RESET}")

        idx = -1
        min_burst = 999999

        for i in range(n):
            if arrival[i] <= time and not completed[i] and burst[i] < min_burst:
                min_burst = burst[i]
                idx = i

        if idx == -1:
            time += 1
            continue

        waiting[idx] = time - arrival[idx]
        time += burst[idx]
        ct[idx] = time
        turnaround[idx] = ct[idx] - arrival[idx]

        gantt.append((processes[idx], time))
        completed[idx] = True
        ready_queue.remove(processes[idx])

        done += 1

    print_table("SJF Scheduling (Non-Preemptive)", processes, arrival, burst, ct, waiting, turnaround)
    print_gantt_chart(gantt)


# ======================================
#                 MAIN
# ======================================
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scheduler.py input.txt")
        sys.exit(1)

    file_path = sys.argv[1]
    processes, arrival, burst = parse_input(file_path)

    zipped = list(zip(processes, arrival, burst))
    zipped.sort(key=lambda x: x[1])
    processes, arrival, burst = zip(*zipped)

    processes = list(processes)
    arrival = list(arrival)
    burst = list(burst)

    fcfs(processes, arrival, burst)
    sjf(processes, arrival, burst)
