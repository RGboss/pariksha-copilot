# -*- coding: utf-8 -*-
"""
Enrichment module for Chapters 18, 19, 20, 21 (Stages 5, 6)
Provides exhaustive, textbook-grade lecture notes, 3 checkpoints, and 5 exam-calibrated questions each.
"""

ENRICHED_CHAPTERS = {}

# ==============================================================
# CHAPTER 18: Python Language Core, Memory & GIL
# ==============================================================
ENRICHED_CHAPTERS["ch-18"] = {
    "summary": "Deep dive into CPython runtime internals, PyObject memory model, Reference Counting & Cyclic Garbage Collector (Generations 0, 1, 2), Global Interpreter Lock (GIL) mechanics and multi-threading vs multi-processing, Mutable vs Immutable objects, Generators/Iterators, Decorators, and Context Managers.",
    "reading_time_mins": 35,
    "lecture_notes": """# Python Language Core: Data Structures, Memory Management & The GIL

## 1. CPython Object Model & Memory Management
In CPython (the standard Python implementation), **everything is an object**. Every variable is a pointer referencing a heap-allocated `PyObject` C structure.

```
+-------------------------------------------------------------+
|                      CPython PyObject                       |
+-------------------------------------------------------------+
| ob_refcnt : Reference Counter (ssize_t)                     |
| ob_type   : Pointer to Type Object (struct _typeobject *)   |
| [payload] : Actual data (e.g. integer digit, string bytes)  |
+-------------------------------------------------------------+
```

### 1.1 Mutable vs Immutable Data Structures
* **Immutable Types:** `int`, `float`, `bool`, `str`, `tuple`, `frozenset`, `bytes`.
  * Cannot be altered in-place after creation.
  * Modifying an immutable variable allocates a brand new object on the heap and updates the pointer.
  * **Integer Interning & Small Int Caching:** CPython pre-allocates small integers in the range $[-5, 256]$. Any variable assigned an integer in this range points to the exact same memory address (`a is b` evaluates to `True`).
* **Mutable Types:** `list`, `dict`, `set`, `bytearray`.
  * Can be altered in-place without changing memory address (`id(obj)`).
  * *Critical Pitfall:* Default mutable arguments in functions (e.g. `def append_item(x, lst=[])`) share the single list across all function calls!

### 1.2 Python Memory Allocator: Arenas, Pools & Blocks
CPython avoids calling the OS `malloc()` for every small object:
* **Arenas:** Large $256 \text{ KB}$ memory chunks allocated via OS `mmap()`.
* **Pools:** $4 \text{ KB}$ sections within an arena, dedicated to small objects of specific size classes (e.g., 16-byte, 32-byte, up to 512 bytes).
* **Blocks:** Small memory slots inside a pool where actual Python objects reside.

---

## 2. Garbage Collection: Reference Counting & Cyclic GC
CPython employs a two-tiered memory reclamation engine:

```
+-------------------------------------------------------------------------+
|                  CPYTHON DUAL GARBAGE COLLECTION                        |
+------------------------------------+------------------------------------+
| Tier 1: Reference Counting         | Tier 2: Generational Cyclic GC     |
| (Immediate, Deterministic)         | (Periodic, Handles Cycles)         |
|                                    |                                    |
| - ob_refcnt increments on assign   | - Generation 0 (Young objects)     |
| - decrements on del / out-of-scope | - Generation 1 (Surviving 0)       |
| - When ob_refcnt == 0:             | - Generation 2 (Long-lived)        |
|   Memory freed immediately!        | - Detects and breaks unreachable   |
|   (Calls tp_dealloc)               |   circular references: A <---> B   |
+------------------------------------+------------------------------------+
```

### 2.1 The Circular Reference Problem
```python
# Circular Reference Example:
node1 = {}
node2 = {}
node1['next'] = node2
node2['prev'] = node1
del node1
del node2
```
After `del`, the objects are unreachable from the root scope, but both retain `ob_refcnt = 1`. Reference counting alone **can never reclaim them**. The **Cyclic GC** periodically traverses doubly linked lists of container objects (`gc.collect()`), detects unreachable isolated subgraphs, and frees them.

---

## 3. The Global Interpreter Lock (GIL) Mechanics
The **Global Interpreter Lock (GIL)** is a mutual exclusion mutex that allows **only one native OS thread to execute Python bytecode at a time**, even on multi-core CPUs.

```
Multi-threading in Python:
Core 1: [ Thread 1 (Holding GIL) ] ---> [ Thread 2 (Holding GIL) ]
Core 2: [ Idle / Waiting for GIL ] ---> [ Idle / Waiting for GIL ]
* Multi-threading does NOT utilize multiple CPU cores for CPU-bound tasks!
```

### 3.1 Why the GIL Exists
1. CPython's memory management relies heavily on `ob_refcnt`. Without a lock, concurrent threads would produce race conditions during refcount updates, causing memory leaks or premature deallocations.
2. Integrating fine-grained locks on every single object would cause catastrophic single-thread performance degradation and deadlocks.

### 3.2 Threading vs Multiprocessing in Python
| Workload Type | Optimal Architecture | Mechanism |
| :--- | :--- | :--- |
| **I/O-Bound** (Network API calls, DB queries, reading files)| `threading` / `asyncio` | The GIL is **automatically released** during OS system calls (socket read/write, sleep). High concurrency achieved. |
| **CPU-Bound** (Cryptographic hashing, Pandas matrix math)| `multiprocessing` / `concurrent.futures.ProcessPoolExecutor` | Spawns separate OS processes, each with its own independent Python interpreter, memory space, and GIL across all CPU cores. |

---

## 4. Advanced Python Features: Generators, Decorators & Context Managers

### 4.1 Generators & The `yield` Keyword
* Regular functions return a complete data collection at once, consuming $O(n)$ RAM.
* A **Generator** yields values on-demand one at a time, implementing the Iterator protocol (`__iter__()`, `__next__()`) with $O(1)$ memory.
```python
# Process a 10 GB banking ledger line-by-line without exhausting RAM:
def read_large_ledger(filepath):
    with open(filepath, 'r') as file:
        for line in file:
            yield line.strip()
```

### 4.2 Decorators & Higher-Order Functions
A decorator takes a function as an argument, adds behavior, and returns a new function using closures.
```python
import functools, time

def audit_log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        print(f"Executed {func.__name__} in {duration:.4f}s")
        return result
    return wrapper

@audit_log
def transfer_funds(acc_from, acc_to, amount):
    ...
```

### 4.3 Context Managers (`with` Statement)
Ensures deterministic resource cleanup (file handles, database locks) via `__enter__()` and `__exit__()`:
```python
class DatabaseTransaction:
    def __enter__(self):
        self.conn = db_pool.get_connection()
        self.conn.begin()
        return self.conn
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.conn.rollback() # Rollback on exception
        else:
            self.conn.commit()   # Commit if clean
        self.conn.close()
```

---

## 5. High-Yield Summary Matrix for Banking IT Exams

| Feature | Mechanism / Rule | Examiner Trap / Distractor |
| :--- | :--- | :--- |
| **GIL Impact** | Only 1 thread executes bytecode | Does NOT hinder I/O-bound multithreading (GIL released during I/O). |
| **Small Int Cache**| Integers -5 to 256 interned | `a = 256; b = 256; a is b -> True`. `a = 500; b = 500; a is b -> False`. |
| **Mutable Default**| `def f(x=[])` creates shared list | Always use `def f(x=None): if x is None: x = []`. |
| **Generators** | `yield` pauses stack state | Consumes $O(1)$ space; cannot be indexed or re-traversed without resetting. |
| **is vs ==** | `==` checks value equality | `is` checks exact memory identity (`id(a) == id(b)`). |
""",
    "checkpoints": [
        {
            "q": "Why does executing CPU-heavy mathematical calculations using Python's 'threading' module on an 8-core CPU fail to achieve speedup compared to a single thread?",
            "a": "Because of CPython's Global Interpreter Lock (GIL). The GIL enforces that only one OS thread can execute Python bytecode at any moment. The 8 threads spend significant CPU cycles competing for the GIL lock (lock contention overhead), preventing parallel execution on multiple cores. CPU-bound parallelism requires the 'multiprocessing' module."
        },
        {
            "q": "Why does 'a = 100; b = 100; print(a is b)' output True, but 'a = 1000; b = 1000; print(a is b)' might output False?",
            "a": "CPython maintains a static pre-allocated array of integer objects for small integers in the range [-5, 256]. Any reference to 100 points to the identical cached PyObject in memory ('is' checks memory pointer identity). For numbers outside this range, Python allocates separate heap objects with distinct memory addresses."
        },
        {
            "q": "What happens if a function definition uses a mutable default parameter, such as 'def add_txn(txn, history=[])'?",
            "a": "Default parameter expressions in Python are evaluated once when the function is defined, NOT each time the function is called. The exact same list object is shared across all subsequent invocations. Any transaction appended in call 1 will persist in call 2, causing data pollution. The correct pattern is 'history=None' with internal initialization."
        }
    ],
    "quiz": [
        {
            "id": 268,
            "q": "In Python, which of the following data types is strictly MUTABLE?",
            "options": [
                "tuple",
                "frozenset",
                "list",
                "str"
            ],
            "answer": 2,
            "explanation": "Lists, dictionaries, and sets are mutable (they can be modified in-place). Tuples, frozensets, strings, and integers are immutable."
        },
        {
            "id": 269,
            "q": "What is the primary operational purpose of the Cyclic Garbage Collector in CPython?",
            "options": [
                "To optimize CPU cache alignment for NumPy arrays.",
                "To detect and reclaim isolated circular reference cycles that cannot be collected by Reference Counting alone.",
                "To automatically compress strings in the constant pool.",
                "To prevent thread deadlocks caused by the GIL."
            ],
            "answer": 1,
            "explanation": "Reference counting immediately reclaims objects whose reference count drops to 0. However, objects referencing each other in a closed cycle retain non-zero counts. CPython's generational cyclic GC detects and frees these cycles."
        },
        {
            "id": 270,
            "q": "Which module in Python should be selected to parallelize a CPU-intensive data encryption task across all available physical CPU cores?",
            "options": [
                "threading",
                "asyncio",
                "multiprocessing",
                "queue"
            ],
            "answer": 2,
            "explanation": "The 'multiprocessing' module spawns independent OS processes, each with its own memory space and GIL, enabling true parallel execution across multiple CPU cores for CPU-bound tasks."
        },
        {
            "id": 271,
            "q": "What is the memory complexity of traversing a massive 10-million line log file using a Python Generator function with 'yield'?",
            "options": [
                "O(n) where n is total file size",
                "O(1) constant memory",
                "O(log n)",
                "O(n^2)"
            ],
            "answer": 1,
            "explanation": "A generator produces items lazily on demand one at a time using 'yield', keeping only the current element in memory. Its memory complexity is strictly O(1)."
        },
        {
            "id": 272,
            "q": "What special dunder methods must a class implement to be compatible with Python's 'with' statement (Context Manager protocol)?",
            "options": [
                "__init__() and __del__()",
                "__enter__() and __exit__()",
                "__iter__() and __next__()",
                "__open__() and __close__()"
            ],
            "answer": 1,
            "explanation": "The Context Manager protocol requires implementing '__enter__()' (executed upon entering the with-block) and '__exit__()' (executed upon exiting or encountering an exception)."
        }
    ]
}

