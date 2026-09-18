# Reliable UDP

A small educational implementation of **reliable data delivery on top of UDP** using Python sockets.

UDP is fast and lightweight, but it does not guarantee delivery, ordering, or retransmission.

So instead of just reading about these concepts, I built a small reliability layer on top of UDP to understand **how reliable transport mechanisms work internally**.

---

## Why I Built This

While learning Computer Networks, I kept seeing concepts such as:

- Sequence numbers
- Acknowledgements
- Timeouts
- Retransmission
- Duplicate detection
- Packet ordering
- Packet loss

Instead of treating them as just theory, I wanted to see what would happen if I had to implement some of these mechanisms myself.

This project is a simplified experiment:

> **What if UDP loses packets or ACKs? Can we build basic reliability ourselves?**

---

## The Problem with UDP

UDP provides a simple datagram-based communication mechanism, but it does not guarantee:

- Packet delivery
- Packet ordering
- Retransmission
- Duplicate suppression
- Reliable acknowledgement

For example, a sender may transmit:

```text
Packet #1
Packet #2
Packet #3
```

The receiver could potentially see:

```text
Packet #1
Packet #3
```

because Packet #2 was lost.

Or the packet may arrive successfully, but the ACK sent back to the sender may be lost.

That creates a problem:

> How does the sender know whether the packet actually reached the receiver?

This project explores a basic solution.

---

# What I Built

I created a small reliability layer on top of UDP using Python's built-in `socket` module.

The implementation includes:

- Sequence numbers
- Acknowledgements (ACKs)
- Timeouts
- Retransmission
- Maximum retry attempts
- Duplicate packet detection
- Basic out-of-order detection
- Simulated packet loss
- Simulated ACK loss
- Basic packet tracking

The underlying communication is still UDP.

The reliability is handled by our application-level logic.

---

# How It Works

## 1. Sequence Numbers

Every packet contains a sequence number.

For example:

```text
1|Hello
2|This is UDP
3|But we are making it reliable
```

The sequence number allows the receiver to identify individual packets.

It can also help detect:

- Missing packets
- Duplicate packets
- Out-of-order packets

---

## 2. Acknowledgements

After receiving a packet, the server sends an acknowledgement.

For example:

```text
ACK|1
```

This tells the client:

> Packet #1 was received.

The client waits for the ACK before moving to the next packet.

---

## 3. Timeout

The client does not wait forever for an ACK.

A timeout is configured:

```python
TIMEOUT = 2
```

If the ACK does not arrive within the timeout period, the client assumes that something went wrong.

Possible reasons include:

- The packet was lost
- The ACK was lost
- The network delayed the packet
- The server did not respond

---

## 4. Retransmission

When a timeout occurs, the client sends the packet again.

Conceptually:

```text
Send Packet #2
        ↓
     Wait
        ↓
   No ACK received
        ↓
     Timeout
        ↓
 Resend Packet #2
```

This is one of the fundamental ideas behind reliable data transfer.

---

## 5. Duplicate Detection

Retransmission creates another problem.

Suppose the server successfully receives Packet #2.

It sends:

```text
ACK|2
```

But the ACK gets lost.

The client does not know that Packet #2 was already received, so it retransmits Packet #2.

The server receives Packet #2 again.

Our server keeps track of received sequence numbers:

```python
received_packets = set()
```

If the sequence number already exists in the set, the server identifies the packet as a duplicate.

Example:

```text
Duplicate packet detected: #2
```

The server can then send the ACK again.

---

## 6. Simulated Packet Loss

Real networks can lose packets, but reproducing unpredictable network behavior locally can be difficult.

So the server includes a simple packet-loss simulation.

For example:

```python
PACKET_LOSS_RATE = 0.20
```

This means the program randomly drops approximately 20% of incoming packets.

This allows the reliability mechanism to be tested locally.

---

## 7. Simulated ACK Loss

The server can also randomly drop ACKs:

