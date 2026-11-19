import os
import re
import json
import pypdf

BASE_DIR = 'E:/study material'
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def safe_extract_text(pdf_path, max_pages=None):
    if not os.path.exists(pdf_path):
        return ""
    try:
        reader = pypdf.PdfReader(pdf_path)
        pages = reader.pages if max_pages is None else reader.pages[:max_pages]
        text_list = []
        for p in pages:
            t = p.extract_text()
            if t:
                text_list.append(t)
        return "\n".join(text_list)
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""

def extract_qa_pairs(text, pattern_type='numbered'):
    """
    Extracts Q&A pairs from text using regex heuristics.
    """
    qa_list = []
    if pattern_type == 'numbered': # e.g. "1) What is..." or "1. What is..."
        # Match "1) What is..." or "1. What is..."
        pattern = r'(?:^|\n)\s*(\d+)[\.\)]\s*(.*?)(?=(?:\n\s*\d+[\.\)]|\Z))'
        matches = re.findall(pattern, text, re.DOTALL)
        for num, block in matches:
            block = block.strip()
            # Split question and answer
            lines = [l.strip() for l in block.split('\n') if l.strip()]
            if not lines:
                continue
            question = lines[0]
            answer = " ".join(lines[1:]) if len(lines) > 1 else ""
            if len(question) > 5 and len(answer) > 5:
                qa_list.append({'q': question, 'a': answer})
    elif pattern_type == 'q_prefix': # e.g. "Q1) What is... Answer: ..."
        pattern = r'(?:^|\n)\s*Q(\d+)[\.\)]\s*(.*?)(?=(?:\n\s*Q\d+[\.\)]|\Z))'
        matches = re.findall(pattern, text, re.DOTALL)
        for num, block in matches:
            block = block.strip()
            parts = re.split(r'Answer\s*:\s*', block, flags=re.IGNORECASE)
            if len(parts) >= 2:
                q = parts[0].strip()
                a = " ".join(parts[1:]).strip()
                if len(q) > 5 and len(a) > 5:
                    qa_list.append({'q': q, 'a': a})
    return qa_list

print("Extracting Question Banks from PDFs...")

# 1. DBMS Q&A
dbms_pdf = os.path.join(BASE_DIR, 'SEBI Grade A (IT Stream)/02_Database_Concepts_and_SQL/100_DBMS_Interview_Questions_and_Answers.pdf')
dbms_qa = extract_qa_pairs(safe_extract_text(dbms_pdf), 'numbered')
print(f"Extracted {len(dbms_qa)} DBMS Q&A items.")

# 2. OS Q&A
os_pdf = os.path.join(BASE_DIR, 'IBPS SO IT Officer/03_Question_Banks_and_MCQs/Operating_System_Question_Bank.pdf')
os_qa = extract_qa_pairs(safe_extract_text(os_pdf), 'numbered')
print(f"Extracted {len(os_qa)} OS Q&A items.")

# 3. Networking Q&A
net_pdf = os.path.join(BASE_DIR, 'IBPS SO IT Officer/03_Question_Banks_and_MCQs/Networking_Question_Bank.pdf')
net_qa = extract_qa_pairs(safe_extract_text(net_pdf), 'numbered')
print(f"Extracted {len(net_qa)} Networking Q&A items.")

# 4. OOPs Q&A
oops_pdf = os.path.join(BASE_DIR, 'SEBI Grade A (IT Stream)/04_Programming_DSA_and_OOPs/Object_Oriented_Programming_Concepts_and_QnA.pdf')
oops_qa = extract_qa_pairs(safe_extract_text(oops_pdf), 'numbered')
print(f"Extracted {len(oops_qa)} OOPs Q&A items.")

# 5. AWS Q&A
aws_pdf = os.path.join(BASE_DIR, 'SBI Specialist Cadre Officer (IT)/04_Cloud_DevOps_and_Linux/AWS_Cloud_Computing_Interview_Questions.pdf')
aws_qa = extract_qa_pairs(safe_extract_text(aws_pdf), 'q_prefix')
print(f"Extracted {len(aws_qa)} AWS Q&A items.")

# 6. Python Q&A
python_pdf = os.path.join(BASE_DIR, 'SEBI Grade A (IT Stream)/03_Data_Analytics_and_Python/Top_50_Python_Interview_Questions.pdf')
python_qa = extract_qa_pairs(safe_extract_text(python_pdf), 'numbered')
print(f"Extracted {len(python_qa)} Python Q&A items.")

# 7. Testing Q&A
testing_pdf = os.path.join(BASE_DIR, 'SBI Specialist Cadre Officer (IT)/02_Software_Engineering_and_System_Design/Software_Testing_and_QA_Interview_Questions.pdf')
testing_qa = extract_qa_pairs(safe_extract_text(testing_pdf, max_pages=30), 'numbered')
print(f"Extracted {len(testing_qa)} Software Testing Q&A items.")

# 8. Extract Linux cheatbook text
linux_cheat_pdf = os.path.join(BASE_DIR, 'SEBI Grade A (IT Stream)/05_Computer_Networks_and_Operating_Systems/Linux_Unix_Microcheat_Book.pdf')
linux_cheat_text = safe_extract_text(linux_cheat_pdf)

# 9. Extract Normalization guide text
norm_pdf = os.path.join(BASE_DIR, 'SEBI Grade A (IT Stream)/02_Database_Concepts_and_SQL/Database_Normalization_Complete_Guide.pdf')
norm_text = safe_extract_text(norm_pdf, max_pages=6)

# 10. Extract Core DBMS notes
core_dbms_pdf = os.path.join(BASE_DIR, 'SEBI Grade A (IT Stream)/02_Database_Concepts_and_SQL/DBMS_and_SQL_Core_Notes.pdf')
core_dbms_text = safe_extract_text(core_dbms_pdf, max_pages=10)

print("Building Stages and Chapters Curriculum...")