# ==============================================================
# CHAPTER 19: Data Manipulation with Pandas, NumPy & Regex
# ==============================================================
ENRICHED_CHAPTERS["ch-19"] = {
    "summary": "Deep dive into NumPy ndarray architecture, contiguous memory strides, SIMD vectorization, broadcasting rules, Pandas DataFrames/Series, .loc[] vs .iloc[] indexing mechanics, handling missing data (NaN), aggregation/merging techniques, and Python Regular Expressions (greedy/lazy quantifiers, lookahead/lookbehind).",
    "reading_time_mins": 35,
    "lecture_notes": """# Data Manipulation with Pandas, NumPy & Regular Expressions

## 1. NumPy Architecture & Vectorized Computing
NumPy provides the high-performance numerical computing foundation for Python. At its core is the **`ndarray`** (N-dimensional array).

```
+-------------------------------------------------------------+
|               PYTHON LIST vs NUMPY NDARRAY                  |
+-------------------------------------------------------------+
| Python List (Array of Pointers):                            |
| [ *Ptr0 | *Ptr1 | *Ptr2 ]                                   |
|    |        |        |                                      |
|    v        v        v                                      |
| [PyObj]  [PyObj]  [PyObj] (Fragmented across heap, pointer  |
|                            chasing, high memory overhead)   |
+-------------------------------------------------------------+
| NumPy ndarray (Dense Contiguous C-Buffer):                   |
| [ int64 | int64 | int64 | int64 | int64 ]                   |
| (Contiguous memory, zero pointer chasing, cache-friendly,   |
|  SIMD CPU vectorization enabled)                            |
+-------------------------------------------------------------+
```

### 1.1 Memory Strides & Memory Layout
* A NumPy array is defined by:
  * **Data Pointer:** Memory address of the raw contiguous buffer.
  * **Dtype:** Data type (e.g., `int32`, `float64`).
  * **Shape:** Tuple representing dimensions (e.g., `(3, 4)`).
  * **Strides:** Tuple of bytes to step in each dimension when traversing the array.
* **C-Order (Row-Major):** Consecutive elements of a row are adjacent in memory (default in NumPy and C).
* **Fortran-Order (Column-Major):** Consecutive elements of a column are adjacent in memory.

### 1.2 Broadcasting Rules
Broadcasting allows NumPy to perform arithmetic operations on arrays of differing shapes without copying data in memory:
* Two dimensions are compatible when:
  1. They are **equal**, OR
  2. One of them is **1**.
* If dimension counts differ, prepends `1`s to the smaller array's shape until dimensions match.
* *Example:* Array $A$ of shape $(4, 3)$ and Array $B$ of shape $(3,)$:
  * Shape of $B$ expands to $(1, 3)$.
  * Dimension 1: $4$ and $1 \implies 1$ is stretched to $4$.
  * Dimension 2: $3$ and $3 \implies$ compatible! Resulting shape: $(4, 3)$.

---

## 2. Pandas Data Manipulation: Series & DataFrames
Pandas builds on top of NumPy, adding labeled indexing and relational operations.

### 2.1 Indexing Mechanics: `.loc[]` vs `.iloc[]`
* **`.loc[]` (Label-Based):**
  * Queries rows and columns by their textual or index labels.
  * **Endpoints are INCLUSIVE!** `df.loc['2023-01-01':'2023-01-05']` includes both start and end dates.
* **`.iloc[]` (Integer Position-Based):**
  * Queries rows and columns by zero-based integer index ($0$ to $N - 1$).
  * **Endpoints are EXCLUSIVE!** `df.iloc[0:5]` selects rows 0, 1, 2, 3, 4 (5 is excluded).

```python
# Real exam comparison:
df.loc[0:2]   # Returns rows with LABELS 0, 1, 2 (3 rows if labeled 0,1,2)
df.iloc[0:2]  # Returns rows at integer POSITIONS 0 and 1 (strictly 2 rows)
```

### 2.2 Missing Data: `NaN` Handling & Imputation
In Pandas, floating-point `np.nan` (IEEE 754 NaN) represents missing values.
* In IEEE floating point: `np.nan == np.nan` evaluates to **`False`**! Always use `pd.isna()` or `df.isna()`.
* **Remedies:**
  * `df.dropna(how='any', subset=['critical_col'])`: Remove records with missing values.
  * `df.fillna(df.mean())` / `df.ffill()`: Impute missing values with mean or forward fill.

### 2.3 GroupBy & Aggregations (Split-Apply-Combine)
```python
# Financial transaction aggregation:
summary = df.groupby(['branch_id', 'txn_type']).agg(
    total_volume=('amount', 'sum'),
    avg_txn=('amount', 'mean'),
    txn_count=('amount', 'count')
).reset_index()
```

---

## 3. Regular Expressions (Regex) in Python (`re` Module)
Regex provides powerful pattern matching for input sanitization, data validation, and financial statement parsing.

### 3.1 Character Classes & Quantifiers
* `^`: Asserts start of string.
* `$`: Asserts end of string.
* `\d`: Any digit `[0-9]`.
* `\w`: Any alphanumeric character or underscore `[a-zA-Z0-9_]`.
* `\s`: Any whitespace (space, tab, newline).
* **Quantifiers:**
  * `*`: 0 or more occurrences (Greedy).
  * `+`: 1 or more occurrences (Greedy).
  * `?`: 0 or 1 occurrence (or makes quantifiers Lazy/Non-Greedy).
  * `{m, n}`: Between $m$ and $n$ occurrences.

### 3.2 Greedy vs Lazy (Non-Greedy) Matching
* By default, quantifiers are **Greedy**: they match as much text as possible.
* Appending `?` makes a quantifier **Lazy**: matches as little text as possible.
```python
text = "<div>Alpha</div><div>Beta</div>"
re.findall(r"<div>.*</div>", text)    # Greedy: ['<div>Alpha</div><div>Beta</div>']
re.findall(r"<div>.*?</div>", text)   # Lazy:   ['<div>Alpha</div>', '<div>Beta</div>']
```

### 3.3 Lookaround Assertions (Zero-Width)
* **Positive Lookahead `(?=...)`:** Asserts that given pattern follows, without including it in the match.
* **Negative Lookahead `(?!...)`:** Asserts that given pattern does NOT follow.
* **Positive Lookbehind `(?<=...)`:** Asserts that given pattern precedes.
```python
# Match price in USD ($1500 -> 1500):
re.findall(r"(?<=\$)\d+", "Total cost: $1500 and tax: $75")  # ['1500', '75']
```

---

## 4. High-Yield Summary Matrix for Banking IT Exams

| Concept | Syntax / Rule | Examiner Trap / Distractor |
| :--- | :--- | :--- |
| **.loc[] vs .iloc[]** | `.loc` is label & inclusive; `.iloc` is integer & exclusive | Slicing with `.loc[1:3]` includes index 3; `.iloc[1:3]` stops at 2. |
| **NaN Equality** | `np.nan == np.nan -> False` | Never test missing data using `== np.nan`. Use `pd.isna()`. |
| **Broadcasting** | Dims match or one is 1 | `(3, 4)` and `(3,)` will FAIL to broadcast (must be `(3, 1)` or `(1, 4)`). |
| **Non-Greedy Regex**| Append `?` (e.g. `.*?`) | Without `?`, `.*` consumes through to the final matching character. |
| **Vectorization** | SIMD memory processing | Vectorized Pandas operations run 100x faster than Python `for` loops. |
""",
    "checkpoints": [
        {
            "q": "What is the critical behavioral difference between slicing a DataFrame using '.loc[0:3]' versus '.iloc[0:3]'?",
            "a": "'.loc[0:3]' is label-based and INCLUSIVE of the endpoint: it returns all rows whose index label falls between 0 and 3 (up to 4 rows). '.iloc[0:3]' is integer-based and EXCLUSIVE of the endpoint: it returns exactly 3 rows at positional indexes 0, 1, and 2."
        },
        {
            "q": "Why does evaluating 'np.nan == np.nan' return False in Python, and how should missing values be checked correctly?",
            "a": "IEEE 754 floating-point standard mandates that NaN (Not a Number) does not equal any value, including itself. To check for missing values, always use Pandas 'pd.isna(x)' or NumPy 'np.isnan(x)' functions."
        },
        {
            "q": "Can a NumPy array of shape (4, 3) be broadcast with an array of shape (4,)? Explain why or why not.",
            "a": "No, they cannot broadcast directly. NumPy aligns trailing dimensions first. Array 1 has trailing dimension 3, while Array 2 has trailing dimension 4. Because 3 != 4 and neither is 1, broadcasting fails with ValueError. Array 2 would need to be reshaped to (4, 1) to broadcast."
        }
    ],
    "quiz": [
        {
            "id": 273,
            "q": "Given a Pandas DataFrame 'df' with default integer index [0, 1, 2, 3, 4], how many rows are returned by 'df.loc[0:2]' versus 'df.iloc[0:2]'?",
            "options": [
                "df.loc returns 2 rows; df.iloc returns 3 rows.",
                "df.loc returns 3 rows (labels 0, 1, 2 inclusive); df.iloc returns 2 rows (positions 0, 1 exclusive of 2).",
                "Both return exactly 2 rows.",
                "Both return exactly 3 rows."
            ],
            "answer": 1,
            "explanation": ".loc is label-based and includes the right endpoint (labels 0, 1, 2 = 3 rows). .iloc is positional and excludes the stop index (indices 0 and 1 = 2 rows)."
        },
        {
            "id": 274,
            "q": "Which rule must be satisfied for two dimensions to be compatible for NumPy array broadcasting?",
            "options": [
                "The dimensions must both be prime numbers.",
                "The dimensions must be equal, or one of them must be 1.",
                "The product of the dimensions must exceed 100.",
                "Both arrays must have identical total byte sizes."
            ],
            "answer": 1,
            "explanation": "NumPy broadcasting compares shapes element-wise starting from trailing dimensions. Two dimensions are compatible if they are equal, or if one of them is 1."
        },
        {
            "id": 275,
            "q": "What is the result of evaluating 'float('nan') == float('nan')' in Python?",
            "options": [
                "True",
                "False",
                "TypeError",
                "None"
            ],
            "answer": 1,
            "explanation": "According to the IEEE 754 standard for floating-point arithmetic, NaN is unequal to every value, including itself. Hence 'float('nan') == float('nan')' evaluates to False."
        },
        {
            "id": 276,
            "q": "Given text = '<b>Bank</b> of <b>India</b>', what will re.findall(r'<b>.*</b>', text) return?",
            "options": [
                "['<b>Bank</b>', '<b>India</b>']",
                "['<b>Bank</b> of <b>India</b>']",
                "['Bank', 'India']",
                "[]"
            ],
            "answer": 1,
            "explanation": "The quantifier '.*' is greedy: it consumes as many characters as possible, matching from the first '<b>' all the way to the final '</b>'. To match individual tags, a lazy quantifier '<b>.*?</b>' must be used."
        },
        {
            "id": 277,
            "q": "Which regular expression pattern utilizes a Positive Lookahead to assert that a string contains at least one digit without including it in the match?",
            "options": [
                "(?=\\d)",
                "(?<=\\d)",
                "(?!\\d)",
                "(?<!\\d)"
            ],
            "answer": 0,
            "explanation": "(?=\\d) is a positive lookahead assertion, confirming that a digit follows at the current position without advancing the match pointer."
        }
    ]
}