```python
ACK_LOSS_RATE = 0.30
```

This is useful because a packet can reach the server successfully while its ACK never reaches the client.

The client should then:

1. Wait for the ACK
2. Hit the timeout
3. Retransmit the packet
4. Receive another ACK

This demonstrates why acknowledgements alone are not enough without timeout and retransmission logic.

---

# Example

A normal transfer might look like:

```text
Client
  |
  | Packet #1
  v
Server
  |
  | ACK #1
  v
Client
```

When an ACK is lost:

```text
Client
  |
  | Packet #2
  v
Server
  |
  | ACK #2
  X
  |
  | ACK lost
  |
Client
  |
  | Timeout
  |
  | Retransmit #2
  v
Server
  |
  | Duplicate detected
  |
  | ACK #2
  v
Client
```

The important part is that the application does not simply assume:

> "I sent the packet, therefore it arrived."

Instead, it uses acknowledgements and retransmission to increase reliability.

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

Responsible for:

- Creating the UDP socket
- Creating packets
- Adding sequence numbers
- Sending packets
- Waiting for ACKs
- Handling timeouts
- Retransmitting packets
- Limiting retry attempts

### `server.py`

Responsible for:

- Creating the UDP socket
- Receiving packets
- Extracting sequence numbers
- Detecting duplicates
- Detecting out-of-order packets
- Simulating packet loss
- Simulating ACK loss
- Sending ACKs

---

# Requirements

This project uses only Python's standard library.

No external Python packages are required.

You need:

- Python 3.x

The project uses built-in modules such as:

```python
socket
random
```

Therefore, there is no `requirements.txt` file.

---

# How to Run

## 1. Clone the repository

```bash
git clone https://github.com/<your-username>/reliable-udp.git
```

Move into the project:

```bash
cd reliable-udp
```

---

## 2. Start the server

Open one terminal and run:

```bash
python server.py
```

You should see something similar to:

```text
==================================================
Reliable UDP Server
==================================================
Server running on 127.0.0.1:5000
Packet loss simulation : 20%
ACK loss simulation    : 30%
Waiting for packets...
```

Keep this terminal running.

---

## 3. Start the client

Open another terminal in the same directory:

```bash
python client.py
```

Example output:

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

The exact output will vary because packet and ACK loss are simulated randomly.

---

# Configuration

The loss rates can be changed in `server.py`.

### Packet loss

```python
PACKET_LOSS_RATE = 0.20
```

For example:

```python
PACKET_LOSS_RATE = 0.50
```

would simulate approximately 50% packet loss.

### ACK loss

```python
ACK_LOSS_RATE = 0.30
```

For example:

```python
ACK_LOSS_RATE = 0.50
```

would simulate approximately 50% ACK loss.

### Client timeout

The client uses:

```python
TIMEOUT = 2
```

This means it waits approximately 2 seconds for an ACK before retrying.

### Maximum retries

The client also limits retransmissions:

```python
MAX_RETRIES = 5
```

If the ACK still does not arrive after the maximum number of attempts, the client stops trying.

---

# What This Project Demonstrates

This project helped me understand that reliable communication is not one single feature.

It is a combination of mechanisms working together.

### Sequence numbers

Help identify individual packets.

### ACKs

Tell the sender that a packet was received.

### Timeouts

Prevent the sender from waiting forever.

### Retransmission

Allows lost packets to be sent again.

### Duplicate detection

Prevents retransmitted packets from being treated as completely new packets.

### Out-of-order detection

Allows the receiver to identify packets arriving in an unexpected order.

Together, these mechanisms create a basic form of reliable data transfer.

---

# What This Is Not

This project is **not a replacement for TCP**.

It is also not a production-ready transport protocol.

Real transport protocols handle many additional problems, including:

- Flow control
- Congestion control
- RTT estimation
- Sophisticated retransmission strategies
- Selective acknowledgements
- Packet corruption
- Connection management
- Efficient buffering
- Network congestion
- Advanced loss recovery

