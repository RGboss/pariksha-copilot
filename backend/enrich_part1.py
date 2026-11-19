# -*- coding: utf-8 -*-
"""
Enrichment module for Chapters 10, 11, 12, 13, 14
Provides exhaustive, textbook-grade lecture notes, 3 checkpoints, and 5 exam-calibrated questions each.
"""

ENRICHED_CHAPTERS = {}

# ==============================================================
# CHAPTER 10: Linux Systems Administration
# ==============================================================
ENRICHED_CHAPTERS["ch-10"] = {
    "summary": "Deep dive into Linux architecture, kernel space vs user space, octal/symbolic permissions, SUID/SGID/Sticky bits, process signals, systemd services, pipes/redirection, and shell text-processing tools (grep, sed, awk).",
    "reading_time_mins": 30,
    "lecture_notes": """# Linux Systems Administration: Architecture, Permissions, Signals & Shell Engineering

## 1. The Linux Kernel Architecture & System Call Interface
Linux is a monolithic Unix-like operating system kernel offering multi-user, preemptive multitasking. 

```
+-------------------------------------------------------------+
|                User Space Applications                      |
|       (Bash, Web Servers, Database Daemons, JVM)           |
+-------------------------------------------------------------+
|               C Standard Library (glibc)                    |
+-------------------------------------------------------------+
|           System Call Interface (sys_call_table)            |
|       open(), read(), write(), fork(), execve(), kill()     |
+-------------------------------------------------------------+
|                     Kernel Space                            |
|  +-------------------+  +-------------------+  +----------+ |
|  | Process Scheduler |  | Virtual Memory VFS|  | IPC / Net| |
|  +-------------------+  +-------------------+  +----------+ |
|  +--------------------------------------------------------+ |
|  |              Device Drivers & Hardware Mgmt            | |
|  +--------------------------------------------------------+ |
+-------------------------------------------------------------+
|                 Hardware (CPU, RAM, Disks, NIC)             |
+-------------------------------------------------------------+
```

### User Space vs Kernel Space
* **User Space (Ring 3 on x86-64):** Where all normal application software, user shells, and JVM runtimes execute. Code running here has limited CPU privileges and cannot access physical hardware directly.
* **Kernel Space (Ring 0 on x86-64):** Where the OS core, device drivers, and interrupt handlers execute. It has unrestricted access to hardware instructions and physical memory.
* **Context Transition:** To read a file or send network bytes, a user process initiates a **System Call** (e.g., `read()`, `write()`). The CPU executes `syscall`, transitioning from Ring 3 to Ring 0. The kernel validates permissions, executes the request, and transitions back to Ring 3.

---

## 2. Unix File Permission Matrix & Special Bits
In Unix/Linux, everything is treated as a stream of bytes or a file (including directories, disks, sockets, and character devices).

### 2.1 The Standard 9-Bit Permission Tuple
A file's access mode consists of 3 sets of permissions for 3 user tiers:
* **User (`u`):** Owner of the file.
* **Group (`g`):** Group members assigned to the file.
* **Others (`o`):** Every other user on the system.

Each set has 3 permission bits:
* **Read (`r` / 4):** View file content; list directory contents (`ls`).
* **Write (`w` / 2):** Modify file content; create/delete files in directory.
* **Execute (`x` / 1):** Execute program/script; enter directory (`cd`) and access files inside.

```
Example: -rwxr-xr--
User   (rwx) = 4 + 2 + 1 = 7
Group  (r-x) = 4 + 0 + 1 = 5
Others (r--) = 4 + 0 + 0 = 4
Octal representation = 754
```

### 2.2 Special Permission Bits (The 4th Octal Digit)
* **SUID (Set User ID - Octal 4000):** When set on an executable binary, any user running the binary executes it with the permissions of the file's **owner** rather than the calling user.
  * *Classic Example:* `/usr/bin/passwd` (owned by `root`, needs to write to `/etc/shadow`).
  * *Symbolic representation:* `-rwsr-xr-x` (lower 's' if execute bit is set, capital 'S' if execute bit is unset).
* **SGID (Set Group ID - Octal 2000):**
  * *On binary:* Executed with group owner privileges.
  * *On directory:* Any new file created inside inherits the directory's **group**, enabling seamless team collaboration.
  * *Symbolic representation:* `drwxr-sr-x`.
* **Sticky Bit (Octal 1000):**
  * *On directory:* Only the file owner, directory owner, or `root` can rename or delete files inside, even if others have write access.
  * *Classic Example:* `/tmp` (`drwxrwxrwt`).
  * *Symbolic representation:* `t` (lower 't' with execute bit, 'T' without).

### 2.3 Default Permissions & `umask`
When a process creates a file or directory, the OS applies a mask:
* **Base Default for Directories:** `777` (`rwxrwxrwx`)
* **Base Default for Files:** `666` (`rw-rw-rw-` - execution is never granted by default for security)
* **Effective Mode Formula:** $\text{Effective Mode} = \text{Base Mode} \ \& \ (\sim\text{umask})$.
* If `umask = 022`:
  * Directory permission: $777 - 022 = 755$ (`rwxr-xr-x`).
  * File permission: $666 - 022 = 644$ (`rw-r--r--`).

---

## 3. Process Management, Signals & Lifecycle
Every Linux process has a unique Process ID (`PID`), Parent Process ID (`PPID`), and is organized in a hierarchical tree rooted at `systemd` (`PID 1`).

### 3.1 Process Creation: `fork()` and `execve()`
1. **`fork()`:** Clones the calling process. It duplicates the page tables using **Copy-On-Write (COW)**. The parent receives the child PID; the child receives `0`.
2. **`execve()`:** Overwrites the current process address space with a new executable program, keeping the same PID.
3. **`wait()` / `waitpid()`:** Parent waits for child termination and collects its exit status code.

### 3.2 Orphan vs Zombie Processes
* **Zombie Process (`<defunct>`, State `Z`):** A child process has finished execution (`exit()`), freed its memory, but its entry remains in the Process Table because its parent has not yet called `wait()` to read its exit code. Zombies consume zero RAM/CPU but exhaust process IDs if unmanaged.
  * *Remedy:* Kill the parent process. The zombie will be reparented to `PID 1` (`systemd`), which immediately invokes `wait()` to purge the zombie.
* **Orphan Process:** A parent terminates before its child. The child is adopted by `PID 1` (`systemd` / `init`) and runs normally to completion.

### 3.3 Critical Inter-Process Communication Signals
Signals are asynchronous notifications sent to a process.
| Signal | Number | Default Action | Catchable? | Usage & Banking Relevance |
| :--- | :---: | :--- | :---: | :--- |
| **SIGHUP** | 1 | Terminate | Yes | Hangup detected on controlling terminal; commonly triggers config reload in daemons (e.g. `nginx -s reload`). |
| **SIGINT** | 2 | Terminate | Yes | Interrupt from keyboard (`Ctrl + C`). Clean exit requested. |
| **SIGQUIT**| 3 | Core Dump | Yes | Quit from keyboard (`Ctrl + \`). Produces core memory dump for debugging. |
| **SIGKILL**| 9 | Immediate Terminate | **NO** | Uncatchable, unignorable kernel-level force kill. Leaves no chance to flush buffers. |
| **SIGSEGV**| 11 | Core Dump | Yes | Segmentation violation (invalid memory access / null pointer dereference). |
| **SIGTERM**| 15 | Terminate | Yes | Standard graceful termination request (used by `systemctl stop`). Gives process time to commit transactions. |
| **SIGSTOP**| 19 | Pause Execution | **NO** | Uncatchable process suspension (`Ctrl + Z` sends `SIGTSTP` which is catchable). |

---

## 4. Shell Redirection, Pipelines & Text Processing
Unix philosophy dictates writing small programs that do one thing well, composable via standard streams:
* **Standard In (`stdin` / FD 0):** Default input stream (keyboard).
* **Standard Out (`stdout` / FD 1):** Normal output stream (terminal).
* **Standard Error (`stderr` / FD 2):** Diagnostic and error messages stream.

```bash
# Redirection primitives:
command > file.txt        # Overwrite stdout to file
command >> file.txt       # Append stdout to file
command 2> err.log        # Redirect stderr to file
command > out.txt 2>&1    # Redirect both stdout and stderr to out.txt
command &> out.txt        # Modern bash shortcut for redirecting both

# Pipelines:
command1 | command2       # Feeds stdout of command1 into stdin of command2
```

### High-Yield Text Processing Utilities
* **`grep`:** Global Regular Expression Print.
  ```bash
  grep -rn "NullPointerException" /var/log/app/   # -r recursive, -n line number
  grep -v "DEBUG" server.log                     # -v invert match (exclude DEBUG)
  ```
* **`awk`:** Pattern scanning and processing language. Operates record by record (`$0` is line, `$1`, `$2` are fields).
  ```bash
  # Print IP address and HTTP status code from web server log:
  awk '{print $1, $9}' access.log
  # Sum memory usage of processes:
  ps aux | awk '{sum += $6} END {print "Total RSS:", sum/1024, "MB"}'
  ```
* **`sed`:** Stream Editor for filtering and transforming text.
  ```bash
  sed -i 's/PORT=8080/PORT=9090/g' application.properties   # In-place substitution
  ```
* **`lsof` & `ss` (System & Socket Inspection):**
  ```bash
  lsof -i :8080               # Find which process PID is holding port 8080
  ss -tulpn                   # Fast modern socket statistics (replaces netstat)
  ```

---

## 5. High-Yield Summary Matrix for Banking IT Exams

| Concept | Octal / Command | Core Mechanism / Exam Focus |
| :--- | :--- | :--- |
| **SUID Bit** | 4000 (`-rwsr-xr-x`) | Runs with file owner privileges; security risk if set on writable files. |
| **SGID Bit** | 2000 (`drwxr-sr-x`) | Forces newly created files in directory to inherit directory group. |
| **Sticky Bit** | 1000 (`drwxrwxrwt`) | Prevents users from deleting other users' files in shared directory (`/tmp`). |
| **Uncatchable Signals** | `SIGKILL` (9), `SIGSTOP` (19) | Cannot be handled, caught, or ignored by application code. |
| **Graceful Shutdown** | `SIGTERM` (15) | Preferred signal sent by container orchestrators / systemd before force-killing. |
| **Zombie Cleansing** | Kill parent process | Zombies consume zero memory but fill PID table; reparent to PID 1 to clean up. |
""",
    "checkpoints": [
        {
            "q": "A banking deployment engineer sets directory permissions to 770 and umask to 027. What are the effective permissions of a newly created subfolder and a newly created configuration file?",
            "a": "Base directory mode is 777. Applying umask 027 (777 - 027) yields 750 (rwxr-x---). Base file mode is 666. Applying umask 027 (666 minus write/execute bits in 027) yields 640 (rw-r-----). User gets read/write, Group gets read, Others get zero access."
        },
        {
            "q": "Why can an application developer NOT write a signal handler in C or Java to intercept SIGKILL (9) or SIGSTOP (19)?",
            "a": "The Linux kernel processes SIGKILL and SIGSTOP entirely within kernel space. It alters the process state directly in the task struct without ever scheduling the process to return to user space or dispatching an interrupt vector to user-defined signal handler routines."
        },
        {
            "q": "A production server shows thousands of '<defunct>' processes in 'ps aux'. How do they impact system resources and how do you resolve them?",
            "a": "Defunct (zombie) processes hold zero RAM and execute zero CPU instructions; their address space has already been deallocated. However, each holds an entry in the kernel Process Table. If the table reaches PID_MAX, no new processes can spawn. Resolution: Send SIGKILL to the unresponsive parent process so PID 1 inherits and reaps them."
        }
    ],
    "quiz": [
        {
            "id": 228,
            "q": "Which Linux command displays the current default file creation permission mask, and what is the effective file permission if umask is 022 on a newly created regular text file (base 666)?",
            "options": [
                "Command 'umask'; effective permission is 644 (rw-r--r--)",
                "Command 'chmod'; effective permission is 755 (rwxr-xr-x)",
                "Command 'chown'; effective permission is 600 (rw-------)",
                "Command 'umask'; effective permission is 777 (rwxrwxrwx)"
            ],
            "answer": 0,
            "explanation": "The 'umask' command inspects the mask. Regular files have a base permission of 666 (no execute bits granted by default). Subtracting mask 022 (bitwise 666 & ~022) results in 644 (Owner: rw-, Group: r--, Others: r--)."
        },
        {
            "id": 229,
            "q": "Which of the following signals CANNOT be intercepted, caught, or ignored by a user-space application handler?",
            "options": [
                "SIGTERM (15)",
                "SIGINT (2)",
                "SIGKILL (9) and SIGSTOP (19)",
                "SIGHUP (1) and SIGUSR1 (10)"
            ],
            "answer": 2,
            "explanation": "In POSIX/Linux, SIGKILL (signal 9) and SIGSTOP (signal 19) are reserved exclusively for the kernel. They terminate or pause the process unconditionally and cannot be intercepted by any signal handler."
        },
        {
            "id": 230,
            "q": "What is the primary function of setting the SGID (Set Group ID) bit on a directory in a shared banking development server?",
            "options": [
                "It prevents all users other than the owner from deleting files inside the directory.",
                "Any file created inside the directory automatically inherits the group ownership of the directory.",
                "It executes all files inside the directory with root privileges.",
                "It restricts network access to only local IP addresses."
            ],
            "answer": 1,
            "explanation": "When SGID is set on a directory (e.g. chmod g+s /shared), any new file created within that directory automatically inherits the directory's group owner, rather than the primary group of the creating user. This facilitates multi-user collaboration."
        },
        {
            "id": 231,
            "q": "What occurs when a child process terminates using exit(), but the parent process never invokes wait() or waitpid()?",
            "options": [
                "The child becomes an Orphan process and is adopted by PID 1.",
                "The child remains in the process table as a Zombie (<defunct>) process.",
                "The operating system forcefully terminates the parent process with SIGABRT.",
                "The child continues executing in the background as a daemon process."
            ],
            "answer": 1,
            "explanation": "When a child finishes executing, its memory and descriptors are freed, but its exit status remains in the process table until the parent reads it via wait(). An uncollected terminated process is a Zombie (State Z). If the parent dies, it is adopted by PID 1 and reaped."
        },
        {
            "id": 232,
            "q": "Which command combination will search for all lines containing 'CRITICAL' in all '.log' files under '/var/logs' and display the matching line count?",
            "options": [
                "grep -r 'CRITICAL' /var/logs/*.log | wc -l",
                "find /var/logs -name '*.log' | sed 's/CRITICAL//g'",
                "cat /var/logs | awk '{print $1}'",
                "ss -tulpn | grep 'CRITICAL'"
            ],
            "answer": 0,
            "explanation": "grep -r 'CRITICAL' /var/logs/*.log searches recursively for matching lines, and piping the output into 'wc -l' (word count lines) calculates the total number of matched lines."
        }
    ]
}

