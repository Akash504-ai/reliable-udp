<p align="center">
  <img width="1200" height="622" alt="Reliable UDP" src="https://github.com/user-attachments/assets/cef33695-f1be-4380-9e90-04a26e453f2c" />
</p>

<p align="center">
  <a href="https://github.com/<your-username>/reliable-udp/stargazers">
    <img alt="GitHub stars" src="https://img.shields.io/github/stars/Akash504-ai/reliable-udp?style=flat-square" />
  </a>
  <a href="https://github.com/<your-username>/reliable-udp">
    <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/Akash504-ai/reliable-udp?style=flat-square" />
  </a>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python&logoColor=white" />
  <img alt="Protocol" src="https://img.shields.io/badge/Protocol-UDP-orange?style=flat-square" />
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green?style=flat-square" />
</p>

# Reliable UDP

A small educational implementation of **reliable data delivery on top of UDP** using Python sockets.

UDP provides fast, connectionless datagram communication, but it does not guarantee delivery, ordering, or retransmission.

This project explores what happens when we build some of those reliability mechanisms ourselves.

> **What if UDP loses a packet or an ACK? Can we build a basic reliability layer on top of it?**

The implementation uses sequence numbers, acknowledgements, timeouts, retransmissions, duplicate detection, and simulated packet loss to demonstrate the core ideas behind reliable transport protocols.

---

## Features

* Sequence numbers for identifying packets
* ACK-based delivery confirmation
* Configurable timeout handling
* Automatic packet retransmission
* Maximum retry limit
* Duplicate packet detection
* Basic out-of-order detection
* Simulated packet loss
* Simulated ACK loss
* Simple packet tracking
* Zero external dependencies

---

## How It Works

The project consists of two components:

```text
┌──────────────┐                       ┌──────────────┐
│              │       UDP Packet      │              │
│    Client    │ ───────────────────>  │    Server    │
│              │                       │              │
│              │       UDP ACK         │              │
│              │ <───────────────────  │              │
└──────────────┘                       └──────────────┘
       │                                      │
       │                                      │
       ▼                                      ▼
 Sequence Numbers                       Packet Tracking
 Timeouts                                Duplicate Detection
 Retransmission                          ACK Generation
 Retry Limit                             Loss Simulation
```

The underlying transport is still **UDP**.

The reliability mechanisms are implemented at the **application level**.

---

# Reliability Flow

For each packet, the client follows this basic process:

```text
             ┌───────────────┐
             │ Create Packet │
             └───────┬───────┘
                     │
                     ▼
             ┌───────────────┐
             │   Send UDP    │
             │    Packet     │
             └───────┬───────┘
                     │
                     ▼
             ┌───────────────┐
             │   Wait for    │
             │      ACK      │
             └───────┬───────┘
                     │
              ┌──────┴──────┐
              │             │
           ACK received   Timeout
              │             │
              ▼             ▼
           Next Packet   Retry Packet
                            │
                            ▼
                       Retry Limit?
                         /      \
                       No        Yes
                       │          │
                       ▼          ▼
                    Resend      Stop
```

This creates a simple **stop-and-wait reliability mechanism**.

---

# Packet Format

Packets use a deliberately simple format:

```text
sequence_number|message
```

For example:

```text
1|Hello
2|This is UDP
3|But we are making it reliable
```

Acknowledgements use:

```text
ACK|sequence_number
```

For example:

```text
ACK|1
```

The simplicity of the format makes the reliability logic easier to understand.

---

# Core Concepts

## Sequence Numbers

Every packet receives a unique sequence number.

```text
1|Hello
2|This is UDP
3|Reliable delivery
```

Sequence numbers allow the receiver to identify:

* Individual packets
* Duplicate packets
* Missing packets
* Unexpected packet order

---

## Acknowledgements

After receiving a packet, the server sends an acknowledgement:

```text
ACK|1
```

The client uses this ACK to determine whether it can move on to the next packet.

Without an acknowledgement, the sender cannot distinguish between:

```text
Packet was lost
```

and:

```text
Packet arrived, but the ACK was lost
```

That is where timeouts become important.

---

## Timeouts

The client waits for an ACK for a limited amount of time.

```python
TIMEOUT = 2
```

If no ACK arrives within that period, the client treats the attempt as unsuccessful and retransmits the packet.

Possible causes include:

* Packet loss
* ACK loss
* Network delay
* Server failure

---

## Retransmission

When a timeout occurs, the client sends the same packet again.

```text
Client                         Server
  │                              │
  │──── Packet #2 ──────────────>│
  │                              │
  │         ACK lost             │
  │                              │
  │       Timeout                │
  │                              │
  │──── Packet #2 ──────────────>│
  │                              │
  │<──────── ACK #2 ─────────────│
  │                              │
```

This is one of the fundamental mechanisms used to provide reliable delivery.

---

## Duplicate Detection

Retransmission introduces another problem.

Consider:

```text
Client                    Server
  │                         │
  │───── Packet #2 ────────>│
  │                         │
  │<──── ACK #2 ────────────│
  X
 ACK lost
  │                         │
  │───── Packet #2 ────────>│
  │                         │
```