print("Chapters 18 and 19 definitions complete.")

# ==============================================================
# CHAPTER 20: OWASP Top 10 Web Security & Vulnerabilities
# ==============================================================
ENRICHED_CHAPTERS["ch-20"] = {
    "summary": "Deep dive into web application attack vectors, OWASP Top 10 (Broken Access Control, Cryptographic Failures, Injection SQLi/Command, Insecure Deserialization, SSRF cloud metadata attacks), Cross-Site Scripting (Stored, Reflected, DOM-based), Cross-Site Request Forgery (CSRF tokens & SameSite cookies), and defensive mitigation.",
    "reading_time_mins": 35,
    "lecture_notes": """# OWASP Top 10 Web Application Vulnerabilities, Attacks & Mitigation

## 1. The Threat Landscape & OWASP Top 10 Framework
The Open Web Application Security Project (OWASP) maintains a consensus ranking of the most critical security vulnerabilities affecting web and banking software.

```
+-------------------------------------------------------------------------+
|                         OWASP TOP 10 TAXONOMY                           |
+-------------------------------------------------------------------------+
| A01: Broken Access Control           | Missing authorization checks;    |
|                                      | IDOR, unauthorized privilege esc.|
| A02: Cryptographic Failures          | Weak ciphers (DES/MD5), exposure |
|                                      | of plaintext sensitive data.     |
| A03: Injection                       | SQLi, Command Injection, LDAP;   |
|                                      | untrusted input parsed as code.  |
| A04: Insecure Design                 | Architectural flaws lacking      |
|                                      | threat modeling and rate limits. |
| A05: Security Misconfiguration       | Default passwords, debug ports,  |
|                                      | verbose stack traces in prod.    |
| A06: Vulnerable/Outdated Components  | Dependencies with known CVEs     |
|                                      | (Log4Shell, Struts).             |
| A07: Identification & Auth Failures  | Credential stuffing, brute force,|
|                                      | missing MFA, weak session tokens.|
| A08: Software & Data Integrity       | Insecure deserialization,        |
|                                      | unverified CI/CD plugin updates. |
| A09: Security Logging & Monitoring   | Insufficient logging, undetected |
|                                      | active breaches and tampering.   |
| A10: Server-Side Request Forgery     | Server tricked into fetching     |
|      (SSRF)                          | internal cloud metadata URLs.    |
+-------------------------------------------------------------------------+
```

---

## 2. In-Depth Vulnerability Analysis & Attack Mechanics

### 2.1 A01: Broken Access Control & IDOR
* **Insecure Direct Object Reference (IDOR):** Occurs when an application provides direct access to objects based on user-supplied input without verifying ownership.
  * *Attack Scenario:* User navigates to `https://bank.com/api/statements?account_id=10045`. Modifying the parameter to `10046` allows the attacker to view another customer's balance.
  * *Remedy:* Enforce server-side session checks: `SELECT * FROM accounts WHERE id = ? AND owner_id = session.userId`.

### 2.2 A03: Injection (SQL Injection - SQLi)
Occurs when untrusted data is concatenated directly into an interpreter string:
```sql
-- Vulnerable Dynamic Query:
SELECT * FROM users WHERE username = 'admin' AND password = '' OR '1'='1';
-- The OR '1'='1' evaluates to TRUE for all rows, bypassing authentication.
```
* **Remedies:**
  * **Parameterized Queries (Prepared Statements):** Compiles the SQL structure first; parameters are treated strictly as data literals, never executable bytecode.
  * **Stored Procedures & ORMs:** Hibernate/JPA using named parameters (`:username`).

### 2.3 Cross-Site Scripting (XSS)
XSS occurs when malicious scripts are injected into trusted web applications:
1. **Stored XSS (Persistent):** Malicious JavaScript is permanently stored in the database (e.g. comment forum, user profile). Every user viewing the page executes the payload.
2. **Reflected XSS (Non-Persistent):** Malicious script is reflected off the web server in an error message or search query URL.
3. **DOM-based XSS:** Vulnerability resides entirely in client-side JavaScript code (e.g., executing `eval()` or `element.innerHTML` on `location.hash`).
* **Defenses:** Context-aware output encoding, strict **Content Security Policy (CSP)** HTTP headers, and setting the `HttpOnly` cookie flag (preventing JavaScript from reading session cookies via `document.cookie`).

### 2.4 Cross-Site Request Forgery (CSRF)
Forces an authenticated victim's browser to send forged HTTP requests to a target application where they are logged in.
* *Mechanics:* Browsers automatically attach stored authentication cookies with cross-origin requests.
* *Defenses:*
  * **Anti-CSRF Tokens (Synchronizer Token Pattern):** Cryptographically random token embedded in HTML forms and validated server-side.
  * **SameSite Cookie Attribute:**
    * `SameSite=Strict`: Cookie is never sent on cross-site requests.
    * `SameSite=Lax`: Cookie is sent only on top-level safe GET navigations (default in modern browsers).

### 2.5 A10: Server-Side Request Forgery (SSRF)
The web server fetches a remote resource without validating the user-supplied URL.
* *Cloud Attack Vector:* An attacker supplies the cloud instance metadata service IP:
  ```
  https://bank-app.com/preview?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/
  ```
  The vulnerable server fetches the link internally and returns temporary AWS IAM credentials, leading to total cloud account compromise!

---

## 3. High-Yield Summary Matrix for Banking IT Exams

| Vulnerability | Attack Vector | Primary Mitigation |
| :--- | :--- | :--- |
| **SQL Injection** | SQL grammar manipulation | Prepared Statements (Parameterized queries) |
| **XSS** | Malicious JavaScript injection | Context-aware HTML encoding + `HttpOnly` flag + CSP |
| **CSRF** | Forged requests using session cookies | Anti-CSRF Synchronizer Tokens + `SameSite=Strict` |
| **SSRF** | Server queries internal cloud metadata | Strict URL whitelist + disable IMDSv1 (use IMDSv2 token) |
| **IDOR** | Tampering with URL record IDs | Server-side user authorization & tenancy validation |
""",
    "checkpoints": [
        {
            "q": "How does setting the 'HttpOnly' flag on a session cookie protect banking customers from Cross-Site Scripting (XSS) account takeover?",
            "a": "The 'HttpOnly' directive instructs the web browser that the cookie cannot be accessed through client-side scripts (e.g., via 'document.cookie'). If an attacker successfully executes an XSS injection payload, they are blocked from stealing the session cookie, preventing automated session hijacking."
        },
        {
            "q": "Why does using Prepared Statements (Parameterized Queries) guarantee immunity against SQL Injection attacks?",
            "a": "In prepared statements, the database engine compiles the SQL query structure and execution plan first. When user inputs are supplied later, the database engine treats them strictly as literal string/numerical parameter values, never as executable SQL commands or operators."
        },
        {
            "q": "What is the primary target of an attacker executing a Server-Side Request Forgery (SSRF) vulnerability against a cloud-hosted banking application?",
            "a": "The attacker targets internal network services and cloud instance metadata APIs (such as http://169.254.169.254 in AWS/GCP). Accessing the metadata endpoint allows the attacker to steal IAM role credentials and security tokens, compromising cloud infrastructure."
        }
    ],
    "quiz": [
        {
            "id": 278,
            "q": "Which defense provides the most robust and complete protection against SQL Injection vulnerabilities?",
            "options": [
                "Client-side JavaScript input length checking",
                "Parameterized Queries (Prepared Statements)",
                "Blacklisting SQL keywords such as 'SELECT' and 'DROP'",
                "Encoding SQL queries using Base64"
            ],
            "answer": 1,
            "explanation": "Parameterized queries separate SQL code from data parameters, ensuring that user inputs can never alter the syntax or execution plan of the query."
        },
        {
            "id": 279,
            "q": "What browser cookie attribute prevents malicious scripts from accessing session tokens via document.cookie during an XSS attack?",
            "options": [
                "Secure",
                "HttpOnly",
                "SameSite",
                "Domain"
            ],
            "answer": 1,
            "explanation": "The HttpOnly flag prevents client-side scripts (like JavaScript) from accessing the cookie, blocking attackers from extracting session cookies via XSS."
        },
        {
            "id": 280,
            "q": "In an AWS cloud environment, what link is notoriously targeted by attackers exploiting Server-Side Request Forgery (SSRF)?",
            "options": [
                "http://localhost:8080/admin",
                "http://169.254.169.254/latest/meta-data/",
                "http://127.0.0.1:3306/mysql",
                "http://10.0.0.1/gateway"
            ],
            "answer": 1,
            "explanation": "The link 169.254.169.254 is the AWS link-local Instance Metadata Service (IMDS). Exploiting SSRF against this endpoint allows attackers to steal IAM temporary credentials."
        },
        {
            "id": 281,
            "q": "Which type of Cross-Site Scripting (XSS) occurs when malicious code is permanently saved in the application's database and served to all subsequent users?",
            "options": [
                "Reflected XSS",
                "DOM-based XSS",
                "Stored (Persistent) XSS",
                "Blind SQL Injection"
            ],
            "answer": 2,
            "explanation": "Stored XSS occurs when untrusted input is permanently written to a database (e.g. user comments, customer feedback) and executed in the browsers of any victims viewing the stored data."
        },
        {
            "id": 282,
            "q": "How does the 'SameSite=Strict' cookie attribute prevent Cross-Site Request Forgery (CSRF) attacks?",
            "options": [
                "It encrypts the cookie using AES-256.",
                "It strictly prevents the browser from sending the cookie in any cross-site request initiated by third-party websites.",
                "It forces the cookie to expire after 5 minutes.",
                "It blocks all HTTP POST requests."
            ],
            "answer": 1,
            "explanation": "SameSite=Strict instructs the browser never to include the cookie in cross-site requests, effectively neutralizing CSRF attacks from external links or malicious forms."
        }
    ]
}

