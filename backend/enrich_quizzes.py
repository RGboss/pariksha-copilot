import json
import os

CURRICULUM_PATH = 'E:/study material/prep_platform/data/curriculum.json'

with open(CURRICULUM_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Dictionary of additional high-yield questions for chapters 10 through 21
additional_quizzes = {
    "ch-10": [
        {
            "id": 228,
            "q": "Which Linux command displays the current default file creation permission mask (umask), and what is the effective file permission if umask is 022 on a newly created file (base 666)?",
            "options": [
                "Command 'umask'; effective permission is 644 (rw-r--r--)",
                "Command 'chmod'; effective permission is 755 (rwxr-xr-x)",
                "Command 'chown'; effective permission is 600 (rw-------)",
                "Command 'umask'; effective permission is 777 (rwxrwxrwx)"
            ],
            "answer": 0,
            "explanation": "The umask command reveals the permission mask. Subtracting umask 022 from default file base permissions 666 gives 644 (User=rw-, Group=r--, Others=r--)."
        },
        {
            "id": 229,
            "q": "In a Linux bash pipeline 'cat accounts.csv | grep \"ACTIVE\" | awk -F\",\" \"{print $2}\" | sort | uniq -c', what is the exact function of the final 'uniq -c' command?",
            "options": [
                "It deletes all unique lines and keeps only duplicates",
                "It filters out adjacent duplicate lines and prefixes each unique line with the count of its occurrences",
                "It sorts the input in reverse numerical order",
                "It splits lines into comma-delimited columns"
            ],
            "answer": 1,
            "explanation": "The 'uniq -c' command removes duplicate adjacent lines from sorted input and prefixes each unique line with the count of times it occurred."
        },
        {
            "id": 230,
            "q": "What is the difference between the hard link and symbolic (soft) link in the Linux Virtual File System (VFS)?",
            "options": [
                "A hard link shares the exact same inode number as the target file, while a soft link is an independent file pointing to the target's pathname",
                "A hard link can span across different mounted disk filesystems, while a soft link cannot",
                "Deleting the original file keeps soft links intact but breaks hard links",
                "Hard links only apply to directories"
            ],
            "answer": 0,
            "explanation": "A hard link is another directory entry pointing directly to the original file's inode number. A symbolic link is a separate file with its own inode whose contents are the path string to the target file."
        }
    ],
    "ch-11": [
        {
            "id": 308,
            "q": "According to the Liskov Substitution Principle (LSP), why does creating a class Square that extends Rectangle violate LSP when Rectangle exposes setWidth(int) and setHeight(int)?",
            "options": [
                "Because Java does not permit overriding setter methods",
                "Because client code assuming a Rectangle invariant (width can change independently of height) will break when passed a Square",
                "Because Square requires more memory than Rectangle",
                "Because inheritance between geometric shapes is disallowed by OOP"
            ],
            "answer": 1,
            "explanation": "LSP states that subtypes must be substitutable for their base types without altering correctness. If client code modifies width expecting height to remain unchanged, passing a Square violates this expectation and breaks program correctness."
        },
        {
            "id": 309,
            "q": "In Java method overriding, what is the rule regarding the return type of the overriding subclass method?",
            "options": [
                "The return type must be strictly void",
                "The return type must be identical or a covariant subtype of the superclass method return type",
                "The return type can be any completely unrelated object type",
                "The return type must be a primitive type"
            ],
            "answer": 1,
            "explanation": "Since Java 5, covariant return types are permitted: the overriding method in a subclass can return a subtype of the return type declared in the superclass method."
        },
        {
            "id": 310,
            "q": "Which design pattern is best suited for decoupling an object's construction process from its representation so that the same construction process can create different representations?",
            "options": [
                "Singleton Pattern",
                "Builder Pattern",
                "Observer Pattern",
                "Adapter Pattern"
            ],
            "answer": 1,
            "explanation": "The Builder pattern separates the construction of a complex object from its representation, allowing the step-by-step creation of diverse configurations."
        }
    ],
    "ch-12": [
        {
            "id": 311,
            "q": "In Java, what is the default initial capacity and load factor of a standard java.util.HashMap, and at what threshold does it trigger resizing?",
            "options": [
                "Capacity 16, Load Factor 0.75, resizes when elements reach 12 (16 * 0.75)",
                "Capacity 10, Load Factor 0.50, resizes when elements reach 5",
                "Capacity 32, Load Factor 1.00, resizes when elements reach 32",
                "Capacity 64, Load Factor 0.80, resizes when elements reach 51"
            ],
            "answer": 0,
            "explanation": "Default capacity is 16 and load factor is 0.75. When the total entries exceed capacity * load factor (16 * 0.75 = 12), the table doubles its capacity to 32."
        },
        {
            "id": 312,
            "q": "What is the difference between Comparable and Comparator interfaces in Java?",
            "options": [
                "Comparable provides natural ordering via compareTo(Object) inside the class; Comparator provides custom external ordering via compare(Object, Object)",
                "Comparable is in java.util while Comparator is in java.lang",
                "Comparable cannot sort Collections while Comparator can only sort arrays",
                "Both interfaces are identical and interchangeable"
            ],
            "answer": 0,
            "explanation": "Comparable defines natural ordering implemented by the domain class itself (compareTo). Comparator is a separate functional interface defining custom sort strategies (compare(o1, o2))."
        },
        {
            "id": 313,
            "q": "Why is java.lang.String designed to be immutable in Java?",
            "options": [
                "Security in class loading and networking, thread safety without synchronization, and caching in the String Pool",
                "To reduce the heap memory footprint to zero",
                "To prevent strings from being stored in ArrayLists",
                "Because primitive types in Java are immutable"
            ],
            "answer": 0,
            "explanation": "String immutability enables the String Constant Pool (sharing references), guarantees thread safety without locking, and ensures security when passing strings as file paths, database URLs, and network sockets."
        }
    ],
    "ch-13": [
        {
            "id": 314,
            "q": "What is the maximum number of nodes in a binary tree of height h (where a root-only tree has height 0)?",
            "options": [
                "2^h",
                "2^(h+1) - 1",
                "2^(h-1)",
                "h^2"
            ],
            "answer": 1,
            "explanation": "The maximum number of nodes in a binary tree of height h is the geometric series 2^0 + 2^1 + ... + 2^h = 2^(h+1) - 1."
        },
        {
            "id": 315,
            "q": "Which data structure is required to efficiently implement Dijkstra's Single-Source Shortest Path algorithm to achieve O((V + E) log V) time complexity?",
            "options": [
                "FIFO Queue",
                "Min-Heap (Priority Queue)",
                "Stack",
                "Circular Array"
            ],
            "answer": 1,
            "explanation": "Dijkstra's algorithm uses a Min-Heap (priority queue) to greedily extract the unvisited vertex with the minimum tentative distance in O(log V) time."
        },
        {
            "id": 316,
            "q": "Given the Preorder traversal [A, B, D, E, C, F] and Inorder traversal [D, B, E, A, F, C] of a binary tree, what is the root of the left subtree of A?",
            "options": [
                "D",
                "B",
                "E",
                "C"
            ],
            "answer": 1,
            "explanation": "In Preorder, the first element (A) is the tree root. In Inorder, elements to the left of A are [D, B, E], forming the left subtree. In Preorder, the first element among [D, B, E] is B, meaning B is the root of the left subtree."
        }
    ],
    "ch-14": [
        {
            "id": 317,
            "q": "If a banking loan application requires applicant age to be an integer between 18 and 60 (inclusive), which test values represent the complete set of Boundary Value Analysis (BVA) test cases?",
            "options": [
                "17, 18, 19, 59, 60, 61",
                "10, 30, 70",
                "18, 35, 60",
                "17, 18, 60, 61 only"
            ],
            "answer": 0,
            "explanation": "Standard 2-boundary BVA tests the minimum boundary (18) with values just below (17), on (18), and just above (19), and the maximum boundary (60) with values just below (59), on (60), and just above (61)."
        },
        {
            "id": 318,
            "q": "What is the formula for Thomas McCabe's Cyclomatic Complexity V(G) of a program control flow graph with E edges, N nodes, and P connected components?",
            "options": [
                "V(G) = E - N + 2P",
                "V(G) = E + N - P",
                "V(G) = E / N * P",
                "V(G) = 2E - N + P"
            ],
            "answer": 0,
            "explanation": "McCabe's Cyclomatic Complexity formula is V(G) = E - N + 2P (or Decision Points + 1 for single component programs). It defines the number of linearly independent execution paths."
        },
        {
            "id": 319,
            "q": "In software testing fundamentals, what is the classic distinction between Verification and Validation?",
            "options": [
                "Verification checks 'Are we building the product right?' (process adherence, reviews); Validation checks 'Are we building the right product?' (customer needs, dynamic testing)",
                "Verification is dynamic testing; Validation is static code inspection",
                "Verification is done by end users; Validation is done by developers",
                "Both terms mean identical testing activities"
            ],
            "answer": 0,
            "explanation": "Verification ensures software conforms to its specified requirements (static reviews, inspections). Validation ensures the software meets real customer expectations and intended use (dynamic execution)."
        }
    ],
    "ch-15": [
        {
            "id": 405,
            "q": "What is the difference between Write-Through and Write-Behind (Write-Back) caching strategies?",
            "options": [
                "Write-Through writes synchronously to both cache and primary DB; Write-Behind writes immediately to cache and updates the primary DB asynchronously in batches",
                "Write-Through updates only the DB; Write-Behind updates only RAM",
                "Write-Through is asynchronous; Write-Behind is synchronous",
                "Write-Behind eliminates the need for a database"
            ],
            "answer": 0,
            "explanation": "Write-Through provides strong consistency by synchronously writing to cache and DB together. Write-Behind provides high write throughput by caching writes immediately and batching writes to the DB asynchronously (with risk of data loss on power failure)."
        },
        {
            "id": 406,
            "q": "In Consistent Hashing used by distributed caches (e.g. Redis Cluster / Dynamo), why are Virtual Nodes (vnodes) utilized?",
            "options": [
                "To encrypt cached keys",
                "To ensure uniform distribution of data keys across physical machines and avoid hot-spot imbalances",
                "To bypass hash calculations",
                "To replicate data to secondary datacenters"
            ],
            "answer": 1,
            "explanation": "Virtual nodes map each physical node to multiple points along the hash ring, ensuring an even distribution of keys across servers and preventing hot spots."
        },
        {
            "id": 407,
            "q": "In an Apache Kafka consumer group, what happens when a new consumer instance joins the group?",
            "options": [
                "The entire topic is deleted",
                "A consumer group Rebalance is triggered, and partition assignments are redistributed among members",
                "All existing consumers stop permanently",
                "Partitions are duplicated"
            ],
            "answer": 1,
            "explanation": "When a consumer joins or leaves, the Group Coordinator triggers a Rebalance to redistribute partition assignments among all active group members."
        }
    ],
    "ch-16": [
        {
            "id": 408,
            "q": "In distributed microservices architectures, how does the Saga Pattern manage data consistency across services instead of a distributed Two-Phase Commit (2PC)?",
            "options": [
                "By locking all databases simultaneously for 10 minutes",
                "By executing a sequence of local transactions, using Compensating Transactions to roll back previous steps if a local transaction fails",
                "By merging all microservices into a single shared database",
                "By ignoring failed transactions"
            ],
            "answer": 1,
            "explanation": "The Saga pattern coordinates distributed transactions as a series of local transactions. If a step fails, the saga executes compensating transactions in reverse order to undo earlier changes."
        },
        {
            "id": 409,
            "q": "Which HTTP methods are defined as Idempotent according to the HTTP/1.1 specification (RFC 7231)?",
            "options": [
                "GET, PUT, DELETE, HEAD, OPTIONS (making multiple identical requests produces the same side-effect as a single request)",
                "POST and PATCH only",
                "POST, PUT, DELETE",
                "No HTTP method is idempotent"
            ],
            "answer": 0,
            "explanation": "An idempotent HTTP method produces identical server side-effects whether called once or multiple times. GET, PUT, DELETE, HEAD, and OPTIONS are idempotent; POST is not."
        },
        {
            "id": 410,
            "q": "In Spring Framework, what is the default scope of a declared Spring Bean?",
            "options": [
                "Prototype",
                "Singleton",
                "Request",
                "Session"
            ],
            "answer": 1,
            "explanation": "In Spring, the default bean scope is Singleton: the Spring IoC container creates and manages exactly one shared instance of the bean per ApplicationContext."
        }
    ],
    "ch-17": [
        {
            "id": 411,
            "q": "Which Amazon S3 storage class is designed for long-term archiving of financial audit records where data retrieval within 3 to 5 hours is acceptable at the lowest possible cost?",
            "options": [
                "Amazon S3 Standard",
                "Amazon S3 Intelligent-Tiering",
                "Amazon S3 Glacier Flexible Retrieval",
                "Amazon S3 One Zone-IA"
            ],
            "answer": 2,
            "explanation": "S3 Glacier Flexible Retrieval (formerly Glacier) is designed for archiving compliance data where retrieval takes between a few minutes to hours at extremely low cost."
        },
        {
            "id": 412,
            "q": "In Docker containerization, what is the primary security advantage of using multi-stage builds in a Dockerfile?",
            "options": [
                "It eliminates the need for base images",
                "It separates build tools and compilers from the final runtime image, drastically reducing image size and attack surface",
                "It forces containers to run in privileged mode",
                "It enables multi-threading on single-core CPUs"
            ],
            "answer": 1,
            "explanation": "Multi-stage builds leave behind SDKs, compilers, and source files in intermediate build containers, copying only the compiled binary artifact into a lean runtime image, minimizing vulnerabilities."
        },
        {
            "id": 413,
            "q": "What is the key difference between the CMD and ENTRYPOINT instructions in a Dockerfile?",
            "options": [
                "ENTRYPOINT sets the default executable for the container, while CMD provides default arguments that can be easily overridden from the docker run CLI",
                "CMD is mandatory while ENTRYPOINT is deprecated",
                "ENTRYPOINT runs during image build while CMD runs at container startup",
                "There is no difference between them"
            ],
            "answer": 0,
            "explanation": "ENTRYPOINT configures the fixed executable command. CMD supplies default parameters that are easily overridden when passing arguments to 'docker run'."
        }
    ],
    "ch-18": [
        {
            "id": 503,
            "q": "What is the output of the following Python snippet?\n\ndef append_item(val, target=[]):\n    target.append(val)\n    return target\n\nprint(append_item(1))\nprint(append_item(2))",
            "options": [
                "[1] and [2]",
                "[1] and [1, 2]",
                "[1] and [2, 1]",
                "Runtime TypeError"
            ],
            "answer": 1,
            "explanation": "In Python, default parameter expressions are evaluated ONCE at function definition time, not at invocation. The list target is created once and shared across subsequent calls that do not pass a target argument."
        },
        {
            "id": 504,
            "q": "What is the difference between shallow copy (copy.copy) and deep copy (copy.deepcopy) in Python?",
            "options": [
                "A shallow copy creates a new container but inserts references to the original nested objects; a deep copy recursively duplicates all nested objects",
                "A shallow copy copies only integers; a deep copy copies strings",
                "A shallow copy is immutable; a deep copy is mutable",
                "Deep copy is only used for dictionary keys"
            ],
            "answer": 0,
            "explanation": "copy.copy() constructs a new collection and populates it with references to the child items found in the original. copy.deepcopy() recursively copies all nested objects, creating completely independent copies."
        },
        {
            "id": 505,
            "q": "What keyword turns a standard Python function into a Generator that yields values lazily on-demand without populating full lists in RAM?",
            "options": [
                "return",
                "yield",
                "generate",
                "await"
            ],
            "answer": 1,
            "explanation": "The 'yield' statement suspends function execution and yields a value back to the caller, resuming state on the next call to next(), achieving O(1) memory usage."
        }
    ],
    "ch-19": [
        {
            "id": 506,
            "q": "In Pandas DataFrame indexing, what is the fundamental difference between df.loc and df.iloc?",
            "options": [
                "df.loc is strictly label-based (using column and index labels); df.iloc is strictly integer position-based (0 to N-1)",
                "df.loc selects columns only; df.iloc selects rows only",
                "df.loc is deprecated in modern Pandas",
                "df.iloc cannot take slice ranges"
            ],
            "answer": 0,
            "explanation": "df.loc accesses rows and columns by text labels or boolean vectors. df.iloc accesses rows and columns by numerical integer positions."
        },
        {
            "id": 507,
            "q": "How does NumPy achieve orders-of-magnitude faster computation than standard Python list loops for numerical operations?",
            "options": [
                "By disabling Python's type checking and executing contiguous C-array memory blocks with SIMD vectorization",
                "By running Python bytecodes in parallel on multiple threads",
                "By converting all numbers into strings",
                "By caching results in a Redis database"
            ],
            "answer": 0,
            "explanation": "NumPy arrays are stored in contiguous C memory blocks with fixed data types, allowing CPU SIMD (Single Instruction Multiple Data) vector instructions to operate without Python interpreter overhead."
        },
        {
            "id": 508,
            "q": "In Python regular expressions (re module), what does the pattern r'\\b\\d{10}\\b' match?",
            "options": [
                "Any sequence of 10 letters",
                "Exactly 10 consecutive digits bounded by word boundaries (e.g. a 10-digit mobile number or bank account token)",
                "Any number greater than 10",
                "A 10-character alphanumeric password"
            ],
            "answer": 1,
            "explanation": "\\b asserts a word boundary, and \\d{10} matches exactly 10 consecutive decimal digits (0-9)."
        }
    ],
    "ch-20": [
        {
            "id": 604,
            "q": "What is an Insecure Direct Object Reference (IDOR) vulnerability in banking web applications?",
            "options": [
                "An application exposes direct internal database keys (e.g., /account/view?id=1052) in request parameters without verifying if the authenticated user owns that resource",
                "An SQL injection attack through database triggers",
                "A hardware fault on physical RAM chips",
                "An unencrypted Wi-Fi router"
            ],
            "answer": 0,
            "explanation": "IDOR occurs when an application provides direct access to objects based on user-supplied input without implementing authorization checks, allowing an attacker to access other users' private records by changing an ID."
        },
        {
            "id": 605,
            "q": "What browser cookie attribute should be configured to prevent Cross-Site Request Forgery (CSRF) attacks by restricting cookie transmission on cross-origin requests?",
            "options": [
                "HttpOnly",
                "Secure",
                "SameSite=Strict",
                "Domain"
            ],
            "answer": 2,
            "explanation": "SameSite=Strict guarantees that the browser never sends the cookie in cross-site requests, effectively neutralizing CSRF attacks."
        },
        {
            "id": 606,
            "q": "What is the difference between Stored XSS and Reflected XSS?",
            "options": [
                "Stored XSS permanently stores the malicious script on the server/database to attack visitors later; Reflected XSS reflects the payload off the server immediately via URL parameters or form submissions",
                "Stored XSS attacks the server hardware; Reflected XSS attacks the router",
                "Reflected XSS requires database access; Stored XSS does not",
                "There is no functional difference"
            ],
            "answer": 0,
            "explanation": "Stored XSS persists on the target server (e.g. database comment, profile field). Reflected XSS reflects off the web server in an error message, search result, or link parameter."
        }
    ],
    "ch-21": [
        {
            "id": 607,
            "q": "In Public Key Infrastructure (PKI) and SSL/TLS, what is the role of a Certificate Authority (CA)?",
            "options": [
                "A trusted third party that verifies an entity's identity and digitally signs its X.509 certificate to bind its public key to its domain name",
                "A router that forwards encrypted packets",
                "A private key storage database",
                "A proxy that decrypts user passwords"
            ],
            "answer": 0,
            "explanation": "A Certificate Authority is a trusted entity that issues digital certificates validating that a public key belongs to the designated organization/domain."
        },
        {
            "id": 608,
            "q": "What is Perfect Forward Secrecy (PFS) in TLS handshakes (achieved via Ephemeral Diffie-Hellman - ECDHE)?",
            "options": [
                "A cryptographic feature ensuring that compromise of the server's long-term private key does NOT compromise previously recorded encrypted session traffic",
                "An encryption scheme that cannot be decrypted even with the private key",
                "A protocol that eliminates symmetric encryption",
                "A firewall rule blocking foreign IPs"
            ],
            "answer": 0,
            "explanation": "PFS generates unique ephemeral session keys per session via Diffie-Hellman. If the server's private master key is compromised in the future, past recorded communications cannot be decrypted."
        },
        {
            "id": 609,
            "q": "Under the Reserve Bank of India (RBI) Cyber Security Framework, what is the mandatory reporting timeframe within which banks must report critical cyber security incidents to the RBI?",
            "options": [
                "Within 2 to 6 hours of incident detection",
                "Within 30 business days",
                "Only during annual audits",
                "Within 72 hours"
            ],
            "answer": 0,
            "explanation": "RBI circulars mandate that commercial banks must report all unusual cybersecurity incidents to the RBI within 2 to 6 hours of detection."
        }
    ]
}

# Apply additional quizzes to curriculum
total_added = 0
for stage in data["stages"]:
    for chapter in stage["chapters"]:
        cid = chapter["id"]
        if cid in additional_quizzes:
            chapter["quiz"].extend(additional_quizzes[cid])
            total_added += len(additional_quizzes[cid])

data["stats"]["total_questions"] = sum(
    sum(len(ch["quiz"]) for ch in s["chapters"]) for s in data["stages"]
)

with open(CURRICULUM_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print(f"Successfully added {total_added} high-yield questions across chapters 10-21!")
print(f"Total embedded questions in curriculum: {data['stats']['total_questions']}")