print("Chapter 10 definition complete.")

# ==============================================================
# CHAPTER 11: Object-Oriented Programming & SOLID Architecture
# ==============================================================
ENRICHED_CHAPTERS["ch-11"] = {
    "summary": "Core OOPs principles (Encapsulation, Abstraction, Inheritance, Polymorphism), virtual method tables (vtables), abstract classes vs interfaces, comprehensive SOLID principles with practical Java code, and Gang of Four design patterns.",
    "reading_time_mins": 30,
    "lecture_notes": """# Object-Oriented Programming (OOPs), Dynamic Dispatch & SOLID Architecture

## 1. The Four Foundational Pillars of OOPs
Object-Oriented Programming models software around entities possessing **State** (attributes/data fields) and **Behavior** (methods/functions).

```
+-------------------------------------------------------------+
|                      FOUR OOP PILLARS                       |
+------------------------------+------------------------------+
| 1. Encapsulation             | 2. Abstraction               |
| - Data Hiding (private fields)| - Interface & Contract       |
| - Controlled Access (get/set)| - Hides Complex Mechanism    |
+------------------------------+------------------------------+
| 3. Inheritance               | 4. Polymorphism              |
| - Code Reuse (IS-A)          | - Compile-time (Overloading) |
| - Class Hierarchies          | - Runtime (Overriding/vtable)|
+------------------------------+------------------------------+
```

### 1.1 Encapsulation & Data Hiding
* Encapsulation bundles data and methods operating on that data within a single class, shielding internal state from arbitrary external mutation.
* Enforced via **Access Modifiers** (in Java/C++):
  * `private`: Accessible only within the declaring class.
  * `protected`: Accessible within the declaring class, package, and subclasses.
  * `public`: Accessible from any package.
  * `default` (package-private in Java): Accessible only within the same package.

### 1.2 Abstraction: Abstract Classes vs Interfaces
Abstraction presents the essential interface while hiding implementation mechanics.
| Property | Abstract Class | Interface (Java 8+) |
| :--- | :--- | :--- |
| **Relationship** | IS-A (strict class inheritance) | CAN-DO (contract / capability) |
| **Multiple Inheritance**| Single inheritance only (`extends`) | Multiple interface implementation (`implements`) |
| **State Fields** | Can maintain non-final instance fields | Fields are implicitly `public static final` constants |
| **Constructors** | Can declare constructors (invoked via `super()`) | No constructors permitted |
| **Default Methods** | Full method bodies allowed | Allowed via `default` and `static` keywords |

### 1.3 Polymorphism & Dynamic Method Dispatch (vtables)
* **Compile-Time Polymorphism (Static / Early Binding):** Method Overloading. Resolved at compile time based on method signature (name and parameter types).
* **Runtime Polymorphism (Dynamic / Late Binding):** Method Overriding. Resolved at runtime based on the actual object instance allocated on the heap.
* **The vtable (Virtual Method Table) Mechanism:**
  When a class defines virtual/overridden methods, the compiler creates a table of function pointers for that class. Every object instance contains an invisible pointer (`vptr`) pointing to this table. At runtime, calling `parentRef.execute()` performs an indirect lookup: `vptr -> vtable[index]()`, invoking the child class implementation with minimal $O(1)$ overhead.

---

## 2. SOLID Architectural Principles: Deep Dive
Formulated by Robert C. Martin ("Uncle Bob"), the SOLID principles prevent architectural rot, high coupling, and fragility in enterprise banking applications.

```
+----+--------------------------------+-------------------------------------+
| S  | Single Responsibility          | A class should have ONE reason to   |
|    | Principle (SRP)                | change.                             |
+----+--------------------------------+-------------------------------------+
| O  | Open / Closed Principle (OCP)  | Open for extension, Closed for      |
|    |                                | modification.                       |
+----+--------------------------------+-------------------------------------+
| L  | Liskov Substitution            | Subtypes must be substitutable for  |
|    | Principle (LSP)                | their base types without breaking.  |
+----+--------------------------------+-------------------------------------+
| I  | Interface Segregation          | Clients should not depend on        |
|    | Principle (ISP)                | methods they do not use.            |
+----+--------------------------------+-------------------------------------+
| D  | Dependency Inversion           | Depend upon abstractions, not on    |
|    | Principle (DIP)                | concrete implementations.           |
+----+--------------------------------+-------------------------------------+
```

### 2.1 Single Responsibility Principle (SRP)
* *Definition:* A class should encompass only one cohesive business concern.
* *Violation:* A `CustomerAccount` class that calculates interest, validates KYC documents, and prints statement PDFs.
* *Remedy:* Segregate into `AccountBalanceService`, `KycVerificationService`, and `StatementReportGenerator`.

### 2.2 Open/Closed Principle (OCP)
* *Definition:* Modules should be extendable with new behavior without altering existing, tested source code.
* *Implementation:* Use polymorphism, abstract interfaces, and strategy design patterns.
```java
// Good design: Open to adding new payment types without modifying existing processors
public interface PaymentProcessor {
    void processTransaction(BigDecimal amount);
}
public class UpiPaymentProcessor implements PaymentProcessor { ... }
public class NeftPaymentProcessor implements PaymentProcessor { ... }
public class ImpsPaymentProcessor implements PaymentProcessor { ... }
```

### 2.3 Liskov Substitution Principle (LSP)
* *Definition:* Objects of a superclass should be replaceable with objects of its subclasses without altering any of the desirable properties of the program (correctness, task performed, etc.).
* *The Classic Violation (Square-Rectangle Problem):*
  If `Square extends Rectangle`, setting width and height independently in `Square` breaks the post-conditions expected by client code using a `Rectangle` reference.
* *Rule:* Subtypes cannot enforce stricter preconditions or weaker postconditions than the base type.

### 2.4 Interface Segregation Principle (ISP)
* *Definition:* No client should be forced to depend on methods it does not use. Large "fat" interfaces must be split into smaller, cohesive role interfaces.
```java
// Fat Interface Violation:
public interface BankingOperations {
    void transferFunds();
    void approveOverdraft(); // Only managers do this
    void auditLedger();      // Only auditors do this
}
// Segregated Interfaces:
public interface TransferService { void transferFunds(); }
public interface OverdraftApprovalService { void approveOverdraft(); }
public interface AuditService { void auditLedger(); }
```

### 2.5 Dependency Inversion Principle (DIP)
* *Definition:* High-level modules (business policy) should not depend on low-level modules (I/O, database drivers). Both should depend upon abstractions (interfaces).
* Foundation for **Inversion of Control (IoC)** and **Dependency Injection (DI)** in frameworks like Spring.

---

## 3. High-Yield Gang of Four (GoF) Design Patterns

### 3.1 Singleton Pattern (Thread-Safe Double-Checked Locking)
Ensures a class has only one instance and provides a global point of access.
```java
public class DatabaseConnectionPool {
    // volatile prevents instruction reordering during initialization
    private static volatile DatabaseConnectionPool instance;
    
    private DatabaseConnectionPool() {
        // private constructor prevents instantiation
    }
    
    public static DatabaseConnectionPool getInstance() {
        if (instance == null) {
            synchronized (DatabaseConnectionPool.class) {
                if (instance == null) {
                    instance = new DatabaseConnectionPool();
                }
            }
        }
        return instance;
    }
}
```

### 3.2 Factory Method & Abstract Factory
* **Factory Method:** Defines an interface for creating an object, but lets subclasses decide which class to instantiate.
* **Abstract Factory:** Creates families of related or dependent objects without specifying their concrete classes.

### 3.3 Strategy Pattern
Defines a family of interchangeable algorithms, encapsulates each one, and makes them interchangeable at runtime (e.g., swapping discount calculations or loan eligibility criteria).

### 3.4 Observer Pattern
Defines a one-to-many dependency between objects so that when one object changes state, all its dependents are notified and updated automatically (e.g., event-driven notification alerts for credit/debit events).

---

## 4. High-Yield Summary Matrix for Banking IT Exams

| Concept | Key Identifier | Real Exam Trap / Examiner Focus |
| :--- | :--- | :--- |
| **Compile-time Polymorphism** | Method Overloading | Return type alone does NOT overload a method. Parameters must differ in count or type. |
| **Runtime Polymorphism** | Method Overriding | Static methods CANNOT be overridden (they are hidden via compile-time class binding). |
| **LSP Violation** | Throwing `UnsupportedOperationException` | If a subclass throws an exception for an inherited base method, it violates LSP. |
| **Double-Checked Locking** | `volatile` keyword | Without `volatile`, a thread can observe a partially constructed instance due to CPU out-of-order execution. |
| **Composition over Inheritance**| HAS-A vs IS-A | Prefer composition for loose coupling and runtime flexibility. |
""",
    "checkpoints": [
        {
            "q": "Why is declaring the Singleton instance variable as 'volatile' strictly required in Java's Double-Checked Locking pattern?",
            "a": "Without 'volatile', the compiler or CPU instruction pipeline may reorder the memory allocation, constructor execution, and pointer assignment. As a result, a concurrent thread could read a non-null instance reference before the constructor finishes executing, accessing a partially initialized, corrupted object."
        },
        {
            "q": "A developer creates 'ReadOnlyAccount' which inherits from 'Account'. When 'deposit()' is called on ReadOnlyAccount, it throws an UnsupportedOperationException. Which SOLID principle is violated and why?",
            "a": "It violates the Liskov Substitution Principle (LSP). Code written to interact with 'Account' expects 'deposit()' to successfully increase the balance. Substituting 'ReadOnlyAccount' breaks client assumptions and program correctness."
        },
        {
            "q": "Can a static method in Java be overridden by a subclass? Explain the exact mechanism.",
            "a": "No, static methods cannot be overridden. If a subclass declares a static method with the exact same signature, it is 'Method Hiding', not overriding. The JVM binds static method calls at compile time based on the reference type, completely bypassing the virtual method table (vtable)."
        }
    ],
    "quiz": [
        {
            "id": 233,
            "q": "Which of the following method declarations will successfully overload the method 'public double computeTax(int amount)' in Java?",
            "options": [
                "public int computeTax(int amount)",
                "public double computeTax(int total, double rate)",
                "private double computeTax(int amount)",
                "public static double computeTax(int amount)"
            ],
            "answer": 1,
            "explanation": "Method overloading requires changing the parameter list (number, types, or order of parameters). Changing only the return type, access modifier, or static keyword does NOT constitute valid method overloading and causes a compile error."
        },
        {
            "id": 234,
            "q": "In the Double-Checked Locking implementation of the Singleton pattern in Java, what critical hazard does the 'volatile' keyword prevent?",
            "options": [
                "It prevents multiple class loaders from loading the class.",
                "It prevents instruction reordering that could expose a partially initialized object reference to another thread.",
                "It automatically synchronizes every read and write method in the entire class.",
                "It forces the object to reside in Metaspace instead of the Young Generation heap."
            ],
            "answer": 1,
            "explanation": "Creating an object involves memory allocation, constructor invocation, and reference assignment. Without 'volatile', JVM/CPU instruction reordering can assign the memory address to the reference variable before constructor execution finishes, causing other threads to access an incompletely initialized object."
        },
        {
            "id": 235,
            "q": "A class has multiple responsibilities including database persistence, business calculation, and generating HTML user notifications. Which SOLID principle does this violate?",
            "options": [
                "Single Responsibility Principle (SRP)",
                "Open/Closed Principle (OCP)",
                "Interface Segregation Principle (ISP)",
                "Dependency Inversion Principle (DIP)"
            ],
            "answer": 0,
            "explanation": "The Single Responsibility Principle (SRP) states that a class should have one, and only one, reason to change. Combining persistence, calculation, and UI presentation violates SRP."
        },
        {
            "id": 236,
            "q": "Which design pattern is best suited for defining a family of interchangeable routing algorithms (e.g., fastest route, cheapest route, shortest route) and swapping them dynamically at runtime?",
            "options": [
                "Decorator Pattern",
                "Strategy Pattern",
                "Observer Pattern",
                "Builder Pattern"
            ],
            "answer": 1,
            "explanation": "The Strategy Pattern defines a family of algorithms, encapsulates each one in a separate class implementing a common interface, and makes them interchangeable at runtime based on context or user preference."
        },
        {
            "id": 237,
            "q": "What happens when an object of a child class is assigned to a parent class reference variable and a method overridden by the child is invoked?",
            "options": [
                "The parent class method executes because the reference type is Parent.",
                "The child class method executes because runtime dynamic dispatch resolves the call via the object's vtable.",
                "A ClassCastException is thrown at runtime.",
                "The compiler produces an ambiguous invocation error."
            ],
            "answer": 1,
            "explanation": "In Java/C++, overridden non-static methods are resolved at runtime via dynamic dispatch (using the virtual method table). Even if the reference is of type Parent, the actual method executed is the Child's implementation."
        }
    ]
}