# ==============================================================
# CHAPTER 21: Applied Cryptography, PKI & RBI Framework
# ==============================================================
ENRICHED_CHAPTERS["ch-21"] = {
    "summary": "Deep dive into Symmetric (AES-256) vs Asymmetric (RSA, ECC) encryption, Cryptographic Hash functions (SHA-256, bcrypt, PBKDF2), Public Key Infrastructure (PKI, X.509, CA hierarchy), TLS 1.3 handshake mechanics, Digital Signatures, and the RBI Cyber Security Framework for Scheduled Commercial Banks (CSOC, CCMP, Network Segmentation).",
    "reading_time_mins": 35,
    "lecture_notes": """# Applied Cryptography, PKI, Digital Signatures & RBI Cyber Security Framework

## 1. Applied Cryptography Foundations
Cryptography protects confidentiality, integrity, authenticity, and non-repudiation in financial transactions.

```
+-------------------------------------------------------------------------+
|                      CRYPTOGRAPHY TAXONOMY                              |
+------------------------------------+------------------------------------+
| 1. Symmetric Key Cryptography      | 2. Asymmetric Key Cryptography     |
| (Shared Secret Key)                | (Public Key + Private Key Pair)    |
|                                    |                                    |
| - Fast, encrypts bulk data         | - Slower, key exchange & signatures|
| - AES-128, AES-256 (GCM/CBC)       | - RSA (2048/4096-bit), ECC (256-bit|
| - Key distribution problem         | - Solves key exchange problem      |
+------------------------------------+------------------------------------+
| 3. Cryptographic Hash Functions & Message Authentication Codes          |
| - One-way, collision-resistant (SHA-256, SHA-3)                         |
| - Password storage: bcrypt, Argon2, PBKDF2 (salted + work factor)       |
| - HMAC (Hash-based Message Authentication Code): Integrity + Auth       |
+-------------------------------------------------------------------------+
```

### 1.1 Symmetric vs Asymmetric Comparison
* **AES (Advanced Encryption Standard):**
  * Block cipher operating on 128-bit blocks. Keys: 128, 192, 256 bits.
  * **AES-GCM (Galois/Counter Mode):** Provides Authenticated Encryption with Associated Data (AEAD), guaranteeing both confidentiality and tamper-proof integrity.
* **RSA (Rivest-Shamir-Adleman):**
  * Based on the mathematical difficulty of factoring the product of two large prime numbers.
* **ECC (Elliptic Curve Cryptography):**
  * Based on the algebraic structure of elliptic curves over finite fields (Discrete Logarithm problem).
  * **Security Equivalence:** A 256-bit ECC key offers equivalent cryptographic strength to a massive 3072-bit RSA key with vastly lower CPU and bandwidth overhead!

---

## 2. Public Key Infrastructure (PKI) & Digital Signatures

### 2.1 Digital Signature Mechanics
A digital signature provides **Authentication, Integrity, and Non-Repudiation** (the sender cannot deny having sent the message).

```
Sender (Alice) Signing:
[Message] ---> [SHA-256 Hash] ---> [Encrypt with Alice's PRIVATE Key] ---> [Digital Signature]

Receiver (Bob) Verification:
1. Decrypts [Digital Signature] using Alice's PUBLIC Key  ===> Yields Hash A
2. Computes [SHA-256 Hash] of received [Message]          ===> Yields Hash B
3. If Hash A == Hash B: Message is authentic and unmodified!
```

### 2.2 X.509 Certificates & Certificate Authorities (CA)
* How does Bob know Alice's public key genuinely belongs to Alice and not an attacker?
* **X.509 Digital Certificate:** A digitally signed statement binding a public key to an identity (Domain Name/Organization), issued by a trusted **Certificate Authority (CA)** (e.g. DigiCert, Let's Encrypt).
* **Certificate Chain:** End-Entity Certificate $\to$ Intermediate CA $\to$ Trusted Root CA (pre-installed in OS/browser trust stores).

### 2.3 TLS 1.3 Handshake Protocol
TLS 1.3 reduces the handshake to **1 round trip (1-RTT)** and mandates **Perfect Forward Secrecy (PFS)** via Ephemeral Diffie-Hellman (ECDHE). Even if a server's private key is stolen years later, past recorded encrypted traffic cannot be decrypted!

---

## 3. Reserve Bank of India (RBI) Cyber Security Framework
Issued under RBI Circular for Scheduled Commercial Banks, Urban Co-operative Banks, and NBFCs to protect the Indian banking payment grid.

```
+-------------------------------------------------------------------------+
|                  RBI CYBER SECURITY CORE MANDATES                       |
+-------------------------------------------------------------------------+
| 1. Cyber Security Operations Center (C-SOC)                             |
|    - Mandatory 24x7x365 continuous security monitoring and SIEM alerts.  |
| 2. Cyber Crisis Management Plan (CCMP)                                  |
|    - Formal incident response protocol approved by the Bank's Board.    |
| 3. Network Segmentation & Demilitarized Zones (DMZ)                    |
|    - Core Banking Systems (CBS) must be strictly isolated from the       |
|      Internet-facing DMZ and Corporate LAN.                            |
| 4. Multi-Factor Authentication (MFA)                                    |
|    - Mandatory for all administrative access and financial transactions.|
| 5. Periodic Vulnerability Assessment & Penetration Testing (VAPT)       |
|    - Mandatory periodic third-party security audits (CERT-In empanelled)|
+-------------------------------------------------------------------------+
```

### 3.1 SEBI Cyber Security and Cyber Resilience Framework
For Stock Brokers, Depositories, and Market Infrastructure Institutions (MIIs):
* Strict API access controls and mutual TLS (mTLS).
* Zero Trust Network Architecture (ZTNA).
* Mandatory reporting of cyber incidents to SEBI and CERT-In within **6 hours** of detection.

---

## 4. High-Yield Summary Matrix for Banking IT Exams

| Concept | Key Property | Real Exam Trap / Examiner Focus |
| :--- | :--- | :--- |
| **Digital Signature** | Encrypted with sender's **Private Key** | Verified using sender's **Public Key**. |
| **Confidentiality** | Encrypted with receiver's **Public Key** | Decrypted using receiver's **Private Key**. |
| **Password Storage** | Salted bcrypt / Argon2 / PBKDF2 | NEVER store passwords using plain MD5 or SHA-256. |
| **ECC vs RSA** | 256-bit ECC $\approx$ 3072-bit RSA | ECC offers superior performance on mobile/embedded devices. |
| **RBI C-SOC** | 24x7 Continuous Real-time Monitoring | Mandated by RBI for all Scheduled Commercial Banks. |
""",
    "checkpoints": [
        {
            "q": "Why is hashing passwords using standard fast cryptographic hashes like SHA-256 or MD5 considered a dangerous security failure, and what should be used instead?",
            "a": "Modern GPUs can compute billions of SHA-256 hashes per second, making offline brute-force and rainbow table attacks trivial. Passwords must be hashed using deliberately slow, salted algorithms with configurable work factors (such as bcrypt, Argon2id, or PBKDF2) to resist hardware-accelerated attacks."
        },
        {
            "q": "In a Public Key Infrastructure (PKI) system, whose key is used to generate a Digital Signature, and whose key is used to verify it?",
            "a": "The digital signature is created by encrypting the message hash using the SENDER'S PRIVATE KEY (guaranteeing authentication and non-repudiation). Anyone can verify the signature by decrypting it using the SENDER'S PUBLIC KEY."
        },
        {
            "q": "What are the core architectural mandates of the RBI Cyber Security Framework regarding Core Banking Solutions (CBS) network isolation?",
            "a": "The RBI framework mandates strict Network Segmentation. Core Banking Solutions (CBS) and database tiers must reside in isolated private network zones with zero direct internet access. Web servers must be placed in a Demilitarized Zone (DMZ), and all administrative access requires Multi-Factor Authentication (MFA) and bastion jump-hosts."
        }
    ],
    "quiz": [
        {
            "id": 283,
            "q": "To create a valid Digital Signature for a banking transfer message, which cryptographic key must the sender use to encrypt the message digest?",
            "options": [
                "Receiver's Public Key",
                "Receiver's Private Key",
                "Sender's Private Key",
                "Sender's Public Key"
            ],
            "answer": 2,
            "explanation": "A digital signature is created by encrypting the message digest with the sender's Private Key. This proves authenticity and non-repudiation because only the sender possesses their private key."
        },
        {
            "id": 284,
            "q": "Which symmetric encryption mode provides Authenticated Encryption with Associated Data (AEAD), ensuring both confidentiality and message integrity?",
            "options": [
                "AES-ECB (Electronic Codebook)",
                "AES-CBC (Cipher Block Chaining)",
                "AES-GCM (Galois/Counter Mode)",
                "DES"
            ],
            "answer": 2,
            "explanation": "AES-GCM provides authenticated encryption (AEAD), combining high-performance counter mode encryption with Galois field authentication to detect ciphertext tampering."
        },
        {
            "id": 285,
            "q": "Approximately what size RSA key is required to match the cryptographic security strength provided by a 256-bit Elliptic Curve Cryptography (ECC) key?",
            "options": [
                "512-bit RSA",
                "1024-bit RSA",
                "2048-bit RSA",
                "3072-bit RSA"
            ],
            "answer": 3,
            "explanation": "According to NIST cryptographic equivalence standards, a 256-bit ECC key provides equivalent security strength to a 3072-bit RSA key while consuming significantly fewer CPU cycles."
        },
        {
            "id": 286,
            "q": "Under the Reserve Bank of India (RBI) Cyber Security Framework, what is the mandatory operational availability requirement for a Bank's Cyber Security Operations Center (C-SOC)?",
            "options": [
                "Business hours only (9 AM to 6 PM)",
                "24x7x365 continuous real-time monitoring",
                "Weekly batch review of firewall logs",
                "On-demand monitoring during active audits"
            ],
            "answer": 1,
            "explanation": "The RBI mandates that all Scheduled Commercial Banks establish a C-SOC operating 24x7x365 to continuously monitor, detect, and respond to cyber threats in real time."
        },
        {
            "id": 287,
            "q": "Which password hashing algorithm is specifically designed to resist GPU-based cracking by incorporating a tunable memory-hard cost factor?",
            "options": [
                "SHA-512",
                "MD5",
                "Argon2 / bcrypt",
                "CRC32"
            ],
            "answer": 2,
            "explanation": "Argon2 (and bcrypt) are deliberately computationally expensive, salted hashing algorithms with memory-hard and time-cost parameters designed to defeat parallel brute-force attacks on GPUs and ASICs."
        }
    ]
}

print("Chapters 20 and 21 definitions complete.")
