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

    processes = [p.strip().upper() for p in lines[0].split("=")[1].split(",")]
    arrival = list(map(int, lines[1].split("=")[1].strip().split(",")))
    burst   = list(map(int, lines[2].split("=")[1].strip().split(",")))

    quantum = None
    priority = None

    for line in lines[3:]:
        if "QT" in line:
            quantum = int(line.split("=")[1].strip())
        if "PS" in line:
            priority = list(map(int, line.split("=")[1].strip().split(",")))

    return processes, arrival, burst, quantum, priority


# ========== TABLE PRINTER ==========
def print_table(title, processes, arrival, burst, ct, wt, tat):
    print(f"\n{MAGENTA}=== {title} ==={RESET}")
    print(f"{YELLOW}{'PID':<8}{'Arrival':<10}{'Burst':<10}{'CT':<10}{'WT':<10}{'TAT':<12}{RESET}")
    print("-" * 65)

    for pid in sorted(processes, key=lambda p: int(p[1:])):
        i = processes.index(pid)
        print(f"{BLUE}{processes[i]:<8}{arrival[i]:<10}{burst[i]:<10}"
              f"{ct[i]:<10}{wt[i]:<10}{tat[i]:<12}{RESET}")

    print("-" * 65)
    print(f"{GREEN}Average WT:  {sum(wt)/len(wt):.2f}{RESET}")
    print(f"{GREEN}Average TAT: {sum(tat)/len(tat):.2f}{RESET}\n")


# ========== GANTT CHART ==========
def print_gantt_chart(gantt):
    print(f"{GREEN}\nGantt Chart:{RESET}")
    print(" ", end="")
    for p, _ in gantt:
        print(f"{GREEN}|  {p}  |{RESET}", end="")
    print()

    print("0", end="")
    for _, t in gantt:
        print(f"{GREEN}    {t}{RESET}", end="")
    print("\n")


# ======================================
#               FCFS
# ======================================
def fcfs(processes, arrival, burst):
    n = len(processes)
    ct = [0]*n
    wt = [0]*n
    tat = [0]*n

    time = 0
    gantt = []

    print(f"{MAGENTA}\n--- FCFS READY QUEUE ---{RESET}")

    for i in range(n):
        if time < arrival[i]:
            time = arrival[i]

        print(f"{CYAN}Time {time}: Ready Queue → [{processes[i]}]{RESET}")

        wt[i] = time - arrival[i]
        time += burst[i]
        ct[i] = time
        tat[i] = ct[i] - arrival[i]
        gantt.append((processes[i], time))

    print_table("FCFS Scheduling", processes, arrival, burst, ct, wt, tat)
    print_gantt_chart(gantt)


# ======================================
#         SJF (NON-PREEMPTIVE)
# ======================================
def sjf(processes, arrival, burst):
    n = len(processes)
    ct = [0]*n
    wt = [0]*n
    tat = [0]*n
    completed = [False]*n

    time = 0
    done = 0
    gantt = []

    print(f"{MAGENTA}\n--- SJF READY QUEUE ---{RESET}")

    while done < n:
        ready = [i for i in range(n) if arrival[i] <= time and not completed[i]]

        if ready:
            print(f"{CYAN}Time {time}: Ready Queue → {[processes[i] for i in ready]}{RESET}")

        idx = min(ready, key=lambda i: burst[i]) if ready else -1

        if idx == -1:
            time += 1
            continue

        time += burst[idx]
        ct[idx] = time
        tat[idx] = ct[idx] - arrival[idx]
        wt[idx] = tat[idx] - burst[idx]
        gantt.append((processes[idx], time))

        completed[idx] = True
        done += 1

    print_table("SJF Scheduling (Non-Preemptive)", processes, arrival, burst, ct, wt, tat)
    print_gantt_chart(gantt)


# ======================================
#     PRIORITY SCHEDULING (NON-PREEMPTIVE)
# ======================================
def priority_scheduling(processes, arrival, burst, priority):
    n = len(processes)
    ct = [0]*n
    wt = [0]*n
    tat = [0]*n
    completed = [False]*n

    time = 0
    done = 0
    gantt = []

    print(f"{MAGENTA}\n--- PRIORITY SCHEDULING READY QUEUE ---{RESET}")
    print(f"{YELLOW}(Lower number = Higher priority){RESET}")

    while done < n:
        ready = [i for i in range(n) if arrival[i] <= time and not completed[i]]

        if ready:
            rq = sorted(ready, key=lambda i: priority[i])
            print(f"{CYAN}Time {time}: Ready Queue → "
                  f"{[(processes[i], priority[i]) for i in rq]}{RESET}")

        idx = min(ready, key=lambda i: priority[i]) if ready else -1

        if idx == -1:
            time += 1
            continue

        time += burst[idx]
        ct[idx] = time
        tat[idx] = ct[idx] - arrival[idx]
        wt[idx] = tat[idx] - burst[idx]
        gantt.append((processes[idx], time))

        completed[idx] = True
        done += 1

    print_table("Priority Scheduling (Non-Preemptive)",
                processes, arrival, burst, ct, wt, tat)
    print_gantt_chart(gantt)


# ======================================
#        ROUND ROBIN (RR)
# ======================================
def round_robin(processes, arrival, burst, quantum):
    n = len(processes)
    remaining = burst.copy()
    ct = [0]*n
    wt = [0]*n
    tat = [0]*n

    time = 0
    queue = []
    gantt = []
    visited = [False]*n

    print(f"{MAGENTA}\n--- RR READY QUEUE ---{RESET}")
    print(f"{YELLOW}Quantum = {quantum}{RESET}")

    while True:
        for i in range(n):
            if arrival[i] <= time and not visited[i]:
                queue.append(i)
                visited[i] = True

        if not queue:
            time += 1
            continue

        print(f"{CYAN}Time {time}: Ready Queue → {[processes[i] for i in queue]}{RESET}")

        idx = queue.pop(0)

        if remaining[idx] > quantum:
            time += quantum
            remaining[idx] -= quantum
            gantt.append((processes[idx], time))
        else:
            time += remaining[idx]
            remaining[idx] = 0
            ct[idx] = time
            tat[idx] = ct[idx] - arrival[idx]
            wt[idx] = tat[idx] - burst[idx]
            gantt.append((processes[idx], time))

        for i in range(n):
            if arrival[i] <= time and not visited[i]:
                queue.append(i)
                visited[i] = True

        if remaining[idx] > 0:
            queue.append(idx)

        if all(r == 0 for r in remaining):
            break

    print_table("Round Robin Scheduling", processes, arrival, burst, ct, wt, tat)
    print_gantt_chart(gantt)


# ======================================
#                 MAIN
# ======================================
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scheduler.py input.txt")
        sys.exit(1)

    processes, arrival, burst, quantum, priority = parse_input(sys.argv[1])

    # Sort internally by arrival time
    zipped = list(zip(processes, arrival, burst))
    zipped.sort(key=lambda x: x[1])
    processes, arrival, burst = map(list, zip(*zipped))

    fcfs(processes, arrival, burst)
    sjf(processes, arrival, burst)

    if priority:
        priority_scheduling(processes, arrival, burst, priority)
    else:
        print(f"{YELLOW}No PS found → Skipping Priority Scheduling.{RESET}")

    if quantum:
        round_robin(processes, arrival, burst, quantum)
    else:
        print(f"{YELLOW}No QT found → Skipping RR Scheduling.{RESET}")