print("Chapter 11 definition complete.")

# ==============================================================
# CHAPTER 12: Java Backend Core, JVM & Collections Framework
# ==============================================================
ENRICHED_CHAPTERS["ch-12"] = {
    "summary": "Deep dive into JVM Architecture (ClassLoader, Runtime Data Areas, Metaspace vs PermGen, Execution Engine, JIT Compiler), Generational Garbage Collection (Eden, Survivor, Old/Tenured, G1, ZGC), Collections Framework internals (HashMap collision resolution, load factors, ConcurrentHashMap), and concurrency primitives (volatile, synchronized, ReentrantLock, ThreadPools).",
    "reading_time_mins": 35,
    "lecture_notes": """# Java Backend Core, JVM Memory Architecture, Garbage Collection & Collections

## 1. JVM Architecture & Runtime Data Areas
The Java Virtual Machine (JVM) provides cross-platform byte-code execution. It manages memory automatically and compiles hot code paths via the Just-In-Time (JIT) compiler.

```
+-------------------------------------------------------------------------+
|                         JVM RUNTIME DATA AREAS                          |
+------------------------------------+------------------------------------+
|            SHARED BY ALL THREADS   |          PER-THREAD PRIVATE        |
|                                    |                                    |
| +--------------------------------+ | +--------------------------------+ |
| |           HEAP MEMORY          | | |           JVM STACK            | |
| |  [Eden] -> [S0 / S1] -> [Old]  | | | (Stack frames, local vars)     | |
| +--------------------------------+ | +--------------------------------+ |
|                                    |                                    |
| +--------------------------------+ | +--------------------------------+ |
| |           METASPACE            | | |       PROGRAM COUNTER (PC)     | |
| | (Class metadata, method byte-  | | | (Current bytecode address)     | |
| |  codes, native memory allocated)| | +--------------------------------+ |
| +--------------------------------+ |                                    |
|                                    | +--------------------------------+ |
| +--------------------------------+ | |       NATIVE METHOD STACK      | |
| |     STRING / RUNTIME CONSTANT  | | | (C/C++ JNI calls)              | |
| |               POOL             | | +--------------------------------+ |
| +--------------------------------+ |                                    |
+------------------------------------+------------------------------------+
|          EXECUTION ENGINE: JIT Compiler (C1/C2) + Garbage Collector     |
+-------------------------------------------------------------------------+
```

### 1.1 Detailed Memory Regions
1. **JVM Heap:**
   * Allocated when the JVM launches. Shared across all concurrent threads.
   * Holds all **Object instances** and array buffers.
   * Subject to automated Garbage Collection (GC).
2. **JVM Stack (Thread-Private):**
   * Created alongside every Java thread.
   * Contains a frame for every active method call: Local Variable Array, Operand Stack, Frame Data.
   * Exceeding stack depth results in `java.lang.StackOverflowError`.
3. **Metaspace (Java 8+ replacing PermGen):**
   * Stores Class definitions, Method metadata, Field structures, and static variables.
   * Allocated out of **Native OS Memory**, avoiding the fixed-limit `java.lang.OutOfMemoryError: PermGen space` of Java 7.
4. **Program Counter (PC) Register:**
   * Tracks the execution address of the JVM bytecode currently being processed by that thread.

---

## 2. Generational Garbage Collection Mechanics
Garbage Collection operates under the **Weak Generational Hypothesis**: *Most allocated objects die very shortly after creation.*

```
+-------------------------------------------------------------------+
|                        JVM HEAP LAYOUT                            |
+------------------------------------+------------------------------+
|        YOUNG GENERATION            |       OLD / TENURED GEN      |
|  (Minor GC - Stop-The-World brief) |  (Major / Full GC - Heavier) |
|                                    |                              |
| +---------+  +----+  +----+        | +--------------------------+ |
| |  Eden   |  | S0 |  | S1 | =====> | |      Tenured Space       | |
| |  (80%)  |  |From|  | To | (Age   | |    (Long-lived objects)  | |
| +---------+  +----+  +----+  > 15) | +--------------------------+ |
+------------------------------------+------------------------------+
```

### 2.1 Object Lifecycle & Minor GC
1. New objects are allocated in the **Eden** space.
2. When Eden fills, a **Minor GC** triggers:
   * Live (reachable) objects are copied to the active **Survivor space** (`To` / `S0`). Dead objects are discarded.
   * Each surviving object has its **Tenuring Age** incremented by 1.
   * On subsequent Minor GCs, live objects ping-pong between `S0` and `S1`.
3. **Tenuring Threshold:** Once an object survives enough GC cycles (default `-XX:MaxTenuringThreshold=15`), it is promoted to the **Old (Tenured) Generation**.
4. **Major / Full GC:** Triggered when the Old Generation fills, cleaning Old and Young spaces.

### 2.2 Modern Garbage Collectors
* **Serial GC (`-XX:+UseSerialGC`):** Single-threaded; suitable for CLI scripts or micro-containers.
* **Parallel GC (`-XX:+UseParallelGC`):** Multi-threaded throughput collector. Minimizes CPU time spent on GC, ideal for non-interactive batch calculations.
* **G1 GC (Garbage-First - Default in Java 9+):** Splits the heap into hundreds of equal-sized non-contiguous regions. Tracks region garbage density and cleans regions with the highest garbage first within a target pause time (`-XX:MaxGCPauseMillis`).
* **ZGC (Z Garbage Collector):** Ultra-low pause time collector (pauses under 1ms), performs concurrent object relocation without stopping application threads.

---

## 3. Java Collections Framework: Deep Implementation Mechanics

```
                        Collection (Interface)
                         /        |         \
                    List         Set        Queue
                   /    \         |            |
         ArrayList   LinkedList HashSet    PriorityQueue
                                  |
                               TreeSet
                      Map (Independent Interface)
                     /      |             \
              HashMap   TreeMap     ConcurrentHashMap
```

### 3.1 `HashMap` Internal Mechanics (Java 8+)
A `HashMap` stores key-value pairs using a hash table backed by an array of `Node<K,V>[] table`.
* **Hash Calculation:** The key's 32-bit hash code is spread using XOR shifting to reduce collisions: `(h = key.hashCode()) ^ (h >>> 16)`.
* **Index Mapping:** Determined via bitwise AND with array capacity: `index = (n - 1) & hash`.
* **Bucket Structure:**
  * By default, each bucket is a Singly Linked List.
  * **Treeify Threshold (8):** If collisions cause a bucket list length to exceed 8 and table capacity is $\ge 64$, the bucket is converted to a balanced **Red-Black Tree**, reducing search complexity from $O(n)$ to $O(\log n)$.
  * **Untreeify Threshold (6):** If bucket size shrinks to 6 during resizing, it converts back to a linked list.
* **Load Factor (0.75):** When `size > capacity * 0.75`, the table doubles in capacity (`n * 2`), rehashing nodes.

### 3.2 Thread-Safe Collections: `Hashtable` vs `Collections.synchronizedMap` vs `ConcurrentHashMap`
* `Hashtable`: Every method is `synchronized` at the entire table level. Massive lock contention under high concurrency. Obsolete.
* `ConcurrentHashMap` (Java 8+): Employs **Lock Striping** via CAS (Compare-And-Swap) for empty bucket insertions and `synchronized` locks only on the head node of the specific colliding bucket. Reads require zero locks. Provides extraordinary concurrent throughput.

---

## 4. Java Multithreading & Memory Visibility
* **`volatile`:** Guarantees that changes made by one thread are immediately visible to all other threads by bypassing CPU L1/L2 caches and reading/writing directly to main memory. *Does NOT guarantee atomicity for compound operations like `count++`.*
* **`synchronized`:** Provides mutual exclusion and memory visibility via intrinsic monitor locks.
* **`AtomicInteger` / `AtomicLong`:** Leverages CPU hardware-level **Compare-And-Swap (CAS)** instructions without thread blocking.
* **`ReentrantLock`:** Offers fairness policies, timed lock acquisition (`tryLock()`), and interruptible locking.
* **`ExecutorService` & Thread Pools:**
  * `corePoolSize`, `maximumPoolSize`, `workQueue`, `RejectedExecutionHandler`.
  * Avoid `Executors.newFixedThreadPool()` in production banking systems because it uses an unbounded `LinkedBlockingQueue`, risking `OutOfMemoryError` under high traffic bursts.

---

## 5. High-Yield Summary Matrix for Banking IT Exams

| Component | Default Values / Mechanism | Examiner Distractor / Trap |
| :--- | :--- | :--- |
| **Metaspace** | Uses Native Host Memory | Does NOT throw PermGen OutOfMemoryError. Replaced in Java 8. |
| **Max Tenuring Threshold**| 15 cycles (`-XX:MaxTenuringThreshold=15`) | Stored in 4-bit object header mark word (maximum possible value is 15). |
| **HashMap Collision** | Linked list to Red-Black Tree at 8 items | Table capacity must also be $\ge 64$; otherwise, table simply doubles capacity. |
| **ConcurrentHashMap**| Bucket-level locking + CAS | Does NOT lock the entire map. Does NOT permit `null` keys or `null` values. |
| **volatile** | Cache coherence (happens-before ordering)| Does NOT make `count++` thread-safe. Use `AtomicInteger` for atomicity. |
""",
    "checkpoints": [
        {
            "q": "Why does ConcurrentHashMap explicitly forbid 'null' keys and 'null' values, whereas standard HashMap allows them?",
            "a": "In a concurrent environment, if map.get(key) returns null, you cannot distinguish whether the key was mapped to null or the key was not present in the map. In single-threaded HashMap, you can call containsKey(key) to disambiguate. In ConcurrentHashMap, the map could be modified between get() and containsKey(), creating a race condition."
        },
        {
            "q": "Why is the expression 'count++' NOT thread-safe even if 'count' is declared as a private volatile integer?",
            "a": "'count++' is not a single atomic operation; it consists of three distinct bytecode steps: (1) read count from memory, (2) add 1 to the value, (3) write the new value back. While volatile guarantees visibility of each step, two concurrent threads can read the same value simultaneously, resulting in a lost update. Thread safety requires AtomicInteger.incrementAndGet() or a synchronized block."
        },
        {
            "q": "What happens when an object in Eden survives its 15th Minor Garbage Collection cycle?",
            "a": "The JVM promotes the object from the Survivor space into the Old (Tenured) Generation. The tenuring age is tracked in the 4-bit age field within the object's Mark Word header (which has a mathematical upper bound of 1111 binary = 15)."
        }
    ],
    "quiz": [
        {
            "id": 238,
            "q": "In Java 8 and later, at what bucket collision threshold does a HashMap bucket list convert into a balanced Red-Black Tree?",
            "options": [
                "When bucket elements reach 4, regardless of table capacity.",
                "When bucket elements reach 8, provided the total table capacity is at least 64.",
                "When bucket elements reach 16, regardless of capacity.",
                "When the load factor exceeds 0.75."
            ],
            "answer": 1,
            "explanation": "In Java 8+, TREEIFY_THRESHOLD is 8. If a bucket's chain length reaches 8 and the table capacity is at least MIN_TREEIFY_CAPACITY (64), the linked list transforms into a Red-Black tree. If the table capacity is under 64, it resizes the table instead of treeifying."
        },
        {
            "id": 239,
            "q": "Where is class metadata, method byte-code, and the runtime constant pool stored in Java 8 and newer versions?",
            "options": [
                "Permanent Generation (PermGen) on JVM Heap",
                "Young Generation (Eden Space)",
                "Metaspace allocated out of Native OS Memory",
                "JVM Thread Private Stack Frame"
            ],
            "answer": 2,
            "explanation": "Starting in Java 8, PermGen was completely removed and replaced by Metaspace, which is allocated out of native OS memory. This prevents PermGen OutOfMemoryError issues caused by dynamic class loading."
        },
        {
            "id": 240,
            "q": "Which Java Garbage Collector partitions the heap into equal-sized independent regions and prioritizes collecting regions with the largest amount of reclaimable space?",
            "options": [
                "Serial Garbage Collector",
                "Parallel Scavenge Collector",
                "Garbage-First (G1) Collector",
                "Concurrent Mark Sweep (CMS) Collector"
            ],
            "answer": 2,
            "explanation": "The G1 (Garbage-First) collector partitions the heap into hundreds of discrete regions and selects the regions with the most garbage ('garbage-first') to reclaim within a configurable pause time target."
        },
        {
            "id": 241,
            "q": "Why does using 'Executors.newFixedThreadPool(50)' present an OutOfMemoryError risk in high-throughput enterprise systems?",
            "options": [
                "It allocates 50 native OS threads immediately upon startup.",
                "It uses an unbounded LinkedBlockingQueue (capacity Integer.MAX_VALUE), which can grow indefinitely and exhaust heap under request spikes.",
                "It forces all tasks to execute synchronously on the main thread.",
                "It disables Garbage Collection for all submitted Runnable objects."
            ],
            "answer": 1,
            "explanation": "newFixedThreadPool uses an unbounded LinkedBlockingQueue by default. If incoming requests arrive faster than 50 threads can process them, queued tasks accumulate without limit, eventually causing OutOfMemoryError."
        },
        {
            "id": 242,
            "q": "What is the key functional difference between Comparable and Comparator interfaces in Java?",
            "options": [
                "Comparable provides natural ordering via compareTo(T o) within the domain class; Comparator provides customized external ordering via compare(T o1, T o2).",
                "Comparable is used only for primitive data types; Comparator is for objects.",
                "Comparable cannot be used with TreeSet; Comparator is mandatory for all Sets.",
                "Comparable supports multiple sorting strategies in separate classes; Comparator allows only one."
            ],
            "answer": 0,
            "explanation": "Comparable defines natural ordering implemented by the class itself (implementing compareTo(T o)). Comparator defines custom external ordering strategies implemented in independent classes (implementing compare(T o1, T o2))."
        }
    ]
}