This project intentionally keeps things small so that the core reliability concepts are easy to understand.

---

# TCP vs This Project

| Feature | UDP | This Project | TCP |
|---|---|---|---|
| Sequence numbers | No guarantee | Yes | Yes |
| ACKs | No | Yes | Yes |
| Retransmission | No | Yes | Yes |
| Timeout | No | Yes | Yes |
| Duplicate detection | No guarantee | Basic | Yes |
| Ordered delivery | No guarantee | Basic detection | Yes |
| Flow control | No | No | Yes |
| Congestion control | No | No | Yes |
| Connection management | No | No | Yes |

The goal is not to recreate TCP.

The goal is to understand **why mechanisms such as sequence numbers, ACKs, timeouts, and retransmissions exist in reliable transport protocols.**

---

# Limitations

This implementation intentionally has several limitations.

### No true sliding window

The current client waits for an ACK before proceeding to the next packet.

This is simpler than a real sliding-window implementation.

### Basic out-of-order handling

The server can detect an out-of-order packet, but it does not implement a complete reordering and delivery mechanism.

### No congestion control

The implementation does not dynamically adjust transmission based on network congestion.

### Fixed timeout

The timeout is currently manually configured instead of being calculated from measured network conditions.

### Simplified packet format

Packets use a simple string format:

```text
sequence_number|message
```

A production protocol would use a more robust packet structure.

---

# Possible Improvements

There are several things that could be added in future versions.

- [ ] Implement a real sliding window
- [ ] Implement packet buffering and reordering
- [ ] Add flow control
- [ ] Add congestion control
- [ ] Add RTT measurement
- [ ] Calculate adaptive retransmission timeouts
- [ ] Implement selective acknowledgements
- [ ] Add packet corruption simulation
- [ ] Add checksums
- [ ] Implement connection establishment
- [ ] Implement connection termination
- [ ] Improve packet format
- [ ] Add automated tests
- [ ] Add performance measurements

---

# Key Takeaway

The biggest thing I learned from this project was that **reliability is a collection of mechanisms**, not a single feature.

UDP gives us a simple way to send datagrams.

Everything else has to be handled by the application if we want additional guarantees.

Building a small version made concepts like:

- Sequence numbers
- ACKs
- Timeouts
- Retransmissions
- Duplicate detection

much easier to understand than simply memorizing their definitions.

---

# Why This Was Interesting

The interesting part wasn't writing:

```python
socket.sendto()
```

or:

```python
socket.recvfrom()
```

The interesting part was asking:

> What happens if this packet disappears?

Then:

> What happens if the ACK disappears?

Then:

> What happens if the same packet arrives twice?

Then:

> What happens if packets arrive out of order?

Those questions lead directly to the mechanisms used by reliable transport protocols.

---

# Related Concepts

This project also helped connect several Computer Networks concepts together:

- UDP
- TCP
- Transport-layer reliability
- Sequence numbers
- Acknowledgements
- Retransmission
- Timeouts
- Packet loss
- Duplicate packets
- Out-of-order delivery
- Sliding windows
- Flow control
- Congestion control
- QUIC
- HTTP/3

---

# Resources

- [RFC 768 — User Datagram Protocol](https://www.rfc-editor.org/rfc/rfc768)
- [RFC 9293 — Transmission Control Protocol](https://www.rfc-editor.org/rfc/rfc9293)
- [RFC 9000 — QUIC: A UDP-Based Multiplexed and Secure Transport](https://www.rfc-editor.org/rfc/rfc9000)
- [RFC 9114 — HTTP/3](https://www.rfc-editor.org/rfc/rfc9114)

---

# Disclaimer

This is an **educational networking project** created to understand basic reliability mechanisms over UDP.

It is not intended to replace TCP, QUIC, or any production transport protocol.

---

## Author

**Akash Santra**

Built as part of my hands-on exploration of Computer Networks and transport-layer protocols.