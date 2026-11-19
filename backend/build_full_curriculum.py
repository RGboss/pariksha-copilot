import os
import json

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Import stage 1 chapters from generate_detailed_curriculum
from backend.generate_detailed_curriculum import stages as stage1_module

# Now build Stages 2 through 6 with the same exhaustive, university-textbook level depth
stage2 = {
    "id": "stage-2",
    "number": 2,
    "title": "Stage 02: Systems Engineering, Computer Networks & Linux Infrastructure",
    "badge": "Core Systems",
    "description": "Rigorous foundation in OSI/TCP-IP networking, subnetting math, transport protocols, OS process scheduling, memory paging, deadlocks, and Linux systems administration.",
    "chapters": [
        {
            "id": "ch-5",
            "stage_id": "stage-2",
            "number": 5,
            "title": "Computer Networks Architecture: OSI 7-Layer Model, TCP/IP Suite & Network Devices",
            "exams": ["ibps", "sebi", "sbi"],
            "reading_time_mins": 25,
            "summary": "Layer-by-layer formal taxonomy of the OSI reference model vs TCP/IP protocol suite, PDU encapsulation/decapsulation, headers, and device hardware (Hub, Switch, Router, Gateway).",
            "lecture_notes": """# Computer Networks Architecture: OSI vs TCP/IP & Network Hardware

## 1. Network Architectures & Layering Philosophy
The fundamental principle of network layering is **modularity**: each layer offers specific services to the layer above while hiding the implementation details of the layers below. Communication between peer layers on separate hosts is governed by **Protocols**, while communication between adjacent layers on the same host is governed by **Service Data Interfaces (APIs)**.

---

## 2. The OSI 7-Layer Reference Model vs TCP/IP Architecture

```
       OSI 7-Layer Model                     TCP/IP 4-Layer Architecture
+-------------------------------+       +-------------------------------+
|  7. Application Layer         |       |                               |
+-------------------------------+       |  Application Layer            |
|  6. Presentation Layer        | ----> |  (HTTP, DNS, SMTP, FTP, SSH)  |
+-------------------------------+       |                               |
|  5. Session Layer             |       +-------------------------------+
+-------------------------------+
|  4. Transport Layer           | ----> |  Transport Layer (TCP, UDP)   |
+-------------------------------+       +-------------------------------+
|  3. Network Layer             | ----> |  Internet Layer (IP, ICMP)    |
+-------------------------------+       +-------------------------------+
|  2. Data Link Layer           |       |  Network Access / Link Layer  |
+-------------------------------+ ----> |  (Ethernet, Wi-Fi, MAC, ARP)  |
|  1. Physical Layer            |       |                               |
+-------------------------------+       +-------------------------------+
```

### Detailed Layer Responsibilities

#### Layer 7: Application Layer
* **Role:** Serves as the window for users and application processes to access network services.
* **Protocols:** HTTP/HTTPS (Web), SMTP/IMAP/POP3 (Email), DNS (Name resolution), FTP/SFTP (File transfer), SSH (Secure shell), DHCP (Dynamic host configuration).
* **PDU:** **Data / Message**.

#### Layer 6: Presentation Layer
* **Role:** Syntax and semantics of information transmitted. Responsible for:
  1. **Translation:** Character code conversion (e.g., EBCDIC to ASCII, Big-Endian to Little-Endian).
  2. **Encryption & Decryption:** SSL/TLS cryptographic formatting.
  3. **Compression:** Lossless and lossy payload compression (gzip, JPEG, MPEG).

#### Layer 5: Session Layer
* **Role:** Establishes, maintains, and synchronizes dialogues between communicating endpoints.
* **Mechanisms:**
  * **Dialog Control:** Simplex, Half-Duplex (one-way at a time), Full-Duplex.
  * **Synchronization Tokens / Checkpointing:** Inserts checkpoints into long data streams; if a crash occurs, retransmission resumes from the last valid checkpoint rather than from the beginning.

#### Layer 4: Transport Layer
* **Role:** **True End-to-End (Process-to-Process) communication**.
* **Key Functions:**
  * **Port Addressing (Service-Point Addressing):** 16-bit port numbers (0 to 65,535) directing traffic to the target operating system process.
  * **Segmentation and Reassembly:** Slices messages into segments with sequence numbers.
  * **Flow Control:** Prevents fast sender from overwhelming slow receiver (Sliding Window Protocol).
  * **Error Control:** Acknowledgments (ACKs) and checksums.
* **Protocols:** TCP (Transmission Control Protocol), UDP (User Datagram Protocol), SCTP.
* **PDU:** **Segment** (TCP) / **Datagram** (UDP).

#### Layer 3: Network Layer
* **Role:** **Host-to-Host delivery and routing across interconnected networks**.
* **Key Functions:**
  * **Logical Addressing:** Global 32-bit IPv4 or 128-bit IPv6 addresses.
  * **Routing:** Selecting optimal path using routing algorithms (Dijkstra SPF, Bellman-Ford).
  * **Packet Fragmentation & Reassembly:** Adapts packets to match link Maximum Transmission Unit (MTU).
* **Protocols:** IPv4, IPv6, ICMP (Ping/Traceroute), IGMP, IPsec, ARP (boundary).
* **PDU:** **Packet**.

#### Layer 2: Data Link Layer (DLL)
* **Role:** **Hop-to-Hop (Node-to-Node) error-free frame delivery over a single physical link**.
* **Sub-layers:**
  1. **Logical Link Control (LLC):** Flow control and multiplexing protocols.
  2. **Media Access Control (MAC):** Physical 48-bit MAC addressing (e.g. `00:1A:2B:3C:4D:5E`), framing, bus arbitration (CSMA/CD in Ethernet, CSMA/CA in Wi-Fi).
* **Error Detection:** Cyclic Redundancy Check (CRC-32 trailer).
* **PDU:** **Frame** (Header + Payload + CRC Trailer).

#### Layer 1: Physical Layer
* **Role:** Transmission of raw, unstructured bit streams over physical transmission media (copper UTP, optical fiber, radio waves).
* **Specifications:** Voltage levels, signal modulation, bit synchronization, pin layouts (RJ-45).
* **PDU:** **Bits**.

---

## 3. Protocol Data Unit (PDU) Encapsulation & Decapsulation
When an application sends data (e.g., an HTTP GET request), it moves **down** the protocol stack through **Encapsulation**:
1. Application generates raw **Data**.
2. Transport layer adds TCP header (Source/Destination Ports, Seq No) $\\implies$ **Segment**.
3. Network layer adds IP header (Source/Destination IP addresses, TTL) $\\implies$ **Packet**.
4. Data Link layer adds MAC header and CRC trailer $\\implies$ **Frame**.
5. Physical layer encodes the frame into electromagnetic/optical signals $\\implies$ **Bits**.
* Upon arrival at the destination, the reverse process (**Decapsulation**) strips headers sequentially.

---

## 4. Hardware Network Devices: Classification & Operating Layers

| Device | Primary Layer | Operational Mechanics & Forwarding Logic |
| :--- | :---: | :--- |
| **Repeater / Hub** | **Layer 1** (Physical) | Multi-port repeater. Does not inspect addresses; **blindly broadcasts** all incoming electrical signals to all ports. Shares one single collision domain! |
| **Bridge / Switch** | **Layer 2** (Data Link) | Intelligent forwarding using **MAC Address Table (CAM Table)**. Isolates collision domains per port! Micro-segmentation eliminates collisions. |
| **Router** | **Layer 3** (Network) | Forwards packets between different subnets based on **IP Routing Tables**. **Breaks Broadcast Domains**. |
| **Layer 3 Switch** | **Layer 2 & 3** | High-performance switch that performs packet routing in dedicated ASIC hardware at wire speed. |
| **Gateway** | **Layer 4-7** | Translates between completely disparate protocol suites (e.g., cloud API gateway translating HTTP/REST to gRPC or legacy mainframe protocols). |

### Collision Domain vs Broadcast Domain (High-Yield MCQ Topic!)
* **Collision Domain:** A physical network segment where packets can collide with one another if transmitted simultaneously.
  * *Hub:* 1 Collision Domain across all ports.
  * *Switch:* **Each individual port is its own separate Collision Domain**.
* **Broadcast Domain:** The group of all devices on a network that receive a broadcast frame (destination MAC `FF:FF:FF:FF:FF:FF`).
  * *Hub & Switch:* By default, pass broadcasts through all ports $\\implies$ 1 Broadcast Domain across the entire LAN (unless split using VLANs).
  * *Router:* **Stops broadcasts**. Each router interface defines a separate Broadcast Domain!

---

## 5. Address Resolution Protocol (ARP) Mechanics
ARP resolves a known logical **IP Address** into a physical **MAC Address** on a local subnet:
1. **ARP Request:** Host broadcasts: *"Who has IP 192.168.1.50? Tell 192.168.1.10."* (Destination MAC: `FF:FF:FF:FF:FF:FF` $\\implies$ Sent to all nodes).
2. **ARP Reply:** Target host replies via **Unicast**: *"I have 192.168.1.50, my MAC is 00:1A:2B:3C:4D:5E."*
3. The sending host caches this mapping in its local **ARP Cache Table** (`arp -a`).""",
            "checkpoints": [
                {
                    "q": "What is the key difference between a Switch and a Router in terms of domains?",
                    "a": "A Switch creates separate Collision Domains per port but maintains a single Broadcast Domain. A Router breaks both Collision Domains AND Broadcast Domains across its interfaces."
                },
                {
                    "q": "Which OSI layer is responsible for translating data between different character encodings or performing TLS encryption?",
                    "a": "The Presentation Layer (Layer 6)."
                },
                {
                    "q": "What is the PDU name at Layer 4 (Transport) and Layer 3 (Network)?",
                    "a": "Transport Layer PDU is a Segment (or Datagram for UDP); Network Layer PDU is a Packet."
                }
            ],
            "quiz": [
                {
                    "id": 201,
                    "q": "How many Collision Domains and Broadcast Domains are present in a 24-port unmanaged Layer 2 Ethernet Switch connected to 24 separate computers?",
                    "options": [
                        "1 Collision Domain and 24 Broadcast Domains",
                        "24 Collision Domains and 1 Broadcast Domain",
                        "24 Collision Domains and 24 Broadcast Domains",
                        "1 Collision Domain and 1 Broadcast Domain"
                    ],
                    "answer": 1,
                    "explanation": "A Layer 2 switch isolates collision domains per port (yielding 24 collision domains), but all ports belong to a single shared broadcast domain."
                },
                {
                    "id": 202,
                    "q": "At which layer of the OSI model does process-to-process communication, port addressing, and end-to-end flow control take place?",
                    "options": [
                        "Network Layer",
                        "Data Link Layer",
                        "Transport Layer",
                        "Session Layer"
                    ],
                    "answer": 2,
                    "explanation": "The Transport Layer (Layer 4) is responsible for end-to-end process-to-process delivery, using port numbers and flow control protocols."
                },
                {
                    "id": 203,
                    "q": "When a computer needs to determine the physical MAC address of a destination host on the same local subnet whose IP is known, which protocol and transmission mode are used for the initial query?",
                    "options": [
                        "RARP via Unicast",
                        "ARP Request via Broadcast (FF:FF:FF:FF:FF:FF)",
                        "DNS query via Multicast",
                        "ICMP Echo Request via Anycast"
                    ],
                    "answer": 1,
                    "explanation": "ARP sends an ARP Request as a broadcast frame to all hosts on the local link, asking the owner of the target IP to respond with its MAC address."
                },
                {
                    "id": 204,
                    "q": "Which network device operates strictly at Layer 1 and blindly retransmits electrical signals across all connected physical ports?",
                    "options": [
                        "Switch",
                        "Router",
                        "Hub",
                        "Bridge"
                    ],
                    "answer": 2,
                    "explanation": "A Hub is a Layer 1 physical device that regenerates signals and broadcasts them out to all connected ports without parsing frames or inspecting addresses."
                },
                {
                    "id": 205,
                    "q": "Which layer of the OSI reference model handles checkpointing and dialogue synchronization so that file transfers can resume from the last known state after an interruption?",
                    "options": [
                        "Transport Layer",
                        "Session Layer",
                        "Presentation Layer",
                        "Application Layer"
                    ],
                    "answer": 1,
                    "explanation": "The Session Layer (Layer 5) manages dialogue control, session tokens, and synchronization checkpoints."
                }
            ]
        },
        {
            "id": "ch-6",
            "stage_id": "stage-2",
            "number": 6,
            "title": "Transport & Application Protocols: TCP 3-Way Handshake, Flow Control, UDP, DNS & TLS",
            "exams": ["ibps", "sebi", "sbi"],
            "reading_time_mins": 25,
            "summary": "Deep dive into TCP state machines, 3-way handshake sequence numbers, connection termination (TIME_WAIT mechanics), Sliding Window, Congestion Control, UDP, DNS resolution, and TLS 1.3 handshake.",
            "lecture_notes": """# Transport & Application Protocols: TCP, UDP, DNS & TLS

## 1. Transmission Control Protocol (TCP) Internals
TCP is a **connection-oriented, reliable, byte-stream protocol** that guarantees in-order delivery, flow control, and congestion control.

### The TCP Header Structure (20 to 60 Bytes)
```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Source Port          |       Destination Port        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Sequence Number                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Acknowledgment Number                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Data |           |U|A|P|R|S|F|                               |
| Offset| Reserved  |R|C|S|S|Y|I|            Window Size        |
| (4b)  |           |G|K|H|T|N|N|                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|           Checksum            |        Urgent Pointer         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Options (0 to 40 bytes)                    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```
* **Data Offset (4 bits):** Length of TCP header in 32-bit (4-byte) words. Minimum value is `5` ($5 \\times 4 = 20$ bytes); maximum is `15` ($15 \\times 4 = 60$ bytes).
* **Control Flags (6 bits):**
  * `SYN` (Synchronize sequence numbers)
  * `ACK` (Acknowledgment field valid)
  * `FIN` (Finish; no more data from sender)
  * `RST` (Reset connection)
  * `PSH` (Push; bypass buffer and deliver to app immediately)
  * `URG` (Urgent pointer valid)

---

## 2. TCP 3-Way Handshake & Connection Termination

### Connection Establishment (3-Way Handshake)
```
Client (Active Open)                                 Server (Passive Open)
  |                                                    | (State: LISTEN)
  | -------- 1. SYN (Seq = x, ACK = 0) --------------> | (State: SYN_RCVD)
  |                                                    |
  | <------- 2. SYN+ACK (Seq = y, ACK = x + 1) ------- |
  | (State: ESTABLISHED)                               |
  |                                                    |
  | -------- 3. ACK (Seq = x + 1, ACK = y + 1) ------> | (State: ESTABLISHED)
```
* **Step 1:** Client picks random Initial Sequence Number (ISN) $x$ and sends SYN.
* **Step 2:** Server responds with its own random ISN $y$, sets ACK flag, and acknowledges $x+1$.
* **Step 3:** Client acknowledges $y+1$. Both endpoints are now `ESTABLISHED`.

### Connection Teardown (4-Way Handshake & TIME_WAIT)
```
Client (Active Close)                                Server (Passive Close)
  | -------- 1. FIN (Seq = u) -----------------------> | (State: CLOSE_WAIT)
  | <------- 2. ACK (Ack = u + 1) -------------------- |
  | (State: FIN_WAIT_2)                                |
  |                                                    | (Server finishes flushing data)
  | <------- 3. FIN (Seq = w, Ack = u + 1) ----------- | (State: LAST_ACK)
  | -------- 4. ACK (Ack = w + 1) -------------------> | (State: CLOSED)
  | (State: TIME_WAIT - waits 2 MSL!)                  |
  | (After 2 MSL -> CLOSED)                            |
```

> **Why does the active closing client enter TIME_WAIT for 2 MSL (Maximum Segment Lifetime)?**
> 1. **Ensure the final ACK arrives at the server:** If the 4th ACK is lost in transit, the server will time out and retransmit its FIN. The client must stay in TIME_WAIT to resend the ACK; if the client closed immediately, it would respond with an RST!
> 2. **Prevent old duplicate segments from corrupting future connections:** Allows delayed packets from the old connection to dissipate completely before a new connection reuses the same IP and port combination.

---

## 3. TCP Flow Control vs Congestion Control
* **Flow Control (End-to-End):** Governed by the **Receiver Window (rwnd)** advertised in the TCP header. Tells the sender how many bytes of buffer space the receiver currently has available.
* **Congestion Control (Network-Wide):** Governed by the **Congestion Window (cwnd)** maintained dynamically by the sender:
  * $\\text{Effective Window} = \\min(\\text{rwnd}, \\text{cwnd})$.
* **TCP Congestion Control Phases:**
  1. **Slow Start:** Exponential growth. $cwnd$ starts at 1 MSS (Maximum Segment Size) and doubles every Round Trip Time (RTT) until reaching **Slow Start Threshold (ssthresh)**.
  2. **Congestion Avoidance:** Additive Increase. Once $cwnd \\ge ssthresh$, $cwnd$ increases linearly by 1 MSS per RTT.
  3. **Fast Retransmit & Fast Recovery:** When 3 duplicate ACKs are received, TCP infers a packet was lost without waiting for retransmission timer expiration, halves $ssthresh$, and retransmits immediately.

---

## 4. UDP (User Datagram Protocol)
* **Header Size:** Fixed at **8 Bytes** (Source Port 16b, Dest Port 16b, Length 16b, Checksum 16b).
* **Characteristics:** Connectionless, unreliable, no handshakes, no acknowledgments, no flow control.
* **Use Cases in Banking & Enterprise:** DNS lookups, SNMP monitoring, real-time audio/video streaming, NTP clock synchronization across banking servers.

---

## 5. Domain Name System (DNS) & TLS 1.3 Handshake
* **DNS Query Flow:** Client $\\rightarrow$ Recursive Resolver $\\rightarrow$ Root Nameserver (`.`) $\\rightarrow$ TLD Nameserver (`.in` / `.com`) $\\rightarrow$ Authoritative Nameserver (`sbi.co.in`) $\\rightarrow$ Returns IP address.
* **Port:** UDP port 53 for standard queries; TCP port 53 for large zone transfers ($> 512$ bytes).
* **TLS 1.3 Cryptographic Handshake (1-RTT):**
  * Client sends `ClientHello` + supported cipher suites + Diffie-Hellman key share.
  * Server sends `ServerHello` + server key share + Digital Certificate + Finished.
  * Symmetric encryption session key is derived immediately $\\implies$ All subsequent application data (HTTP/2 or HTTP/3) is encrypted!""",
            "checkpoints": [
                {
                    "q": "What is the purpose of the 2MSL timer in TCP's TIME_WAIT state?",
                    "a": "It ensures that the final ACK reaches the remote host (resending if needed) and guarantees that old duplicate packets from the connection expire so they don't corrupt a new connection reusing the same port."
                },
                {
                    "q": "How does TCP distinguish between a network packet loss and a slow receiver?",
                    "a": "A slow receiver explicitly advertises a smaller rwnd (flow control). Network congestion is inferred by packet loss (either retransmission timeout or receiving 3 duplicate ACKs)."
                },
                {
                    "q": "What is the size of a standard UDP header compared to a minimum TCP header?",
                    "a": "UDP header is exactly 8 bytes. TCP header is a minimum of 20 bytes (up to 60 bytes with options)."
                }
            ],
            "quiz": [
                {
                    "id": 206,
                    "q": "During TCP connection establishment, if a client sends SYN with Seq = 5000, what will be the values of ACK and SYN in the server's SYN+ACK response?",
                    "options": [
                        "SYN flag set, ACK = 5000",
                        "SYN flag set, ACK = 5001",
                        "ACK flag set only, ACK = 5000",
                        "SYN flag set, ACK = 5002"
                    ],
                    "answer": 1,
                    "explanation": "A SYN packet consumes one sequence number; therefore, the server's acknowledgment acknowledges the next expected sequence number, which is x + 1 = 5001."
                },
                {
                    "id": 207,
                    "q": "What is the size of the UDP header in bytes?",
                    "options": [
                        "4 bytes",
                        "8 bytes",
                        "16 bytes",
                        "20 bytes"
                    ],
                    "answer": 1,
                    "explanation": "The UDP header consists of four 16-bit fields (Source Port, Destination Port, Length, Checksum) totaling exactly 8 bytes (64 bits)."
                },
                {
                    "id": 208,
                    "q": "What event triggers the TCP Fast Retransmit mechanism before the retransmission timer expires?",
                    "options": [
                        "Receipt of a single negative ACK (NACK)",
                        "Receipt of 3 duplicate ACKs",
                        "Expiration of the TIME_WAIT period",
                        "Reduction of the receiver window to zero"
                    ],
                    "answer": 1,
                    "explanation": "Receiving 3 duplicate ACKs (4 identical ACKs total) informs the sender that a specific segment was dropped, triggering immediate Fast Retransmit without waiting for the timeout."
                },
                {
                    "id": 209,
                    "q": "Which port and transport protocol are typically utilized by DNS for standard name resolution queries under 512 bytes?",
                    "options": [
                        "Port 53 via UDP",
                        "Port 53 via TCP",
                        "Port 80 via UDP",
                        "Port 443 via TCP"
                    ],
                    "answer": 0,
                    "explanation": "Standard DNS resolution queries use UDP on port 53 for low latency and minimal overhead."
                },
                {
                    "id": 210,
                    "q": "In the TCP header, what is the maximum possible header size permitted by the 4-bit Data Offset field?",
                    "options": [
                        "20 bytes",
                        "40 bytes",
                        "60 bytes",
                        "128 bytes"
                    ],
                    "answer": 2,
                    "explanation": "The 4-bit Data Offset stores the header length in 32-bit (4-byte) words. The maximum 4-bit value is 15 (1111 in binary), yielding 15 * 4 = 60 bytes."
                }
            ]
        },
        {
            "id": "ch-7",
            "stage_id": "stage-2",
            "number": 7,
            "title": "IPv4 Subnetting Math, CIDR Supernetting & Routing Protocols (RIP, OSPF, BGP)",
            "exams": ["ibps", "sebi", "sbi"],
            "reading_time_mins": 25,
            "summary": "Classful addressing vs CIDR, calculating Network IDs, Broadcast IDs, and usable host ranges, Distance Vector (Bellman-Ford, Split Horizon) vs Link State (Dijkstra, OSPF Areas).",
            "lecture_notes": """# IPv4 Subnetting Math & Routing Protocols

## 1. Classful Addressing vs Classless Inter-Domain Routing (CIDR)
An IPv4 address is a 32-bit binary number represented in dotted-decimal notation.

### Classful Address Ranges
| Class | First Octet Range | Default Subnet Mask | Prefix | Purpose |
| :--- | :---: | :---: | :---: | :--- |
| **Class A** | `1.0.0.0` - `126.255.255.255` | `255.0.0.0` | `/8` | Very large networks ($2^{24}$ hosts) |
| **Class B** | `128.0.0.0` - `191.255.255.255` | `255.255.0.0` | `/16`| Medium-to-large networks ($2^{16}$ hosts) |
| **Class C** | `192.0.0.0` - `223.255.255.255` | `255.255.255.0` | `/24`| Small networks ($2^8$ hosts) |
| **Class D** | `224.0.0.0` - `239.255.255.255` | N/A | N/A | **Multicast Groups** |
| **Class E** | `240.0.0.0` - `255.255.255.255` | N/A | N/A | Experimental / Research |

* **Reserved Ranges:**
  * `127.0.0.0/8`: Reserved for **Loopback testing** (e.g. `127.0.0.1` / `localhost`).
  * **Private IP Ranges (RFC 1918):**
    * `10.0.0.0` to `10.255.255.255` (10/8 prefix)
    * `172.16.0.0` to `172.31.255.255` (172.16/12 prefix)
    * `192.168.0.0` to `192.168.255.255` (192.168/16 prefix)

---

## 2. The Step-by-Step Subnetting Formula & Cheat Method
In CIDR notation `IP / N`, the prefix $N$ specifies that the first $N$ bits belong to the **Network ID**, and the remaining $(32 - N)$ bits belong to the **Host ID**.

### Core Mathematical Formulas:
* **Total IP Addresses in Subnet:** $2^{(32 - N)}$
* **Usable Host IP Addresses:** $2^{(32 - N)} - 2$
  * *(Subtract 1 for Network ID where all host bits are 0)*
  * *(Subtract 1 for Directed Broadcast ID where all host bits are 1)*
* **Subnet Block Size:** $256 - \\text{Interesting Octet Mask Value}$

### Complete CIDR Calculation Reference Table
| CIDR | Subnet Mask | Block Size | Total IPs | Usable Hosts | Typical Application |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **/24** | `255.255.255.0` | 256 | 256 | 254 | Standard Departmental LAN |
| **/25** | `255.255.255.128` | 128 | 128 | 126 | Sub-branch floor |
| **/26** | `255.255.255.192` | 64 | 64 | 62 | Regional office cluster |
| **/27** | `255.255.255.224` | 32 | 32 | 30 | Branch teller desks |
| **/28** | `255.255.255.240` | 16 | 16 | 14 | ATM machine subnet |
| **/29** | `255.255.255.248` | 8 | 8 | 6 | Bank server cluster |
| **/30** | `255.255.255.252` | 4 | 4 | **2** | **Point-to-Point Router Links** |

---

## 3. Worked Subnetting Problem (Classic IBPS SO / SEBI Question)
**Problem:** A banking ATM network is assigned IP address `172.20.15.142` with subnet mask `255.255.255.224`. Find:
1. CIDR Prefix notation
2. Network ID
3. First usable host IP
4. Last usable host IP
5. Directed Broadcast Address

### Step-by-Step Solution:
1. **Find CIDR Prefix:**
   * Mask `255.255.255.224`: First 3 octets = 24 bits.
   * In 4th octet, 224 in binary is `11100000` (3 bits).
   * Total prefix $N = 24 + 3 = \\mathbf{/27}$.
2. **Find Block Size:**
   * $\\text{Block Size} = 256 - 224 = \\mathbf{32}$.
3. **List the Subnet Increments in the 4th Octet:**
   * Subnet 0: `.0`
   * Subnet 1: `.32`
   * Subnet 2: `.64`
   * Subnet 3: `.96`
   * Subnet 4: `.128`
   * Subnet 5: `.160`
4. **Locate where the target IP (.142) resides:**
   * `.142` falls between `.128` and `.160`.
   * **Network ID:** `172.20.15.128`
   * **Next Subnet:** `172.20.15.160`
   * **Broadcast Address:** One IP before the next subnet = `172.20.15.159`
   * **First Usable Host:** Network ID + 1 = `172.20.15.129`
   * **Last Usable Host:** Broadcast Address - 1 = `172.20.15.158`
   * **Total Usable Hosts:** $2^{(32 - 27)} - 2 = 2^5 - 2 = \\mathbf{30}$.

---

## 4. Routing Protocols: Distance Vector vs Link State

```
+------------------------------------+   +------------------------------------+
|  Distance Vector (RIP)             |   |  Link State (OSPF)                 |
|  - Bellman-Ford Algorithm          |   |  - Dijkstra's SPF Algorithm        |
|  - Metric: Hop Count (Max 15)      |   |  - Metric: Cost / Bandwidth        |
|  - Shares full routing table       |   |  - Shares only link state changes  |
|  - Slow convergence                |   |  - Very fast convergence           |
|  - Count-to-Infinity problem       |   |  - Divided into Areas (Area 0)     |
+------------------------------------+   +------------------------------------+
```

### 1. Distance Vector Routing (RIP - Routing Information Protocol)
* **Algorithm:** Bellman-Ford algorithm.
* **Routing Logic:** Each router sends its entire routing table to directly connected neighbors at periodic intervals (every 30 seconds).
* **Metric:** Hop count. Maximum metric is 15. A hop count of **16 denotes infinity / unreachable**.
* **Count-to-Infinity Problem:** When a link fails, routers slowly increment hop counts in a loop. Mitigated by:
  * **Split Horizon:** A router never advertises a route back out the same interface from which it learned it.
  * **Poison Reverse:** Overrides Split Horizon by advertising the failed route back with an infinite metric (16).

### 2. Link State Routing (OSPF - Open Shortest Path First)
* **Algorithm:** Dijkstra's Shortest Path First (SPF).
* **Routing Logic:** Every router floods Link State Advertisements (LSAs) containing the status of its direct links. Every router builds a complete topological map of the entire network and independently computes the shortest path tree.
* **Hierarchical Design:** Uses **Areas** to limit LSA flooding. **Area 0 (Backbone Area)** is mandatory.""",
            "checkpoints": [
                {
                    "q": "What is the subnet mask and usable host count for a /30 subnet?",
                    "a": "Mask is 255.255.255.252. Usable hosts = 2^(32-30) - 2 = 4 - 2 = 2 hosts (perfect for point-to-point links)."
                },
                {
                    "q": "What is the maximum hop count allowed by the Routing Information Protocol (RIP)?",
                    "a": "15 hops. A hop count of 16 indicates the destination is unreachable."
                },
                {
                    "q": "How does Split Horizon mitigate routing loops in Distance Vector protocols?",
                    "a": "It prevents a router from advertising routing information back out of the same interface through which it originally learned that route."
                }
            ],
            "quiz": [
                {
                    "id": 211,
                    "q": "How many usable host IP addresses are available in a subnetwork with CIDR notation 10.50.0.0/28?",
                    "options": [
                        "16",
                        "14",
                        "30",
                        "6"
                    ],
                    "answer": 1,
                    "explanation": "A /28 subnet has 32 - 28 = 4 host bits. Total IPs = 2^4 = 16. Subtracting 2 (Network ID and Broadcast ID) leaves exactly 14 usable host IP addresses."
                },
                {
                    "id": 212,
                    "q": "Which IP address range is reserved by RFC 1918 for Class B private networking?",
                    "options": [
                        "10.0.0.0 to 10.255.255.255",
                        "172.16.0.0 to 172.31.255.255",
                        "192.168.0.0 to 192.168.255.255",
                        "169.254.0.0 to 169.254.255.255"
                    ],
                    "answer": 1,
                    "explanation": "RFC 1918 defines 172.16.0.0/12 (172.16.0.0 through 172.31.255.255) as the Class B private address space."
                },
                {
                    "id": 213,
                    "q": "Given the IP address 192.168.10.68 with subnet mask 255.255.255.240 (/28), what is the directed broadcast address of the subnet?",
                    "options": [
                        "192.168.10.79",
                        "192.168.10.64",
                        "192.168.10.255",
                        "192.168.10.78"
                    ],
                    "answer": 0,
                    "explanation": "Block size = 256 - 240 = 16. Subnets are .0, .16, .32, .48, .64, .80. IP .68 belongs to subnet starting at .64. Next subnet is .80, so the broadcast address is 192.168.10.79."
                },
                {
                    "id": 214,
                    "q": "Which shortest path algorithm is utilized by the Open Shortest Path First (OSPF) routing protocol?",
                    "options": [
                        "Bellman-Ford Algorithm",
                        "Dijkstra's Algorithm",
                        "Floyd-Warshall Algorithm",
                        "Kruskal's Algorithm"
                    ],
                    "answer": 1,
                    "explanation": "OSPF is a Link State routing protocol that runs Dijkstra's Shortest Path First (SPF) algorithm to calculate the shortest loop-free path to all destinations."
                },
                {
                    "id": 215,
                    "q": "In the RIP routing protocol, what numerical metric value signifies infinity / an unreachable network?",
                    "options": [
                        "15",
                        "16",
                        "255",
                        "100"
                    ],
                    "answer": 1,
                    "explanation": "RIP allows a maximum of 15 valid hops; 16 represents infinity, indicating the route is dead/unreachable."
                }
            ]
        }
    ]
}

# Module provides stage2 dictionary
if __name__ == "__main__":
    pass
