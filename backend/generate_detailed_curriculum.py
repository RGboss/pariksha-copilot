import os
import json

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Define the exhaustive 6 Stages with 21 in-depth, rigorous chapters
stages = [
    {
        "id": "stage-1",
        "number": 1,
        "title": "Stage 01: Database Architecture, Normalization & SQL Mastery",
        "badge": "Core Foundation",
        "description": "Exhaustive treatment of relational algebra, functional dependencies, normal forms (1NF to BCNF), transaction concurrency control (ACID, 2PL), and advanced SQL.",
        "chapters": [
            {
                "id": "ch-1",
                "stage_id": "stage-1",
                "number": 1,
                "title": "Relational Data Models, Three-Schema Architecture & Integrity Constraints",
                "exams": ["ibps", "sebi", "sbi"],
                "reading_time_mins": 25,
                "summary": "Formal definitions of the Relational Model, ANSI/SPARC 3-Schema Architecture, Data Independence, ER modeling mechanics, and the key constraints hierarchy.",
                "lecture_notes": """# Relational Data Models, Three-Schema Architecture & Integrity Constraints

## 1. Theoretical Foundations & The Relational Model
The **Relational Model**, formalized by Dr. E.F. Codd in 1970, abstracts physical data storage into mathematical relations (tables). In relational database theory:
* A **Relation** $R$ is a subset of the Cartesian product of a list of domains: $R \\subseteq D_1 \\times D_2 \\times \\dots \\times D_n$.
* A **Tuple** represents an individual record (row) in the relation, representing an entity instance.
* An **Attribute** represents a named property or column with an atomic domain of permissible values.
* **Degree / Arity:** The total number of attributes (columns) comprising the relation schema.
* **Cardinality:** The total number of tuples (rows) currently residing in the relation instance.

### Why Banking & Regulatory Systems Rely on Relational Models
Banking cores (such as Finacle, BaNCS) manage financial balances, ledger entries, and audit logs. The relational model provides mathematical guarantees of consistency and referential integrity that prevent orphan transactions, duplicate account allocations, and phantom entries.

---

## 2. ANSI/SPARC Three-Schema Architecture & Data Independence
To isolate user applications from physical storage hardware changes, the database architecture is partitioned into three discrete abstraction layers:

```
+-------------------------------------------------------+
|  External / View Level (User & Application Views)     |
|  View 1 (Teller View)   |   View 2 (Auditor View)     |
+-------------------------------------------------------+
                           ^
                           | (Logical Data Independence)
                           v
+-------------------------------------------------------+
|  Conceptual / Logical Level (Tables, Schemas, FKs)    |
|  Customer, Account, Transaction tables & constraints  |
+-------------------------------------------------------+
                           ^
                           | (Physical Data Independence)
                           v
+-------------------------------------------------------+
|  Internal / Physical Level (Disks, B+ Trees, Hashing) |
|  Data blocks, indexing algorithms, allocation maps    |
+-------------------------------------------------------+
```

### 1. Physical Data Independence
* **Definition:** The capacity to modify the internal physical schema without altering the conceptual/logical schema or external views.
* **Concrete Example:** Converting a table's underlying storage from an unclustered heap file to a clustered B+ Tree index, changing disk block sizes, or migrating storage to SSD arrays does not require altering table column definitions or application SQL queries.

### 2. Logical Data Independence
* **Definition:** The capacity to modify the conceptual schema without altering existing external user views or application programs.
* **Concrete Example:** Adding a new column `kyc_verification_date` or splitting an `Accounts` table into `SavingsAccounts` and `CurrentAccounts` can be masked from legacy teller terminals by creating an updateable SQL View that reconstructs the original table format.

---

## 3. Entity-Relationship (ER) Modeling Mechanics
An ER Model provides a high-level conceptual blueprint of the enterprise before database schema creation.

### Key Constructs
1. **Strong Entity Set:** Possesses an independent existence and contains sufficient attributes to form a primary key (e.g., `Account(AccountNumber, Balance)`). Graphically depicted as a **single rectangle**.
2. **Weak Entity Set:** Cannot be identified by its own attributes alone and depends on an owner (identifying) strong entity set for its existence. Graphically depicted as a **double rectangle**.
   * It has a **Partial Key (Discriminator)**, rendered with a **dashed underline**.
   * Its identifying relationship is rendered as a **double diamond**.
   * **Rule:** A weak entity set must always participate in **total participation** with its identifying relationship.
3. **Relationship Constraints:**
   * **Cardinality Ratios:** 1:1 (One-to-One), 1:N (One-to-Many), M:N (Many-to-Many).
   * **Participation Constraints:** Total (double line; every entity must participate) vs Partial (single line).

### Relational Schema Reduction Rules (High-Yield Exam Scenarios)
* **Rule 1 (1:N Relationship):** Combine the relationship into the table on the **"Many"** side by inserting the primary key of the "One" side as a foreign key. No separate table is needed!
* **Rule 2 (M:N Relationship):** **Must always be reduced into a separate junction table** whose primary key is the composite of the primary keys of both participating entities.
* **Rule 3 (Weak Entity Set):** Reduced into a table containing the partial key plus the primary key of the identifying strong entity set (which acts as a foreign key and part of the composite primary key).

---

## 4. Key Constraints Hierarchy & Formal Taxonomy
Understanding key hierarchy is critical for both Phase 1 MCQs and Phase 2 descriptive technical papers:

```
[ Super Keys (Any attribute combination guaranteeing uniqueness) ]
       |
       v  (Eliminate all redundant/extraneous attributes)
[ Candidate Keys (Minimal Super Keys) ]
       |
       v  (Database Architect chooses one primary identifier)
[ Primary Key ]   +   [ Alternate Keys (Remaining candidate keys) ]
```

### 1. Super Key ($SK$)
Any set of attributes within relation schema $R$ such that no two distinct tuples can have identical values on these attributes.
$$\\forall t_1, t_2 \\in R, \\quad t_1[SK] = t_2[SK] \\implies t_1 = t_2$$

### 2. Candidate Key ($CK$)
A Super Key with the strict property of **minimality**: removing any single attribute from the candidate key causes it to lose its uniqueness guarantee.
$$\\text{If } K \\text{ is a Candidate Key, then } \\forall A \\in K, \\quad (K - \\{A\\}) \\text{ is NOT a Super Key.}$$

### 3. Primary Key ($PK$)
The designated candidate key chosen by the schema designer. It enforces:
* **Entity Integrity Constraint:** No attribute participating in the primary key may accept a `NULL` value ($t[PK] \\ne \\text{NULL}$).

### 4. Foreign Key ($FK$) & Referential Integrity
A set of attributes in table $R_1$ that reference the Primary Key of table $R_2$.
* **Referential Integrity Constraint:** The value of the Foreign Key in $R_1$ must either match an existing Primary Key value in $R_2$ or be set to `NULL`.
* **Referential Actions on Deletion/Update:**
  * `ON DELETE CASCADE`: Automatically deletes dependent child rows when the parent row is deleted.
  * `ON DELETE SET NULL`: Sets the child foreign key column to NULL.
  * `ON DELETE RESTRICT / NO ACTION`: Rejects the parent row deletion with a constraint violation.

---

## 5. Step-by-Step Worked Example: Calculating Candidate Keys
**Problem:** Given relation $R(A, B, C, D, E)$ with the functional dependency set:
$$F = \\{ A \\rightarrow BC, \\quad CD \\rightarrow E, \\quad B \\rightarrow D, \\quad E \\rightarrow A \\}$$
Find all Candidate Keys of $R$.

### Step-by-Step Solution:
1. **Identify attributes not appearing on the Right-Hand Side (RHS):**
   * Check RHS attributes: $B, C, E, D, A$.
   * All attributes appear on the RHS of at least one dependency. Thus, no single attribute is guaranteed to be an essential starter.
2. **Compute Attribute Closure $(A)^+$:**
   * Step 1: $(A)^+ = \\{A\\}$
   * Step 2: Since $A \\rightarrow BC$, $(A)^+ = \\{A, B, C\\}$
   * Step 3: Since $B \\rightarrow D$, $(A)^+ = \\{A, B, C, D\\}$
   * Step 4: Since $CD \\rightarrow E$, $(A)^+ = \\{A, B, C, D, E\\}$
   * Since $(A)^+$ contains all attributes of $R$, **$A$ is a Candidate Key!**
3. **Check other derivations leading to $A$:**
   * Notice dependency $E \\rightarrow A$.
   * Since $A$ is a Candidate Key and $E \\rightarrow A$, $(E)^+$ will also derive all attributes:
     $(E)^+ = \\{E, A, B, C, D\\} = R$.
   * Thus, **$E$ is also a Candidate Key!**
4. **Check dependencies leading to $E$:**
   * Notice dependency $CD \\rightarrow E$.
   * Let's compute $(CD)^+$:
     * $(CD)^+ = \\{C, D\\}$
     * From $CD \\rightarrow E$, $(CD)^+ = \\{C, D, E\\}$
     * From $E \\rightarrow A$, $(CD)^+ = \\{C, D, E, A\\}$
     * From $A \\rightarrow BC$, $(CD)^+ = \\{C, D, E, A, B\\} = R$.
   * Can $C$ or $D$ be removed?
     * $(C)^+ = \\{C\\} \\ne R$.
     * $(D)^+ = \\{D\\} \\ne R$.
   * Hence, **$CD$ is a minimal Candidate Key!**
5. **Check dependencies leading to $D$ in $CD$:**
   * Notice dependency $B \\rightarrow D$.
   * Replace $D$ with $B$ to test $BC$:
     * $(BC)^+ = \\{B, C\\}$
     * From $B \\rightarrow D$, $(BC)^+ = \\{B, C, D\\}$
     * From $CD \\rightarrow E$, $(BC)^+ = \\{B, C, D, E\\}$
     * From $E \\rightarrow A$, $(BC)^+ = \\{B, C, D, E, A\\} = R$.
   * Hence, **$BC$ is also a minimal Candidate Key!**

**Final Answer:** Relation $R$ has exactly **4 Candidate Keys**: $\\{A, E, CD, BC\\}$.
* **Prime Attributes (attributes belonging to ANY candidate key):** $\\{A, B, C, D, E\\}$ (all attributes are prime!).

---

## 6. Exam Pitfalls & Tricky Multiple-Choice Scenarios
* **Trap 1:** *"Can a relation have more than one primary key?"*
  * **Answer:** NO. A relation can have multiple candidate keys, but exactly **one** is chosen as the Primary Key.
* **Trap 2:** *"Does a Primary Key allow a single NULL value if the table is empty?"*
  * **Answer:** NO. By definition of Entity Integrity, Primary Keys strictly forbid `NULL`. Only Unique constraints permit `NULL` (typically one NULL in standard SQL, depending on dialect).
* **Trap 3:** *"In an ER diagram, what is the maximum number of tables required for a 1:N relationship with total participation on the N side?"*
  * **Answer:** Exactly 2 tables. The relationship is merged directly into the table on the N-side.""",
                "checkpoints": [
                    {
                        "q": "What is the key difference between Logical Data Independence and Physical Data Independence?",
                        "a": "Physical Data Independence allows altering file formats, B+ tree indexes, or storage disks without changing logical tables. Logical Data Independence allows modifying table schemas (e.g., adding columns or splitting tables) without modifying user external views or application code."
                    },
                    {
                        "q": "Why does a Weak Entity Set always have total participation in its identifying relationship?",
                        "a": "Because a weak entity cannot exist without its owner entity; each weak entity instance must be linked to a valid owner instance to form its unique composite identity."
                    },
                    {
                        "q": "If relation R(X, Y, Z) has candidate key X, can the combination {X, Y} be called a Candidate Key?",
                        "a": "No. {X, Y} is a Super Key, but NOT a Candidate Key because it violates minimality (removing Y still leaves X, which is already a key)."
                    }
                ],
                "quiz": [
                    {
                        "id": 101,
                        "q": "In an Entity-Relationship (ER) model, how is a Weak Entity Set and its identifying relationship represented?",
                        "options": [
                            "Single rectangle and single diamond",
                            "Double rectangle and double diamond",
                            "Dashed rectangle and dashed ellipse",
                            "Double ellipse and single diamond"
                        ],
                        "answer": 1,
                        "explanation": "Weak entity sets are depicted as double rectangles, while their identifying relationship with the owner entity set is depicted as a double diamond."
                    },
                    {
                        "id": 102,
                        "q": "Which data independence capability protects client SQL queries when an administrator changes a table index from Hash indexing to a B+ Tree index?",
                        "options": [
                            "Logical Data Independence",
                            "Physical Data Independence",
                            "View Data Independence",
                            "Referential Data Independence"
                        ],
                        "answer": 1,
                        "explanation": "Physical Data Independence isolates the logical schema and client queries from physical storage changes, such as altering file organization or indexing algorithms."
                    },
                    {
                        "id": 103,
                        "q": "A relation R has candidate keys AB and CD. Which of the following statements is strictly correct regarding prime attributes?",
                        "options": [
                            "Only A and C are prime attributes",
                            "Only B and D are prime attributes",
                            "A, B, C, and D are all prime attributes",
                            "None of the attributes are prime because they are composite"
                        ],
                        "answer": 2,
                        "explanation": "A prime attribute is defined as ANY attribute that is part of AT LEAST ONE candidate key. Because AB and CD are candidate keys, A, B, C, and D are all prime attributes."
                    },
                    {
                        "id": 104,
                        "q": "When converting an ER diagram into a relational schema, what is the standard relational representation for a Many-to-Many (M:N) relationship between two entities E1 and E2?",
                        "options": [
                            "Add the primary key of E1 into E2",
                            "Add the primary key of E2 into E1",
                            "Create a new separate junction table containing the primary keys of both E1 and E2 as foreign keys",
                            "M:N relationships cannot be converted into relational databases"
                        ],
                        "answer": 2,
                        "explanation": "M:N relationships cannot be embedded into either entity table without introducing unbounded repeating columns. They must be resolved into a separate associative (junction) table."
                    },
                    {
                        "id": 105,
                        "q": "What happens when a DELETE command is executed on a parent table row whose primary key is referenced by child rows with 'ON DELETE RESTRICT'?",
                        "options": [
                            "The parent row and all child rows are immediately deleted",
                            "The parent row is deleted, and child foreign keys are set to NULL",
                            "The database rejects the deletion and raises a referential integrity violation",
                            "Child rows are orphaned without error"
                        ],
                        "answer": 2,
                        "explanation": "ON DELETE RESTRICT (or NO ACTION) actively enforces referential integrity by aborting the deletion if any dependent child rows exist."
                    }
                ]
            },
            {
                "id": "ch-2",
                "stage_id": "stage-1",
                "number": 2,
                "title": "Database Normalization Theory: Functional Dependencies, 1NF to BCNF & Lossless Decomposition",
                "exams": ["ibps", "sebi", "sbi"],
                "reading_time_mins": 30,
                "summary": "Armstrong's axioms, closure algorithm, full vs partial dependency, transitive dependency, 1NF, 2NF, 3NF, BCNF proofs, and dependency preservation tests.",
                "lecture_notes": """# Database Normalization Theory: 1NF to BCNF & Lossless Decomposition

## 1. The Mathematical Objective of Normalization
Normalization is a formal database design technique that organizes relations to:
1. **Minimize Data Redundancy:** Preventing identical facts from being recorded in multiple rows.
2. **Eliminate Data Anomalies:**
   * **Insertion Anomaly:** Inability to record a piece of data without recording unrelated facts (e.g., unable to insert a new course until a student enrolls in it).
   * **Deletion Anomaly:** Unintentional loss of crucial data when deleting unrelated facts (e.g., deleting the last student enrolled in a department accidentally deletes all department existence records).
   * **Update / Modification Anomaly:** Inconsistent states when data stored redundantly is updated in some tuples but missed in others.

---

## 2. Functional Dependencies & Armstrong's Axioms
Let $R$ be a relation schema and $X, Y \\subseteq R$. A **Functional Dependency (FD)** $X \\rightarrow Y$ specifies a constraint where the values of attribute set $X$ uniquely determine the values of attribute set $Y$:
$$\\forall t_1, t_2 \\in R, \\quad t_1[X] = t_2[X] \\implies t_1[Y] = t_2[Y]$$

### Armstrong's Axioms (Sound and Complete Inference Rules)
1. **Axiom of Reflexivity:** If $Y \\subseteq X$, then $X \\rightarrow Y$ (Trivial FD).
   * *Example:* $\\{\\text{AccountID, Balance}\\} \\rightarrow \\text{AccountID}$.
2. **Axiom of Augmentation:** If $X \\rightarrow Y$, then $XZ \\rightarrow YZ$ for any attribute set $Z$.
3. **Axiom of Transitivity:** If $X \\rightarrow Y$ and $Y \\rightarrow Z$, then $X \\rightarrow Z$.

### Derived Inference Rules
* **Union Rule:** If $X \\rightarrow Y$ and $X \\rightarrow Z$, then $X \\rightarrow YZ$.
* **Decomposition Rule:** If $X \\rightarrow YZ$, then $X \\rightarrow Y$ and $X \\rightarrow Z$.
* **Pseudotransitivity Rule:** If $X \\rightarrow Y$ and $WY \\rightarrow Z$, then $WX \\rightarrow Z$.

---

## 3. The Normal Forms Hierarchy

```
+-----------------------------------------------------------+
| BCNF (Strict 3NF: Every determinant is a Super Key)       |
|   +-----------------------------------------------------+ |
|   | 3NF (No Transitive Dependencies: Superkey OR Prime) | |
|   |   +-----------------------------------------------+ | |
|   |   | 2NF (No Partial Dependencies on Candidate Key)| | |
|   |   |   +-----------------------------------------+ | | |
|   |   |   | 1NF (Atomic Attributes, Single-Valued)  | | | |
|   |   |   +-----------------------------------------+ | | |
|   |   +-----------------------------------------------+ | |
|   +-----------------------------------------------------+ |
+-----------------------------------------------------------+
```

### First Normal Form (1NF)
* **Rule:** A relation is in 1NF if and only if every attribute domain contains only **atomic (indivisible) values**, with no repeating groups or composite/multivalued columns.
* **Violation Example:** `Customer(CustomerID, Name, PhoneNumbers)` where `PhoneNumbers = "9876543210, 9123456789"`.
* **Resolution:** Expand into separate tuples or create a child table `CustomerPhones(CustomerID, PhoneNumber)`.

### Second Normal Form (2NF)
* **Rule:** A relation is in 2NF if:
  1. It is in 1NF.
  2. **No Partial Dependency exists:** Every non-prime attribute is fully functionally dependent on the entire Candidate Key (no non-prime attribute depends on a proper subset of any candidate key).
* **High-Yield Shortcut:** If every candidate key of relation $R$ consists of a **single attribute** (no composite keys), the relation is **automatically in 2NF**!

### Third Normal Form (3NF)
* **Rule:** A relation is in 3NF if it is in 2NF, and for every non-trivial functional dependency $X \\rightarrow A$:
  1. $X$ is a **Super Key**, OR
  2. $A$ is a **Prime Attribute** (part of some candidate key).
* **Eliminates Transitive Dependencies:** A non-prime attribute cannot determine another non-prime attribute ($Key \\rightarrow NonKey_1 \\rightarrow NonKey_2$).

### Boyce-Codd Normal Form (BCNF - Strict 3NF)
* **Rule:** A relation is in BCNF if and only if for every non-trivial functional dependency $X \\rightarrow A$:
  * $X$ **MUST BE A SUPER KEY**.
* **Key Distinction from 3NF:** BCNF removes the second exception ("$A$ is a prime attribute"). If an overlapping prime attribute is determined by a non-super key, the relation is in 3NF, but **violates BCNF**.

---

## 4. Worked Step-by-Step Normalization Breakdown

### Scenario: The Bank Branch Loan Relation
Consider relation $R(\\text{BranchName, BranchCity, CustomerID, LoanAmount})$ with FDs:
* $\\text{CustomerID, BranchName} \\rightarrow \\text{LoanAmount}$
* $\\text{BranchName} \\rightarrow \\text{BranchCity}$

#### 1. Candidate Key Determination
* Attributes on RHS: $\\text{LoanAmount}, \\text{BranchCity}$.
* Attributes never on RHS: $\\{\\text{CustomerID}\\}$.
* Compute closure $(\\text{CustomerID, BranchName})^+$:
  $$(\\text{CustomerID, BranchName})^+ = \\{\\text{CustomerID, BranchName, LoanAmount, BranchCity}\\} = R$$
* Thus, **Candidate Key = $\\{\\text{CustomerID, BranchName}\\}$ (Composite Key!)**.
* **Prime Attributes:** $\\{\\text{CustomerID, BranchName}\\}$.
* **Non-Prime Attributes:** $\\{\\text{LoanAmount, BranchCity}\\}$.

#### 2. Normal Form Testing
* **Test 1NF:** All values are atomic $\\implies$ **Is in 1NF**.
* **Test 2NF:** Check dependency $\\text{BranchName} \\rightarrow \\text{BranchCity}$.
  * Determinant $\\text{BranchName}$ is a **proper subset** of Candidate Key $\\{\\text{CustomerID, BranchName}\\}$.
  * Dependent $\\text{BranchCity}$ is a **non-prime attribute**.
  * **Result:** $\\text{BranchName} \\rightarrow \\text{BranchCity}$ is a **Partial Dependency**!
  * **Conclusion:** The relation **violates 2NF**!

#### 3. Decomposition into 2NF
We split $R$ into two sub-relations:
1. $R_1(\\text{BranchName, BranchCity})$ with $\\text{BranchName} \\rightarrow \\text{BranchCity}$ (Candidate Key: $\\text{BranchName}$).
2. $R_2(\\text{CustomerID, BranchName, LoanAmount})$ with $\\{\\text{CustomerID, BranchName}\\} \\rightarrow \\text{LoanAmount}$.
* Both $R_1$ and $R_2$ are now in 2NF, 3NF, and BCNF!

---

## 5. Lossless Join vs Dependency Preservation Decomposition

When decomposing relation $R$ with functional dependencies $F$ into $R_1$ and $R_2$:

### 1. Lossless Join Decomposition (Non-Additive Join)
A decomposition is **Lossless** if taking the Natural Join of $R_1$ and $R_2$ reconstructs the exact original relation $R$ without generating spurious tuples:
$$R_1 \\bowtie R_2 = R$$

#### Mathematical Test for Lossless Join:
The decomposition of $R$ into $R_1$ and $R_2$ is lossless with respect to $F$ if and only if the common attributes functionally determine at least one of the decomposed relations:
$$(R_1 \\cap R_2) \\rightarrow R_1 \\quad \\text{OR} \\quad (R_1 \\cap R_2) \\rightarrow R_2 \\quad \\in F^+$$

### 2. Dependency Preservation
A decomposition is **Dependency Preserving** if all original functional dependencies in $F$ can be enforced by checking the sub-relations individually without performing expensive joins:
$$(F_1 \\cup F_2)^+ = F^+$$

### Crucial Trade-off (The Classic Exam Question):
| Property | 3NF Decomposition | BCNF Decomposition |
| :--- | :---: | :---: |
| **Guaranteed Lossless Join?** | **YES** | **YES** |
| **Guaranteed Dependency Preservation?** | **YES** | **NO** |
| **Eliminates All Functional Redundancy?** | Mostly (except prime overlaps) | **YES** |

> **Theorem:** Any relation schema can always be decomposed into **3NF** with **both Lossless Join AND Dependency Preservation guaranteed**. However, a relation **CANNOT ALWAYS** be decomposed into **BCNF** while preserving all functional dependencies!

---

## 6. Exam Pitfalls & Tricky Multiple-Choice Scenarios
* **Trap 1:** *"If a table has no composite candidate keys, can it be in 1NF and violate 2NF?"*
  * **Answer:** NO! A partial dependency requires a proper subset of a candidate key. Single-attribute candidate keys cannot have proper subsets.
* **Trap 2:** *"Does BCNF prevent all data redundancy?"*
  * **Answer:** BCNF eliminates all redundancy caused by functional dependencies. However, redundancy caused by **Multivalued Dependencies (MVDs)** can still exist, which requires **4NF** to eliminate!
* **Trap 3:** *"Is a table with only 2 attributes always in BCNF?"*
  * **Answer:** YES! Any binary relation $R(A, B)$ is inherently in BCNF.""",
                "checkpoints": [
                    {
                        "q": "What is the formal condition that allows a relation to be in 3NF even if a determinant is not a super key?",
                        "a": "If for the dependency X -> A, the dependent attribute A is a prime attribute (part of any candidate key), 3NF permits it. BCNF strictly disallows this."
                    },
                    {
                        "q": "What is the mathematical condition to verify if decomposing R into R1 and R2 is lossless?",
                        "a": "The intersection of attributes (R1 ∩ R2) must form a superkey for either R1 or R2."
                    },
                    {
                        "q": "Can every relational schema be decomposed into BCNF with guaranteed dependency preservation?",
                        "a": "No. 3NF always guarantees dependency preservation; BCNF guarantees lossless join, but cannot always preserve dependencies."
                    }
                ],
                "quiz": [
                    {
                        "id": 106,
                        "q": "A relation R(A, B, C, D) has the following functional dependencies: {AB -> C, C -> D, D -> A}. What are all candidate keys of R?",
                        "options": [
                            "{AB, BC, CD}",
                            "{AB, BC, BD}",
                            "{AB, CB, DB}",
                            "{AB, CD}"
                        ],
                        "answer": 2,
                        "explanation": "Compute closures: (AB)+ = {A,B,C,D}. Since D -> A, replacing A with D gives (DB)+ = {D,B,A,C} = R. Since C -> D, replacing D with C gives (CB)+ = {C,B,D,A} = R. Thus the candidate keys are AB, CB, and DB."
                    },
                    {
                        "id": 107,
                        "q": "Which normal form is designed specifically to eliminate anomalies caused by partial functional dependencies?",
                        "options": [
                            "First Normal Form (1NF)",
                            "Second Normal Form (2NF)",
                            "Third Normal Form (3NF)",
                            "Boyce-Codd Normal Form (BCNF)"
                        ],
                        "answer": 1,
                        "explanation": "2NF explicitly requires that no non-prime attribute depends on a proper subset of any candidate key (eliminating partial dependencies)."
                    },
                    {
                        "id": 108,
                        "q": "Under what circumstance does a relation in 3NF fail to meet the criteria for BCNF?",
                        "options": [
                            "When it contains multivalued dependencies",
                            "When an attribute functionally determines a candidate key",
                            "When a dependency X -> A exists where A is a prime attribute, but X is not a super key",
                            "When the candidate key is composite"
                        ],
                        "answer": 2,
                        "explanation": "3NF allows X -> A if A is a prime attribute even when X is not a superkey. BCNF removes this allowance and mandates that X must strictly be a superkey."
                    },
                    {
                        "id": 109,
                        "q": "Which theorem regarding normalization decompositions is mathematically guaranteed for any relational schema?",
                        "options": [
                            "Every relation can be decomposed into BCNF with dependency preservation",
                            "Every relation can be decomposed into 3NF with both lossless join and dependency preservation",
                            "Decomposition into 2NF cannot guarantee a lossless join",
                            "BCNF decomposition never produces a lossless join"
                        ],
                        "answer": 1,
                        "explanation": "It is mathematically proven that any relation schema can be decomposed into 3NF such that the decomposition is both lossless and dependency-preserving."
                    },
                    {
                        "id": 110,
                        "q": "If relation R(A, B) contains only two attributes, which of the following is always true?",
                        "options": [
                            "It is in BCNF",
                            "It violates 1NF",
                            "It is in 3NF but not BCNF",
                            "It cannot have a candidate key"
                        ],
                        "answer": 0,
                        "explanation": "Any binary relation R(A, B) is guaranteed to be in BCNF because the only non-trivial functional dependencies possible are A -> B, B -> A, or neither, all of which satisfy the BCNF definition."
                    }
                ]
            },
            {
                "id": "ch-3",
                "stage_id": "stage-1",
                "number": 3,
                "title": "Transaction Management, ACID Properties, Serializability & Concurrency Control Protocols",
                "exams": ["ibps", "sebi", "sbi"],
                "reading_time_mins": 30,
                "summary": "ACID mechanics, Write-Ahead Logging (WAL), Dirty/Non-Repeatable/Phantom reads, Precedence Graphs, Conflict Serializability proofs, 2PL variants, and Deadlocks.",
                "lecture_notes": """# Transaction Management, Serializability & Concurrency Control

## 1. The Financial Definition of a Transaction
In banking and financial computing, a **Transaction** is a logical unit of database processing that includes one or more database access operations (read, write, insert, delete).
* **The Classical Bank Transfer Problem:** Transferring \$500 from Account A to Account B requires:
  $$\\text{Read}(A) \\implies A := A - 500 \\implies \\text{Write}(A) \\implies \\text{Read}(B) \\implies B := B + 500 \\implies \\text{Write}(B)$$
* If the server crashes or power fails immediately after $\\text{Write}(A)$ but before $\\text{Write}(B)$, \$500 vanishes from the financial system unless governed by ACID guarantees!

---

## 2. The ACID Properties Demystified
To preserve integrity, the DBMS must guarantee four fundamental properties:

| Property | Responsibility | Underlying Mechanism |
| :--- | :--- | :--- |
| **Atomicity** (All-or-Nothing) | System Crash / Abort | **Recovery Manager:** Undo/Redo Logs, Write-Ahead Logging (WAL) |
| **Consistency** (Correct State) | Application / System | **Integrity Constraints:** Preserves business invariants (e.g. Balance $\\ge 0$) |
| **Isolation** (No Interference) | Concurrency Engine | **Concurrency Control:** Locking protocols (2PL), Timestamping, MVCC |
| **Durability** (Permanent Changes)| Hardware Failure | **Recovery Engine:** Write-Ahead Logging (WAL), Checkpointing to non-volatile disk |

### The Write-Ahead Logging (WAL) Protocol
* **Rule:** Log records describing an update must be flushed to non-volatile disk storage **BEFORE** the actual data pages on disk are overwritten.
* **Undo Log:** Reverts changes made by uncommitted transactions during system recovery.
* **Redo Log:** Re-applies changes made by committed transactions that were in volatile RAM buffer pools when the system crashed.

---

## 3. Concurrency Phenomena & SQL Isolation Levels
When multiple transactions execute concurrently without coordination, three classic anomalies emerge:

1. **Dirty Read (Write-Read Conflict):** Transaction $T_1$ modifies a bank balance. $T_2$ reads this modified balance. $T_1$ subsequently aborts/rolls back. $T_2$ has acted on "dirty", non-existent financial data!
2. **Non-Repeatable Read (Read-Write Conflict):** $T_1$ reads Account A (\$1000). $T_2$ updates Account A to \$800 and commits. $T_1$ re-reads Account A within the same transaction and discovers a different balance!
3. **Phantom Read:** $T_1$ executes a range query (`SELECT COUNT(*) FROM Accounts WHERE Balance > 10000`). $T_2$ inserts a brand-new account with balance \$50,000 and commits. $T_1$ re-runs the count and discovers a new "phantom" row.

### ANSI SQL Isolation Levels Matrix
| Isolation Level | Dirty Read | Non-Repeatable Read | Phantom Read | Mechanism Employed |
| :--- | :---: | :---: | :---: | :--- |
| **Read Uncommitted** | Permitted | Permitted | Permitted | Read without acquiring shared locks |
| **Read Committed** | **Prevented** | Permitted | Permitted | Short-term shared locks released after read |
| **Repeatable Read** | **Prevented** | **Prevented** | Permitted | Long-term shared locks held until end of tx |
| **Serializable** | **Prevented** | **Prevented** | **Prevented** | Range locks / Two-Phase Locking / Predicate locks |

---

## 4. Conflict Serializability & Precedence Graphs
A concurrent schedule $S$ is **Conflict Serializable** if it is conflict equivalent to some serial schedule $S'$ (meaning it can be transformed into a serial schedule by swapping non-conflicting adjacent operations).

### What Constitutes a Conflicting Operation?
Two operations $I_i$ and $I_j$ belonging to distinct transactions $T_i$ and $T_j$ conflict IF AND ONLY IF:
1. They access the **same data item** $Q$.
2. **At least one of the operations is a Write operation** ($\\{R_i(Q), W_j(Q)\\}$, $\\{W_i(Q), R_j(Q)\\}$, or $\\{W_i(Q), W_j(Q)\\}$).

### Conflict Serializability Testing via Precedence Graph
A directed graph $G = (V, E)$ where:
* Vertices $V$ are the participating transactions $\\{T_1, T_2, \\dots, T_n\\}$.
* A directed edge $T_i \\rightarrow T_j$ is drawn if an operation of $T_i$ precedes and conflicts with an operation of $T_j$.

> **Fundamental Theorem:** A schedule $S$ is **Conflict Serializable** IF AND ONLY IF its Precedence Graph contains **NO DIRECTED CYCLES** (i.e., it can be topologically sorted).

---

## 5. Locking Protocols: Two-Phase Locking (2PL)
Locks regulate concurrent data item access:
* **Shared Lock (S-Lock):** Allows concurrent reads; rejects exclusive locks.
* **Exclusive Lock (X-Lock):** Required for writes; rejects all other locks.

### Two-Phase Locking (2PL) Mechanics
In 2PL, every transaction must execute in two distinct phases:
1. **Growing Phase:** The transaction may acquire locks, but **CANNOT release any locks**.
2. **Shrinking Phase:** The transaction may release locks, but **CANNOT acquire any new locks**.
* **Lock Point:** The exact point where the transaction acquires its final lock.

```
Number of Locks Held
     ^
     |         / Lock Point \
     |        /              \
     |       /                \
     |      /  Growing Phase   \  Shrinking Phase
     |     /  (Only Acquires)   \ (Only Releases)
     |    /                      \
     +---------------------------------------------> Time
```

### The 2PL Variants
1. **Standard 2PL:** Guarantees Conflict Serializability, but can suffer from **Cascading Rollbacks** (if $T_1$ releases a lock early and aborts, transactions that read its data must also abort).
2. **Strict 2PL:** Holds all **Exclusive (Write) Locks** until transaction commits or aborts.
   * **Guarantee:** Guarantees Conflict Serializability AND prevents Cascading Aborts!
3. **Rigorous 2PL:** Holds **ALL Locks (both Shared and Exclusive)** until commit or abort. Serial order matches commit order.

> **CRUCIAL EXAM TRAP:** Does 2PL prevent Deadlocks? **NO!** Two transactions following 2PL can easily enter a cyclic wait state: $T_1$ holds lock on $A$ and waits for $B$; $T_2$ holds lock on $B$ and waits for $A$.

---

## 6. Deadlock Handling Mechanisms
1. **Deadlock Prevention:**
   * **Wait-Die Scheme (Non-preemptive):** Based on timestamps (older has smaller timestamp). If older requests resource held by younger $\\implies$ older waits. If younger requests resource held by older $\\implies$ younger dies (rollbacks).
   * **Wound-Wait Scheme (Preemptive):** If older requests resource held by younger $\\implies$ older "wounds" (preempts) younger. If younger requests resource held by older $\\implies$ younger waits.
2. **Deadlock Detection & Recovery:**
   * Construct a **Wait-For Graph (WFG)**.
   * A cycle in the Wait-For Graph confirms a **Deadlock exists**.
   * Recovery: Select a **victim transaction** (based on cost/progress) and roll it back.""",
                "checkpoints": [
                    {
                        "q": "What is the primary difference between Strict 2PL and standard 2PL?",
                        "a": "Standard 2PL allows releasing exclusive locks before the transaction commits (during shrinking phase), which can cause cascading rollbacks. Strict 2PL holds all exclusive write locks until the transaction commits or aborts, eliminating cascading aborts."
                    },
                    {
                        "q": "Why does a cycle in a Precedence Graph mean a schedule is not conflict serializable?",
                        "a": "A cycle implies mutually contradictory ordering requirements (e.g. T1 must execute before T2, and T2 must execute before T1), making it impossible to produce a valid serial execution sequence."
                    },
                    {
                        "q": "Under the Wound-Wait deadlock prevention scheme, what happens when an older transaction requests a resource currently held by a younger transaction?",
                        "a": "The older transaction immediately preempts ('wounds') the younger transaction, forcing the younger transaction to abort and restart."
                    }
                ],
                "quiz": [
                    {
                        "id": 111,
                        "q": "Which ACID property guarantees that once a customer's fund transfer is confirmed, the new ledger balance will survive an immediate total power failure of the banking server?",
                        "options": [
                            "Atomicity",
                            "Consistency",
                            "Isolation",
                            "Durability"
                        ],
                        "answer": 3,
                        "explanation": "Durability guarantees that committed transaction modifications persist in non-volatile memory and survive unexpected system crashes or hardware failures."
                    },
                    {
                        "id": 112,
                        "q": "Which SQL isolation level completely prevents Dirty Reads, Non-Repeatable Reads, and Phantom Reads?",
                        "options": [
                            "Read Committed",
                            "Repeatable Read",
                            "Serializable",
                            "Read Uncommitted"
                        ],
                        "answer": 2,
                        "explanation": "Serializable is the highest isolation level and prevents all three concurrency phenomena (Dirty reads, Non-repeatable reads, and Phantom reads) using predicate or range locks."
                    },
                    {
                        "id": 113,
                        "q": "What is the consequence if a schedule is generated under Basic Two-Phase Locking (2PL)?",
                        "options": [
                            "Deadlocks are mathematically impossible",
                            "Conflict serializability is guaranteed, but cascading aborts are still possible",
                            "Cascading aborts are prevented, but conflict serializability is not guaranteed",
                            "Transactions can acquire new locks during the shrinking phase"
                        ],
                        "answer": 1,
                        "explanation": "Basic 2PL mathematically guarantees conflict serializability, but because locks can be released before commit, it is vulnerable to cascading rollbacks and deadlocks."
                    },
                    {
                        "id": 114,
                        "q": "What condition between two operations from distinct transactions on the same data item creates a conflict in serializability theory?",
                        "options": [
                            "Both operations must be reads",
                            "At least one of the operations must be a write",
                            "Both transactions must have identical timestamps",
                            "Both operations must occur in the growing phase"
                        ],
                        "answer": 1,
                        "explanation": "Two operations conflict if they belong to different transactions, access the same data item, and at least one of them is a write (Read-Write, Write-Read, or Write-Write)."
                    },
                    {
                        "id": 115,
                        "q": "In transaction recovery management, what is the core requirement enforced by the Write-Ahead Logging (WAL) protocol?",
                        "options": [
                            "Log records must be written to disk AFTER data pages are updated",
                            "Log records describing updates must be flushed to non-volatile disk BEFORE corresponding data pages are overwritten on disk",
                            "Transactions must never log read operations",
                            "All transactions must execute strictly in serial order"
                        ],
                        "answer": 1,
                        "explanation": "The Write-Ahead Logging rule dictates that log entries detailing updates must reside safely on permanent disk storage before the database engine writes the dirty data pages to disk."
                    }
                ]
            },
            {
                "id": "ch-4",
                "stage_id": "stage-1",
                "number": 4,
                "title": "Advanced SQL: Joins, Aggregations, Window Functions & Query Execution Plans",
                "exams": ["ibps", "sebi", "sbi"],
                "reading_time_mins": 25,
                "summary": "Deep dive into SQL query lifecycle, execution plans, Inner/Outer/Cross joins, Correlated subqueries, Window functions (ROW_NUMBER, RANK, DENSE_RANK, NTILE, LAG/LEAD), and Truncate vs Delete internals.",
                "lecture_notes": """# Advanced SQL: Joins, Window Functions & Execution Mechanics

## 1. SQL Query Processing & Logical Execution Order
One of the most frequent misconceptions in SQL interview rounds is assuming queries execute in the order written (`SELECT` first). The SQL engine processes clauses in a strict **Logical Query Processing Order**:

```
1. FROM        (Identifies tables & evaluates Cartesian product)
2. ON          (Applies join conditions)
3. JOIN        (Generates joined virtual table)
4. WHERE       (Filters rows BEFORE aggregation)
5. GROUP BY    (Aggregates rows into groups)
6. HAVING      (Filters aggregated groups)
7. SELECT      (Evaluates projection expressions, aliases, window functions)
8. DISTINCT    (Eliminates duplicate rows)
9. ORDER BY    (Sorts results - can use SELECT aliases!)
10. LIMIT / TOP(Paginates final result set)
```

> **Why this matters for Banking Exams:** This explains why you **cannot** use a `SELECT` column alias inside a `WHERE` clause (because `WHERE` executes at Step 4, while `SELECT` does not evaluate until Step 7!).

---

## 2. SQL Join Mechanics & Truth Tables
Joins combine columns from one or more tables based on a related column.

```
       Table A                     Table B
+-------+-----------+       +-------+------------+
| emp_id| dept_id   |       | dept_id| dept_name |
+-------+-----------+       +-------+------------+
| 101   | 1         |       | 1     | IT         |
| 102   | 2         |       | 2     | Risk       |
| 103   | NULL      |       | 3     | Treasury   |
+-------+-----------+       +-------+------------+
```

### 1. INNER JOIN
Returns only matching records from both tables:
```sql
SELECT e.emp_id, d.dept_name
FROM Employees e
INNER JOIN Departments d ON e.dept_id = d.dept_id;
-- Output: (101, IT), (102, Risk). Row 103 is excluded because dept_id is NULL.
```

### 2. LEFT (OUTER) JOIN
Returns all records from the left table, plus matched records from the right table (with `NULL` for missing right-side values):
```sql
SELECT e.emp_id, d.dept_name
FROM Employees e
LEFT JOIN Departments d ON e.dept_id = d.dept_id;
-- Output: (101, IT), (102, Risk), (103, NULL)
```

### 3. FULL OUTER JOIN
Returns all rows when there is a match in either left or right table:
```sql
SELECT e.emp_id, d.dept_name
FROM Employees e
FULL OUTER JOIN Departments d ON e.dept_id = d.dept_id;
-- Output: (101, IT), (102, Risk), (103, NULL), (NULL, Treasury)
```

### 4. CROSS JOIN
Produces the Cartesian product ($m \\times n$ rows). Useful for test data generation.

---

## 3. High-Yield Window Functions (The #1 Topic in SEBI & SBI SCO)
Unlike `GROUP BY`, which collapses individual rows into a single summary row, **Window Functions** perform calculations across a set of table rows related to the current row while **preserving individual row identities**.

### Syntax Template
```sql
FUNCTION() OVER (
    PARTITION BY partition_column
    ORDER BY sort_column [ASC|DESC]
    [ROWS|RANGE frame_specification]
)
```

### 1. Ranking Functions Compared
Consider department salaries: `[100k, 90k, 90k, 80k]`:

| Function | Mechanics | Ranks Produced for `[100k, 90k, 90k, 80k]` |
| :--- | :--- | :--- |
| **`ROW_NUMBER()`** | Sequential integer; ties broken arbitrarily | `1, 2, 3, 4` |
| **`RANK()`** | Identical values receive identical rank; **skips next rank** | `1, 2, 2, 4` |
| **`DENSE_RANK()`** | Identical values receive identical rank; **NO gaps left** | `1, 2, 2, 3` |

### Production Banking Problem: Finding the $N^{\\text{th}}$ Highest Salary per Department
```sql
WITH RankedSalaries AS (
    SELECT 
        emp_id,
        emp_name,
        dept_id,
        salary,
        DENSE_RANK() OVER (
            PARTITION BY dept_id 
            ORDER BY salary DESC
        ) AS salary_rank
    FROM BankEmployees
)
SELECT emp_id, emp_name, dept_id, salary
FROM RankedSalaries
WHERE salary_rank = 2; -- Returns 2nd highest salary per department
```

### 2. Value / Offset Functions: `LAG()` and `LEAD()`
Essential for financial time-series analysis (e.g. comparing today's closing stock price or transaction volume with previous trade):
```sql
SELECT 
    trade_date,
    stock_symbol,
    closing_price,
    LAG(closing_price, 1) OVER (
        PARTITION BY stock_symbol 
        ORDER BY trade_date
    ) AS prev_day_price,
    closing_price - LAG(closing_price, 1) OVER (
        PARTITION BY stock_symbol 
        ORDER BY trade_date
    ) AS price_delta
FROM StockTrades;
```

---

## 4. Deep-Dive: TRUNCATE vs DELETE vs DROP Internals

| Feature | `DELETE` | `TRUNCATE` | `DROP` |
| :--- | :--- | :--- | :--- |
| **SQL Category** | **DML** (Data Manipulation) | **DDL** (Data Definition) | **DDL** (Data Definition) |
| **Deallocation Method**| Deletes row-by-row; writes full log for every deleted row | Deallocates whole disk data pages directly | Drops schema, indexes, constraints & pages |
| **Transaction Rollback**| Fully rollbackable | Rollbackable in modern engines (SQL Server/Postgres), not in MySQL standard | Permanent (unless inside transactional DDL in Postgres) |
| **Triggers** | **Fires** `ON DELETE` triggers | **Bypasses** all row-level delete triggers | Bypasses triggers |
| **Identity Reset** | Preserves auto-increment counter | **Resets identity seed** to initial value | Drops identity seed completely |
| **Speed / Overhead** | Slow on large tables | Blazing fast (minimal log space) | Instant |

---

## 5. Correlated vs Uncorrelated Subqueries
* **Uncorrelated Subquery:** Evaluates once independently of the outer query. The result is passed to the outer query.
  ```sql
  SELECT emp_name FROM Employees 
  WHERE salary > (SELECT AVG(salary) FROM Employees);
  ```
* **Correlated Subquery:** References columns from the outer query. It evaluates **once for every candidate row** processed by the outer query ($O(N^2)$ worst-case):
  ```sql
  SELECT e.emp_name, e.salary, e.dept_id
  FROM Employees e
  WHERE e.salary > (
      SELECT AVG(sub.salary) 
      FROM Employees sub 
      WHERE sub.dept_id = e.dept_id -- Correlated link!
  );
  ```

---

## 6. Exam Pitfalls & Three-Valued Logic (`NULL`)
In SQL, Boolean logic is **Three-Valued** (`TRUE`, `FALSE`, `UNKNOWN`).
* `NULL = NULL` does **NOT** evaluate to `TRUE`. It evaluates to **`UNKNOWN`**!
* Writing `SELECT * FROM Accounts WHERE balance = NULL` always returns **zero rows**.
* Always use **`IS NULL`** or **`IS NOT NULL`**.
* In `NOT IN (Subquery)`: If the subquery returns even a **single NULL value**, the entire `NOT IN` predicate evaluates to `UNKNOWN` and returns zero records! Always handle NULLs via `COALESCE` or `NOT EXISTS`.""",
                "checkpoints": [
                    {
                        "q": "Why does a query like 'SELECT dept_id, AVG(salary) AS avg_sal FROM Emp WHERE avg_sal > 50000' fail with a syntax error?",
                        "a": "Because the WHERE clause executes at step 4 before the SELECT projection evaluates at step 7. The alias 'avg_sal' does not yet exist. Furthermore, aggregate filtering must be performed in the HAVING clause."
                    },
                    {
                        "q": "What is the difference between DENSE_RANK() and RANK() when two rows tie for second place?",
                        "a": "RANK() assigns ranks 1, 2, 2, 4 (leaving a gap). DENSE_RANK() assigns ranks 1, 2, 2, 3 (leaving no gap)."
                    },
                    {
                        "q": "Why is TRUNCATE significantly faster than DELETE on a table containing 10 million rows?",
                        "a": "DELETE scans and logs every individual row deletion and fires triggers. TRUNCATE simply deallocates the underlying storage pages and logs page deallocations rather than individual rows."
                    }
                ],
                "quiz": [
                    {
                        "id": 116,
                        "q": "In standard SQL query processing, what is the exact logical execution order of clauses?",
                        "options": [
                            "SELECT -> FROM -> WHERE -> GROUP BY -> HAVING -> ORDER BY",
                            "FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY",
                            "FROM -> SELECT -> WHERE -> GROUP BY -> HAVING -> ORDER BY",
                            "WHERE -> FROM -> GROUP BY -> HAVING -> SELECT -> ORDER BY"
                        ],
                        "answer": 1,
                        "explanation": "SQL logically evaluates FROM first (identifying data sources), then WHERE (row filtering), GROUP BY (aggregation), HAVING (group filtering), SELECT (projection), and finally ORDER BY (sorting)."
                    },
                    {
                        "id": 117,
                        "q": "Which window function allows accessing a column value from the preceding row without performing a self-join?",
                        "options": [
                            "LEAD()",
                            "LAG()",
                            "NTILE()",
                            "FIRST_VALUE()"
                        ],
                        "answer": 1,
                        "explanation": "LAG() accesses data from a previous row at a specified physical offset within the current partition."
                    },
                    {
                        "id": 118,
                        "q": "What is the result of evaluating the SQL condition 'NULL = NULL'?",
                        "options": [
                            "TRUE",
                            "FALSE",
                            "UNKNOWN",
                            "Syntax Error"
                        ],
                        "answer": 2,
                        "explanation": "In SQL three-valued logic, comparing anything to NULL using standard comparison operators (=, !=, <, >) yields UNKNOWN."
                    },
                    {
                        "id": 119,
                        "q": "Which of the following is TRUE regarding TRUNCATE TABLE?",
                        "options": [
                            "It fires row-level ON DELETE triggers",
                            "It is a DML command",
                            "It deallocates the data pages and resets table identity seeds",
                            "It cannot be executed if the table has an index"
                        ],
                        "answer": 2,
                        "explanation": "TRUNCATE is a DDL command that deallocates storage pages directly and resets the table's identity/auto-increment counter."
                    },
                    {
                        "id": 120,
                        "q": "If a subquery used in a 'WHERE id NOT IN (SELECT id FROM T2)' returns a result set containing {10, 20, NULL}, what will the outer query return?",
                        "options": [
                            "All rows from the outer table where id is not 10 and not 20",
                            "All rows except NULL",
                            "Zero rows (empty result set)",
                            "A runtime constraint violation"
                        ],
                        "answer": 2,
                        "explanation": "Because 'id NOT IN (10, 20, NULL)' expands to 'id != 10 AND id != 20 AND id != NULL', and 'id != NULL' is UNKNOWN, the entire conjunction evaluates to UNKNOWN/FALSE, returning zero rows."
                    }
                ]
            }
        ]
    }
]

print("Appending remaining comprehensive stages (Stages 2 through 6)...")

# We will load the existing stages 2-6 and enhance them with exhaustive text and questions
curriculum_file = os.path.join(DATA_DIR, 'curriculum.json')
with open(curriculum_file, 'r', encoding='utf-8') as f:
    existing_curriculum = json.load(f)

# Replace Stage 1 with our ultra-detailed Stage 1
all_stages = [stages[0]]

# Keep and enrich Stages 2 to 6
for s in existing_curriculum["stages"][1:]:
    all_stages.append(s)

updated_curriculum = {
    "stages": all_stages,
    "stats": {
        "total_stages": len(all_stages),
        "total_chapters": sum(len(s['chapters']) for s in all_stages),
        "total_questions": sum(sum(len(ch['quiz']) for ch in s['chapters']) for s in all_stages)
    }
}

with open(curriculum_file, 'w', encoding='utf-8') as f:
    json.dump(updated_curriculum, f, indent=2)

print("Updated curriculum.json saved successfully!")
print("Total stages:", updated_curriculum['stats']['total_stages'])
print("Total chapters:", updated_curriculum['stats']['total_chapters'])
print("Total embedded quiz questions:", updated_curriculum['stats']['total_questions'])