The server has already processed Packet #2.

The retransmitted packet must therefore be recognized as a duplicate.

The server keeps track of received sequence numbers:

```python
received_packets = set()
```

If the sequence number is already present, the packet is treated as a duplicate and the ACK can be sent again.

---

## Out-of-Order Detection

UDP does not guarantee packet ordering.

For example, packets could arrive as:

```text
1
3
2
```

The server tracks the expected sequence number and can identify packets that arrive unexpectedly.

This implementation focuses on **detecting** out-of-order packets rather than implementing a complete packet-reordering buffer.

---

# Simulated Packet Loss

Testing reliability requires failure scenarios.

The server therefore includes configurable packet-loss simulation.

```python
PACKET_LOSS_RATE = 0.20
```

A value of `0.20` represents approximately **20% simulated packet loss**.

For example:

```python
PACKET_LOSS_RATE = 0.50
```

simulates approximately 50% packet loss.

This makes it possible to observe retransmission behavior without requiring a real unreliable network.

---

# Simulated ACK Loss

The server can also simulate lost acknowledgements:

```python
ACK_LOSS_RATE = 0.30
```

This demonstrates an important scenario:

```text
Packet arrives successfully
        ↓
Server sends ACK
        ↓
ACK is lost
        ↓
Client waits
        ↓
Timeout
        ↓
Client retransmits
        ↓
Server detects duplicate
        ↓
Server sends ACK again
```

This shows why reliable delivery requires more than simply sending an ACK.

---

# Example

### Normal transfer

```text
Client                         Server
  │                              │
  │──── Packet #1 ──────────────>│
  │                              │
  │<──────── ACK #1 ─────────────│
  │                              │
  │──── Packet #2 ──────────────>│
  │                              │
  │<──────── ACK #2 ─────────────│
  │                              │
  │──── Packet #3 ──────────────>│
  │                              │
  │<──────── ACK #3 ─────────────│
  │                              │
```

### Transfer with packet loss

```text
Client                         Server
  │                              │
  │──── Packet #2 ──────────────>│
  X                              │
 Packet lost                     │
  │                              │
  │       Timeout                │
  │                              │
  │──── Packet #2 ──────────────>│
  │                              │
  │<──────── ACK #2 ─────────────│
  │                              │
```

### Transfer with ACK loss

```text
Client                         Server
  │                              │
  │──── Packet #2 ──────────────>│
  │                              │
  │<──────── ACK #2 ─────────────│
  X                              │
 ACK lost                        │
  │                              │
  │       Timeout                │
  │                              │
  │──── Packet #2 ──────────────>│
  │                              │
  │                     Duplicate detected
  │                              │
  │<──────── ACK #2 ─────────────│
  │                              │
```

---

# Project Structure

```text
reliable-udp/
│
├── client.py
├── server.py
├── README.md
└── .gitignore
```

### `client.py`

Handles:

* UDP socket creation
* Packet creation
* Sequence numbers
* Packet transmission
* ACK reception
* Timeout handling
* Retransmission
* Retry limits

### `server.py`

Handles:

* UDP socket creation
* Packet reception
* Sequence number extraction
* Duplicate detection
* Out-of-order detection
* Packet-loss simulation
* ACK-loss simulation
* ACK transmission

---

# Requirements

The project uses only Python's standard library.

No external packages are required.

### Requirements

* Python 3.x
* A terminal capable of running two processes

The implementation primarily uses:

```python
socket
random
```

Therefore, there is no `requirements.txt`.

---

# Getting Started

## 1. Clone the repository

```bash
git clone https://github.com/<your-username>/reliable-udp.git
cd reliable-udp
```

## 2. Start the server

Open a terminal and run:

```bash
python server.py
```

Example:

```text
==================================================
Reliable UDP Server
==================================================
Server running on 127.0.0.1:5000
Packet loss simulation : 20%
ACK loss simulation    : 30%
Waiting for packets...
```

Keep the server running.

## 3. Start the client

Open a second terminal:

```bash
python client.py
```

Example:

```text
📤 Sending packet #1: Hello
✅ ACK received for #1

📤 Sending packet #2: This is UDP
⏰ Timeout for packet #2
🔄 Retrying (1/5)...

📤 Sending packet #2: This is UDP
✅ ACK received for #2

📤 Sending packet #3: But we are making it reliable
✅ ACK received for #3

Transfer completed.
Socket closed.
```

Because packet and ACK loss are simulated randomly, your output will vary between runs.

---

# Configuration

The reliability behavior can be adjusted directly in the source files.

### Packet loss

In `server.py`:

```python
PACKET_LOSS_RATE = 0.20
```

### ACK loss

In `server.py`:

```python
ACK_LOSS_RATE = 0.30
```

### Timeout

In `client.py`:

```python
TIMEOUT = 2
```

### Maximum retries

In `client.py`:

```python
MAX_RETRIES = 5
```

Increasing the loss rates is a simple way to make the reliability behavior easier to observe.

---

# What This Demonstrates

The project connects several Computer Networks concepts into one working experiment.

