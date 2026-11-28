package com.pariksha.copilot.data

import kotlinx.serialization.Serializable

@Serializable
data class UserProfile(
    val name: String,
    val email: String,
    val targetExam: String = "SEBI Grade A (IT Stream)",
    val token: String = "",
    val isLoggedIn: Boolean = false,
    val streakDays: Int = 7,
    val dailyTargetHours: Int = 5
)

@Serializable
data class ChatMessage(
    val id: String = java.util.UUID.randomUUID().toString(),
    val role: String, // "user" or "model"
    val content: String,
    val timestamp: Long = System.currentTimeMillis(),
    val isLoading: Boolean = false,
    val isError: Boolean = false
)

@Serializable
data class ModelInfo(
    val id: String,
    val name: String,
    val description: String = ""
)

@Serializable
data class FlashcardItem(
    val id: String,
    val question: String,
    val answer: String,
    val topic: String,
    val box: Int = 1, // Leitner box 1 to 5
    val difficulty: String = "Medium",
    val isFlipped: Boolean = false
)

@Serializable
data class StudyTaskItem(
    val id: String,
    val title: String,
    val subject: String,
    val estimatedMinutes: Int,
    val isCompleted: Boolean = false,
    val priority: String = "High" // High, Medium, Low
)

val AVAILABLE_MODELS = listOf(
    ModelInfo("gemini-2.5-flash", "Gemini 2.5 Flash", "Super fast, high quality exam tutor"),
    ModelInfo("gemini-2.5-pro", "Gemini 2.5 Pro", "Deepest reasoning for complex mains"),
    ModelInfo("gemini-2.0-flash", "Gemini 2.0 Flash", "Latest generation low-latency model"),
    ModelInfo("gemini-1.5-flash", "Gemini 1.5 Flash", "Lightweight, cost-effective"),
    ModelInfo("gemini-1.5-pro", "Gemini 1.5 Pro", "Long context analysis for full papers")
)

val EXAM_OPTIONS = listOf(
    "SEBI Grade A (IT Stream)",
    "SBI SCO (Deputy Manager IT)",
    "IBPS SO (IT Officer Scale-I)",
    "RBI Grade B (General/DEPR)",
    "UPSC CSE 2027 (IAS/IPS)",
    "SSC CGL (Tier 1 & 2)",
    "Railways RRB NTPC",
    "GATE CSE / IT",
    "NABARD Grade A Officer",
    "Custom / State PSC"
)

val DEFAULT_FLASHCARDS = listOf(
    FlashcardItem(
        id = "fc-1",
        question = "What is the primary role and statutory objective of SEBI under the SEBI Act, 1992?",
        answer = "To protect the interests of investors in securities, promote the development of, and regulate the securities market in India through registration, insider trading prevention, and market surveillance.",
        topic = "Securities Market Regulations",
        box = 1,
        difficulty = "High Yield"
    ),
    FlashcardItem(
        id = "fc-2",
        question = "What are the 4 ACID properties in Database Management Systems (DBMS)?",
        answer = "1. Atomicity (All or nothing)\n2. Consistency (Maintains schema constraints)\n3. Isolation (Transactions execute independently)\n4. Durability (Committed changes survive system crash)",
        topic = "Database Management Systems",
        box = 2,
        difficulty = "Core Concept"
    ),
    FlashcardItem(
        id = "fc-3",
        question = "Differentiate between TCP and UDP protocols in Computer Networking.",
        answer = "TCP is connection-oriented, reliable (3-way handshake, retransmissions, flow control via sliding window). UDP is connectionless, unreliable, low-overhead, ideal for real-time streaming and DNS queries.",
        topic = "Computer Networks",
        box = 3,
        difficulty = "High Yield"
    ),
    FlashcardItem(
        id = "fc-4",
        question = "What is the difference between Symmetric and Asymmetric Key Encryption?",
        answer = "Symmetric uses a single secret key for encryption & decryption (AES, DES). Asymmetric uses a mathematically linked public-private key pair (RSA, ECC), solving the key exchange problem.",
        topic = "Cybersecurity & IT",
        box = 1,
        difficulty = "Mains Level"
    )
)

