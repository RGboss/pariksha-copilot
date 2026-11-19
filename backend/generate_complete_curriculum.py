import os
import sys
import json

BASE_PLATFORM = os.path.dirname(os.path.dirname(__file__))
if BASE_PLATFORM not in sys.path:
    sys.path.insert(0, BASE_PLATFORM)

DATA_DIR = os.path.join(BASE_PLATFORM, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Import stage 1 and stage 2 chapters we already designed
from backend.generate_detailed_curriculum import stages as s1_list
from backend.build_full_curriculum import stage2 as s2_dict

stage2 = s2_dict

# Now we define Stage 2 remaining chapters (Ch 8, 9, 10)
ch8 = {
    "id": "ch-8",
    "stage_id": "stage-2",
    "number": 8,
    "title": "Operating Systems: Process Lifecycle, Context Switching & CPU Scheduling Gantt Charts",
    "exams": ["ibps", "sebi", "sbi"],
    "reading_time_mins": 25,
    "summary": "Process states, Process Control Block (PCB), Context Switch overhead, FCFS Convoy Effect, SJF/SRTF optimality proofs, Round Robin time quantum dynamics, and Turnaround/Waiting time calculations.",
    "lecture_notes": """# Operating Systems: Process Scheduling & CPU Algorithms

## 1. Process Concepts & Process State Machine
A **Process** is an active program in execution. It represents the fundamental unit of work in modern operating systems.
* **Process Memory Layout:**
  * **Text Segment:** Executable machine code instructions.
  * **Data Segment:** Global and static variables initialized before runtime.
  * **Heap Segment:** Dynamically allocated memory at runtime (`malloc` in C, `new` in Java/C++). Grows upward.
  * **Stack Segment:** Local variables, function parameters, and return addresses. Grows downward toward heap.

```
+------------------------------------+ High Memory
|  Stack (Local variables, frames)   |
|         |                          |
|         v (Grows Downward)         |
|                                    |
|         ^ (Grows Upward)           |
|         |                          |
|  Heap (Dynamic memory allocation)  |
+------------------------------------+
|  Data Segment (Global / Static)    |
+------------------------------------+
|  Text Segment (Compiled Code)      |
+------------------------------------+ Low Memory
```

### The 5-State Process Model
1. **New:** The process is being created.
2. **Ready:** The process is loaded in RAM and waiting to be assigned to a CPU core.
3. **Running:** Instructions are actively being executed by the CPU.
4. **Waiting / Blocked:** The process is waiting for an event (e.g. Disk I/O, database socket read, semaphore signal).
5. **Terminated:** The process has finished execution and its PCB is being reclaimed.

### Process Control Block (PCB) & Context Switching
The **PCB** is the OS data structure storing all state information for a process: Process ID (PID), Program Counter (PC), CPU registers, CPU scheduling priority, Memory-management information, and Open file descriptors.
* **Context Switching:** Saving the CPU state (registers, PC) of the running process into its PCB and restoring the state of the next selected process from its PCB.
* **Overhead:** Context switching is **pure overhead**—the CPU performs zero productive user work during a context switch. Frequency must be carefully balanced!

---

## 2. CPU Scheduling Metrics & Mathematical Definitions
* **Arrival Time ($AT$):** Time at which the process arrives in the Ready Queue.
* **Burst Time ($BT$):** Time duration required by the process for CPU execution.
* **Completion Time ($CT$):** Time at which the process finishes execution.
* **Turnaround Time ($TAT$):** Total elapsed time from arrival to completion:
  $$\\mathbf{TAT = CT - AT}$$
* **Waiting Time ($WT$):** Total time spent sitting in the ready queue waiting for CPU:
  $$\\mathbf{WT = TAT - BT}$$
* **Response Time ($RT$):** Time from arrival until the first time the process is allocated the CPU:
  $$\\mathbf{RT = \\text{First CPU Time} - AT}$$

---

## 3. Step-by-Step Worked Numerical: CPU Scheduling Algorithms

**Problem Scenario:** Given 4 processes:
| Process | Arrival Time ($AT$) | Burst Time ($BT$) |
| :---: | :---: | :---: |
| $P_1$ | 0 | 7 |
| $P_2$ | 2 | 4 |
| $P_3$ | 4 | 1 |
| $P_4$ | 5 | 4 |

Calculate the **Average Waiting Time** under:
1. **First-Come, First-Served (FCFS)**
2. **Shortest Job First (Non-preemptive SJF)**
3. **Shortest Remaining Time First (Preemptive SRTF)**
4. **Round Robin (Time Quantum = 2)**

---

### Case 1: First-Come, First-Served (FCFS)
* Execution order: $P_1$ arrives first $\\implies$ runs from 0 to 7. Then $P_2$ runs 7 to 11. Then $P_3$ runs 11 to 12. Then $P_4$ runs 12 to 16.
* **Gantt Chart:** `[P1: 0-7] [P2: 7-11] [P3: 11-12] [P4: 12-16]`
* Calculation:
  * $P_1$: $CT = 7 \\implies TAT = 7 - 0 = 7, \\quad WT = 7 - 7 = 0$
  * $P_2$: $CT = 11 \\implies TAT = 11 - 2 = 9, \\quad WT = 9 - 4 = 5$
  * $P_3$: $CT = 12 \\implies TAT = 12 - 4 = 8, \\quad WT = 8 - 1 = 7$
  * $P_4$: $CT = 16 \\implies TAT = 16 - 5 = 11, \\quad WT = 11 - 4 = 7$
* **Average Waiting Time (FCFS):** $\\frac{0 + 5 + 7 + 7}{4} = \\frac{19}{4} = \\mathbf{4.75\\text{ ms}}$.

---

### Case 2: Shortest Remaining Time First (Preemptive SRTF)
* At $t = 0$: Only $P_1$ is present (Remaining $BT = 7$).
* At $t = 2$: $P_2$ arrives with $BT = 4$. Remaining $BT(P_1) = 7 - 2 = 5$. Since $4 < 5$, **$P_1$ is preempted! $P_2$ takes CPU**.
* At $t = 4$: $P_3$ arrives with $BT = 1$. Remaining $BT(P_2) = 4 - 2 = 2$. Since $1 < 2$, **$P_2$ is preempted! $P_3$ takes CPU**.
* At $t = 5$: $P_3$ finishes ($CT = 5$). $P_4$ arrives with $BT = 4$.
  * Ready processes: $P_2$ (rem: 2), $P_4$ (rem: 4), $P_1$ (rem: 5).
  * Shortest is $P_2$ (2 ms) $\\implies P_2$ runs from 5 to 7 ($CT = 7$).
* At $t = 7$: $P_4$ (rem: 4) vs $P_1$ (rem: 5) $\\implies P_4$ runs from 7 to 11 ($CT = 11$).
* At $t = 11$: $P_1$ runs its remaining 5 ms from 11 to 16 ($CT = 16$).
* **Gantt Chart:** `[P1: 0-2] [P2: 2-4] [P3: 4-5] [P2: 5-7] [P4: 7-11] [P1: 11-16]`
* Calculation:
  * $P_1$: $CT = 16 \\implies TAT = 16 - 0 = 16, \\quad WT = 16 - 7 = 9$
  * $P_2$: $CT = 7 \\implies TAT = 7 - 2 = 5, \\quad WT = 5 - 4 = 1$
  * $P_3$: $CT = 5 \\implies TAT = 5 - 4 = 1, \\quad WT = 1 - 1 = 0$
  * $P_4$: $CT = 11 \\implies TAT = 11 - 5 = 6, \\quad WT = 6 - 4 = 2$
* **Average Waiting Time (SRTF):** $\\frac{9 + 1 + 0 + 2}{4} = \\frac{12}{4} = \\mathbf{3.0\\text{ ms}}$!
* **Proof of Optimality:** SRTF reduces average waiting time by **36.8%** compared to FCFS!

---

## 4. Key Scheduling Anomalies & Theoretical Insights
1. **The Convoy Effect (FCFS):** A single huge CPU-bound process blocks dozens of quick I/O-bound processes, drastically decreasing overall system throughput.
2. **Starvation (SJF / SRTF / Priority):** Long processes may sit in the Ready queue indefinitely if a continuous stream of short processes arrives.
   * **Mitigation:** **Aging**—gradually increasing the priority of processes that wait in the system for long periods.
3. **Round Robin Quantum Tradeoff:**
   * If Quantum $q \\rightarrow \\infty$, Round Robin degenerates into **FCFS**.
   * If Quantum $q \\rightarrow 0$, context switch overhead dominates, causing CPU thrashing.""",
    "checkpoints": [
        {
            "q": "Why is Shortest Remaining Time First (SRTF) provably optimal for minimizing average waiting time?",
            "a": "Because scheduling the job with the shortest remaining execution time minimizes the delay imposed on all subsequent waiting jobs in the queue."
        },
        {
            "q": "What is the Convoy Effect in operating system scheduling?",
            "a": "The situation in FCFS scheduling where multiple short I/O-bound processes are forced to wait behind one large CPU-bound process, resulting in poor CPU and device utilization."
        },
        {
            "q": "How does the OS solve the problem of starvation in priority-based scheduling?",
            "a": "By implementing Aging, which gradually increases the priority of waiting processes over time until they are guaranteed execution."
        }
    ],
    "quiz": [
        {
            "id": 216,
            "q": "Which process memory segment dynamically expands upward to allocate memory requested at runtime via malloc() or new?",
            "options": [
                "Stack Segment",
                "Heap Segment",
                "Text Segment",
                "Data Segment"
            ],
            "answer": 1,
            "explanation": "The Heap segment stores dynamically allocated memory at runtime and grows upward toward higher memory addresses."
        },
        {
            "id": 217,
            "q": "What is the formula to compute Process Waiting Time (WT)?",
            "options": [
                "WT = Completion Time - Arrival Time",
                "WT = Turnaround Time - Burst Time",
                "WT = Turnaround Time + Arrival Time",
                "WT = Burst Time - Arrival Time"
            ],
            "answer": 1,
            "explanation": "Waiting Time is the total turnaround time minus the time actually spent executing on the CPU: WT = TAT - BT."
        },
        {
            "id": 218,
            "q": "What occurs when the time quantum in a Round Robin scheduling algorithm is configured to be arbitrarily large (larger than any process burst time)?",
            "options": [
                "It degenerates into Shortest Job First",
                "It causes CPU thrashing due to excessive context switching",
                "It behaves identically to First-Come First-Served (FCFS)",
                "It causes immediate deadlock"
            ],
            "answer": 2,
            "explanation": "If the time quantum exceeds the burst time of every process, no process is ever preempted by timer expiration, making it behave like FCFS."
        },
        {
            "id": 219,
            "q": "What technique is used by modern operating systems to prevent starvation in priority scheduling?",
            "options": [
                "Paging",
                "Aging",
                "Context Switching",
                "Segmentation"
            ],
            "answer": 1,
            "explanation": "Aging gradually increments the priority of long-waiting processes, guaranteeing they will eventually reach the highest priority and execute."
        },
        {
            "id": 220,
            "q": "Which scheduling algorithm provably achieves the minimal average waiting time for a given set of stationary processes?",
            "options": [
                "First-Come First-Served (FCFS)",
                "Round Robin (RR)",
                "Shortest Remaining Time First (SRTF)",
                "Priority Scheduling"
            ],
            "answer": 2,
            "explanation": "SRTF (preemptive Shortest Job First) is mathematically proven to yield the lowest possible average waiting time."
        }
    ]
}

ch9 = {
    "id": "ch-9",
    "stage_id": "stage-2",
    "number": 9,
    "title": "Deadlocks, Banker's Algorithm Safe State Analysis, Memory Paging & Belady's Anomaly",
    "exams": ["ibps", "sebi", "sbi"],
    "reading_time_mins": 25,
    "summary": "The 4 Coffman conditions, Resource Allocation Graphs, Banker's safety algorithm step-by-step matrix check, Paging translation math, TLB EMAT formulas, and Page Replacement algorithms (FIFO vs LRU vs Optimal).",
    "lecture_notes": """# Deadlocks, Memory Paging & Virtual Memory Architecture

## 1. Deadlock Theory & The 4 Coffman Conditions
A **Deadlock** is a state in which every process in a set is waiting for an event that only another process in the same set can cause.
* **The 4 Necessary and Sufficient Coffman Conditions:**
  1. **Mutual Exclusion:** At least one resource must be held in a non-shareable mode (only one process at a time).
  2. **Hold and Wait:** A process must currently hold at least one resource and be waiting to acquire additional resources held by others.
  3. **No Preemption:** Resources cannot be forcibly preempted from a process; they can only be released voluntarily after task completion.
  4. **Circular Wait:** A closed chain of processes $\\{P_0, P_1, \\dots, P_n\\}$ exists such that $P_0$ waits for $P_1$, $P_1$ waits for $P_2$, $\\dots$, and $P_n$ waits for $P_0$.

---

## 2. Deadlock Handling Strategies
1. **Deadlock Ignorance (Ostrich Algorithm):** Stick head in the sand; assume deadlocks never happen. Used by general-purpose OS (Linux/Windows) due to low frequency and high cost of dynamic avoidance.
2. **Deadlock Prevention:** Design protocols that mathematically eliminate at least one of the 4 Coffman conditions:
   * Eliminate *Hold and Wait:* Require processes to request all resources at once before execution begins.
   * Eliminate *Circular Wait:* **Impose a strict global linear ordering on all resource types** ($F: R \\rightarrow \\mathbb{N}$). A process can only request resources with an index higher than any resource it currently holds!
3. **Deadlock Avoidance (Banker's Algorithm):** OS dynamically inspects resource allocation state to ensure the system never enters an **Unsafe State**.

---

## 3. Step-by-Step Worked Example: Dijkstra's Banker's Algorithm

**Problem:** System has 5 processes ($P_0$ to $P_4$) and 3 resource types: $A$ (10 instances), $B$ (5 instances), $C$ (7 instances).

Current snapshot:
| Process | Allocation ($A, B, C$) | Max Demand ($A, B, C$) | Need Matrix ($A, B, C$) |
| :---: | :---: | :---: | :---: |
| $P_0$ | $0, 1, 0$ | $7, 5, 3$ | $7, 4, 3$ |
| $P_1$ | $2, 0, 0$ | $3, 2, 2$ | $1, 2, 2$ |
| $P_2$ | $3, 0, 2$ | $9, 0, 2$ | $6, 0, 0$ |
| $P_3$ | $2, 1, 1$ | $2, 2, 2$ | $0, 1, 1$ |
| $P_4$ | $0, 0, 2$ | $4, 3, 3$ | $4, 3, 1$ |

* **Total Allocated:** $A = 0+2+3+2+0 = 7, \\quad B = 1+0+0+1+0 = 2, \\quad C = 0+0+2+1+2 = 5$.
* **Available Vector:**
  $$\\text{Available} = [10-7, \\, 5-2, \\, 7-5] = [3, 3, 2]$$

### Safety Algorithm Execution:
* **Step 1:** Look for a process whose $\\text{Need} \\le \\text{Available} = [3, 3, 2]$.
  * Check $P_0$: Need $[7, 4, 3] \\le [3, 3, 2]$? **False**.
  * Check $P_1$: Need $[1, 2, 2] \\le [3, 3, 2]$? **TRUE!**
  * Execute $P_1$: Upon completion, $P_1$ releases its allocation $[2, 0, 0]$.
    $$\\text{New Available} = [3, 3, 2] + [2, 0, 0] = \\mathbf{[5, 3, 2]}$$
* **Step 2:** Look for next process with $\\text{Need} \\le [5, 3, 2]$:
  * Check $P_3$: Need $[0, 1, 1] \\le [5, 3, 2]$? **TRUE!**
  * Execute $P_3$: Releases $[2, 1, 1]$.
    $$\\text{New Available} = [5, 3, 2] + [2, 1, 1] = \\mathbf{[7, 4, 3]}$$
* **Step 3:** Look for next process with $\\text{Need} \\le [7, 4, 3]$:
  * Check $P_0$: Need $[7, 4, 3] \\le [7, 4, 3]$? **TRUE!**
  * Execute $P_0$: Releases $[0, 1, 0]$.
    $$\\text{New Available} = [7, 4, 3] + [0, 1, 0] = \\mathbf{[7, 5, 3]}$$
* **Step 4:** Check $P_2$: Need $[6, 0, 0] \\le [7, 5, 3]$? **TRUE!**
  * Execute $P_2$: Releases $[3, 0, 2]$.
    $$\\text{New Available} = [7, 5, 3] + [3, 0, 2] = \\mathbf{[10, 5, 5]}$$
* **Step 5:** Check $P_4$: Need $[4, 3, 1] \\le [10, 5, 5]$? **TRUE!**
  * Execute $P_4$: Releases $[0, 0, 2]$.
    $$\\text{New Available} = [10, 5, 5] + [0, 0, 2] = [10, 5, 7] = \\text{All Resources Free!}$$

**Conclusion:** The system is in a **SAFE STATE**.
* A valid Safe Sequence is: $\\mathbf{\\langle P_1, P_3, P_0, P_2, P_4 \\rangle}$. No deadlock can occur!

---

## 4. Memory Paging, Address Translation & TLB Calculations
* **Paging:** Divides physical RAM into fixed-size **Frames**, and logical process address space into same-size **Pages**.
  * Eliminates **External Fragmentation**.
  * Still subject to **Internal Fragmentation** (only in the last allocated page frame).

### Logical to Physical Address Translation
Logical Address consists of:
$$\\text{Logical Address} = \\langle \\text{Page Number } (p), \\quad \\text{Offset } (d) \\rangle$$
Physical Address is generated via Page Table:
$$\\text{Physical Address} = \\langle \\text{Frame Number } (f), \\quad \\text{Offset } (d) \\rangle$$

### Translation Lookaside Buffer (TLB) & Effective Memory Access Time (EMAT)
Because accessing the page table in RAM requires an extra memory access, hardware uses a fast associative cache called the **TLB**.
$$\\mathbf{EMAT = h \\cdot (t_{\\text{TLB}} + t_M) + (1 - h) \\cdot (t_{\\text{TLB}} + 2 \\cdot t_M)}$$
* $h$ = TLB Hit Ratio
* $t_{\\text{TLB}}$ = TLB lookup time
* $t_M$ = Main Memory access time (Note: On a TLB miss, we must access RAM twice—once for the page table, once for the actual data byte!).

---

## 5. Page Replacement Algorithms & Belady's Anomaly
When a page fault occurs and no free memory frames exist, a page must be evicted:
1. **FIFO (First-In, First-Out):** Evicts the oldest page.
   * **Belady's Anomaly:** For some reference strings, **increasing the number of page frames results in MORE page faults**!
2. **LRU (Least Recently Used):** Replaces the page that has not been referenced for the longest time. Stack algorithm; **mathematically immune to Belady's Anomaly**.
3. **Optimal Page Replacement (OPT):** Evicts the page that will not be used for the longest period in the future. Provably optimal baseline, but requires future knowledge (unimplementable in practice).""",
    "checkpoints": [
        {
            "q": "What is Belady's Anomaly and which page replacement algorithm experiences it?",
            "a": "Belady's Anomaly is the counter-intuitive phenomenon where increasing the number of physical memory frames leads to an increase in page faults. It occurs in FIFO; stack-based algorithms like LRU are immune."
        },
        {
            "q": "How can the Circular Wait condition for deadlocks be eliminated during system design?",
            "a": "By imposing a strict global linear numbering on all resources and enforcing that processes may only request resources in strictly increasing order."
        },
        {
            "q": "What type of memory fragmentation is present in a Paged memory architecture?",
            "a": "Internal fragmentation within the final page frame allocated to a process."
        }
    ],
    "quiz": [
        {
            "id": 221,
            "q": "Which of the following is NOT one of the four necessary Coffman conditions for a deadlock to occur?",
            "options": [
                "Mutual Exclusion",
                "Hold and Wait",
                "Preemption Permitted",
                "Circular Wait"
            ],
            "answer": 2,
            "explanation": "No Preemption is the required Coffman condition. If preemption is permitted, deadlocks are prevented."
        },
        {
            "id": 222,
            "q": "In an operating system using paging, if the TLB access time is 20 ns, main memory access time is 100 ns, and the TLB hit ratio is 90%, what is the Effective Memory Access Time (EMAT)?",
            "options": [
                "120 ns",
                "130 ns",
                "140 ns",
                "220 ns"
            ],
            "answer": 1,
            "explanation": "EMAT = 0.90 * (20 + 100) + 0.10 * (20 + 2 * 100) = 0.90 * 120 + 0.10 * 220 = 108 + 22 = 130 ns."
        },
        {
            "id": 223,
            "q": "Which page replacement algorithm can suffer from Belady's Anomaly?",
            "options": [
                "Least Recently Used (LRU)",
                "Optimal Page Replacement (OPT)",
                "First-In First-Out (FIFO)",
                "Most Recently Used (MRU)"
            ],
            "answer": 2,
            "explanation": "FIFO is not a stack algorithm and can exhibit Belady's Anomaly where allocating more physical memory frames increases the total page fault count."
        },
        {
            "id": 224,
            "q": "In Dijkstra's Banker's Algorithm, what formula computes the Need matrix?",
            "options": [
                "Need = Max - Allocation",
                "Need = Allocation + Available",
                "Need = Max + Allocation",
                "Need = Available - Allocation"
            ],
            "answer": 0,
            "explanation": "The Need matrix represents remaining resource claims: Need[i][j] = Max[i][j] - Allocation[i][j]."
        },
        {
            "id": 225,
            "q": "What form of memory fragmentation is completely eliminated by Paging?",
            "options": [
                "Internal Fragmentation",
                "External Fragmentation",
                "Virtual Fragmentation",
                "Cache Fragmentation"
            ],
            "answer": 1,
            "explanation": "Paging eliminates external fragmentation by allowing physical memory to be allocated in non-contiguous fixed-size page frames anywhere in RAM."
        }
    ]
}

ch10 = {
    "id": "ch-10",
    "stage_id": "stage-2",
    "number": 10,
    "title": "Linux Systems Administration: File Permissions, Shell Scripting & Process Management",
    "exams": ["ibps", "sebi", "sbi"],
    "reading_time_mins": 20,
    "summary": "UNIX architecture, file system permissions (rwx, octal notation, umask), process signals (SIGTERM vs SIGKILL), pipes, and text stream manipulation (grep, awk, sed).",
    "lecture_notes": """# Linux Systems Administration, Shell & Process Control

## 1. The UNIX / Linux Architecture
Linux is a multi-user, multitasking POSIX-compliant operating system.
* **Kernel:** The core module executing in privileged CPU mode (Ring 0). Manages hardware, processes, virtual memory, and system calls.
* **Shell:** Command-line interpreter executing in user mode (Ring 3). Interprets user commands into kernel system calls (`/bin/bash`, `/bin/zsh`).
* **File System Hierarchy Standard (FHS):** Everything in Linux is a file (including hardware devices under `/dev`, kernel state in `/proc`, and system configuration in `/etc`).

---

## 2. Linux File Permissions & Octal Calculation
Every file and directory possesses an owner (User), a primary Group, and Others.
```
- r w x  r - x  r - -    1  root  admin  4096  Nov 18 2026  server.sh
  \___/  \___/  \___/
  User   Group  Others
```
* `r` (Read) = **4**
* `w` (Write) = **2**
* `x` (Execute) = **1**

### Common Permission Combinations
| Octal | Symbolic | Meaning |
| :---: | :--- | :--- |
| **755** | `rwxr-xr-x` | User has full control; Group & Others can read and execute (standard for scripts & directories). |
| **644** | `rw-r--r--` | User can read and write; Group & Others can read only (standard for config & data files). |
| **700** | `rwx------` | User only; completely private (standard for SSH private keys `~/.ssh/id_rsa`). |
| **777** | `rwxrwxrwx` | Completely open to all users (security violation in enterprise banking!). |

* **chmod (Change Mode):** `chmod 755 run.sh` or `chmod u+x run.sh`.
* **chown (Change Owner):** `chown appuser:appgroup /var/log/bank.log`.

---

## 3. Process Signals & Administration
* `ps aux` / `ps -ef`: Lists all active running processes.
* `top` / `htop`: Real-time interactive CPU, RAM, and load average monitor.
* **Inter-Process Signals:**
  * **Signal 15 (`SIGTERM`):** Graceful termination signal. Gives the process a chance to flush buffers, close database connections, and shut down cleanly.
  * **Signal 9 (`SIGKILL`):** Immediate forceful termination. Bypasses the application process entirely; handled directly by the kernel. Cannot be caught or ignored!
  * **Signal 1 (`SIGHUP`):** Hangup signal. Frequently used to instruct background daemons (like Nginx) to reload configuration without dropping connections.

---

## 4. Pipes & Stream Processing Tools (grep, awk, sed)
* **Standard Streams:** `stdin` (0), `stdout` (1), `stderr` (2).
* **Pipe (`|`):** Connects the `stdout` of one command directly to the `stdin` of the next.

### Practical Banking IT Commands
```bash
# 1. Search for payment failures in transaction logs:
grep -i "PAYMENT_FAILED" /var/log/banking/tx.log

# 2. Extract column 1 (IP) and column 7 (Endpoint) from web access logs:
awk '{print $1, $7}' /var/log/nginx/access.log

# 3. Replace all occurrences of outdated server hostname:
sed -i 's/old-db.bank.internal/new-db.bank.internal/g' /etc/app.conf

# 4. Find all files modified in the last 24 hours:
find /var/log -type f -name "*.log" -mtime -1
```""",
    "checkpoints": [
        {
            "q": "What is the difference between SIGTERM (signal 15) and SIGKILL (signal 9)?",
            "a": "SIGTERM requests a graceful shutdown, allowing the process to clean up state and close files. SIGKILL immediately terminates the process forcefully via the kernel and cannot be intercepted or ignored."
        },
        {
            "q": "In Linux permissions, what does the octal code 644 represent?",
            "a": "User has Read/Write (6 = 4+2), Group has Read-only (4), and Others have Read-only (4)."
        }
    ],
    "quiz": [
        {
            "id": 226,
            "q": "Which signal number is transmitted to a process when executing 'kill -9 <PID>'?",
            "options": [
                "SIGHUP (1)",
                "SIGINT (2)",
                "SIGKILL (9)",
                "SIGTERM (15)"
            ],
            "answer": 2,
            "explanation": "Signal 9 is SIGKILL, which forces immediate termination by the Linux kernel without allowing the process to handle or intercept the signal."
        },
        {
            "id": 227,
            "q": "What permissions are assigned by the command 'chmod 754 script.sh'?",
            "options": [
                "User: rwx, Group: r-x, Others: r--",
                "User: rwx, Group: rw-, Others: r--",
                "User: r-x, Group: r-x, Others: rwx",
                "User: rwx, Group: r--, Others: ---"
            ],
            "answer": 0,
            "explanation": "7 = 4+2+1 (rwx), 5 = 4+0+1 (r-x), 4 = 4+0+0 (r--)."
        }
    ]
}

# Attach remaining chapters to Stage 2
stage2["chapters"].extend([ch8, ch9, ch10])

print("Finished compiling comprehensive Stage 2 chapters!")

# ==============================================================
# STAGE 3: SOFTWARE ENGINEERING, OOPS & ALGORITHMS
# ==============================================================
stage3 = {
    "id": "stage-3",
    "number": 3,
    "title": "Stage 03: Software Engineering, OOPs & Algorithms",
    "badge": "Core Coding & Design",
    "description": "Essential for SEBI Grade A Phase 2 hands-on coding, SBI SCO developer technical interview rounds, and IBPS SO professional knowledge.",
    "chapters": [
        {
            "id": "ch-11",
            "stage_id": "stage-3",
            "number": 11,
            "title": "Object-Oriented Programming (OOPs) Paradigms, Dynamic Dispatch & SOLID Architecture",
            "exams": ["sebi", "sbi", "ibps"],
            "reading_time_mins": 25,
            "summary": "Deep dive into Encapsulation, Runtime vs Compile-time Polymorphism, virtual method tables (vtables), Diamond problem, and the 5 SOLID design principles with Java implementations.",
            "lecture_notes": """# Object-Oriented Programming Paradigms & SOLID Architecture

## 1. The 4 Pillars of Object-Oriented Programming

### 1. Encapsulation
* **Definition:** The bundling of data (state) and the methods (behavior) that manipulate that data into a single computational unit (Class), restricting direct external access to mutable state via access modifiers (`private`, `protected`, `public`).
* **Objective:** Prevents unintended direct state tampering and maintains internal invariants.

### 2. Abstraction
* **Definition:** Exposing essential characteristics of an entity while hiding complex implementation details from callers.
* **Java Mechanism:** Abstract Classes and Interfaces.

### 3. Inheritance
* **Definition:** The mechanism by which a subclass acquires state and behavior from a superclass (IS-A relationship).
* **The Diamond Problem:** When a class inherits from two parent classes that share a common ancestor. Java avoids this for classes by disallowing multiple class inheritance, while supporting multiple interface inheritance via default methods (with explicit conflict resolution rules).

### 4. Polymorphism
* **Compile-Time (Static) Polymorphism:** Method Overloading.
  * Resolved at compile time based on method name and parameter types (**Static Binding**).
* **Runtime (Dynamic) Polymorphism:** Method Overriding.
  * Resolved at runtime via **Dynamic Method Dispatch**.
  * The Java Virtual Machine uses a **Virtual Method Table (vtable)** attached to the class metadata. When `parentRef.display()` is called, the JVM looks up the actual runtime instance's vtable entry to invoke the overridden subclass method!

---

## 2. Overloading vs Overriding Rules in Java

| Feature | Method Overloading | Method Overriding |
| :--- | :--- | :--- |
| **Binding Time** | Compile-Time (Static Binding) | Runtime (Dynamic Binding via vtable) |
| **Method Name** | Identical | Identical |
| **Parameter Signature** | **Must be different** (type, count, order) | **Must be identical** |
| **Return Type** | Can be different | Must be identical or a **covariant subtype** |
| **Access Modifier** | Any | Cannot be more restrictive than parent |
| **Static Methods** | Can be overloaded | **Cannot be overridden!** (Method Hiding) |
| **Private Methods**| Can be overloaded | Cannot be overridden (not visible to child) |

---

## 3. The SOLID Principles with Enterprise Java Examples
The SOLID principles, formulated by Robert C. Martin ("Uncle Bob"), are the foundation of clean, maintainable enterprise software:

### 1. S - Single Responsibility Principle (SRP)
* *"A class should have one, and only one, reason to change."*
* **Violation:** A `BankAccount` class that calculates interest, updates database tables, and formats PDF monthly statements.
* **Clean Design:** Separate into `BankAccount`, `InterestCalculator`, `AccountRepository`, and `StatementPdfGenerator`.

### 2. O - Open/Closed Principle (OCP)
* *"Software entities should be open for extension, but closed for modification."*
* **Clean Design:** Use polymorphism and interfaces. To support new payment gateways (e.g. UPI, NEFT, RTGS), create new classes implementing a common `PaymentGateway` interface without modifying existing payment processing code.

### 3. L - Liskov Substitution Principle (LSP)
* *"Subtypes must be substitutable for their base types without altering program correctness."*
* **Classic Violation:** The Square-Rectangle problem. If a `Square` inherits from `Rectangle`, changing the width alters the height, violating the expectations of code expecting a standard `Rectangle`.

### 4. I - Interface Segregation Principle (ISP)
* *"Clients should not be forced to depend upon interfaces that they do not use."*
* **Clean Design:** Instead of a bloated interface `BankingService` with 50 methods, split into `TellerOperations`, `AuditOperations`, and `CustomerOnlineOperations`.

### 5. D - Dependency Inversion Principle (DIP)
* *"High-level modules should not depend on low-level modules. Both should depend on abstractions."*
* **Clean Design:** Spring Boot Dependency Injection (IoC). Controllers depend on an interface `AccountService`, which is injected at runtime, rather than instantiating `new AccountServiceImpl()`.

```java
// DIP Example in Banking Backend:
public interface AccountRepository {
    Account findById(Long id);
    void save(Account account);
}

@Service
public class AccountService {
    private final AccountRepository repository; // Depends on abstraction!

    @Autowired
    public AccountService(AccountRepository repository) {
        this.repository = repository;
    }
}
```""",
            "checkpoints": [
                {
                    "q": "Why can static methods not be overridden polymorphically in Java?",
                    "a": "Because static methods belong to the class rather than an object instance, and their call resolution occurs at compile-time based on reference type (Method Hiding) rather than runtime dynamic dispatch via vtable."
                },
                {
                    "q": "What is the Dependency Inversion Principle (DIP)?",
                    "a": "High-level policy modules should not depend on low-level detail modules; both should depend on abstractions (interfaces)."
                }
            ],
            "quiz": [
                {
                    "id": 301,
                    "q": "Which SOLID principle is violated if an update to a banking tax calculation engine requires modifying the core Account class code directly?",
                    "options": [
                        "Single Responsibility Principle",
                        "Open/Closed Principle",
                        "Liskov Substitution Principle",
                        "Interface Segregation Principle"
                    ],
                    "answer": 1,
                    "explanation": "The Open/Closed Principle states that classes should be open for extension without requiring modification of existing source code."
                },
                {
                    "id": 302,
                    "q": "In Java, what is the technical term for declaring a static method in a subclass with the identical signature to a static method in the superclass?",
                    "options": [
                        "Method Overriding",
                        "Method Hiding",
                        "Method Overloading",
                        "Dynamic Binding"
                    ],
                    "answer": 1,
                    "explanation": "Static methods cannot be overridden dynamically; redefining them in a child class is known as Method Hiding."
                }
            ]
        },
        {
            "id": "ch-12",
            "stage_id": "stage-3",
            "number": 12,
            "title": "Java Backend Core, JVM Memory Architecture, Garbage Collection & Collections Framework",
            "exams": ["sbi", "sebi", "ibps"],
            "reading_time_mins": 25,
            "summary": "JVM memory areas (Stack, Heap, Metaspace), Generational Garbage Collection algorithms, HashMap internal bucket chaining and treeification (Java 8 Red-Black trees), ArrayList vs LinkedList, and ConcurrentHashMap locks.",
            "lecture_notes": """# Java Backend Core, JVM Memory & Collections Framework

## 1. JVM Memory Model Architecture
When a Java application executes, the JVM allocates memory into distinct regions:

```
+-----------------------------------------------------------+
|                      JVM Memory Pool                      |
+-----------------------------------------------------------+
| Thread 1 Stack | Thread 2 Stack | Thread 3 Stack          |
| - Method Frames| - Method Frames| - Method Frames         |
| - Local vars   | - Local vars   | - Local vars            |
+-----------------------------------------------------------+
|                          HEAP                             |
|  [Young Generation: Eden, S0, S1] | [Old / Tenured Gen]   |
|  - All Objects and Arrays live here!                      |
+-----------------------------------------------------------+
|                       METASPACE                           |
|  - Class metadata, bytecodes, static variables (Native)   |
+-----------------------------------------------------------+
```

### 1. JVM Stack
* Allocated per-thread (thread-safe by isolation).
* Stores **Stack Frames** created upon each method call. A frame contains:
  * Local primitive variables (`int`, `double`, `boolean`).
  * Object references (pointers to objects residing in the Heap).
  * Method operands and return values.

### 2. Heap Memory
* Shared among all threads.
* All object instances and instance variables reside on the Heap.
* Managed exclusively by the **Garbage Collector (GC)**.

### 3. Metaspace (Java 8+)
* Replaced the older `PermGen` (Permanent Generation).
* Allocates class metadata directly from **native OS memory**, eliminating arbitrary `java.lang.OutOfMemoryError: PermGen space` exceptions.

---

## 2. Generational Garbage Collection Mechanics
The **Weak Generational Hypothesis** observes that:
1. Most created objects have very short lifespans (used within a method and discarded).
2. Objects that survive multiple garbage collection cycles tend to remain alive for a very long time.

### Generational Heap Layout
* **Young Generation:**
  * **Eden Space:** All newly created objects are initially allocated here.
  * **Survivor Spaces ($S_0$ and $S_1$):** When Eden fills up, a **Minor GC** triggers. Surviving objects are moved to one of the survivor spaces, and their age counter increments.
* **Old / Tenured Generation:**
  * Objects that survive a configured number of GC cycles (default threshold: 15) are **promoted** to the Old Generation.
  * When Old Generation reaches capacity, a **Major GC / Full GC** triggers (causes **Stop-The-World (STW)** pauses).

---

## 3. Java Collections Framework: HashMap Deep Dive

### HashMap Internals (Java 8+)
A `HashMap` is an array of hash buckets: `Node<K,V>[] table`.
* **Hash Calculation:** The key's `hashCode()` is scrambled via a bitwise shift function to minimize collision clustering:
  $$\\text{index} = (n - 1) \\& \\text{hash}(key)$$
* **Collision Resolution:** When multiple keys produce the same bucket index:
  * In Java 7: Stored as a singly linked list ($O(N)$ lookup).
  * **Java 8+ Treeification:** When a bucket's linked list length reaches $\\ge 8$ (`TREEIFY_THRESHOLD`) and total table capacity $\\ge 64$, the bucket converts from a linked list into a **Red-Black Balanced Binary Search Tree**!
  * **Result:** Worst-case lookup improves from $O(N)$ to **$O(\\log N)$**!

### The equals() and hashCode() Contract (Crucial!)
* If two objects are equal according to `equals()`, their `hashCode()` **MUST** produce the exact same integer value:
  $$a.\\text{equals}(b) \\implies a.\\text{hashCode}() == b.\\text{hashCode}()$$
* If you override `equals()` without overriding `hashCode()`, two logical equal objects will generate different bucket indexes, causing `map.get(key)` to return `null`!

---

## 4. Concurrent Collections in Multithreaded Banking
* `ArrayList` vs `Vector`: `ArrayList` is unsynchronized and fast; `Vector` synchronizes every method, creating thread contention.
* `HashMap` vs `ConcurrentHashMap`:
  * `HashMap`: Not thread-safe. Concurrent modifications can cause infinite loops in older JVMs or lost updates.
  * `ConcurrentHashMap`: In Java 8, uses **fine-grained node-level locks (synchronized on the first node of each bucket) and lock-free Compare-And-Swap (CAS)** operations, allowing concurrent reads and writes across different buckets without locking the entire map!""",
            "checkpoints": [
                {
                    "q": "What happens when a HashMap bucket has 8 or more colliding entries in Java 8?",
                    "a": "If the table capacity is at least 64, the linked list converts into a balanced Red-Black Tree, reducing lookup time complexity from O(N) to O(log N)."
                },
                {
                    "q": "Why must you override hashCode() whenever you override equals() in Java?",
                    "a": "Because equal objects must produce identical hash codes; otherwise, hash-based collections (HashMap, HashSet) will look in the wrong buckets and fail to retrieve stored objects."
                }
            ],
            "quiz": [
                {
                    "id": 303,
                    "q": "In the Java 8+ HotSpot JVM, where is class metadata stored after the elimination of PermGen?",
                    "options": [
                        "In the Java Heap Space",
                        "In Metaspace using native OS memory",
                        "In the Thread Stack",
                        "In the Eden Space"
                    ],
                    "answer": 1,
                    "explanation": "Java 8 replaced PermGen with Metaspace, which allocates class metadata dynamically from native host memory."
                },
                {
                    "id": 304,
                    "q": "In Java 8, how does ConcurrentHashMap achieve high concurrent throughput without synchronizing entire tables?",
                    "options": [
                        "By locking the entire table on every read",
                        "By synchronizing only the first node of each bucket and utilizing lock-free Compare-And-Swap (CAS) instructions",
                        "By disabling garbage collection",
                        "By disallowing updates from multiple threads"
                    ],
                    "answer": 1,
                    "explanation": "ConcurrentHashMap locks individual bucket nodes and uses CAS operations, allowing concurrent access to different buckets without global blocking."
                }
            ]
        },
        {
            "id": "ch-13",
            "stage_id": "stage-3",
            "number": 13,
            "title": "Data Structures & Algorithms: Binary Trees, Heaps, Graph Algorithms & Big-O Complexities",
            "exams": ["sebi", "sbi", "ibps"],
            "reading_time_mins": 25,
            "summary": "Master asymptotic notation (Big-O, Omega, Theta), Master Theorem, BST properties, Inorder traversal sorted order, Binary Heap BuildHeap in O(N), BFS vs DFS, Dijkstra shortest path, and Kruskal/Prim MST.",
            "lecture_notes": """# Data Structures & Algorithms: Trees, Heaps, Graphs & Complexities

## 1. Asymptotic Complexity & The Master Theorem
* **Big-O ($O$):** Asymptotic Upper Bound ($f(n) \\le c \\cdot g(n)$).
* **Big-Omega ($\\Omega$):** Asymptotic Lower Bound.
* **Big-Theta ($\\Theta$):** Asymptotic Tight Bound.

### Master Theorem for Divide-and-Conquer Recurrences
For recurrences of the form:
$$T(n) = a \\, T\\left(\\frac{n}{b}\\right) + f(n), \\quad \\text{where } a \\ge 1, \\, b > 1$$
Let $c_{\\text{crit}} = \\log_b a$:
1. If $f(n) = O(n^c)$ where $c < \\log_b a \\implies \\mathbf{T(n) = \\Theta(n^{\\log_b a})}$.
2. If $f(n) = \\Theta(n^{\\log_b a} \\log^k n) \\implies \\mathbf{T(n) = \\Theta(n^{\\log_b a} \\log^{k+1} n)}$.
   * *MergeSort:* $T(n) = 2T(n/2) + O(n) \\implies a=2, b=2, \\log_2 2 = 1 \\implies \\mathbf{O(n \\log n)}$.
3. If $f(n) = \\Omega(n^c)$ where $c > \\log_b a \\implies \\mathbf{T(n) = \\Theta(f(n))}$.

---

## 2. Binary Search Trees (BST) & Heap Structures
* **BST Invariant:** For every node $N$, all nodes in its left subtree $< N$, and all nodes in its right subtree $> N$.
  * **Inorder Traversal (Left, Root, Right):** **ALWAYS visits keys in strictly ascending sorted order!**
* **Binary Heap:**
  * Complete binary tree satisfying the heap property (parent $\\le$ children for Min-Heap; parent $\\ge$ children for Max-Heap).
  * Represented compactly as an array: for node at index $i$, Left child $= 2i + 1$, Right child $= 2i + 2$, Parent $= \\lfloor (i - 1) / 2 \\rfloor$.
  * **BuildHeap Algorithm:** Building a heap from an unordered array of $N$ elements takes **$O(N)$ time** using bottom-up heapification, NOT $O(N \\log N)$!

---

## 3. Graph Algorithms: Traversals, Shortest Paths & MST
* **Breadth-First Search (BFS):** Uses a **Queue**. Time: $O(V + E)$. Finds shortest path in unweighted graphs.
* **Depth-First Search (DFS):** Uses a **Stack / Recursion**. Time: $O(V + E)$. Used for cycle detection and topological sorting in DAGs.
* **Dijkstra's Algorithm:**
  * Greedy single-source shortest path for weighted graphs.
  * Uses a Min-Heap priority queue. Time: $O((V + E) \\log V)$.
  * **Limitation:** Fails if the graph contains **negative weight edges** (requires Bellman-Ford in $O(V \\cdot E)$).
* **Minimum Spanning Tree (MST):**
  * **Kruskal's Algorithm:** Sort edges, greedily pick minimum edge using Disjoint Set Union (DSU) to avoid cycles. Time: $O(E \\log E)$.
  * **Prim's Algorithm:** Grow MST from a starting vertex using a priority queue. Time: $O(E \\log V)$.""",
            "checkpoints": [
                {
                    "q": "Why does building a binary heap take O(N) time instead of O(N log N)?",
                    "a": "Because bottom-up BuildHeap runs heapify on nodes level by level; most nodes are near the leaves where tree height is small. The mathematical summation of nodes times height converges to linear O(N) time."
                },
                {
                    "q": "What graph traversal traversal on a BST produces sorted output?",
                    "a": "Inorder traversal (Left, Root, Right)."
                }
            ],
            "quiz": [
                {
                    "id": 305,
                    "q": "What is the time complexity of the bottom-up BuildHeap algorithm to build a Min-Heap from an unsorted array of N elements?",
                    "options": [
                        "O(N log N)",
                        "O(N)",
                        "O(log N)",
                        "O(N^2)"
                    ],
                    "answer": 1,
                    "explanation": "Bottom-up BuildHeap has a time complexity of O(N) because the majority of nodes reside near the leaves and require very few heapify swaps."
                },
                {
                    "id": 306,
                    "q": "Which algorithm is capable of finding shortest paths in a directed graph containing negative weight edges (and detecting negative weight cycles)?",
                    "options": [
                        "Dijkstra's Algorithm",
                        "Bellman-Ford Algorithm",
                        "Prim's Algorithm",
                        "Kruskal's Algorithm"
                    ],
                    "answer": 1,
                    "explanation": "Bellman-Ford operates in O(V*E) time and correctly handles negative edge weights, detecting whether negative weight cycles exist."
                }
            ]
        },
        {
            "id": "ch-14",
            "stage_id": "stage-3",
            "number": 14,
            "title": "Software Engineering Lifecycles (SDLC, Agile/Scrum) & Software Testing/QA",
            "exams": ["ibps", "sbi", "sebi"],
            "reading_time_mins": 20,
            "summary": "Waterfall, V-Model, Spiral model risk analysis, Agile Manifesto, Scrum roles & ceremonies, Black-box testing (Boundary Value, Equivalence), White-box testing, Unit, Integration, and Regression testing.",
            "lecture_notes": """# Software Engineering Lifecycles & Testing Methodologies

## 1. SDLC Methodologies
* **Waterfall Model:** Linear-sequential phases. Inflexible; requirements must be locked upfront.
* **V-Model:** Verification and Validation model. Pairs each development phase with an associated testing phase (e.g. Unit tests pair with Detailed Design; Acceptance tests pair with Requirements).
* **Spiral Model (Barry Boehm):** Risk-driven iterative model. Each cycle incorporates: Objective setting $\\rightarrow$ Risk analysis $\\rightarrow$ Development & Prototyping $\\rightarrow$ Review.

---

## 2. Agile & The Scrum Framework
* **Scrum Ceremonies:**
  * **Sprint Planning:** Team defines sprint goal and selects backlog items.
  * **Daily Standup (15 mins):** What I did yesterday, what I will do today, any blockers.
  * **Sprint Review:** Demonstration of completed user stories to stakeholders.
  * **Sprint Retrospective:** Team inspects process improvements for the next sprint.
* **Scrum Roles:** Product Owner (defines backlog & priorities), Scrum Master (removes blockers & enforces Scrum process), Development Team.

---

## 3. Software Testing & Quality Assurance
* **Black-Box Testing (Functional):**
  * **Equivalence Partitioning:** Divides input data into valid and invalid equivalence classes; tests one representative value from each partition.
  * **Boundary Value Analysis (BVA):** Tests values at the edges (Min, Min+1, Nominal, Max-1, Max), where defects statistically cluster.
* **White-Box Testing (Structural):**
  * Statement Coverage, Branch / Decision Coverage, Path Coverage.
* **Testing Pyramid Levels:**
  1. **Unit Testing:** Smallest testable unit (isolated via mocks/stubs using Mockito/JUnit).
  2. **Integration Testing:** Tests interactions between combined modules.
  3. **Regression Testing:** Re-executing existing test suites after bug fixes or new features to ensure existing functionality remains un-broken.""",
            "checkpoints": [
                {
                    "q": "What is Boundary Value Analysis (BVA)?",
                    "a": "A black-box test design technique that tests data at the extreme boundaries (minimum, maximum, and values immediately above and below limits), where most software faults occur."
                }
            ],
            "quiz": [
                {
                    "id": 307,
                    "q": "Which SDLC model is characterized by explicit risk analysis and prototyping at each spiral phase?",
                    "options": [
                        "Waterfall Model",
                        "Spiral Model",
                        "RAD Model",
                        "V-Model"
                    ],
                    "answer": 1,
                    "explanation": "The Spiral Model, created by Barry Boehm, incorporates iterative prototyping with explicit risk analysis in every cycle."
                }
            ]
        }
    ]
}

# ==============================================================
# STAGE 4: ADVANCED ARCHITECTURE & CLOUD (SBI SCO FOCUS)
# ==============================================================
stage4 = {
    "id": "stage-4",
    "number": 4,
    "title": "Stage 04: Enterprise System Design, Spring Microservices & Cloud",
    "badge": "Advanced Architecture",
    "description": "Crucial for SBI SCO Deputy Manager (IT Developer / Systems) screening and technical architecture interviews: Scalability, Caching, Kafka, Spring Boot, AWS, and Docker.",
    "chapters": [
        {
            "id": "ch-15",
            "stage_id": "stage-4",
            "number": 15,
            "title": "System Design: Scalability, Caching (Redis), Distributed Streaming (Kafka) & CAP Theorem",
            "exams": ["sbi", "sebi"],
            "reading_time_mins": 25,
            "summary": "Horizontal vs Vertical scaling, Load Balancers, Redis Cache-Aside, Cache Stampede solutions, Apache Kafka topics & partitions, and Brewer's CAP Theorem.",
            "lecture_notes": """# System Design: Scalability, Caching, Kafka & CAP Theorem

## 1. High-Level System Architecture & Scalability
In large-scale banking systems (such as SBI's core processing millions of transactions per second during peak hours), single-server architectures fail.
* **Vertical Scaling (Scale-Up):** Adding more CPU cores, RAM, and SSD storage to a single server instance. Limited by hardware physical caps and forms a **Single Point of Failure (SPOF)**.
* **Horizontal Scaling (Scale-Out):** Deploying multiple stateless application instances behind a **Load Balancer**. Provides fault tolerance and elastic scaling.

```
                   [ Internet Clients ]
                            |
                            v
                   [ Load Balancer (Nginx / ALB) ]
                   /        |        \\
                  v         v         v
             [ App Pod 1 ] [ App Pod 2 ] [ App Pod 3 ]
                  \\         |         /
                   v        v        v
              [ Redis Distributed Cache Cluster ]
                            | (Cache Miss)
                            v
              [ Primary Database (PostgreSQL / Oracle) ]
                            | (Replication)
                            v
              [ Read-Replicas for Reporting Queries ]
```

---

## 2. Distributed Caching & The Cache-Aside Pattern
In-memory caching engines like **Redis** provide sub-millisecond retrieval by holding data in RAM.

### The Cache-Aside (Lazy-Loading) Flow
1. Application receives a Read request for user balance (`account:1001`).
2. App queries Redis:
   * **Cache Hit:** Redis returns balance immediately.
   * **Cache Miss:** App queries Primary Database, writes result to Redis with a **Time-To-Live (TTL)**, and returns data.
3. On Write/Update: App updates Primary DB and **invalidates (deletes)** the cache key in Redis!

### Common Caching Pitfalls
* **Cache Stampede (Dog-Piling):** Occurs when a high-traffic cache key expires. Thousands of concurrent client threads experience a cache miss simultaneously and hammer the primary database, crashing it.
  * *Solution:* Mutex locking (only one thread queries DB and populates cache) or probabilistic early expiration.
* **Cache Penetration:** Requests query keys that do not exist in both cache and DB (e.g. attacker querying random non-existent accounts).
  * *Solution:* Use a **Bloom Filter** or cache `null` values with a short TTL.

---

## 3. Distributed Event Streaming: Apache Kafka
Kafka is a distributed, fault-tolerant, append-only commit log used in banking for event-driven architectures (payment processing, transaction fraud detection, audit trails).

### Key Architectural Constructs
* **Topic:** A category or feed name to which messages are published.
* **Partition:** The fundamental unit of scalability in Kafka. A topic is split into multiple partitions distributed across brokers.
  * **Ordering Guarantee:** Messages within the **same partition** are guaranteed to be in strict sequential order.
  * **Partition Key:** Messages with the same key (e.g. `account_id`) always hash to the **exact same partition**, guaranteeing per-account sequential transaction order!
* **Consumer Groups:** A group of consumers that collaboratively consume a topic. Each partition is consumed by exactly one consumer within the group, enabling parallel data processing.

---

## 4. Brewer's CAP Theorem
In any distributed asynchronous data store subject to **Network Partitions ($P$)**, you can guarantee **Consistency ($C$)** OR **Availability ($A$)**, but **never both simultaneously**:
* **Consistency ($C$):** Every read receives the most recent write or an error.
* **Availability ($A$):** Every non-failing node returns a non-error response, without guarantee that it contains the most recent write.
* **Partition Tolerance ($P$):** The system continues to operate despite arbitrary packet loss or network link failure between nodes.

> **Why CA systems don't exist in distributed networks:** Real-world physical networks will inevitably experience fiber cuts, router reboots, or packet drops. Since $P$ is a physical inevitability, distributed systems must choose between **CP** (Consistency over Availability, e.g. MongoDB, HBase) or **AP** (Availability over Consistency, e.g. Cassandra, DynamoDB). Banking ledger systems choose **CP** because returning stale or incorrect financial balances is unacceptable.""",
            "checkpoints": [
                {
                    "q": "Why does Kafka partition topics?",
                    "a": "To enable horizontal scalability and parallel consumption across multiple consumers in a consumer group, while preserving strict message ordering within each individual partition."
                },
                {
                    "q": "What is Cache Stampede and how is it mitigated?",
                    "a": "When a popular cached key expires, thousands of concurrent requests miss the cache and hit the database simultaneously. It is mitigated using distributed mutex locks or early probabilistic cache background refreshing."
                }
            ],
            "quiz": [
                {
                    "id": 401,
                    "q": "In an Apache Kafka cluster, what condition guarantees that messages from a producer are consumed in strict sequential order?",
                    "options": [
                        "All messages must be sent to the same consumer group",
                        "All messages must be published with the same partition key so they route to the same partition",
                        "Kafka automatically guarantees global ordering across all partitions",
                        "The topic must have at least 10 partitions"
                    ],
                    "answer": 1,
                    "explanation": "Kafka only guarantees strict message ordering within an individual partition. Using the same partition key ensures related messages land in the same partition."
                },
                {
                    "id": 402,
                    "q": "According to the CAP Theorem, why can a distributed database not achieve both Consistency and Availability during a network partition?",
                    "options": [
                        "Hardware CPU clock drift prevents it",
                        "If nodes are partitioned, returning data guarantees availability but risks returning stale/inconsistent data; refusing requests guarantees consistency but breaks availability",
                        "Normalization rules disallow it",
                        "TCP sockets time out"
                    ],
                    "answer": 1,
                    "explanation": "When network partition P occurs, nodes cannot synchronize state. The system must either reject operations (sacrificing Availability) or serve local state (sacrificing Consistency)."
                }
            ]
        },
        {
            "id": "ch-16",
            "stage_id": "stage-4",
            "number": 16,
            "title": "Microservices Architecture, Spring Boot Ecosystem & Distributed Resilience",
            "exams": ["sbi", "sebi"],
            "reading_time_mins": 25,
            "summary": "Monolithic vs Microservices architecture, Spring Boot core annotations, Inversion of Control, API Gateway patterns, Circuit Breakers (Resilience4j), and RESTful API standards.",
            "lecture_notes": """# Microservices Architecture, Spring Boot & Distributed Resilience

## 1. Monolith vs Microservices Architecture
* **Monolithic Architecture:** Entire banking application (Authentication, Accounts, Loans, Cards, Notifications) packaged into a single deployable artifact (WAR/JAR). Simple to deploy initially, but suffers from tight coupling, slow deployments, and full system failure if a single module crashes.
* **Microservices Architecture:** Decomposes application into small, autonomous, loosely coupled services organized around business capabilities. Each service owns its own database (**Database-per-Service Pattern**).

---

## 2. Spring Boot Core Foundations
Spring Boot eliminates boilerplate XML configuration via convention-over-configuration:
* **`@RestController`:** Combines `@Controller` and `@ResponseBody` to produce JSON API responses.
* **`@Service` & `@Repository`:** Semantic annotations for business logic and data access (translates SQL exceptions into Spring DataAccessException).
* **Dependency Injection (IoC):**
  ```java
  @RestController
  @RequestMapping("/api/v1/accounts")
  public class AccountController {
      private final AccountService accountService;

      // Constructor Injection is preferred for immutability & easy mock testing!
      public AccountController(AccountService accountService) {
          this.accountService = accountService;
      }

      @GetMapping("/{id}")
      public ResponseEntity<AccountDto> getAccount(@PathVariable Long id) {
          return ResponseEntity.ok(accountService.getAccount(id));
      }
  }
  ```

---

## 3. Distributed Resilience: The Circuit Breaker Pattern
In a microservices cluster, if Service A synchronously calls Service B, and Service B begins timing out, Service A's thread pool quickly becomes exhausted, causing **cascading system failure**.

### Circuit Breaker States (Resilience4j / Netflix Hystrix)
```
          [ Closed State ]  <--- (Success rate restores)
            |          ^
(Failure    |          |
 threshold  |          | (Canary requests
 exceeded)  v          |  succeed)
          [ Open State ]
            |
            | (Wait duration expires)
            v
          [ Half-Open State ]
```
* **Closed:** Normal operation; requests pass through.
* **Open:** When failure rate crosses threshold (e.g. 50%), circuit opens. All subsequent requests fail-fast immediately or execute a **Fallback method** without hitting the failing downstream service!
* **Half-Open:** After a cooldown period, a small sample of test requests are permitted through. If they succeed, circuit closes; if they fail, circuit re-opens.""",
            "checkpoints": [
                {
                    "q": "What is the primary role of a Circuit Breaker in microservices?",
                    "a": "To fail-fast and return fallback responses when a downstream dependency fails, preventing thread exhaustion and cascading system outages across the architecture."
                }
            ],
            "quiz": [
                {
                    "id": 403,
                    "q": "In a Spring Boot application, what is the best practice for dependency injection to support immutability and unit testability?",
                    "options": [
                        "Field injection using @Autowired on private fields",
                        "Constructor injection",
                        "Setter injection only",
                        "Manual instantiation using 'new'"
                    ],
                    "answer": 1,
                    "explanation": "Constructor injection ensures that required dependencies are immutable (can be declared final) and allows easy instantiation in unit tests without a Spring context."
                }
            ]
        },
        {
            "id": "ch-17",
            "stage_id": "stage-4",
            "number": 17,
            "title": "Cloud Computing Infrastructure (AWS Architecture) & Docker Containerization",
            "exams": ["sbi", "sebi"],
            "reading_time_mins": 25,
            "summary": "AWS core services (EC2, S3, IAM, VPC public/private subnets, Security Groups), Docker container mechanics (Linux Namespaces & Cgroups), and Dockerfile best practices.",
            "lecture_notes": """# Cloud Computing Architecture (AWS) & Docker Containers

## 1. Amazon Web Services (AWS) Enterprise Infrastructure
* **Compute (Amazon EC2):** Elastic Compute Cloud virtual servers.
* **Storage (Amazon S3):** Simple Storage Service object store delivering 99.999999999% (11 9's) durability.
* **Amazon VPC (Virtual Private Cloud):** Logically isolated virtual network.
  * **Public Subnet:** Connected to an **Internet Gateway (IGW)**; hosts public-facing load balancers.
  * **Private Subnet:** No direct internet access; hosts internal microservices and databases. Outbound internet updates route through a **NAT Gateway** in the public subnet!
  * **Security Groups vs Network ACLs:**
    * **Security Group:** **Stateful** firewall operating at the instance level. If inbound traffic is allowed, return traffic is automatically allowed.
    * **NACL (Network Access Control List):** **Stateless** firewall operating at the subnet boundary. Both inbound and outbound rules must be explicitly defined.

---

## 2. Docker Containers vs Virtual Machines
* **Virtual Machines:** Hypervisor virtualizes physical hardware; each VM carries a full Guest OS (heavy, gigabytes in size, slow startup).
* **Docker Containers:** Share the **Host OS Kernel**; isolated using native Linux kernel primitives:
  * **Namespaces:** Provide isolated workspaces (PID isolates processes, NET isolates network interfaces, MNT isolates filesystems).
  * **Cgroups (Control Groups):** Enforce CPU, memory, and I/O resource limits per container.

```dockerfile
# Production Multi-Stage Dockerfile for Spring Boot
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
USER 1001
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```""",
            "checkpoints": [
                {
                    "q": "What is the difference between AWS Security Groups and Network ACLs?",
                    "a": "Security Groups are stateful firewalls operating at the instance/ENI level. Network ACLs are stateless firewalls operating at the subnet boundary."
                }
            ],
            "quiz": [
                {
                    "id": 404,
                    "q": "Which Linux kernel feature enables Docker to isolate network interfaces, process IDs, and file system mount points for a container?",
                    "options": [
                        "Cgroups",
                        "Namespaces",
                        "SELinux",
                        "Chroot only"
                    ],
                    "answer": 1,
                    "explanation": "Linux Namespaces provide isolated views of system resources (PID, NET, MNT, IPC, UTS) to each container."
                }
            ]
        }
    ]
}

# ==============================================================
# STAGE 5: DATA ANALYTICS & SCRIPTING (SEBI GRADE A FOCUS)
# ==============================================================
stage5 = {
    "id": "stage-5",
    "number": 5,
    "title": "Stage 05: Python Scripting, NumPy & Pandas Data Analytics",
    "badge": "SEBI Specialization",
    "description": "Customized for the SEBI Grade A IT syllabus: Python language fundamentals, memory management (GIL), NumPy arrays, Pandas DataFrames, and regular expressions.",
    "chapters": [
        {
            "id": "ch-18",
            "stage_id": "stage-5",
            "number": 18,
            "title": "Python Language Core: Data Structures, Memory Management & The GIL",
            "exams": ["sebi"],
            "reading_time_mins": 25,
            "summary": "Lists vs Tuples, Dictionary hash table implementation, List comprehensions, Generators (yield), Reference Counting, Cyclic GC, and the Global Interpreter Lock (GIL).",
            "lecture_notes": """# Python Core: Data Structures, Memory & GIL

## 1. Python Data Structures Taxonomy
* **Lists:** Dynamic arrays. Mutable, elements stored as pointers. Appending is amortized $O(1)$.
* **Tuples:** Immutable sequences. Memory-efficient; can serve as dictionary keys (if all contained items are hashable).
* **Dictionaries & Sets:** Implemented via **Hash Tables with open addressing**. Average lookup and insertion is $O(1)$.
* **List Comprehensions:** Executed at C-level speed:
  ```python
  even_squares = [x**2 for x in range(100) if x % 2 == 0]
  ```

---

## 2. Python Memory Management & The GIL
* **Reference Counting:** Every Python object carries a `PyObject_HEAD` containing an `ob_refcnt`. When a reference is created, counter increments; when variable falls out of scope, counter decrements. If `ob_refcnt == 0`, memory is deallocated immediately!
* **Cyclic Garbage Collector:** Detects circular reference cycles (e.g. `objA.ref = objB` and `objB.ref = objA`) using generational heuristics.
* **The Global Interpreter Lock (GIL):** A mutex lock in CPython that ensures only one native thread executes Python bytecode at any given moment.
  * **Consequence:** For CPU-bound tasks, multithreading in Python does NOT achieve true multi-core speedup! You must use the **`multiprocessing`** module to spawn separate OS processes with independent GILs.""",
            "checkpoints": [
                {
                    "q": "Why does Python's GIL prevent CPU-bound tasks from executing in parallel using the threading module?",
                    "a": "Because the GIL restricts CPython bytecode execution to a single native thread at a time, forcing threads to time-slice on one CPU core. True multi-core execution requires multiprocessing."
                }
            ],
            "quiz": [
                {
                    "id": 501,
                    "q": "What is the primary memory management mechanism utilized by CPython to deallocate objects as soon as they become unreachable?",
                    "options": [
                        "Generational Copying only",
                        "Reference Counting",
                        "Mark and Sweep only",
                        "Manual free() calls"
                    ],
                    "answer": 1,
                    "explanation": "CPython uses reference counting as its primary memory management system, supplemented by a cyclic garbage collector to resolve circular references."
                }
            ]
        },
        {
            "id": "ch-19",
            "stage_id": "stage-5",
            "number": 19,
            "title": "Data Manipulation with Pandas, NumPy & Regular Expressions",
            "exams": ["sebi"],
            "reading_time_mins": 25,
            "summary": "NumPy vectorized operations, Pandas DataFrames, loc vs iloc indexing, GroupBy aggregations, handling missing data, and regex parsing with the re module.",
            "lecture_notes": """# Data Analytics with Pandas, NumPy & RegEx

## 1. Pandas DataFrame Manipulation
* `df.loc[row_label, col_label]`: Label-based indexing.
* `df.iloc[row_index, col_index]`: Integer position-based indexing (0 to $N-1$).
* **Vectorized Filtering & Aggregation:**
  ```python
  import pandas as pd

  # Load regulatory trade data
  df = pd.DataFrame({
      'tr_id': [101, 102, 103, 104],
      'symbol': ['RELIANCE', 'TCS', 'RELIANCE', 'INFY'],
      'volume': [5000, 12000, 8500, 3000],
      'status': ['SUCCESS', 'SUCCESS', 'FAILED', 'SUCCESS']
  })

  # High-volume successful trades
  high_vol = df[(df['volume'] > 4000) & (df['status'] == 'SUCCESS')]

  # Group by stock symbol and aggregate volume metrics
  summary = df.groupby('symbol')['volume'].agg(['mean', 'sum', 'count'])
  ```

---

## 2. Python Regular Expressions (`re` Module)
* `re.search(pattern, str)`: Scans string to find first match anywhere.
* `re.match(pattern, str)`: Matches ONLY at the beginning of the string!
* `re.findall(pattern, str)`: Returns all non-overlapping matches as a list.
* `re.sub(pattern, repl, str)`: Finds and replaces matching substrings.""",
            "checkpoints": [
                {
                    "q": "What is the key functional difference between re.match() and re.search() in Python?",
                    "a": "re.match() matches only at the start of the string, whereas re.search() scans through the entire string to find a match anywhere."
                }
            ],
            "quiz": [
                {
                    "id": 502,
                    "q": "In Python's 're' module, which function checks for a pattern match ONLY at the beginning of a string?",
                    "options": [
                        "re.search()",
                        "re.match()",
                        "re.findall()",
                        "re.compile()"
                    ],
                    "answer": 1,
                    "explanation": "re.match() is anchored to the beginning of the string; it returns None if the pattern does not match at index 0."
                }
            ]
        }
    ]
}

# ==============================================================
# STAGE 6: CYBER SECURITY & BANKING REGULATORY STANDARDS
# ==============================================================
stage6 = {
    "id": "stage-6",
    "number": 6,
    "title": "Stage 06: Cyber Security & Banking Regulatory Standards",
    "badge": "Regulatory Compliance",
    "description": "Essential web security principles, OWASP Top 10 vulnerabilities, applied cryptography, and the Reserve Bank of India (RBI) Cyber Security Framework.",
    "chapters": [
        {
            "id": "ch-20",
            "stage_id": "stage-6",
            "number": 20,
            "title": "OWASP Top 10 Web Application Vulnerabilities, Attacks & Mitigation",
            "exams": ["ibps", "sbi", "sebi"],
            "reading_time_mins": 25,
            "summary": "Deep dive into SQL Injection (In-band, Blind), Cross-Site Scripting (Stored, Reflected, DOM), CSRF tokens, Insecure Direct Object References (IDOR), and defense-in-depth.",
            "lecture_notes": """# OWASP Top 10 Web Vulnerabilities & Secure Engineering

## 1. SQL Injection (SQLi)
* **Mechanics:** Attacker injects malicious SQL tokens into input parameters to manipulate database queries.
* **Vulnerable Query:**
  ```sql
  -- Input: admin' OR '1'='1
  SELECT * FROM Users WHERE username = 'admin' OR '1'='1' AND password = 'xyz';
  ```
* **Definitive Defense:** **Parameterized Queries (Prepared Statements)**.
  ```java
  // Safe: PreparedStatement compiles query template before binding values
  String sql = "SELECT * FROM Users WHERE username = ? AND password = ?";
  PreparedStatement stmt = conn.prepareStatement(sql);
  stmt.setString(1, inputUser);
  stmt.setString(2, inputPassword);
  ```

---

## 2. Cross-Site Scripting (XSS) & Cross-Site Request Forgery (CSRF)
* **XSS:** Executing malicious JavaScript in the victim's browser context.
  * **Stored XSS:** Malicious payload is permanently saved in the database (e.g. comment field) and executed whenever other users view the page.
  * **Mitigation:** Context-sensitive HTML entity encoding and strict **Content Security Policy (CSP)** HTTP headers.
* **CSRF:** Tricking an authenticated user into executing unwanted actions on a trusted banking site where they have an active session cookie.
  * **Mitigation:** Anti-CSRF synchronization tokens and `SameSite=Strict` cookie attributes.""",
            "checkpoints": [
                {
                    "q": "Why do Prepared Statements eliminate SQL Injection?",
                    "a": "Because the SQL engine compiles the query template before parameter insertion. User inputs are treated strictly as literal data values and can never alter the query's executable structure."
                }
            ],
            "quiz": [
                {
                    "id": 601,
                    "q": "Which technique provides the most robust and complete defense against SQL Injection vulnerabilities?",
                    "options": [
                        "Client-side JavaScript string validation",
                        "Prepared Statements with Parameterized Queries",
                        "Filtering input for single quotes",
                        "Base64 encoding all form parameters"
                    ],
                    "answer": 1,
                    "explanation": "Prepared Statements compile the query syntax before binding input parameters, ensuring user inputs are treated as literal values rather than executable code."
                }
            ]
        },
        {
            "id": "ch-21",
            "stage_id": "stage-6",
            "number": 21,
            "title": "Applied Cryptography, PKI, Digital Signatures & RBI Cyber Security Framework",
            "exams": ["ibps", "sbi", "sebi"],
            "reading_time_mins": 25,
            "summary": "Symmetric (AES) vs Asymmetric (RSA/ECC) cryptography, Public Key Infrastructure (PKI), Digital Signature properties, and RBI mandatory cyber security directives for commercial banks.",
            "lecture_notes": """# Applied Cryptography & RBI Cyber Security Framework

## 1. Cryptography Taxonomy: Symmetric vs Asymmetric
* **Symmetric Encryption (AES):** Same secret key for encryption and decryption. Highly optimized in hardware (AES-NI). Used for bulk data at rest and data in transit.
* **Asymmetric Encryption (RSA, ECC):** Key pair consisting of a **Public Key** and a **Private Key**.
  * Encrypt with Public Key $\\implies$ Only Private Key can decrypt (**Confidentiality**).
  * Sign hash with Private Key $\\implies$ Public Key verifies (**Digital Signature**).

### Properties of a Digital Signature
1. **Authentication:** Proves the exact identity of the signer.
2. **Data Integrity:** Guarantees data was not altered after signing.
3. **Non-Repudiation:** The signer cannot deny signing the transaction.
* *(Note: A digital signature alone does NOT encrypt the message payload; Confidentiality requires separate encryption!)*

---

## 2. The RBI Cyber Security Framework for Commercial Banks
Mandated by the Reserve Bank of India to protect Indian financial infrastructure:
1. **Board-Approved Cyber Security Policy:** Formal policy reviewed annually.
2. **24/7 Security Operations Center (SOC):** Continuous real-time monitoring and SIEM log retention.
3. **Multi-Factor Authentication (MFA):** Mandatory for all administrative access and customer fund transactions.
4. **Vulnerability Assessment & Penetration Testing (VAPT):** Periodic third-party testing.
5. **Incident Reporting:** Mandatory reporting of cyber incidents to RBI within 2 to 6 hours of detection.""",
            "checkpoints": [
                {
                    "q": "What three security properties does a Digital Signature provide?",
                    "a": "Authentication, Data Integrity, and Non-repudiation. (It does not provide confidentiality without separate payload encryption)."
                }
            ],
            "quiz": [
                {
                    "id": 602,
                    "q": "Which security property is NOT provided by a standard Digital Signature generated via private key hashing?",
                    "options": [
                        "Authentication",
                        "Data Integrity",
                        "Non-repudiation",
                        "Confidentiality"
                    ],
                    "answer": 3,
                    "explanation": "Digital Signatures provide authentication, integrity, and non-repudiation. They do not conceal the message content (confidentiality), which requires encryption."
                },
                {
                    "id": 603,
                    "q": "Under RBI Cybersecurity directives, what control is strictly mandated for all administrative access and sensitive payment processing?",
                    "options": [
                        "Multi-Factor Authentication (MFA)",
                        "Single 8-character password",
                        "Access over unencrypted HTTP",
                        "Manual paper signoff"
                    ],
                    "answer": 0,
                    "explanation": "The RBI Cybersecurity Framework mandates Multi-Factor Authentication (MFA) across all administrative portals and sensitive banking transactions."
                }
            ]
        }
    ]
}

# Assemble final master curriculum with all 6 Stages and all 21 Chapters
master_curriculum = {
    "stages": [
        s1_list[0],  # Stage 1: Chapters 1 to 4
        stage2,      # Stage 2: Chapters 5 to 10
        stage3,      # Stage 3: Chapters 11 to 14
        stage4,      # Stage 4: Chapters 15 to 17
        stage5,      # Stage 5: Chapters 18 to 19
        stage6       # Stage 6: Chapters 20 to 21
    ],
    "stats": {
        "total_stages": 6,
        "total_chapters": 21,
        "total_questions": sum(
            sum(len(ch['quiz']) for ch in s['chapters']) 
            for s in [s1_list[0], stage2, stage3, stage4, stage5, stage6]
        )
    }
}

out_curriculum_path = os.path.join(DATA_DIR, 'curriculum.json')
with open(out_curriculum_path, 'w', encoding='utf-8') as f:
    json.dump(master_curriculum, f, indent=2)

print("=" * 60)
print(f"MASTER CURRICULUM GENERATED SUCCESSFULLY: {out_curriculum_path}")
print(f"Total Stages: {master_curriculum['stats']['total_stages']}")
print(f"Total Chapters: {master_curriculum['stats']['total_chapters']}")
print(f"Total Embedded Assessment Questions: {master_curriculum['stats']['total_questions']}")
print("=" * 60)