# Build curriculum stages
stages = [
    {
        "id": "stage-1",
        "number": 1,
        "title": "Stage 01: Core Foundation & Data Architecture (DBMS & SQL)",
        "badge": "High-Yield Foundation",
        "description": "Forms 35-40% of professional knowledge in IBPS SO, 30% in SEBI Grade A, and vital SQL interview screening in SBI SCO.",
        "chapters": [
            {
                "id": "ch-1",
                "stage_id": "stage-1",
                "number": 1,
                "title": "Relational Database Concepts, ER Modeling & Integrity Constraints",
                "exams": ["ibps", "sebi", "sbi"],
                "reading_time_mins": 12,
                "summary": "Master Relational Model foundations: Entities, Weak Entity Sets, Keys (Primary, Candidate, Super, Foreign), and Integrity Constraints.",
                "lecture_notes": """### 1. The Relational Database Architecture
A **Database Management System (DBMS)** is system software for storing, managing, and retrieving structured data while maintaining security, concurrency, and integrity.

#### The Three-Schema Architecture (ANSI/SPARC)
1. **Physical / Internal Level:** How data is physically stored on disk blocks, B+ Trees, hashing.
2. **Logical / Conceptual Level:** What data is stored (tables, schemas, relationships, constraints). Completely independent of physical storage (Physical Data Independence).
3. **External / View Level:** User-specific views (e.g. masking sensitive bank customer data such as credit card numbers or hashes). (Logical Data Independence).

---

### 2. Entity-Relationship (ER) Modeling Essentials
* **Entity:** A real-world object (e.g., `Customer`, `BankAccount`, `Transaction`).
* **Strong Entity Set:** Has sufficient attributes to form a primary key. Represented as a single rectangle.
* **Weak Entity Set:** Does not have a primary key of its own; depends on an identifying owner entity set via an identifying relationship. Represented as a **double rectangle** with its partial key (discriminator) underlined with a **dashed line**.
* **Cardinality Ratios:** 1:1 (One-to-One), 1:N (One-to-Many), M:N (Many-to-Many).
  * *Important Rule for Exam:* A Many-to-Many relationship table **always requires a separate junction table** whose primary key is the composite of the two foreign keys.

---

### 3. Key Constraints Hierarchy
1. **Super Key (SK):** Any set of attributes that uniquely identifies a row (e.g., `{RollNo}`, `{RollNo, Name}`).
2. **Candidate Key (CK):** A **minimal** Super Key. No proper subset of a Candidate Key can be a super key.
3. **Primary Key (PK):** The chosen Candidate Key. It cannot accept `NULL` values.
4. **Foreign Key (FK):** Attribute referencing the Primary Key of another relation. Enforces **Referential Integrity**.
   * On deletion of referenced row: `ON DELETE CASCADE`, `ON DELETE SET NULL`, or `ON DELETE RESTRICT`.""",
                "checkpoints": [
                    {
                        "q": "What happens if you try to insert a Foreign Key value that does not exist in the referenced parent table?",
                        "a": "The DBMS rejects the insertion with a Referential Integrity Constraint violation."
                    },
                    {
                        "q": "What is the key difference between a Super Key and a Candidate Key?",
                        "a": "A Candidate Key is a minimal Super Key (removing any attribute destroys uniqueness), whereas a Super Key can contain extraneous attributes."
                    }
                ],
                "quiz": [
                    {
                        "id": 101,
                        "q": "In an Entity-Relationship (ER) model, how is a Weak Entity Set graphically represented?",
                        "options": ["Single Rectangle", "Double Rectangle", "Dashed Ellipse", "Diamond inside Diamond"],
                        "answer": 1,
                        "explanation": "Weak Entity Sets are represented by a double rectangle, and their identifying relationship is represented by a double diamond."
                    },
                    {
                        "id": 102,
                        "q": "Which data independence allows changing the conceptual schema without altering user views or application programs?",
                        "options": ["Physical Data Independence", "Logical Data Independence", "Storage Independence", "Concurrency Independence"],
                        "answer": 1,
                        "explanation": "Logical Data Independence is the capacity to change the conceptual schema without having to change external schemas or application programs."
                    },
                    {
                        "id": 103,
                        "q": "A relation R has candidate keys AB and CD. Which of the following are prime attributes?",
                        "options": ["A, B, C, D", "Only A and C", "Only B and D", "None of these"],
                        "answer": 0,
                        "explanation": "An attribute that is part of ANY candidate key is called a prime attribute. Since AB and CD are candidate keys, A, B, C, and D are all prime attributes."
                    }
                ]
            },
            {
                "id": "ch-2",
                "stage_id": "stage-1",
                "number": 2,
                "title": "Database Normalization: 1NF, 2NF, 3NF, BCNF & Lossless Decomposition",
                "exams": ["ibps", "sebi", "sbi"],
                "reading_time_mins": 15,
                "summary": "Master functional dependencies, identifying minimal covers, normal form tests, and lossless vs dependency-preserving decompositions.",
                "lecture_notes": """### 1. Why Normalize?
Normalization minimizes **Insertion**, **Deletion**, and **Update Anomalies** and eliminates data redundancy.

### 2. Normal Forms Step-by-Step
* **1NF (First Normal Form):**
  * All attribute values are atomic (indivisible). No repeating groups, arrays, or comma-separated values in a single cell.
* **2NF (Second Normal Form):**
  * Table must be in 1NF.
  * **No Partial Dependency:** No non-prime attribute should depend on a *proper subset* of any Candidate Key.
  * *Note:* If every candidate key is a single attribute (not composite), the table is automatically in 2NF!
* **3NF (Third Normal Form):**
  * Table must be in 2NF.
  * **No Transitive Dependency:** No non-prime attribute should depend on another non-prime attribute ($X \\rightarrow Y$ and $Y \\rightarrow Z$).
  * *Formal Rule:* For every non-trivial functional dependency $X \\rightarrow A$:
    * Either $X$ is a **Super Key**, OR
    * $A$ is a **Prime Attribute** (part of some candidate key).
* **BCNF (Boyce-Codd Normal Form - Strict 3NF):**
  * For every non-trivial functional dependency $X \\rightarrow A$, $X$ **MUST** be a **Super Key**.
  * Eliminates anomalies caused by overlapping candidate keys.

---

### 3. Comparison Summary Table
| Normal Form | Condition | Preserves Dependencies? | Eliminates Redundancy? |
| :--- | :--- | :---: | :---: |
| **1NF** | Atomic attributes | Yes | Minimal |
| **2NF** | No partial dependencies | Yes | Partial |
| **3NF** | $X$ is superkey OR $A$ is prime | **Always Guaranteed** | High |
| **BCNF** | $X$ is strictly superkey | Not Always Guaranteed | Maximum |""",
                "checkpoints": [
                    {
                        "q": "If a relation has no composite candidate keys (all candidate keys consist of single attributes), can it violate 2NF?",
                        "a": "No. Partial dependency requires a proper subset of a composite candidate key. Single-attribute candidate keys cannot have proper subsets."
                    },
                    {
                        "q": "Can every relational schema be decomposed into BCNF while preserving all functional dependencies?",
                        "a": "No. 3NF always guarantees dependency preservation; BCNF does not."
                    }
                ],
                "quiz": [
                    {
                        "id": 104,
                        "q": "In functional dependency X -> Y, if Y is a subset of X, what is this dependency called?",
                        "options": ["Non-trivial functional dependency", "Trivial functional dependency", "Transitive dependency", "Multivalued dependency"],
                        "answer": 1,
                        "explanation": "If Y is a subset of X (e.g. {RollNo, Name} -> Name), the dependency is trivial and automatically holds true in all relations."
                    },
                    {
                        "id": 105,
                        "q": "A relation R(A, B, C) has functional dependencies: A -> B and B -> C. Which normal form does it violate?",
                        "options": ["1NF", "2NF", "3NF", "BCNF only"],
                        "answer": 2,
                        "explanation": "A is the candidate key. A -> B and B -> C creates a transitive dependency where non-prime attribute C depends on non-prime attribute B. Hence it violates 3NF."
                    },
                    {
                        "id": 106,
                        "q": "What condition guarantees that a decomposition of R into R1 and R2 is Lossless?",
                        "options": ["R1 union R2 = R", "(R1 intersection R2) -> R1 OR (R1 intersection R2) -> R2", "R1 and R2 have disjoint attributes", "Both R1 and R2 must be in BCNF"],
                        "answer": 1,
                        "explanation": "A decomposition is lossless if and only if the common attributes (R1 intersection R2) functionally determine at least one of the decomposed relations (R1 or R2)."
                    }
                ]
            },
            {
                "id": "ch-3",
                "stage_id": "stage-1",
                "number": 3,
                "title": "Transactions, ACID Properties, Serializability & Concurrency Control",
                "exams": ["ibps", "sebi", "sbi"],
                "reading_time_mins": 14,
                "summary": "ACID properties, Dirty Reads, Conflict vs View Serializability, Two-Phase Locking (2PL), and Deadlocks.",
                "lecture_notes": """### 1. The ACID Properties
* **A - Atomicity:** All operations in a transaction succeed, or all are rolled back. Managed by **Recovery Manager (Undo/Redo Logs)**.
* **C - Consistency:** Database moves from one valid state to another, satisfying all integrity constraints.
* **I - Isolation:** Concurrent transactions execute without interfering with one another. Managed by **Concurrency Control Subsystem**.
* **D - Durability:** Once committed, changes survive system crashes or power failures. Managed by **Write-Ahead Logging (WAL)**.

---

### 2. Concurrency Anomalies
1. **Dirty Read (Write-Read Conflict):** Reading uncommitted data written by another transaction that later rolls back.
2. **Non-Repeatable Read (Read-Write Conflict):** Reading the same row twice within a transaction returns different values because another transaction modified it.
3. **Phantom Read:** Re-executing a range query returns new rows inserted by another committed transaction.

### 3. SQL Isolation Levels
| Isolation Level | Dirty Read | Non-Repeatable Read | Phantom Read |
| :--- | :---: | :---: | :---: |
| **Read Uncommitted** | Possible | Possible | Possible |
| **Read Committed** | Prevented | Possible | Possible |
| **Repeatable Read** | Prevented | Prevented | Possible |
| **Serializable** | Prevented | Prevented | Prevented |

---

### 4. Serializability & Locking Protocols
* **Conflict Serializability:** Tested using a **Precedence Graph**. If the precedence graph has **NO CYCLES**, the schedule is Conflict Serializable.
* **Two-Phase Locking (2PL):**
  * **Growing Phase:** Locks can be acquired, none can be released.
  * **Shrinking Phase:** Locks can be released, none can be acquired.
  * *Guarantee:* Standard 2PL guarantees Conflict Serializability, but can suffer from Cascading Rollbacks and Deadlocks.
  * **Strict 2PL:** Releases exclusive locks only after commit/abort $\\implies$ Prevents cascading aborts!""",
                "checkpoints": [
                    {
                        "q": "Does 2PL (Two-Phase Locking) prevent deadlocks?",
                        "a": "No! 2PL guarantees serializability, but transactions can still enter cyclic wait states leading to deadlocks."
                    },
                    {
                        "q": "Which isolation level prevents Dirty Reads but still allows Non-Repeatable Reads?",
                        "a": "Read Committed."
                    }
                ],
                "quiz": [
                    {
                        "id": 107,
                        "q": "Which component of the DBMS is responsible for guaranteeing the Atomicity and Durability of transactions?",
                        "options": ["Query Optimizer", "Recovery Management / Write-Ahead Logging", "Concurrency Control Manager", "Buffer Pool Manager"],
                        "answer": 1,
                        "explanation": "Recovery Manager using Write-Ahead Logging (WAL) and undo/redo logs ensures transactions can be rolled back upon failure and committed data persists across crashes."
                    },
                    {
                        "id": 108,
                        "q": "If a precedence graph generated from a concurrent schedule contains a cycle, what does this prove?",
                        "options": ["The schedule is deadlock-free", "The schedule is NOT conflict serializable", "The schedule is recoverable", "The schedule is in 3NF"],
                        "answer": 1,
                        "explanation": "A concurrent schedule is conflict serializable if and only if its precedence graph has no directed cycles (can be topologically sorted)."
                    }
                ]
            },
            {
                "id": "ch-4",
                "stage_id": "stage-1",
                "number": 4,
                "title": "SQL Mastery: Joins, Window Functions, Group By & Subqueries",
                "exams": ["ibps", "sebi", "sbi"],
                "reading_time_mins": 14,
                "summary": "Core DDL/DML, Join mechanics, Aggregations with HAVING, Subqueries, and Window Functions (RANK vs DENSE_RANK).",
                "lecture_notes": """### 1. DDL vs DML vs DCL vs TCL
* **DDL (Data Definition):** `CREATE`, `ALTER`, `DROP`, `TRUNCATE`, `RENAME`. Auto-committed in standard relational engines.
* **DML (Data Manipulation):** `SELECT` (DQL), `INSERT`, `UPDATE`, `DELETE`.
* **TCL (Transaction Control):** `COMMIT`, `ROLLBACK`, `SAVEPOINT`.

### 2. TRUNCATE vs DELETE vs DROP
* **DELETE:** DML command. Row-by-row operation. Can be rolled back inside a transaction. Fires row-level triggers. Slower on large tables.
* **TRUNCATE:** DDL command. Deallocates data pages directly. Resets identity seed. Cannot be rolled back in standard SQL. Bypasses DML triggers. Much faster.
* **DROP:** Removes table structure and all data permanently.

---

### 3. Window Functions (Crucial for SEBI & SBI SCO)
Window functions perform calculations across a set of table rows related to the current row without collapsing them into a single row like `GROUP BY`:
* `ROW_NUMBER()`: Assigns a unique sequential integer (1, 2, 3, 4...).
* `RANK()`: Assigns rank; ties get the same rank and skip subsequent ranks (1, 2, 2, 4...).
* `DENSE_RANK()`: Assigns rank; ties get the same rank WITHOUT skipping (1, 2, 2, 3...).

```sql
-- Finding 2nd Highest Salary per Department:
SELECT dept_id, emp_name, salary
FROM (
    SELECT dept_id, emp_name, salary,
           DENSE_RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) as rnk
    FROM Employees
) sub
WHERE sub.rnk = 2;
```""",
                "checkpoints": [
                    {
                        "q": "What does a query return if you write `WHERE salary = NULL`?",
                        "a": "It returns 0 rows, because NULL compared to anything with '=' evaluates to UNKNOWN. You must write `WHERE salary IS NULL`."
                    }
                ],
                "quiz": [
                    {
                        "id": 109,
                        "q": "What is the difference between RANK() and DENSE_RANK() when two rows share the second position?",
                        "options": ["RANK() gives (1, 2, 2, 3) while DENSE_RANK() gives (1, 2, 2, 4)", "RANK() gives (1, 2, 2, 4) while DENSE_RANK() gives (1, 2, 2, 3)", "Both produce identical ranks", "DENSE_RANK() cannot use PARTITION BY"],
                        "answer": 1,
                        "explanation": "RANK() leaves gaps after ties (1, 2, 2, 4), whereas DENSE_RANK() does not leave gaps (1, 2, 2, 3)."
                    },
                    {
                        "id": 110,
                        "q": "Which clause must be used to filter aggregated results generated by a GROUP BY query?",
                        "options": ["WHERE", "HAVING", "LIMIT", "ORDER BY"],
                        "answer": 1,
                        "explanation": "WHERE filters rows before grouping; HAVING filters the aggregated groups after GROUP BY is applied."
                    }
                ]
            }
        ]
    },
    {
        "id": "stage-2",
        "number": 2,
        "title": "Stage 02: Systems, Networks & Infrastructure",
        "badge": "High Weightage",
        "description": "Crucial for IBPS SO IT (25-30% questions), SEBI Grade A Paper 2, and SBI SCO systems engineering.",
        "chapters": [
            {
                "id": "ch-5",
                "stage_id": "stage-2",
                "number": 5,
                "title": "OSI 7-Layer & TCP/IP Architecture, PDU Encapsulation & Network Devices",
                "exams": ["ibps", "sebi", "sbi"],
                "reading_time_mins": 14,
                "summary": "OSI reference model layers, PDUs, Physical layer devices, switches, routers, and encapsulation headers.",
                "lecture_notes": """### 1. The 7 Layers of OSI Model
1. **Physical (Layer 1):** Unstructured raw bit stream over physical medium. Devices: Hub, Repeater.
2. **Data Link (Layer 2):** Framing, Physical (MAC) addressing, error detection (CRC). Devices: Switch, Bridge.
3. **Network (Layer 3):** Packets, Logical (IP) addressing, routing. Protocols: IP, ICMP, ARP. Device: Router.
4. **Transport (Layer 4):** Segments / Datagrams. Process-to-process communication, port numbers, flow/error control. Protocols: TCP, UDP.
5. **Session (Layer 5):** Dialog control, synchronization tokens, checkpoints.
6. **Presentation (Layer 6):** Data translation, encryption/decryption, compression (JPEG, ASCII, TLS).
7. **Application (Layer 7):** Network virtual terminal, user interface. Protocols: HTTP, DNS, SMTP, FTP.

---

### 2. Protocol Data Units (PDUs)
* Layer 7 to 5: **Data / Message**
* Layer 4: **Segment** (TCP) / **Datagram** (UDP)
* Layer 3: **Packet**
* Layer 2: **Frame** (Header + Payload + CRC Trailer)
* Layer 1: **Bits**""",
                "checkpoints": [
                    {
                        "q": "At which layer of the OSI model does a Network Switch primarily operate?",
                        "a": "Data Link Layer (Layer 2), inspecting hardware MAC addresses."
                    }
                ],
                "quiz": [
                    {
                        "id": 201,
                        "q": "Which OSI layer is responsible for data encryption, decryption, and compression?",
                        "options": ["Session Layer", "Presentation Layer", "Application Layer", "Transport Layer"],
                        "answer": 1,
                        "explanation": "The Presentation Layer (Layer 6) handles syntax and semantics of information exchanged, including encryption and compression."
                    },
                    {
                        "id": 202,
                        "q": "What is the PDU (Protocol Data Unit) at the Transport Layer called for TCP?",
                        "options": ["Frame", "Packet", "Segment", "Bitstream"],
                        "answer": 2,
                        "explanation": "The Transport Layer PDU for TCP is a Segment; for UDP it is a Datagram."
                    }
                ]
            },
            {
                "id": "ch-6",
                "stage_id": "stage-2",
                "number": 6,
                "title": "Transport & Application Protocols: TCP 3-Way Handshake, UDP, DNS & HTTP",
                "exams": ["ibps", "sebi", "sbi"],
                "reading_time_mins": 15,
                "summary": "Deep dive into TCP connection establishment, sequence numbers, TIME_WAIT, UDP, DNS, and HTTP/HTTPS.",
                "lecture_notes": """### 1. TCP 3-Way Handshake
1. **Client $\\rightarrow$ Server:** `SYN` (Seq = x)
2. **Server $\\rightarrow$ Client:** `SYN + ACK` (Seq = y, Ack = x + 1)
3. **Client $\\rightarrow$ Server:** `ACK` (Seq = x + 1, Ack = y + 1)
* Once step 3 is transmitted, connection state becomes `ESTABLISHED`.

### 2. Connection Teardown & TIME_WAIT
* Active close sends `FIN` $\\rightarrow$ Peer sends `ACK` $\\rightarrow$ Peer sends `FIN` $\\rightarrow$ Active close sends `ACK` and enters `TIME_WAIT`.
* **Why TIME_WAIT (2MSL)?**
  1. Guarantees the remote peer receives the final ACK (if ACK was lost, peer re-sends FIN).
  2. Allows old duplicate packets to expire in the network before a new socket reuses the port.

### 3. TCP vs UDP Header Comparison
* **TCP Header:** 20 to 60 Bytes (minimum 20 bytes). Contains Sequence number, Ack number, Window size, Flags (SYN, ACK, FIN, RST, PSH, URG), Checksum.
* **UDP Header:** Fixed 8 Bytes! (Source Port 16b, Dest Port 16b, Length 16b, Checksum 16b). Low latency, no handshakes.""",
                "checkpoints": [
                    {
                        "q": "What is the size of a standard UDP header?",
                        "a": "Exactly 8 bytes (64 bits)."
                    }
                ],
                "quiz": [
                    {
                        "id": 203,
                        "q": "What is the purpose of the TIME_WAIT state in TCP connection termination?",
                        "options": ["To calculate RTT for next connection", "To ensure final ACK arrives and linger packets expire", "To authenticate credentials", "To flush DNS cache"],
                        "answer": 1,
                        "explanation": "TIME_WAIT ensures the final ACK reached the other end and allows lingering duplicate packets to expire safely (lasting 2 Maximum Segment Lifetimes)."
                    },
                    {
                        "id": 204,
                        "q": "Which protocol uses UDP port 53 for standard name resolution queries?",
                        "options": ["HTTP", "DNS", "DHCP", "FTP"],
                        "answer": 1,
                        "explanation": "DNS (Domain Name System) uses UDP port 53 for quick lookup queries, and TCP port 53 for large zone transfers."
                    }
                ]
            },
            {
                "id": "ch-7",
                "stage_id": "stage-2",
                "number": 7,
                "title": "IPv4 Subnetting, CIDR Calculations & Routing Algorithms",
                "exams": ["ibps", "sebi", "sbi"],
                "reading_time_mins": 15,
                "summary": "Subnet masks, calculating network/broadcast IDs, usable host ranges, and Distance Vector vs Link State routing.",
                "lecture_notes": """### 1. IPv4 Address Classes
* **Class A:** 1.0.0.0 to 126.255.255.255 (Default Mask: 255.0.0.0 or /8)
* **Class B:** 128.0.0.0 to 191.255.255.255 (Default Mask: 255.255.0.0 or /16)
* **Class C:** 192.0.0.0 to 223.255.255.255 (Default Mask: 255.255.255.0 or /24)
* **Class D:** 224.0.0.0 to 239.255.255.255 (Multicasting)
* **Class E:** 240.0.0.0 to 254.255.255.255 (Experimental / Research)
* *Note:* `127.0.0.0/8` is reserved for Loopback testing.

### 2. CIDR Subnetting Formulas
* Subnet bits borrowed = $N - \\text{default prefix}$.
* Total Subnets created = $2^{(\\text{borrowed bits})}$.
* Host bits remaining = $32 - N$.
* **Total IP addresses per subnet:** $2^{(32 - N)}$.
* **Usable Host addresses per subnet:** $2^{(32 - N)} - 2$ (Subtract Network ID and Broadcast ID).

---

### 3. Routing Protocols
* **Distance Vector (RIP):** Uses Hop Count (Maximum 15 hops, 16 is unreachable). Bellman-Ford algorithm. Suffers from Count-to-Infinity problem (solved via Split Horizon and Poison Reverse).
* **Link State (OSPF):** Uses Bandwidth / Cost. Dijkstra's Shortest Path First (SPF) algorithm. Fast convergence, no hop limit.""",
                "checkpoints": [
                    {
                        "q": "How many usable hosts can be configured on a subnet with mask /28?",
                        "a": "Host bits = 32 - 28 = 4. Usable hosts = 2^4 - 2 = 14."
                    }
                ],
                "quiz": [
                    {
                        "id": 205,
                        "q": "What is the maximum hop count allowed by the Routing Information Protocol (RIP) before a destination is declared unreachable?",
                        "options": ["15", "16", "255", "30"],
                        "answer": 0,
                        "explanation": "RIP defines 15 as the maximum valid hop count; a metric of 16 indicates that the network is unreachable."
                    },
                    {
                        "id": 206,
                        "q": "Given IP address 192.168.1.130 with subnet mask 255.255.255.192 (/26), what is the Network ID?",
                        "options": ["192.168.1.0", "192.168.1.128", "192.168.1.64", "192.168.1.192"],
                        "answer": 1,
                        "explanation": "Block size = 256 - 192 = 64. Subnets are .0, .64, .128, .192. IP .130 falls into the subnet starting at 192.168.1.128."
                    }
                ]
            },
            {
                "id": "ch-8",
                "stage_id": "stage-2",
                "number": 8,
                "title": "Operating Systems: Process Lifecycle & CPU Scheduling Algorithms",
                "exams": ["ibps", "sebi", "sbi"],
                "reading_time_mins": 15,
                "summary": "Process states, PCB, Context Switching, FCFS Convoy Effect, SJF/SRTF optimality, Round Robin, and Turnaround/Waiting times.",
                "lecture_notes": """### 1. Process Lifecycle States
* **New $\\rightarrow$ Ready $\\rightarrow$ Running $\\rightarrow$ Waiting/Blocked $\\rightarrow$ Terminated.**
* **Long-Term Scheduler (Job Scheduler):** Controls degree of multiprogramming by moving jobs from disk pool into Ready queue.
* **Short-Term Scheduler (CPU Scheduler):** Selects which ready process executes on the CPU core.
* **Context Switching:** Saving state of running process into its Process Control Block (PCB) and restoring state of newly selected process. Pure overhead!

---

### 2. CPU Scheduling Metrics
* **Turnaround Time (TAT):** $\\text{Completion Time} - \\text{Arrival Time}$
* **Waiting Time (WT):** $\\text{Turnaround Time} - \\text{Burst Time}$
* **Response Time:** Time from arrival to first execution on CPU.

### 3. Scheduling Algorithms
* **FCFS:** Non-preemptive. Simple, but suffers from the **Convoy Effect** (short interactive jobs delayed behind long CPU-bound tasks).
* **SJF (Shortest Job First):** Provably optimal in minimizing average waiting time. Preemptive version is called **SRTF** (Shortest Remaining Time First). May cause starvation.
* **Round Robin (RR):** Preemptive based on Time Quantum $q$. If $q$ is too large $\\implies$ degenerates to FCFS. If $q$ is too small $\\implies$ high context-switch overhead.""",
                "checkpoints": [
                    {
                        "q": "Which scheduling algorithm is provably optimal for minimizing average waiting time?",
                        "a": "Shortest Job First (SJF) / Shortest Remaining Time First (SRTF)."
                    }
                ],
                "quiz": [
                    {
                        "id": 207,
                        "q": "What is the phenomenon in FCFS where short processes wait a long time for a single big CPU-bound process to release the CPU?",
                        "options": ["Starvation", "Convoy Effect", "Belady's Anomaly", "Priority Inversion"],
                        "answer": 1,
                        "explanation": "The Convoy Effect occurs in FCFS when small processes queue up behind a massive process, drastically degrading CPU and device utilization."
                    },
                    {
                        "id": 208,
                        "q": "If the time quantum in a Round Robin scheduling algorithm is set to extremely large, how does it behave?",
                        "options": ["It behaves like Shortest Job First", "It behaves like First-Come First-Served (FCFS)", "It causes frequent deadlocks", "It minimizes response time"],
                        "answer": 1,
                        "explanation": "If the time quantum is larger than the burst time of every process, no process is preempted and Round Robin degenerates into FCFS."
                    }
                ]
            },
            {
                "id": "ch-9",
                "stage_id": "stage-2",
                "number": 9,
                "title": "Deadlocks, Banker's Algorithm, Paging & Virtual Memory",
                "exams": ["ibps", "sebi", "sbi"],
                "reading_time_mins": 16,
                "summary": "Coffman conditions, Deadlock avoidance via Banker's algorithm, Paging, Page Faults, and Belady's Anomaly.",
                "lecture_notes": """### 1. The 4 Coffman Conditions for Deadlock
Deadlock occurs IF AND ONLY IF all 4 conditions hold simultaneously:
1. **Mutual Exclusion:** At least one non-shareable resource.
2. **Hold and Wait:** A process holds at least one resource while waiting for another.
3. **No Preemption:** Resources cannot be forcibly taken from a process.
4. **Circular Wait:** A closed chain of processes, each waiting for a resource held by the next.

* **Prevention:** Invalidate at least one condition (e.g. impose total ordering on all resource types to prevent Circular Wait).
* **Avoidance:** **Banker's Algorithm** ensures the system remains in a **Safe State** before granting allocation.

---

### 2. Memory Paging & Virtual Memory
* **Paging:** Divides physical memory into fixed-size **Frames**, and logical memory into same-size **Pages**.
  * Eliminates **External Fragmentation**, but suffers from **Internal Fragmentation** in the last page frame.
* **Translation Lookaside Buffer (TLB):** Fast hardware cache storing recent page table translations.
* **Page Replacement Algorithms:**
  * **FIFO:** Replaces oldest page. Suffers from **Belady's Anomaly** (increasing frame count increases page faults!).
  * **LRU (Least Recently Used):** Replaces page not used for the longest time. Stack algorithm; immune to Belady's Anomaly.
  * **Optimal (OPT):** Replaces page that will not be used for longest duration in the future. Benchmark algorithm.""",
                "checkpoints": [
                    {
                        "q": "What type of memory fragmentation is present in a Paged memory architecture?",
                        "a": "Internal Fragmentation (within the final allocated page frame)."
                    }
                ],
                "quiz": [
                    {
                        "id": 209,
                        "q": "Which page replacement algorithm can experience Belady's Anomaly?",
                        "options": ["LRU (Least Recently Used)", "FIFO (First In First Out)", "Optimal Algorithm", "LFU (Least Frequently Used)"],
                        "answer": 1,
                        "explanation": "FIFO can exhibit Belady's Anomaly, where giving more memory frames to a process paradoxically increases the number of page faults."
                    },
                    {
                        "id": 210,
                        "q": "What is the Need matrix formula in Dijkstra's Banker's algorithm?",
                        "options": ["Need = Max - Allocation", "Need = Allocation + Available", "Need = Max + Allocation", "Need = Max - Available"],
                        "answer": 0,
                        "explanation": "In Banker's algorithm, Need[i][j] = Max[i][j] - Allocation[i][j]."
                    }
                ]
            },
            {
                "id": "ch-10",
                "stage_id": "stage-2",
                "number": 10,
                "title": "Unix & Linux Administration, Shell Commands & Permissions",
                "exams": ["ibps", "sebi", "sbi"],
                "reading_time_mins": 12,
                "summary": "Linux file hierarchy, permissions (chmod, chown), process inspection (ps, top, kill), pipelines, grep, awk, and sed.",
                "lecture_notes": """### 1. Essential Linux Commands
* **File Operations:**
  * `ls -la`: List all files including hidden with detailed permissions.
  * `chmod 754 file`: User=rwx (7), Group=r-x (5), Others=r-- (4).
  * `chown user:group file`: Change owner and group.
* **Process Management:**
  * `ps aux` / `top` / `htop`: Inspect active running processes and CPU/RAM usage.
  * `kill -9 <PID>`: Send SIGKILL to immediately terminate process.
* **Text Processing & Pipelines:**
  * `grep -i "error" server.log`: Case-insensitive pattern search.
  * `awk '{print $1, $3}' access.log`: Column parsing.
  * `sed 's/foo/bar/g' file.txt`: Stream editor search and replace.
  * `find /var/log -name "*.log" -mtime -7`: Find files modified in last 7 days.""",
                "checkpoints": [
                    {
                        "q": "In Linux permissions, what does octal 755 represent?",
                        "a": "User has Read/Write/Execute (7), Group has Read/Execute (5), Others have Read/Execute (5)."
                    }
                ],
                "quiz": [
                    {
                        "id": 211,
                        "q": "Which signal number is sent by default with the command 'kill -9 <pid>' in Linux?",
                        "options": ["SIGTERM (15)", "SIGKILL (9)", "SIGHUP (1)", "SIGINT (2)"],
                        "answer": 1,
                        "explanation": "Signal 9 is SIGKILL, which forces immediate process termination and cannot be caught or ignored."
                    }
                ]
            }
        ]
    },
    {
        "id": "stage-3",
        "number": 3,
        "title": "Stage 03: Software Engineering, OOPs & Algorithms",
        "badge": "Core Coding & Design",
        "description": "Essential for SEBI Grade A Phase 2 Coding, SBI SCO Deputy Manager Technical Interviews, and IBPS SO.",
        "chapters": [
            {
                "id": "ch-11",
                "stage_id": "stage-3",
                "number": 11,
                "title": "OOPs Paradigms & SOLID Software Architecture Principles",
                "exams": ["sebi", "sbi", "ibps"],
                "reading_time_mins": 14,
                "summary": "Encapsulation, Polymorphism, Abstraction, Inheritance, and the 5 SOLID design principles with Java examples.",
                "lecture_notes": """### 1. The 4 Pillars of OOPs
1. **Encapsulation:** Bundling data and functions operating on that data within a class, hiding internal implementation via private variables and public getters/setters.
2. **Abstraction:** Exposing only relevant details to the outside world while hiding complex internal logic (Abstract classes & Interfaces).
3. **Inheritance:** Mechanism where a child class acquires properties of a parent class (Code reusability).
4. **Polymorphism:**
   * **Compile-time (Static):** Method Overloading (same method name, different parameter signature). Resolved at compile-time.
   * **Runtime (Dynamic):** Method Overriding (subclass redefines parent method with identical signature). Resolved dynamically via virtual method table (**vtable**).

---

### 2. The SOLID Principles
* **S - Single Responsibility Principle:** A class should have one, and only one, reason to change.
* **O - Open/Closed Principle:** Software artifacts should be **open for extension**, but **closed for modification**.
* **L - Liskov Substitution Principle:** Subtypes must be substitutable for their base types without breaking program behavior.
* **I - Interface Segregation Principle:** Clients should not be forced to depend on interfaces they do not use (prefer small, role-specific interfaces).
* **D - Dependency Inversion Principle:** High-level modules should not depend on low-level modules; both should depend on abstractions.""",
                "checkpoints": [
                    {
                        "q": "Why can static methods not be overridden in Java?",
                        "a": "Static methods are bound at compile-time to the class type (Static Binding), not resolved via runtime dynamic dispatch."
                    }
                ],
                "quiz": [
                    {
                        "id": 301,
                        "q": "Which SOLID principle states that high-level modules should depend on abstractions rather than concrete classes?",
                        "options": ["Single Responsibility Principle", "Liskov Substitution Principle", "Dependency Inversion Principle", "Open/Closed Principle"],
                        "answer": 2,
                        "explanation": "Dependency Inversion Principle (DIP) states that high-level modules should not depend on low-level modules; both should depend on abstractions (interfaces)."
                    },
                    {
                        "id": 302,
                        "q": "In Java, what occurs if a subclass defines a static method with the exact same name and signature as a static method in its parent class?",
                        "options": ["Method Overriding", "Method Hiding", "Compilation Error", "Runtime Exception"],
                        "answer": 1,
                        "explanation": "Static methods cannot be overridden; re-declaring them in a subclass is known as Method Hiding."
                    }
                ]
            },
            {
                "id": "ch-12",
                "stage_id": "stage-3",
                "number": 12,
                "title": "Java Backend Core, JVM Memory Management & Collections Framework",
                "exams": ["sebi", "sbi", "ibps"],
                "reading_time_mins": 15,
                "summary": "JVM architecture, Garbage Collection generations, HashMap internal buckets and treeification, ArrayList vs LinkedList.",
                "lecture_notes": """### 1. JVM Memory Model
* **Stack:** Stores method invocation frames, local primitive variables, and references to objects. Thread-isolated.
* **Heap:** Shared memory pool storing all instantiated objects and class member variables. Managed by the **Garbage Collector**.
* **Metaspace (Java 8+):** Stores class metadata in native memory (replaced PermGen).

### 2. Generational Garbage Collection
* **Young Generation:**
  * **Eden Space:** All newly created objects are allocated here.
  * **Survivor Spaces (S0 and S1):** Objects that survive Minor GC are moved between S0 and S1 with an aging counter.
* **Tenured / Old Generation:** Long-surviving objects promoted from Young gen. Cleaned by Major / Full GC.

---

### 3. Java Collections Framework & HashMap Internals
* **HashMap Structure:** Array of buckets (Node objects with hash, key, value, next).
  * **Index Formula:** `index = (n - 1) & hash(key)`.
  * **Collision Resolution:** Chaining with singly linked list.
  * **Java 8 Treeification:** When a bucket reaches $\\ge 8$ elements (`TREEIFY_THRESHOLD`) and table capacity $\\ge 64$, the linked list converts to a **Red-Black Tree** to guarantee $O(\\log N)$ worst-case search instead of $O(N)$!
* **ConcurrentHashMap:** Uses node-level locking (CAS + synchronized blocks) rather than synchronizing the entire map.""",
                "checkpoints": [
                    {
                        "q": "What happens if you override equals() in Java without overriding hashCode()?",
                        "a": "Equal objects will generate different hash codes, violating the Java specification and causing HashMaps and HashSets to lose or duplicate elements."
                    }
                ],
                "quiz": [
                    {
                        "id": 303,
                        "q": "In Java 8, when does a HashMap bucket convert its linked list into a balanced Red-Black Tree?",
                        "options": ["When bucket size reaches 4", "When bucket size reaches 8 and capacity >= 64", "When total elements reach 100", "HashMap never uses trees"],
                        "answer": 1,
                        "explanation": "When the number of colliding elements in a bucket reaches TREEIFY_THRESHOLD (8) and the overall array capacity is at least 64, it converts into a Red-Black Tree."
                    }
                ]
            },
            {
                "id": "ch-13",
                "stage_id": "stage-3",
                "number": 13,
                "title": "Data Structures & Algorithms: Trees, Heaps, Graphs & Complexities",
                "exams": ["sebi", "sbi", "ibps"],
                "reading_time_mins": 16,
                "summary": "Binary Search Trees, Heaps, Graph traversals (BFS/DFS), Dijkstra, Kruskal, and Master Theorem for complexities.",
                "lecture_notes": """### 1. Binary Search Trees & Heaps
* **BST Property:** For every node $N$, all keys in the left subtree $< N$, and all keys in the right subtree $> N$.
  * **Inorder Traversal:** Inorder traversal (Left $\\rightarrow$ Root $\\rightarrow$ Right) of a BST **always yields sorted ascending order**!
* **Binary Heap:**
  * Complete binary tree where parent $\\le$ children (Min-Heap) or parent $\\ge$ children (Max-Heap).
  * BuildHeap on unsorted array of size $N$ takes $O(N)$ time.
  * Insert: $O(\\log N)$, Extract Min/Max: $O(\\log N)$.

---

### 2. Graphs & Traversal
* **Breadth-First Search (BFS):** Uses a **Queue**. Finds shortest path in unweighted graphs. Time: $O(V + E)$.
* **Depth-First Search (DFS):** Uses a **Stack / Recursion**. Detects cycles, topological sorting in DAG. Time: $O(V + E)$.
* **Dijkstra's Shortest Path:** Greedy algorithm using Min-Heap priority queue. Time: $O((V + E) \\log V)$. **Fails with negative weight edges!**
* **Minimum Spanning Tree (MST):**
  * **Kruskal's Algorithm:** Greedy on edges with Disjoint Set Union (DSU). Time: $O(E \\log E)$.
  * **Prim's Algorithm:** Greedy on vertices using priority queue. Time: $O(E \\log V)$.""",
                "checkpoints": [
                    {
                        "q": "What traversal on a Binary Search Tree produces elements in sorted ascending order?",
                        "a": "Inorder traversal (Left, Root, Right)."
                    }
                ],
                "quiz": [
                    {
                        "id": 304,
                        "q": "What is the time complexity of building a Binary Heap from an unsorted array of N elements?",
                        "options": ["O(N log N)", "O(N)", "O(log N)", "O(N^2)"],
                        "answer": 1,
                        "explanation": "Using bottom-up heapification, the geometric series summation converges to O(N) time complexity."
                    },
                    {
                        "id": 305,
                        "q": "Can Dijkstra's algorithm find correct shortest paths in graphs containing negative edge weights?",
                        "options": ["Yes, always", "No, it requires Bellman-Ford for negative weights", "Yes, if the graph is a DAG", "Yes, if weights are integers"],
                        "answer": 1,
                        "explanation": "Dijkstra's algorithm assumes edge weights are non-negative and can fail or loop infinitely if negative edge weights/cycles exist."
                    }
                ]
            },
            {
                "id": "ch-14",
                "stage_id": "stage-3",
                "number": 14,
                "title": "Software Engineering Lifecycles (SDLC, Agile) & Software Testing/QA",
                "exams": ["ibps", "sbi", "sebi"],
                "reading_time_mins": 13,
                "summary": "Waterfall, Spiral, Agile/Scrum ceremonies, Black-box vs White-box testing, Unit, Integration, and Regression testing.",
                "lecture_notes": """### 1. SDLC Methodologies
* **Waterfall Model:** Sequential phases. Requirements must be frozen upfront. High risk, late testing.
* **Spiral Model:** Risk-driven iterative model. Best suited for high-budget, mission-critical systems.
* **Agile & Scrum Framework:**
  * Iterative sprints (typically 2-4 weeks).
  * **Scrum Ceremonies:** Sprint Planning, Daily Standup (15 mins), Sprint Review (demo), Sprint Retrospective.
  * **Scrum Roles:** Product Owner, Scrum Master, Development Team.

---

### 2. Software Testing & Quality Assurance
* **Black-Box Testing:** Testing software functionality without knowledge of internal code logic (Boundary Value Analysis, Equivalence Partitioning).
* **White-Box Testing:** Testing internal structures and control flow (Statement coverage, Branch coverage, Path coverage).
* **Testing Levels:**
  1. **Unit Testing:** Individual components/classes tested in isolation (JUnit, Mockito).
  2. **Integration Testing:** Testing interactions between integrated modules.
  3. **System Testing:** End-to-end functional and non-functional validation.
  4. **Regression Testing:** Re-running test suites after bug fixes or new features to ensure existing functionality remains un-broken.""",
                "checkpoints": [
                    {
                        "q": "What is the primary objective of Regression Testing?",
                        "a": "To ensure that recent code modifications or fixes have not introduced new defects into previously working features."
                    }
                ],
                "quiz": [
                    {
                        "id": 306,
                        "q": "Which SDLC model incorporates explicit risk assessment and prototyping in each iterative cycle?",
                        "options": ["Waterfall Model", "Spiral Model", "V-Model", "RAD Model"],
                        "answer": 1,
                        "explanation": "The Spiral Model, introduced by Barry Boehm, is explicitly risk-driven."
                    }
                ]
            }
        ]
    },
    {
        "id": "stage-4",
        "number": 4,
        "title": "Stage 04: Advanced Architecture & Cloud (SBI SCO Focus)",
        "badge": "Enterprise Systems",
        "description": "Crucial for SBI SCO Deputy Manager (Developer / Systems) technical screening and in-depth architecture interview.",
        "chapters": [
            {
                "id": "ch-15",
                "stage_id": "stage-4",
                "number": 15,
                "title": "System Design: Scalability, Caching (Redis), Message Queues (Kafka) & CAP",
                "exams": ["sbi", "sebi"],
                "reading_time_mins": 16,
                "summary": "Vertical vs Horizontal scaling, Load Balancers, Redis Cache-Aside, Kafka message streaming, and Brewer's CAP Theorem.",
                "lecture_notes": """### 1. Scaling Patterns & Load Balancing
* **Vertical Scaling:** Increasing CPU/RAM on a single machine (hardware limits, single point of failure).
* **Horizontal Scaling:** Adding more commodity server instances behind a **Load Balancer**.
* **Load Balancing Algorithms:** Round Robin, Least Connections, IP Hash (for session stickiness).

---

### 2. Caching & The Cache-Aside Pattern
* **Redis / Memcached:** In-memory key-value data stores delivering sub-millisecond read access.
* **Cache-Aside Flow:**
  1. Application checks Redis for Key.
  2. **Cache Hit:** Returns data immediately.
  3. **Cache Miss:** Queries primary relational database, writes result into Redis with a **TTL (Time to Live)**, and returns data.
* **Cache Stampede / Dog-piling:** Multiple concurrent requests hit the DB when a high-traffic cache key expires. Mitigated by mutex locks or probabilistic early refreshing.

---

### 3. Asynchronous Messaging: Apache Kafka
* **Kafka Architecture:** Producers, Topics, Partitions, Brokers, and Consumer Groups.
* **Partitions:** Unit of horizontal scalability in Kafka. Messages with the same partition key always route to the same partition, guaranteeing **ordered delivery per key**.

---

### 4. Brewer's CAP Theorem
In a distributed asynchronous network subject to network partitions (P), a system can guarantee **Consistency (C)** OR **Availability (A)**, but **never both simultaneously**:
* **CP Systems:** (e.g. MongoDB, HBase, Zookeeper). Rejects writes or returns errors if nodes cannot sync to avoid returning stale data.
* **AP Systems:** (e.g. Cassandra, DynamoDB). Accepts writes and reads locally; guarantees eventual consistency.""",
                "checkpoints": [
                    {
                        "q": "Why does Kafka partition topics?",
                        "a": "To allow parallel message processing across multiple consumer instances in a consumer group and distribute storage across brokers."
                    }
                ],
                "quiz": [
                    {
                        "id": 401,
                        "q": "According to the CAP Theorem, why can a distributed system not provide both Consistency and Availability during a network partition?",
                        "options": ["Hardware CPUs lack multi-threading", "If network links fail, nodes must choose between returning stale data (Available) or refusing requests (Consistent)", "Database normalization prevents it", "TCP handshakes time out"],
                        "answer": 1,
                        "explanation": "When network partition P occurs, a system must either continue answering with potentially out-of-sync local data (Availability) or wait/error until partitions heal (Consistency)."
                    }
                ]
            },
            {
                "id": "ch-16",
                "stage_id": "stage-4",
                "number": 16,
                "title": "Microservices Architecture, Spring Boot & RESTful APIs",
                "exams": ["sbi", "sebi"],
                "reading_time_mins": 15,
                "summary": "Monolith vs Microservices tradeoffs, Spring Boot IoC annotations, API Gateway, Circuit Breaker (Resilience4j), and JWT.",
                "lecture_notes": """### 1. Spring Boot & Dependency Injection
* **Inversion of Control (IoC):** The Spring container creates, manages, and injects object dependencies rather than objects instantiating them manually via `new`.
* **Key Annotations:**
  * `@RestController`: Combines `@Controller` and `@ResponseBody` for JSON API endpoints.
  * `@Service`: Marks business logic layer.
  * `@Repository`: Marks data access layer, automatically translating database exceptions.
  * `@Autowired`: Injects bean dependencies (Constructor injection is preferred for immutability and testability).

---

### 2. Distributed Microservices Resilience
* **API Gateway:** Central entry point handling authentication, TLS termination, request routing, and rate limiting.
* **Circuit Breaker Pattern (Resilience4j):**
  * **Closed:** Normal operation; requests pass through.
  * **Open:** If failure rate exceeds threshold (e.g. 50%), requests immediately fail-fast without hitting the failing downstream service.
  * **Half-Open:** After a cool-down duration, a limited number of test requests are allowed to check if the downstream service has recovered.""",
                "checkpoints": [
                    {
                        "q": "What HTTP status code is returned when a client is authenticated but lacks required authorization roles?",
                        "a": "403 Forbidden (401 is for unauthenticated requests)."
                    }
                ],
                "quiz": [
                    {
                        "id": 402,
                        "q": "In a Microservices architecture, what is the primary role of a Circuit Breaker pattern?",
                        "options": ["To encrypt all REST payloads", "To prevent a single failing microservice from causing cascading failures across the entire cluster", "To load balance between database replicas", "To generate JWT tokens"],
                        "answer": 1,
                        "explanation": "Circuit Breakers fail fast and return fallback responses when a downstream dependency fails, preventing thread exhaustion and cascading system outages."
                    }
                ]
            },
            {
                "id": "ch-17",
                "stage_id": "stage-4",
                "number": 17,
                "title": "Cloud Computing Fundamentals (AWS Architecture) & Docker Containers",
                "exams": ["sbi", "sebi"],
                "reading_time_mins": 14,
                "summary": "AWS EC2, S3, IAM, VPC, Docker containerization, Dockerfile instructions, and Kubernetes orchestration fundamentals.",
                "lecture_notes": """### 1. AWS Core Services
* **Compute (Amazon EC2):** Scalable virtual servers. Instance types: General Purpose, Compute Optimized, Memory Optimized.
* **Storage:**
  * **Amazon S3:** Object storage designed for 99.999999999% (11 9's) durability. Buckets and keys.
  * **Amazon EBS:** Block storage volumes attached to EC2 instances.
* **Networking (Amazon VPC):** Isolated virtual network in the cloud. Contains Subnets (Public & Private), Internet Gateways, NAT Gateways, Route Tables, and Security Groups (stateful) vs Network ACLs (stateless).
* **Security (AWS IAM):** Users, Groups, Roles (temporary STS credentials), and JSON Policies.

---

### 2. Docker Containers vs Virtual Machines
* **Virtual Machines:** Hypervisor virtualizes hardware; each VM carries its own full Guest OS (heavy, slow boot).
* **Containers:** Share the Host OS kernel; isolated using Linux **Namespaces** (PID, Net, Mount) and **Cgroups** (CPU/RAM limits). Lightweight, starts in milliseconds.
* **Key Dockerfile Commands:**
  * `FROM`: Base image.
  * `WORKDIR`: Working directory.
  * `COPY`: Copy files from host to container.
  * `RUN`: Execute build commands.
  * `ENTRYPOINT` vs `CMD`: Default executable and default arguments.""",
                "checkpoints": [
                    {
                        "q": "Are AWS Security Groups stateful or stateless?",
                        "a": "Stateful (if inbound traffic is allowed, return outbound traffic is automatically allowed regardless of outbound rules)."
                    }
                ],
                "quiz": [
                    {
                        "id": 403,
                        "q": "Which Linux kernel feature enables Docker to isolate process IDs, network interfaces, and file systems between containers?",
                        "options": ["Cgroups", "Namespaces", "SELinux", "Swap Memory"],
                        "answer": 1,
                        "explanation": "Linux Namespaces provide isolated workspaces (PID, NET, MNT, IPC, UTS) for containers, while Cgroups enforce CPU and memory limits."
                    }
                ]
            }
        ]
    },
    {
        "id": "stage-5",
        "number": 5,
        "title": "Stage 05: Data Analytics & Scripting (SEBI Grade A Focus)",
        "badge": "SEBI Specialization",
        "description": "Customized for the SEBI Grade A IT syllabus: Python data structures, NumPy, Pandas DataFrame filtering, and RegEx.",
        "chapters": [
            {
                "id": "ch-18",
                "stage_id": "stage-5",
                "number": 18,
                "title": "Python Core: Data Structures, Performance & Memory Management",
                "exams": ["sebi"],
                "reading_time_mins": 14,
                "summary": "Lists vs Tuples, Dict hashing, List comprehensions, Generators, GIL, and Garbage Collection via Reference Counting.",
                "lecture_notes": """### 1. Python Data Structures
* **Lists vs Tuples:**
  * Lists are mutable, dynamic arrays.
  * Tuples are immutable, fixed-size, and can be used as dictionary keys (if all contained items are hashable).
* **Dictionaries & Sets:** Implemented via Hash Tables with open addressing. $O(1)$ average lookup time.
* **List Comprehensions:** Fast C-level loop execution:
  ```python
  squared_evens = [x**2 for x in numbers if x % 2 == 0]
  ```

---

### 2. Python Internals & Memory
* **Memory Management:** Handled by **Reference Counting** supplemented by a cyclic garbage collector.
* **Global Interpreter Lock (GIL):** A mutex that protects access to Python objects, preventing multiple native threads from executing Python bytecodes simultaneously. (For CPU-bound tasks, use `multiprocessing` instead of `threading`).
* **Generators:** Yield values on demand using `yield` keyword, consuming $O(1)$ memory instead of building massive lists.""",
                "checkpoints": [
                    {
                        "q": "Why can a list not be used as a key in a Python dictionary?",
                        "a": "Lists are mutable and do not implement __hash__(); dictionary keys must be hashable and immutable."
                    }
                ],
                "quiz": [
                    {
                        "id": 501,
                        "q": "What is the primary mechanism used by CPython for primary memory management and deallocating unused objects?",
                        "options": ["Mark and Sweep only", "Reference Counting supplemented by Cyclic Garbage Collection", "Manual free() calls", "Generational Copying"],
                        "answer": 1,
                        "explanation": "CPython uses reference counting as its main memory management strategy; when an object's reference count drops to 0, it is deallocated immediately."
                    }
                ]
            },
            {
                "id": "ch-19",
                "stage_id": "stage-5",
                "number": 19,
                "title": "Data Manipulation with Pandas, NumPy & Regular Expressions",
                "exams": ["sebi"],
                "reading_time_mins": 15,
                "summary": "Pandas DataFrames, loc vs iloc, groupby aggregations, merging datasets, and Python re module for string parsing.",
                "lecture_notes": """### 1. Pandas DataFrame Essentials
* **Structure:** 2D tabular data with labeled axes (rows and columns).
* **loc vs iloc:**
  * `df.loc[row_label, col_label]`: Label-based indexing.
  * `df.iloc[row_idx, col_idx]`: Integer position-based indexing (0-indexed).
* **Vectorized Filtering:**
  ```python
  # Filtering high-value transactions
  fraud_cases = df[(df['amount'] > 100000) & (df['flag'] == 1)]
  ```
* **GroupBy Aggregations:**
  ```python
  summary = df.groupby('branch')['transaction_amt'].agg(['mean', 'sum', 'count'])
  ```

---

### 2. Regular Expressions in Python (`re` module)
* `re.search(pattern, string)`: Scans entire string for first match.
* `re.match(pattern, string)`: Matches ONLY at the start of the string.
* `re.findall(pattern, string)`: Returns all non-overlapping matches as a list.
* `re.sub(pattern, replacement, string)`: Search and replace.""",
                "checkpoints": [
                    {
                        "q": "What is the difference between df.loc and df.iloc in Pandas?",
                        "a": "df.loc is label-based (using column names and index labels), whereas df.iloc is integer position-based (0 to N-1)."
                    }
                ],
                "quiz": [
                    {
                        "id": 502,
                        "q": "In Python's 're' module, which function searches ONLY at the beginning of a string for a match?",
                        "options": ["re.search()", "re.match()", "re.findall()", "re.compile()"],
                        "answer": 1,
                        "explanation": "re.match() checks for a match only at the beginning of the string, while re.search() scans through the entire string."
                    }
                ]
            }
        ]
    },
    {
        "id": "stage-6",
        "number": 6,
        "title": "Stage 06: Cyber Security & Banking Regulatory Standards",
        "badge": "Regulatory Compliance",
        "description": "Essential cyber security topics, OWASP Top 10 vulnerabilities, cryptography, and RBI IT security guidelines.",
        "chapters": [
            {
                "id": "ch-20",
                "stage_id": "stage-6",
                "number": 20,
                "title": "OWASP Top 10 Web Vulnerabilities, Attacks & Mitigation",
                "exams": ["ibps", "sbi", "sebi"],
                "reading_time_mins": 14,
                "summary": "SQL Injection, Cross-Site Scripting (XSS), CSRF, Insecure Deserialization, Broken Access Control, and secure defenses.",
                "lecture_notes": """### 1. OWASP Top 10 Vulnerabilities
1. **SQL Injection (SQLi):** Attacker injects malicious SQL fragments into input fields.
   * *Mitigation:* Parameterized queries / Prepared Statements, ORM frameworks, input validation.
2. **Cross-Site Scripting (XSS):**
   * **Stored XSS:** Malicious script permanently stored in database.
   * **Reflected XSS:** Script reflected off server in error message or search query.
   * *Mitigation:* Context-sensitive output encoding, Content Security Policy (CSP).
3. **Cross-Site Request Forgery (CSRF):** Forces victim's browser to execute unwanted actions on a trusted site where they are authenticated.
   * *Mitigation:* Anti-CSRF synchronization tokens, `SameSite=Strict` cookies.
4. **Broken Access Control:** Insecure Direct Object References (IDOR), parameter tampering to access unauthorized accounts.""",
                "checkpoints": [
                    {
                        "q": "How do Parameterized Queries (Prepared Statements) prevent SQL Injection?",
                        "a": "They separate the SQL query structure from user-supplied data, ensuring input parameters are treated strictly as literal values rather than executable code."
                    }
                ],
                "quiz": [
                    {
                        "id": 601,
                        "q": "Which technique is the most effective defense against SQL Injection in web applications?",
                        "options": ["Client-side JavaScript validation", "Prepared Statements with Parameterized Queries", "Base64 encoding input", "Restarting database daily"],
                        "answer": 1,
                        "explanation": "Prepared Statements with parameterized queries ensure user inputs cannot alter the underlying SQL query syntax."
                    }
                ]
            },
            {
                "id": "ch-21",
                "stage_id": "stage-6",
                "number": 21,
                "title": "Applied Cryptography, PKI, SSL/TLS Handshake & RBI Cyber Framework",
                "exams": ["ibps", "sbi", "sebi"],
                "reading_time_mins": 15,
                "summary": "Symmetric vs Asymmetric encryption, Digital Signatures, Public Key Infrastructure, TLS 1.3 handshake, and RBI cyber directives.",
                "lecture_notes": """### 1. Cryptography Essentials
* **Symmetric Encryption (AES):** Same secret key used for encryption and decryption. Very fast; used for bulk data at rest and in transit.
* **Asymmetric Encryption (RSA, ECC):** Key pair consisting of Public Key and Private Key.
  * Public key encrypts $\\implies$ Only private key can decrypt (Confidentiality).
  * Private key signs hash $\\implies$ Public key verifies (Digital Signature $\\implies$ Authenticity, Integrity, Non-Repudiation).

---

### 2. Public Key Infrastructure (PKI) & TLS Handshake
* **Certificate Authority (CA):** Digitally signs digital certificates (X.509 standard) binding public keys to domain identities.
* **TLS Handshake Flow:** Client Hello $\\rightarrow$ Server Hello + Certificate $\\rightarrow$ Key Exchange (Diffie-Hellman) $\\rightarrow$ Shared symmetric session key generated $\\rightarrow$ Encrypted application data flows over AES-GCM.

---

### 3. RBI Cyber Security Framework for Banks
* Mandatory board-approved **Cyber Security Policy**.
* 24/7 **Security Operations Center (SOC)** for continuous monitoring and log retention.
* Mandatory **Multi-Factor Authentication (MFA)** for all administrative access and sensitive banking transactions.
* Periodic Vulnerability Assessment and Penetration Testing (**VAPT**).""",
                "checkpoints": [
                    {
                        "q": "What three security properties does a Digital Signature guarantee?",
                        "a": "Authentication, Data Integrity, and Non-repudiation (it does NOT provide confidentiality without separate encryption)."
                    }
                ],
                "quiz": [
                    {
                        "id": 602,
                        "q": "Which cryptographic algorithm is a modern, widely accepted standard for Symmetric bulk data encryption?",
                        "options": ["RSA", "AES (Advanced Encryption Standard)", "Diffie-Hellman", "SHA-256"],
                        "answer": 1,
                        "explanation": "AES (Advanced Encryption Standard) is the worldwide standard for symmetric key cryptography."
                    },
                    {
                        "id": 603,
                        "q": "Under RBI Cybersecurity guidelines, what is the mandatory requirement for all sensitive administrative and payment actions?",
                        "options": ["Single static password", "Multi-Factor Authentication (MFA)", "Using unencrypted HTTP", "Manual paper ledger"],
                        "answer": 1,
                        "explanation": "RBI mandates Multi-Factor Authentication (MFA) to safeguard critical customer transactions and banking admin portals."
                    }
                ]
            }
        ]
    }
]

curriculum = {
    "stages": stages,
    "stats": {
        "total_stages": len(stages),
        "total_chapters": sum(len(s['chapters']) for s in stages),
        "total_questions": sum(sum(len(ch['quiz']) for ch in s['chapters']) for s in stages),
        "extracted_raw_qa_count": {
            "dbms": len(dbms_qa),
            "os": len(os_qa),
            "networking": len(net_qa),
            "oops": len(oops_qa),
            "aws": len(aws_qa),
            "python": len(python_qa),
            "testing": len(testing_qa)
        }
    }
}

out_file = os.path.join(DATA_DIR, 'curriculum.json')
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(curriculum, f, indent=2)

print(f"Curriculum generated successfully: {out_file}")
print(f"Total Stages: {curriculum['stats']['total_stages']}")
print(f"Total Chapters: {curriculum['stats']['total_chapters']}")
print(f"Total Embedded Chapter Quiz Questions: {curriculum['stats']['total_questions']}")