val DEFAULT_TASKS = listOf(
    StudyTaskItem(
        id = "task-1",
        title = "Solve 25 MCQs on SQL Normalization (1NF, 2NF, 3NF, BCNF)",
        subject = "DBMS",
        estimatedMinutes = 45,
        isCompleted = false,
        priority = "High"
    ),
    StudyTaskItem(
        id = "task-2",
        title = "Revise SEBI Regulations & ICDR Guidelines (Chapter 3)",
        subject = "Securities Law",
        estimatedMinutes = 60,
        isCompleted = true,
        priority = "High"
    ),
    StudyTaskItem(
        id = "task-3",
        title = "Active Recall Flashcards: OSI vs TCP/IP Protocol Stack",
        subject = "Networking",
        estimatedMinutes = 30,
        isCompleted = false,
        priority = "Medium"
    ),
    StudyTaskItem(
        id = "task-4",
        title = "Read Monthly Financial & Banking Awareness Capsule",
        subject = "General Awareness",
        estimatedMinutes = 40,
        isCompleted = false,
        priority = "Medium"
    )
)

@Serializable
data class QuizQuestion(
    val id: String,
    val prompt: String,
    val options: List<String>,
    val correctOptionIndex: Int,
    val explanation: String,
    val subject: String,
    val citation: String = ""
)

@Serializable
data class QuizItem(
    val id: String,
    val title: String,
    val description: String,
    val subject: String,
    val durationMinutes: Int = 10,
    val questions: List<QuizQuestion>
)

@Serializable
data class QuizAttemptResult(
    val quizId: String,
    val totalQuestions: Int,
    val correctCount: Int,
    val scorePercentage: Double,
    val timeSpentSeconds: Int,
    val answers: Map<Int, Int> = emptyMap()
)

