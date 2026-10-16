# CPU Scheduling Simulator Using FCFS, SJF and Round Robin

**Operating Systems (OSY) — Micro Project Report**

**Student Name:** Ayush Junghare  
**Course / Branch:** Diploma in Computer Engineering / CSE  
**Academic Year:** 2026 - 2027  
**Institute:** Tulsiramji Gaikwad Patil College Of Engineering & Technology  
**Guide / Faculty:** Aniket Dhenge
---

## 1. Abstract

CPU scheduling is an important function of an operating system. When multiple processes are ready to execute, the operating system decides which process receives CPU time. Different scheduling algorithms can produce different waiting times, turnaround times and response times for the same set of processes.

This project implements an interactive CPU Scheduling Simulator for three algorithms: First Come, First Served (FCFS), non-preemptive Shortest Job First (SJF), and Round Robin (RR). The user enters each process's arrival time and burst time and chooses a time quantum for Round Robin. The simulator produces Gantt charts, calculates per-process scheduling metrics, and compares average performance values through a local web interface. It is intended as an educational tool for understanding and demonstrating CPU scheduling concepts.

## 2. Introduction

A process is a program in execution. Several processes may be ready to use the CPU at the same time, but a single CPU core generally executes one process at a time. CPU scheduling selects a process from the ready queue and allocates CPU execution to it. The choice of scheduling policy influences fairness, responsiveness and the time a process spends waiting.

FCFS schedules processes in arrival order. SJF selects the shortest available CPU burst and, in this project, runs that process to completion. Round Robin gives each ready process a limited time slice called a time quantum and places unfinished processes at the back of the ready queue.

## 3. Problem Statement

Students often learn CPU scheduling algorithms through formulas and static examples. Manually drawing Gantt charts and calculating several metrics for multiple algorithms can be time-consuming and may make it difficult to compare the effect of each algorithm. This project addresses that problem by providing a small interactive simulator that calculates results automatically and displays the schedules visually.

## 4. Objectives

1. Implement FCFS, non-preemptive SJF and Round Robin scheduling.
2. Accept process IDs, arrival times and burst times as user input.
3. Allow the user to configure the Round Robin time quantum.
4. Generate a Gantt chart for each algorithm.
5. Calculate completion time, turnaround time, waiting time and response time for each process.
6. Calculate average metrics, CPU utilization and throughput.
7. Compare all three algorithms using the same set of processes.
8. Provide a simple local web interface suitable for practical demonstrations.

## 5. Scope

The application is designed for learning, classroom demonstrations and small scheduling examples. It supports up to 20 processes per simulation, uses non-negative integer arrival times and positive integer burst times, and compares three CPU scheduling algorithms. It does not control or modify the scheduling behaviour of the host operating system.

## 6. Hardware and Software Requirements

### Hardware

- Desktop computer or laptop
- Minimum 2 GB RAM recommended
- Keyboard, mouse or touchpad

### Software

- Python 3.10 or newer recommended
- Modern web browser such as Chrome, Edge or Firefox
- Windows, Linux or macOS
- No third-party Python package or external API key required

## 7. System Design

### Input

- Process ID (PID)
- Arrival Time (AT)
- Burst Time (BT)
- Round Robin Time Quantum (TQ)

### Processing

The Python backend validates the input and runs the three scheduling algorithms. It creates a timeline of CPU execution segments and calculates the process metrics. The browser interface requests the results from the local server and renders Gantt charts, metric cards, per-process tables and a comparison table.

### Output

- Gantt chart for FCFS, SJF and Round Robin
- Completion time (CT) for every process
- Turnaround time (TAT) for every process
- Waiting time (WT) for every process
- Response time (RT) for every process
- Average waiting, turnaround and response times
- CPU utilization and throughput
- Side-by-side algorithm comparison

### Architecture Flow

```text
User enters processes and time quantum
                 |
                 v
       Input validation
                 |
                 v
     Scheduling algorithms
       /       |       \
      v        v        v
    FCFS      SJF    Round Robin
       \       |       /
        v      v      v
    Calculate process metrics
                 |
                 v
   Local API returns JSON results
                 |
                 v
 Gantt charts + tables + comparison
```

## 8. Algorithms Used

### 8.1 First Come, First Served (FCFS)

**Principle:** The process that arrives first gets the CPU first. It is non-preemptive.

**Steps:**
1. Sort processes by arrival time.
2. If the CPU is idle, move the clock to the next process's arrival time and show the idle interval.
3. Execute the selected process for its full burst time.
4. Record its completion time and continue until all processes finish.

**Advantage:** Simple to understand and implement.  
**Limitation:** A short process can wait behind a long process; this is commonly called the convoy effect.

### 8.2 Shortest Job First (SJF), Non-preemptive

**Principle:** From the processes that have already arrived and are waiting, select the process with the smallest burst time. Once it starts, it runs until completion.

**Steps:**
1. Identify all processes whose arrival time is not later than the current clock.
2. Select the ready process with the smallest burst time.
3. If multiple ready processes have equal burst times, use earlier arrival time and then input order as tie-breakers.
4. Execute the selected process until it finishes.
5. Repeat until all processes complete.

**Advantage:** Can reduce average waiting time for a known workload.  
**Limitation:** The CPU burst length is usually not known exactly in advance in a real operating system; this simulator assumes it is provided.