# ==============================================================
# CHAPTER 13: Data Structures & Algorithms
# ==============================================================
ENRICHED_CHAPTERS["ch-13"] = {
    "summary": "Comprehensive coverage of Trees (BST, AVL balancing rotations, B/B+ Trees in DB engines), Heaps & Priority Queues, Graph Algorithms (BFS, DFS, Dijkstra, Bellman-Ford, Prim, Kruskal, Topological Sort), and Asymptotic Big-O Complexity Analysis.",
    "reading_time_mins": 35,
    "lecture_notes": """# Data Structures & Algorithms: Trees, Heaps, Graph Algorithms & Big-O

## 1. Asymptotic Notation & Complexity Analysis
Algorithm efficiency is measured against input size $n$ as $n \to \infty$:
* **Big-O ($O$):** Asymptotic Upper Bound ($f(n) \le c \cdot g(n)$). Worst-case execution guarantee.
* **Big-Omega ($\Omega$):** Asymptotic Lower Bound ($f(n) \ge c \cdot g(n)$). Best-case execution guarantee.
* **Big-Theta ($\Theta$):** Asymptotic Tight Bound ($c_1 \cdot g(n) \le f(n) \le c_2 \cdot g(n)$). Average and exact growth rate.

### Master Theorem for Divide-and-Conquer Recurrences
For recurrences of form: $T(n) = a T(n/b) + f(n)$, where $a \ge 1, b > 1$:
Let $c_{crit} = \log_b a$:
1. If $f(n) = O(n^c)$ where $c < c_{crit}$, then $T(n) = \Theta(n^{\log_b a})$.
2. If $f(n) = \Theta(n^{c_{crit}} \log^k n)$, then $T(n) = \Theta(n^{\log_b a} \log^{k+1} n)$.
   * *Example (MergeSort):* $T(n) = 2T(n/2) + \Theta(n) \implies a=2, b=2 \implies c_{crit} = \log_2 2 = 1$. Since $f(n) = \Theta(n^1)$, $T(n) = \Theta(n \log n)$.
3. If $f(n) = \Omega(n^c)$ where $c > c_{crit}$ and regularity holds, then $T(n) = \Theta(f(n))$.

---

## 2. Advanced Tree Data Structures

### 2.1 Binary Search Trees (BST) & Degeneracy
* **Property:** For any node $X$, all keys in the left subtree $< X.key <$ all keys in right subtree.
* **Degeneracy:** If elements are inserted in sorted order ($1, 2, 3, 4, 5$), the BST degenerates into a singly linked list with $O(n)$ search, insertion, and deletion.

### 2.2 AVL Trees (Self-Balancing BST)
* **Balance Factor ($BF$):** $BF(node) = \text{Height}(Left) - \text{Height}(Right) \in \{-1, 0, +1\}$.
* When an insertion causes $BF \notin \{-1, 0, +1\}$, one of 4 rotations restores balance in $O(1)$ time:
  1. **LL Rotation (Single Right):** Inserted into left subtree of left child.
  2. **RR Rotation (Single Left):** Inserted into right subtree of right child.
  3. **LR Rotation (Double: Left then Right):** Inserted into right subtree of left child.
  4. **RL Rotation (Double: Right then Left):** Inserted into left subtree of right child.
* Guaranteed search/insert/delete: $O(\log n)$.

```
   LL Imbalance:                Balanced via Right Rotation:
        30 (BF=+2)                         20
       /                                  /  \
     20 (BF=+1)        =========>       10    30
    /
  10
```

### 2.3 B-Trees and B+ Trees in Banking Database Engines
* Relational database indexes (like PostgreSQL and Oracle) do NOT use AVL or Red-Black trees because node pointer chasing causes excessive random disk I/O.
* **B+ Tree Properties:**
  * Massive branching factor (fan-out of 100+ to 1000+), keeping tree height low ($h \le 3$ even for millions of records).
  * **Internal Nodes** store only routing keys and page pointers (no record payloads).
  * **Leaf Nodes** store all actual data pointers/payloads, linked sequentially in a Doubly Linked List for blazing-fast range scans (`WHERE amount BETWEEN 1000 AND 5000`).

---

## 3. Heaps, Priority Queues & HeapSort
A **Binary Heap** is a complete binary tree represented compactly as a flat array without pointer overhead.
* For a node at zero-based array index $i$:
  * Left child: $2i + 1$
  * Right child: $2i + 2$
  * Parent node: $\lfloor (i - 1) / 2 \rfloor$
* **Max-Heap:** Parent key $\ge$ children keys (root is maximum).
* **Min-Heap:** Parent key $\le$ children keys (root is minimum).
* **`Heapify` Operation:** $O(\log n)$.
* **Building a Heap (`BuildHeap`):** Bottom-up heapify runs in mathematical $O(n)$ time (not $O(n \log n)$).
* **HeapSort:** In-place sorting with $O(n \log n)$ guarantee in all cases (best, worst, average). Unstable sort.

---

## 4. Graph Algorithms & Shortest Path Protocols

```
+------------------------------------------------------------------------+
|                      GRAPH ALGORITHM TAXONOMY                          |
+--------------------------+-----------------------+---------------------+
| Traversal / Connectivity | Shortest Path         | Minimum Spanning Tr.|
| - BFS: O(V + E) Queue    | - Dijkstra: Non-neg   | - Kruskal: O(E log E|
| - DFS: O(V + E) Stack    | - Bellman-Ford: Neg wt|   (Disjoint Set/UF) |
| - Topological Sort: DAG  | - Floyd-Warshall: All | - Prim: O(E + V logV|
+--------------------------+-----------------------+---------------------+
```

### 4.1 Breadth-First Search (BFS) vs Depth-First Search (DFS)
* **BFS:** Uses a FIFO Queue. Finds shortest unweighted path between source and destinations. Level-by-level traversal. Time: $O(V + E)$, Space: $O(V)$.
* **DFS:** Uses a LIFO Stack (or recursion). Traverses deeply before backtracking. Detects cycles, topological sorting, and strongly connected components (Kosaraju / Tarjan). Time: $O(V + E)$, Space: $O(V)$.

### 4.2 Topological Sorting (Kahn's Algorithm & DFS)
* Applicable **ONLY** to Directed Acyclic Graphs (DAG).
* Produces a linear ordering where for every directed edge $u \to v$, vertex $u$ precedes $v$.
* **Kahn's Algorithm (BFS-based):**
  1. Compute in-degree of all vertices.
  2. Enqueue all vertices with in-degree 0.
  3. While queue is non-empty, dequeue vertex $u$, add to topological list, and decrement in-degree of all neighbors $v$. If in-degree of $v$ becomes 0, enqueue $v$.
  4. If processed count $< V$, graph contains a **cycle**.

### 4.3 Shortest Path Algorithms
1. **Dijkstra's Algorithm:**
   * Greedy algorithm. Finds shortest path from single source to all vertices on **non-negative edge weights**.
   * Time complexity with Min-Heap / PriorityQueue: $O((V + E) \log V)$.
   * *Critical Examiner Trap:* Dijkstra FAILS on graphs with negative edge weights or negative cycles!
2. **Bellman-Ford Algorithm:**
   * Dynamic programming approach. Handles negative edge weights.
   * Relaxes all $E$ edges $V - 1$ times.
   * Runs a $V$-th pass: if any edge can still be relaxed, a **Negative Weight Cycle** exists!
   * Time complexity: $O(V \cdot E)$.
3. **Floyd-Warshall Algorithm:**
   * All-pairs shortest path dynamic programming: $D^k[i, j] = \min(D^{k-1}[i, j], D^{k-1}[i, k] + D^{k-1}[k, j])$.
   * Time complexity: $O(V^3)$.

### 4.4 Minimum Spanning Tree (MST)
Spans all $V$ vertices with exactly $V - 1$ edges minimizing total edge cost.
* **Kruskal's Algorithm:** Edge-centric. Sorts edges by weight, adds greedily using **Disjoint Set Union (Union-Find)** with path compression to prevent cycles. Complexity: $O(E \log E)$.
* **Prim's Algorithm:** Vertex-centric. Grows a tree from a start vertex, greedily adding lowest-weight cut edges via PriorityQueue. Complexity: $O(E \log V)$.

---

## 5. Comprehensive Big-O Reference Matrix

| Algorithm / Data Structure | Best Case | Average Case | Worst Case | Worst Space | Stable? |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **QuickSort** | $O(n \log n)$ | $O(n \log n)$ | $O(n^2)$ (sorted pivot) | $O(\log n)$ | No |
| **MergeSort** | $O(n \log n)$ | $O(n \log n)$ | $O(n \log n)$ | $O(n)$ | Yes |
| **HeapSort** | $O(n \log n)$ | $O(n \log n)$ | $O(n \log n)$ | $O(1)$ | No |
| **AVL Tree Search** | $O(1)$ | $O(\log n)$ | $O(\log n)$ | $O(n)$ | - |
| **Unbalanced BST Search**| $O(1)$ | $O(\log n)$ | $O(n)$ | $O(n)$ | - |
| **Hash Table Lookup** | $O(1)$ | $O(1)$ | $O(n)$ | $O(n)$ | - |
""",
    "checkpoints": [
        {
            "q": "Why does Dijkstra's algorithm fail to produce correct shortest paths on graphs containing negative edge weights?",
            "a": "Dijkstra is a greedy algorithm based on the assumption that once a node is extracted from the Priority Queue with the minimum tentative distance, its shortest path has been permanently finalized. A negative weight edge encountered later can retroactively reduce the distance to an already-visited node, violating the greedy invariant."
        },
        {
            "q": "Why do relational database storage engines use B+ Trees instead of AVL or Red-Black Trees for indexing on disks?",
            "a": "Binary search trees have a branching factor of 2, creating deep trees (height 20+ for 1M records) requiring 20+ random disk seeks. B+ Trees have large fan-outs (100-1000+), reducing tree height to 3-4 levels. Furthermore, B+ Tree leaf nodes form a sequential doubly-linked list, allowing high-speed range queries with contiguous block reads."
        },
        {
            "q": "How does Kahn's algorithm detect whether a directed graph contains a cycle during Topological Sorting?",
            "a": "Kahn's algorithm only enqueues vertices whose in-degree reaches zero. If the graph contains a directed cycle, vertices within the cycle will never have their in-degrees reduced to zero. Thus, when the queue empties, if the count of visited vertices is less than |V|, a cycle is conclusively detected."
        }
    ],
    "quiz": [
        {
            "id": 243,
            "q": "What is the tight worst-case time complexity of the HeapSort algorithm for an array of n elements?",
            "options": [
                "O(n)",
                "O(n log n)",
                "O(n^2)",
                "O(log n)"
            ],
            "answer": 1,
            "explanation": "HeapSort builds a heap in O(n) time and then performs n-1 extract-max operations, each taking O(log n) time. Its time complexity is strictly O(n log n) across all cases (best, average, worst)."
        },
        {
            "id": 244,
            "q": "Which of the following shortest-path algorithms is capable of detecting negative-weight cycles in a directed graph?",
            "options": [
                "Dijkstra's Algorithm",
                "Prim's Algorithm",
                "Bellman-Ford Algorithm",
                "Kruskal's Algorithm"
            ],
            "answer": 2,
            "explanation": "Bellman-Ford relaxes all edges V-1 times. If any edge can still be relaxed on a V-th iteration, a negative-weight cycle is present and reported."
        },
        {
            "id": 245,
            "q": "What is the balance factor of an AVL tree node, and what rotation is applied when a node has a balance factor of +2 and its left child has a balance factor of -1?",
            "options": [
                "Balance factor is Height(Left) - Height(Right); requires an LR (Left-Right) Double Rotation.",
                "Balance factor is Degree(Left) - Degree(Right); requires an LL Single Right Rotation.",
                "Balance factor is Key(Left) - Key(Right); requires an RR Single Left Rotation.",
                "Balance factor is Depth(Node); requires an RL Double Rotation."
            ],
            "answer": 0,
            "explanation": "Balance Factor = Height(Left) - Height(Right). When BF is +2 (left-heavy) and the left child's BF is -1 (right-heavy), it represents an LR imbalance requiring an LR double rotation (left rotation on child, followed by right rotation on parent)."
        },
        {
            "id": 246,
            "q": "What data structure does Kruskal's algorithm utilize to achieve an efficient edge cycle check in O(alpha(V)) time?",
            "options": [
                "Fibonacci Heap",
                "Disjoint Set Union (Union-Find) with path compression",
                "Adjacency Matrix",
                "Segment Tree"
            ],
            "answer": 1,
            "explanation": "Kruskal's algorithm uses a Disjoint Set Union (DSU / Union-Find) data structure with union-by-rank and path compression, enabling near-constant O(alpha(V)) cycle detection per edge."
        },
        {
            "id": 247,
            "q": "Which traversal of a Binary Search Tree (BST) visits nodes in strictly ascending numerical key order?",
            "options": [
                "Pre-order Traversal (Root, Left, Right)",
                "In-order Traversal (Left, Root, Right)",
                "Post-order Traversal (Left, Right, Root)",
                "Level-order Traversal (Breadth-First)"
            ],
            "answer": 1,
            "explanation": "By definition of a BST, all keys in the left subtree are smaller than the root, and all keys in the right subtree are greater. An In-order traversal (Left, Root, Right) produces sorted ascending order."
        }
    ]
}

