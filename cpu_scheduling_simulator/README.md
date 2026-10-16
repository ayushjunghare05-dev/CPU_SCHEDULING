# CPU Scheduling Simulator — OSY Micro Project

A local, interactive web application for demonstrating three Operating Systems CPU scheduling algorithms:

- **FCFS (First Come, First Served)** — non-preemptive
- **SJF (Shortest Job First)** — non-preemptive; chooses the shortest burst among the processes that have already arrived
- **Round Robin** — preemptive time-slicing with a configurable time quantum

The simulator shows Gantt charts, per-process completion/turnaround/waiting/response times, averages, CPU utilization, throughput, and a side-by-side comparison.

## Requirements

- Python 3.10 or newer recommended
- No third-party Python packages are required.
- A modern browser

## Run on Windows

1. Extract the project ZIP.
2. Open Command Prompt or PowerShell in the `cpu_scheduling_simulator` folder.
3. (Recommended) Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Start the local server:

   ```powershell
   py app.py
   ```

5. Open **http://127.0.0.1:5000** in your browser.

## Run on Linux/macOS

```bash
python3 app.py
```

Then open **http://127.0.0.1:5000**.

## How to use

1. Edit the process ID, arrival time (AT), and burst time (BT) values, or use **Load sample data**.
2. Set a positive time quantum for Round Robin.
3. Select **Run simulation**. The app runs all algorithms against the same inputs.
4. Inspect the Gantt charts and result table. Scroll down to compare the average metrics.

## Formulas

- **Completion Time (CT):** time at which a process finishes.
- **Turnaround Time (TAT):** `CT − AT`
- **Waiting Time (WT):** `TAT − BT`
- **Response Time (RT):** `First CPU Start − AT`
- **CPU Utilization:** `(Total CPU Burst Time ÷ final completion time) × 100`
- **Throughput:** `Number of processes ÷ final completion time`

Times are measured from time zero, so an initial idle period is included in the Gantt chart and in the CPU-utilization/throughput denominator. Context-switch overhead is not modeled.

## Scheduling/tie-breaking rules

- **FCFS:** sort by arrival time; for equal arrival times, retain the order in the input table.
- **SJF:** among arrived and waiting processes, choose the smallest burst time; ties use arrival time and then input order. Once selected, a process runs to completion.
- **Round Robin:** run each ready process for up to the time quantum. Processes that arrive during a time slice are added to the ready queue before the unfinished current process is put back into the queue.
- If no process is ready, the CPU is shown as **IDLE** until the next arrival.

## Project structure

```text
cpu_scheduling_simulator/
├── app.py                 # Local HTTP server / API endpoint
├── scheduler.py           # Scheduling algorithms and metric calculations
├── requirements.txt       # No external dependencies
├── README.md              # Setup guide and project notes
├── test_algorithms.py     # Unit tests for the scheduling calculations
└── static/
    ├── index.html         # Dashboard structure
    ├── styles.css         # Responsive dashboard styling
    └── app.js             # UI interactions, Gantt charts and comparison
```

## Viva points to prepare

1. Why is CPU scheduling needed? To share CPU time among ready processes and improve system responsiveness and efficiency.
2. What is the convoy effect? In FCFS, short processes may wait behind a long process.
3. Why can SJF reduce average waiting time? It prioritizes shorter ready jobs, though burst time generally needs to be estimated in a real OS.
4. What is the purpose of the Round Robin quantum? It limits one turn of CPU execution to improve fairness and responsiveness.
5. What happens if the quantum is too large? Round Robin can behave similarly to FCFS for many workloads. If it is too small, scheduling/context-switch overhead can rise; this demo does not model that overhead.
6. Can one algorithm always be best? No. Performance depends on arrival times, burst times, and quantum.

## Limitations

This is an educational simulator, not an operating-system scheduler. It assumes known CPU burst times, uses integer time units, omits context-switch costs and I/O blocking, and implements non-preemptive SJF (not SRTF).