| Mechanism              | Purpose                          |
| ---------------------- | -------------------------------- |
| Sequence numbers       | Identify individual packets      |
| ACKs                   | Confirm packet reception         |
| Timeouts               | Detect missing responses         |
| Retransmission         | Recover from packet/ACK loss     |
| Retry limit            | Prevent infinite retransmission  |
| Duplicate detection    | Recognize retransmitted packets  |
| Out-of-order detection | Identify unexpected packet order |
| Loss simulation        | Test reliability under failure   |

The important idea is that **reliability is not one mechanism**.

It emerges from several mechanisms working together.

---

# UDP vs Reliable UDP vs TCP

| Feature                | UDP |    This Project | TCP |
| ---------------------- | --: | --------------: | --: |
| Datagram communication |   ✓ |               ✓ |   — |
| Sequence numbers       |   — |               ✓ |   ✓ |
| ACKs                   |   — |               ✓ |   ✓ |
| Retransmission         |   — |               ✓ |   ✓ |
| Timeout                |   — |               ✓ |   ✓ |
| Duplicate handling     |   — |           Basic |   ✓ |
| Ordered delivery       |   — | Basic detection |   ✓ |
| Flow control           |   — |               — |   ✓ |
| Congestion control     |   — |               — |   ✓ |
| Connection management  |   — |               — |   ✓ |
| Sliding window         |   — |               — |   ✓ |
| Selective ACK          |   — |               — |   ✓ |

**This project is not intended to recreate TCP.**

Instead, it demonstrates why several mechanisms are necessary when reliable delivery is required.

---

# Limitations

This is intentionally a small educational implementation.

It does **not** provide the guarantees or sophistication of a production transport protocol.

### Stop-and-wait only

The client waits for an ACK before sending the next packet.

There is no true sliding-window implementation.

### Basic out-of-order handling

Out-of-order packets can be detected, but there is no complete buffering and reordering system.

### No flow control

The sender does not dynamically adapt to receiver capacity.

### No congestion control

The implementation does not react to network congestion.

### Fixed timeout

The timeout is manually configured rather than calculated from measured RTT.

### Simplified packet format

Packets are represented as:

```text
sequence_number|message
```

A production protocol would require a more robust packet format.

### No corruption detection

The project simulates packet loss, but does not currently simulate corrupted packets or implement checksums.

---

# Future Improvements

Possible extensions include:

* [ ] Sliding-window protocol
* [ ] Packet buffering and reordering
* [ ] Flow control
* [ ] Congestion control
* [ ] RTT measurement
* [ ] Adaptive retransmission timeout
* [ ] Selective acknowledgements
* [ ] Packet corruption simulation
* [ ] Checksums
* [ ] Connection establishment
* [ ] Connection termination
* [ ] Structured packet format
* [ ] Automated tests
* [ ] Performance benchmarks
* [ ] Throughput and packet-loss visualization

---

# Learning Outcomes

Building this project helped connect theoretical Computer Networks concepts with an actual implementation.

Instead of only memorizing definitions, I was able to experiment with:

* UDP socket communication
* Sequence numbers
* Acknowledgements
* Timeouts
* Retransmission
* Packet loss
* ACK loss
* Duplicate packets
* Out-of-order delivery
* Stop-and-wait reliability

The most useful part was intentionally introducing failures and observing how the protocol responds.

---

# Key Takeaway

UDP gives applications a lightweight way to exchange datagrams, but it does not provide the reliability guarantees associated with TCP.

This project demonstrates how an application can add some basic reliability mechanisms:

```text
UDP
 │
 ├── Sequence Numbers
 ├── ACKs
 ├── Timeouts
 ├── Retransmission
 ├── Duplicate Detection
 └── Retry Limits
 │
 ▼
Basic Reliable Data Transfer
```

The goal is not to build a replacement for TCP.

The goal is to understand **why reliable transport protocols need these mechanisms in the first place.**

---

# Related Concepts

This project connects to several broader networking topics:

* UDP
* TCP
* Reliable Data Transfer
* Sequence Numbers
* Acknowledgements
* Retransmission
* Timeouts
* Packet Loss
* Duplicate Detection
* Out-of-Order Delivery
* Stop-and-Wait Protocol
* Sliding Windows
* Flow Control
* Congestion Control
* QUIC
* HTTP/3

---

# References

* [RFC 768 — User Datagram Protocol](https://www.rfc-editor.org/rfc/rfc768)
* [RFC 9293 — Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc9293)
* [RFC 9000 — QUIC](https://www.rfc-editor.org/rfc/rfc9000)
* [RFC 9114 — HTTP/3](https://www.rfc-editor.org/rfc/rfc9114)

---

# Disclaimer

This is an **educational networking project** created to explore basic reliability mechanisms over UDP.

It is not intended to replace TCP, QUIC, or any production transport protocol.

---

## Author

**Akash Santra**

Built as part of my hands-on exploration of **Computer Networks and transport-layer protocols**.

---

<p align="center">
  <sub>Built with Python sockets · Educational project · Computer Networks</sub>
</p>