# ==============================================================
# CHAPTER 14: Software Engineering Lifecycles & Testing QA
# ==============================================================
ENRICHED_CHAPTERS["ch-14"] = {
    "summary": "Exhaustive coverage of SDLC models (Waterfall, V-Model, Spiral, Agile/Scrum ceremonies, Burndown charts), Testing paradigms (Unit, Integration, System, Regression, Smoke vs Sanity), Black-box vs White-box techniques (BVA, Equivalence Partitioning), Cyclomatic Complexity calculations, and CI/CD pipelines.",
    "reading_time_mins": 30,
    "lecture_notes": """# Software Engineering Lifecycles (SDLC), Agile Scrum & Software Testing QA

## 1. Software Development Life Cycle (SDLC) Models
SDLC defines the structured phased workflow for designing, developing, testing, and maintaining mission-critical enterprise software.

```
+-------------------------------------------------------------------------+
|                              SDLC MODELS                                |
+------------------------+-----------------------+------------------------+
| 1. Waterfall           | 2. V-Model            | 3. Spiral Model        |
| - Linear, sequential   | - Verification &      | - Risk-driven,         |
| - Requirements frozen  |   Validation coupled  |   iterative prototyping|
+------------------------+-----------------------+------------------------+
| 4. Agile / Scrum Framework                                              |
| - Cross-functional squads, 2-4 week sprints, rapid iterative feedback  |
+-------------------------------------------------------------------------+
```

### 1.1 Waterfall vs V-Model vs Spiral
* **Waterfall Model:** Linear sequential phases (Requirements $\to$ Design $\to$ Implementation $\to$ Verification $\to$ Maintenance). Inflexible; changes are costly once a phase completes.
* **V-Model (Verification & Validation):** Emphasizes that test planning begins concurrently with design phases:
  * Requirements Analysis $\iff$ User Acceptance Testing (UAT)
  * System Architecture $\iff$ System Testing
  * High-Level Design $\iff$ Integration Testing
  * Low-Level Unit Design $\iff$ Unit Testing
* **Boehm's Spiral Model:** Risk-driven model combining Waterfall discipline with iterative prototyping. Each loop involves 4 quadrants:
  1. Determine objectives and constraints.
  2. Identify and resolve risks (via prototyping and simulations).
  3. Develop and verify next-level product.
  4. Plan next iteration.

### 1.2 Agile & Scrum Methodology
Scrum divides development into time-boxed iterations (usually 2–4 weeks) called **Sprints**.
* **Key Scrum Roles:**
  * **Product Owner (PO):** Owns the Product Backlog, prioritizes user stories by business value.
  * **Scrum Master:** Servant-leader, removes operational impediments, coaches the team on Scrum values.
  * **Development Squad:** Self-organizing, cross-functional team delivering potentially shippable increments.
* **Scrum Ceremonies:**
  1. **Sprint Planning:** Select stories from backlog and establish the Sprint Goal.
  2. **Daily Standup (15 mins):** What did I do yesterday? What will I do today? Any blockers?
  3. **Sprint Review / Demo:** Showcase working software to stakeholders.
  4. **Sprint Retrospective:** Continuous process improvement (What went well? What can be improved?).
* **Scrum Artifacts:**
  * **Product Backlog:** Prioritized list of all features and requirements.
  * **Sprint Backlog:** User stories committed for the current sprint.
  * **Sprint Burndown Chart:** Tracks remaining work (story points) over time. Downward slope toward zero indicates healthy sprint velocity.

---

## 2. Software Testing Paradigms & Quality Assurance
Software testing verifies that a system meets specified requirements and identifies defects before production deployment.

```
                  Testing Pyramid
                      /     \
                     /  E2E  \       (Slow, Expensive, Few)
                    /---------\
                   /Integration\     (API & Database interactions)
                  /-------------\
                 /  Unit Tests   \   (Fast, Isolated, Thousands)
                +-----------------+
```

### 2.1 Testing Levels
1. **Unit Testing:** Tests individual components, classes, or methods in isolation. Dependencies are replaced with **Mocks** and **Stubs** (e.g., JUnit, Mockito).
2. **Integration Testing:** Verifies communication and data flow between interacting modules (e.g., Spring Controller calling Database via Hibernate repository).
3. **System Testing:** Validates end-to-end integrated application against functional and non-functional specifications.
4. **Acceptance Testing (UAT):** Conducted by business users or regulators to confirm system meets contractual and regulatory needs.

### 2.2 Smoke Testing vs Sanity Testing vs Regression Testing
* **Smoke Testing ("Build Verification Test"):** Broad and shallow test run on initial build to ensure critical core functions work before deeper testing begins (e.g., can the banking portal boot up and authenticate?).
* **Sanity Testing:** Narrow and deep test executed after a bug fix to verify that the specific defect is corrected without breaking immediately adjacent functions.
* **Regression Testing:** Re-running existing test suites after code modifications to guarantee that new changes have not introduced unintended defects into pre-existing functionality.

---

## 3. Black-Box vs White-Box Test Design Techniques

### 3.1 Black-Box Testing (Specification-Based)
Tests functionality without viewing source code:
* **Equivalence Class Partitioning (ECP):** Divides input domain into valid and invalid partitions. Selecting one representative value per partition tests the entire class.
* **Boundary Value Analysis (BVA):** Testing shows that the highest defect density occurs at the boundary edges of input ranges.
  * *Example:* If allowed transfer amount is \$100 to \$10,000, test boundary values: \$99 (just below), \$100 (min boundary), \$101 (just above), \$9,999 (just below), \$10,000 (max boundary), \$10,001 (just above).

### 3.2 White-Box Testing (Structural)
Inspects internal program logic, loops, and control flow graphs:
* **Statement Coverage:** Percentage of executable source code statements executed by tests.
* **Branch / Decision Coverage:** Ensures every branch (True and False outcomes of every `if`/`switch`) has been traversed.
* **McCabe's Cyclomatic Complexity ($V(G)$):**
  Measures the number of linearly independent paths through a program's source code, indicating testing difficulty and minimum test cases required for complete branch coverage:
  $$V(G) = E - N + 2P$$
  * Where $E$ = Number of edges in the Control Flow Graph.
  * $N$ = Number of nodes in the Control Flow Graph.
  * $P$ = Number of connected components (typically $P = 1$ for a single program).
  * *Alternative Rule:* $V(G) = \text{Predicate (Decision) Nodes} + 1$.

---

## 4. Continuous Integration & Continuous Delivery (CI/CD)
* **Continuous Integration (CI):** Developers merge code into central branch frequently. Automated builds run unit tests and static code analysis (SonarQube) on every commit.
* **Continuous Delivery (CD):** Automated pipeline tests and prepares releasable artifacts for one-click manual production deployment.
* **Continuous Deployment:** Every change passing automated gates deploys straight to production without human intervention.

---

## 5. High-Yield Summary Matrix for Banking IT Exams

| Concept | Key Equation / Property | Exam Distinction / Trap |
| :--- | :--- | :--- |
| **Cyclomatic Complexity** | $V(G) = E - N + 2$ or $P_{decisions} + 1$ | Equals minimum test cases needed for 100% basis path coverage. |
| **Boundary Value Analysis** | Tests $\{min-1, min, min+1, max-1, max, max+1\}$ | Detects off-by-one errors ($<$ vs $\le$). |
| **Smoke vs Sanity** | Smoke = Broad & Shallow; Sanity = Narrow & Deep | Smoke tests whole build stability; Sanity verifies specific patch fix. |
| **Spiral Model** | Key feature: Risk Management & Analysis | Selected for high-budget, high-risk systems with shifting requirements. |
| **Verification vs Validation**| Verification = "Are we building the product right?" | Validation = "Are we building the right product?" (Meets customer intent). |
""",
    "checkpoints": [
        {
            "q": "A banking loan calculation function contains 4 'if' decision statements and no loops. What is its Cyclomatic Complexity, and what does this number represent?",
            "a": "Using the Predicate Nodes rule: V(G) = Predicate Nodes + 1 = 4 + 1 = 5. This signifies that there are 5 linearly independent execution paths through the function, requiring a minimum of 5 distinct test cases to achieve 100% branch/basis path coverage."
        },
        {
            "q": "What is the fundamental difference between Verification and Validation in software quality engineering?",
            "a": "Verification evaluates intermediate work products against specifications ('Are we building the product right?' - includes code reviews, static analysis, unit inspections). Validation evaluates the completed software to ensure it satisfies user needs and business requirements ('Are we building the right product?' - includes acceptance testing and UAT)."
        },
        {
            "q": "Why is the Spiral Model uniquely chosen over Waterfall for high-risk, multi-million dollar regulatory banking implementations?",
            "a": "The Spiral Model explicitly incorporates risk analysis and risk mitigation in every single loop cycle through iterative prototyping, cost evaluations, and regulatory sign-offs before heavy capital is committed to full-scale development."
        }
    ],
    "quiz": [
        {
            "id": 248,
            "q": "A control flow graph for a fund transfer module has 14 edges and 10 nodes with 1 connected component. What is McCabe's Cyclomatic Complexity V(G)?",
            "options": [
                "4",
                "6",
                "8",
                "12"
            ],
            "answer": 1,
            "explanation": "Cyclomatic Complexity V(G) = E - N + 2P. With E = 14, N = 10, and P = 1: V(G) = 14 - 10 + 2(1) = 6."
        },
        {
            "id": 249,
            "q": "An online fixed deposit system accepts tenure from 7 days to 3650 days. Using Boundary Value Analysis, which set of input test values should be selected to test the lower boundary?",
            "options": [
                "6 days, 7 days, 8 days",
                "0 days, 7 days, 14 days",
                "1 day, 7 days, 30 days",
                "5 days, 7 days, 10 days"
            ],
            "answer": 0,
            "explanation": "Boundary Value Analysis tests the boundary point itself, one value immediately below, and one value immediately above. For minimum tenure 7 days, the values are 6 (invalid), 7 (valid min), and 8 (valid just above)."
        },
        {
            "id": 250,
            "q": "Which SDLC model maps each development phase directly to an associated testing phase, ensuring test strategy planning occurs concurrently with architecture design?",
            "options": [
                "Waterfall Model",
                "V-Model (Verification and Validation Model)",
                "Big Bang Model",
                "RAD Model"
            ],
            "answer": 1,
            "explanation": "The V-Model pairs development phases on the left side with testing verification phases on the right side (e.g., Requirements with UAT, Architecture with System Testing, Detailed Design with Unit Testing)."
        },
        {
            "id": 251,
            "q": "What is the primary objective of a 'Smoke Test' when a newly compiled build is delivered to the QA team?",
            "options": [
                "To rigorously test all edge cases and boundary conditions of every module.",
                "To verify that the build is stable enough and critical paths work before committing QA resources to detailed testing.",
                "To measure maximum system throughput under peak concurrent user load.",
                "To calculate cyclomatic complexity of all changed source files."
            ],
            "answer": 1,
            "explanation": "Smoke Testing (Build Verification Testing) is a broad, shallow test designed to ensure the build compiles, launches, and core functionalities operate properly before comprehensive test execution begins."
        },
        {
            "id": 252,
            "q": "In Scrum, who is solely accountable for prioritizing items in the Product Backlog to maximize business value?",
            "options": [
                "Scrum Master",
                "Lead Developer",
                "Product Owner",
                "QA Automation Lead"
            ],
            "answer": 2,
            "explanation": "The Product Owner is solely responsible for managing the Product Backlog, including expressing backlog items clearly and ordering them to best achieve goals and missions."
        }
    ]
}

print("Chapters 12, 13, 14 definitions complete.")