### 8.3 Round Robin (RR)

**Principle:** Each ready process receives up to a fixed time quantum. If a process does not finish in that slice, it returns to the end of the ready queue.

**Steps:**
1. Add processes to the ready queue when they arrive.
2. Select the process at the front of the queue.
3. Execute it for the smaller of the time quantum and its remaining burst time.
4. Add processes that arrived during the slice to the queue.
5. If the current process is unfinished, append it to the back of the queue. Otherwise, record its completion time.
6. Repeat until all processes finish.

**Advantage:** Provides each ready process with regular CPU opportunities and is commonly associated with time-sharing systems.  
**Limitation:** A very large quantum can make the schedule resemble FCFS; a very small quantum can increase scheduling overhead. The simulator does not model context-switch overhead.

## 9. Formulas

| Metric | Formula | Meaning |
|---|---|---|
| Completion Time (CT) | Time at which the process finishes | End time for a process |
| Turnaround Time (TAT) | `CT − AT` | Total elapsed time from arrival to completion |
| Waiting Time (WT) | `TAT − BT` | Time spent waiting in the ready queue |
| Response Time (RT) | `First CPU Start − AT` | Delay until the process first gets CPU time |
| Average Waiting Time | `Sum of all WT ÷ Number of processes` | Mean waiting time |
| Average Turnaround Time | `Sum of all TAT ÷ Number of processes` | Mean turnaround time |
| CPU Utilization | `Total burst time ÷ final completion time × 100` | Percentage of elapsed time spent executing processes |
| Throughput | `Number of processes ÷ final completion time` | Processes completed per time unit |

The simulator measures elapsed time from time zero. Therefore, if all processes arrive after time zero, any initial idle period is included in the CPU-utilization and throughput denominator.

## 10. Sample Input

| Process | Arrival Time (AT) | Burst Time (BT) |
|---|---:|---:|
| P1 | 0 | 5 |
| P2 | 1 | 3 |
| P3 | 2 | 8 |
| P4 | 3 | 6 |

Round Robin Time Quantum: **2 time units**

## 11. Sample Output Summary

For the sample input above, the simulator calculates the following results. Values are in time units unless a percent sign is shown.

| Algorithm | Average Waiting Time | Average Turnaround Time | Average Response Time | CPU Utilization | Throughput |
|---|---:|---:|---:|---:|---:|
| FCFS | 5.75 | 11.25 | 5.75 | 100% | 0.182 |
| SJF (Non-preemptive) | 5.25 | 10.75 | 5.25 | 100% | 0.182 |
| Round Robin (TQ = 2) | 9.75 | 15.25 | 2.00 | 100% | 0.182 |

**Observation:** In this example, SJF has the lowest average waiting and turnaround times. Round Robin has the lowest average response time. This does not mean one algorithm is always best; the result depends on arrival times, burst times and time quantum. The total CPU burst time is 22 units, so all three algorithms finish at time 22 and use the CPU continuously in this sample.

## 12. Implementation Details

- **Backend:** Python standard library HTTP server and JSON handling
- **Frontend:** HTML, CSS and vanilla JavaScript
- **Visualization:** CSS-based proportional Gantt chart segments and result tables
- **Communication:** Browser sends process data to a local JSON endpoint
- **Storage:** No database required; inputs are held in the current browser session only

## 13. Testing

The scheduling engine includes automated unit tests for:

1. FCFS metric calculation
2. SJF process selection and metric calculation
3. Round Robin time-slice behaviour and completion times
4. CPU idle-time representation
5. Rejection of an invalid time quantum
6. Rejection of duplicate process IDs

The local web server and simulation endpoint were also checked using the sample process set.

## 14. Advantages

- Easy-to-use interface for entering processes
- Automatically calculates scheduling metrics
- Visual Gantt chart makes execution order easier to understand
- Compares all algorithms with the same input values
- No paid service, API key or third-party package required
- Runs locally on a student's computer

## 15. Limitations

- Only FCFS, non-preemptive SJF and Round Robin are implemented
- Processes use a single CPU burst; I/O blocking is not modelled
- Context-switch overhead is ignored
- Burst times are assumed to be known
- Scheduling times must be whole numbers
- The simulator is a learning tool and does not schedule the computer's real processes

## 16. Future Enhancements

- Add preemptive SJF / Shortest Remaining Time First (SRTF)
- Add Priority Scheduling and Multilevel Queue scheduling
- Allow process arrival and execution animation
- Add downloadable CSV or PDF reports
- Add context-switch overhead as an optional parameter
- Add separate CPU and I/O bursts
- Add more test cases and performance visualizations

## 17. Conclusion

The CPU Scheduling Simulator demonstrates how FCFS, non-preemptive SJF and Round Robin allocate CPU time differently. By showing each Gantt chart and calculating waiting, turnaround and response times, the project makes it easier to analyse algorithm behaviour using a common set of inputs. The sample run shows that SJF gives lower average waiting time for this workload, while Round Robin provides better first response. The project meets its educational objective of providing an interactive and explainable demonstration of core CPU scheduling concepts.

## References

1. Operating Systems course notes and laboratory manual.
2. Silberschatz, Galvin and Gagne, *Operating System Concepts*, CPU Scheduling chapter.
3. Python documentation, `http.server`, `json` and `pathlib` modules.