val DEFAULT_QUIZZES = listOf(
    QuizItem(
        id = "quiz-dbms",
        title = "DBMS & Normalization CBT Mock",
        description = "High-yield test covering Boyce-Codd Normal Form, Functional Dependencies, Relational Algebra, and Indexing.",
        subject = "Database Management Systems",
        durationMinutes = 10,
        questions = listOf(
            QuizQuestion(
                id = "dbms-q1",
                prompt = "A relation is in Boyce-Codd Normal Form (BCNF) if and only if for every non-trivial functional dependency X -> Y:",
                options = listOf(
                    "A. Y is a prime attribute",
                    "B. X is a superkey of the relation",
                    "C. X is a primary key and Y is atomic",
                    "D. No transitive dependencies exist"
                ),
                correctOptionIndex = 1,
                explanation = "A relation is in BCNF if for every functional dependency X -> Y, X is a superkey. Unlike 3NF, BCNF does not allow Y to be a prime attribute if X is not a superkey.",
                subject = "DBMS",
                citation = "Silberschatz Database System Concepts, Chapter 8"
            ),
            QuizQuestion(
                id = "dbms-q2",
                prompt = "In transaction processing, the 'Durability' property of ACID guarantees which of the following?",
                options = listOf(
                    "A. All operations in a transaction succeed or all fail",
                    "B. Concurrent transactions do not interfere with each other",
                    "C. Once committed, changes persist even in the event of a power crash",
                    "D. The database remains in a valid schema state before and after execution"
                ),
                correctOptionIndex = 2,
                explanation = "Durability ensures that once a transaction commits, its modifications are permanently recorded in non-volatile storage and will survive system failures.",
                subject = "DBMS",
                citation = "Database Management Systems by Ramakrishnan & Gehrke"
            ),
            QuizQuestion(
                id = "dbms-q3",
                prompt = "Which SQL constraint enforces referential integrity between two relational tables?",
                options = listOf(
                    "A. PRIMARY KEY",
                    "B. UNIQUE KEY",
                    "C. FOREIGN KEY",
                    "D. CHECK CONSTRAINT"
                ),
                correctOptionIndex = 2,
                explanation = "A FOREIGN KEY creates a link between data in two tables, preventing actions that would destroy links and ensuring values in the child table match the parent table.",
                subject = "DBMS",
                citation = "SQL-92 Standard / ISO/IEC 9075"
            ),
            QuizQuestion(
                id = "dbms-q4",
                prompt = "What is the primary operational advantage of a B+ Tree index over a binary search tree in secondary storage databases?",
                options = listOf(
                    "A. B+ trees eliminate all hash collisions completely",
                    "B. High fan-out minimizes disk I/O operations and leaf-level linked lists enable fast range queries",
                    "C. B+ trees require zero memory overhead for parent nodes",
                    "D. B+ trees guarantee constant O(1) retrieval time for all lookups"
                ),
                correctOptionIndex = 1,
                explanation = "Because secondary storage has slow block reads, B+ Trees use a wide branching factor (high fan-out) to keep the tree height low (typically 3-4 levels), minimizing disk seek operations. The sequential linked list at leaf nodes allows fast range scanning.",
                subject = "DBMS",
                citation = "Navathe & Elmasri Fundamentals of Database Systems"
            ),
            QuizQuestion(
                id = "dbms-q5",
                prompt = "Which isolation level in ANSI SQL prevents 'Dirty Reads' and 'Non-Repeatable Reads', but may still experience 'Phantom Reads'?",
                options = listOf(
                    "A. Read Uncommitted",
                    "B. Read Committed",
                    "C. Repeatable Read",
                    "D. Serializable"
                ),
                correctOptionIndex = 2,
                explanation = "Repeatable Read locks rows that are read, preventing dirty reads and non-repeatable reads. However, newly inserted rows matching a range query (phantom rows) can still appear in subsequent queries unless Serializable isolation is used.",
                subject = "DBMS",
                citation = "ANSI SQL-92 Transaction Isolation Levels"
            )
        )
    ),
    QuizItem(
        id = "quiz-networking",
        title = "Networking & OSI Model Assessment",
        description = "Test your grasp on TCP 3-Way Handshake, Subnetting, Transport Layer protocols, and DNS/TLS handshakes.",
        subject = "Computer Networks",
        durationMinutes = 10,
        questions = listOf(
            QuizQuestion(
                id = "net-q1",
                prompt = "During the TCP 3-Way Handshake, which sequence of flags is exchanged between Client and Server?",
                options = listOf(
                    "A. SYN -> ACK -> FIN",
                    "B. SYN -> SYN-ACK -> ACK",
                    "C. ACK -> SYN -> SYN-ACK",
                    "D. PUSH -> ACK -> URG"
                ),
                correctOptionIndex = 1,
                explanation = "The client initiates connection with SYN, the server acknowledges and synchronizes with SYN-ACK, and the client confirms with ACK before payload data transfer begins.",
                subject = "Networking",
                citation = "RFC 793 Transmission Control Protocol"
            ),
            QuizQuestion(
                id = "net-q2",
                prompt = "What is the usable number of host addresses available in an IPv4 network with subnet mask /28 (255.255.255.240)?",
                options = listOf(
                    "A. 16 hosts",
                    "B. 14 hosts",
                    "C. 30 hosts",
                    "D. 12 hosts"
                ),
                correctOptionIndex = 1,
                explanation = "A /28 subnet leaves 4 bits for hosts: 2^4 = 16 total IP addresses. Subtracting 2 (1 for network ID and 1 for broadcast address) yields 14 usable host IPs.",
                subject = "Networking",
                citation = "RFC 1519 Classless Inter-Domain Routing (CIDR)"
            ),
            QuizQuestion(
                id = "net-q3",
                prompt = "Which layer of the OSI 7-Layer Reference Model is responsible for end-to-end flow control, error recovery, and port addressing?",
                options = listOf(
                    "A. Network Layer (Layer 3)",
                    "B. Data Link Layer (Layer 2)",
                    "C. Transport Layer (Layer 4)",
                    "D. Session Layer (Layer 5)"
                ),
                correctOptionIndex = 2,
                explanation = "The Transport Layer (Layer 4, e.g. TCP/UDP) handles end-to-end communication, port addressing (socket binding), segmentation, and flow/congestion control.",
                subject = "Networking",
                citation = "Kurose & Ross Computer Networking: A Top-Down Approach"
            ),
            QuizQuestion(
                id = "net-q4",
                prompt = "In TLS 1.3 cryptographic handshakes, which key exchange mechanism replaced standard RSA key transport to guarantee Perfect Forward Secrecy (PFS)?",
                options = listOf(
                    "A. Triple DES (3DES)",
                    "B. Static Diffie-Hellman",
                    "C. Ephemeral Diffie-Hellman (ECDHE)",
                    "D. MD5 Message Digest"
                ),
                correctOptionIndex = 2,
                explanation = "TLS 1.3 mandatorily requires Ephemeral Diffie-Hellman (ECDHE or DHE), ensuring that each session generates unique disposable keys so compromising a server's private key cannot decrypt past recorded sessions.",
                subject = "Networking",
                citation = "RFC 8446 The Transport Layer Security (TLS) Protocol Version 1.3"
            ),
            QuizQuestion(
                id = "net-q5",
                prompt = "Which protocol uses UDP port 53 for standard name resolution queries and falls back to TCP when response payloads exceed 512 bytes (EDNS0)?",
                options = listOf(
                    "A. DHCP",
                    "B. NTP",
                    "C. DNS",
                    "D. SNMP"
                ),
                correctOptionIndex = 2,
                explanation = "The Domain Name System (DNS) operates on UDP 53 for low-latency queries, but utilizes TCP 53 when responses exceed traditional UDP limits or during zone transfers (AXFR).",
                subject = "Networking",
                citation = "RFC 1035 Domain Names - Implementation and Specification"
            )
        )
    ),
    QuizItem(
        id = "quiz-sebi-law",
        title = "Securities Market & Regulatory Framework",
        description = "SEBI Act 1992, ICDR Regulations, Insider Trading (PIT 2015), and Capital Market infrastructure.",
        subject = "Securities Regulations",
        durationMinutes = 10,
        questions = listOf(
            QuizQuestion(
                id = "law-q1",
                prompt = "Under the SEBI (Prohibition of Insider Trading) Regulations 2015, what does UPSI stand for?",
                options = listOf(
                    "A. Unified Payment Security Interface",
                    "B. Unpublished Price Sensitive Information",
                    "C. Universal Primary Stock Issuance",
                    "D. Underwritten Public Shareholder Interest"
                ),
                correctOptionIndex = 1,
                explanation = "UPSI stands for Unpublished Price Sensitive Information, referring to non-public information relating to a company which upon becoming generally available is likely to materially affect securities prices.",
                subject = "Securities Law",
                citation = "SEBI (PIT) Regulations, 2015 Regulation 2(1)(n)"
            ),
            QuizQuestion(
                id = "law-q2",
                prompt = "The Securities Appellate Tribunal (SAT) is a statutory body established to hear appeals against orders passed by:",
                options = listOf(
                    "A. Only the Reserve Bank of India",
                    "B. SEBI, IRDAI, and PFRDA",
                    "C. Only the National Company Law Tribunal",
                    "D. Ministry of Corporate Affairs exclusively"
                ),
                correctOptionIndex = 1,
                explanation = "SAT hears and disposes of appeals against orders passed by SEBI, the Insurance Regulatory and Development Authority of India (IRDAI), and the Pension Fund Regulatory and Development Authority (PFRDA).",
                subject = "Securities Law",
                citation = "SEBI Act, 1992 Section 15K"
            ),
            QuizQuestion(
                id = "law-q3",
                prompt = "In Indian stock exchanges, the rolling settlement cycle for equity cash market trades is currently:",
                options = listOf(
                    "A. T+3 Days",
                    "B. T+2 Days",
                    "C. T+1 Day (with optional T+0 same day settlement)",
                    "D. T+5 Days"
                ),
                correctOptionIndex = 2,
                explanation = "Indian capital markets successfully transitioned to the T+1 settlement cycle in January 2023, and SEBI introduced a phased beta implementation of T+0 same-day settlement in 2024.",
                subject = "Securities Law",
                citation = "SEBI Circular on T+1 and T+0 Settlement Framework"
            )
        )
    )
)
