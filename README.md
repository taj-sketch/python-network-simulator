# Mini Internet Protocol Stack Simulator

A Python simulation of a message travelling through a layered network stack, from one host to another through a router. Follow the logs to see encapsulation, forwarding, checksum checks and acknowledgements at each layer.

**Python · Standard library only · Layer 2 / 3 / 4 · Alternating-bit transfer**

```text
Host A                 Router R1                  Host B
10.0.1.10       <---->  two interfaces  <---->     10.0.2.20
                      forwards packets
```

## Quick start

Run with Python 3 from the repository root. No packages or network access are required.

```bash
git clone https://github.com/taj-sketch/python-network-simulator.git
cd python-network-simulator
python -X utf8 main.py 1200
```

The argument is the positive message size in bytes. This example splits 1,200 bytes into **500 + 500 + 200**, with sequence numbers **0, 1, 0**. Its final output is:

```text
Simulation completed successfully.
Total application data requested: 1200 bytes
Total application data delivered to Host B: 1200 bytes
Total DATA segments sent: 3
End-to-end data verification: PASSED
```

On Windows, `py -X utf8 main.py 1200` also works when the Python launcher is installed. UTF-8 mode supports the arrow characters used in the logs.

## How it works

| Layer | Representation | Behaviour |
| --- | --- | --- |
| Data link (L2) | `EthernetFrame` | Next-hop MAC lookup, address/type checks and a new frame for each hop |
| Network (L3) | `IPPacket` | Static route lookup, interface selection, TTL decrement and expired-packet drops |
| Transport (L4) | `UDPSegment` | 16-bit one's-complement checksum, DATA/ACK messages and alternating sequence numbers |

The sender splits the generated payload into chunks of at most **500 bytes**. Each chunk travels down the stack as a segment, packet and frame. The router checks the incoming frame, decrements the packet's TTL, selects the next hop and creates the outgoing frame.

Host B accepts a valid segment with the expected sequence number, appends its data and sends a matching ACK. The sender advances only after the correct ACK; otherwise it makes another attempt, up to **three total attempts** per chunk. Duplicate data is acknowledged again without being appended twice.

## Try the boundary cases

```bash
python -X utf8 main.py 1
python -X utf8 main.py 500
python -X utf8 main.py 501
python -X utf8 main.py 1200
```

| Message size | Chunks | Sequence numbers |
| --- | --- | --- |
| 1 byte | 1 | 0 |
| 500 bytes | 500 | 0 |
| 501 bytes | 500 + 1 | 0, 1 |
| 1,200 bytes | 500 + 500 + 200 | 0, 1, 0 |

Delivery checks also pass for 499, 1,000, 1,501 and 65,000 bytes. Invalid or missing arguments produce a usage/error message. Checksum corruption, duplicate delivery and TTL expiry have been checked separately.

## Code guide

| File | Responsibility |
| --- | --- |
| [`main.py`](main.py) | Validate input, build the topology, split the payload and drive DATA/ACK attempts |
| [`config.py`](config.py) | Device addresses, interfaces, routing/MAC tables and protocol constants |
| [`protocol.py`](protocol.py) | Frame, packet and segment classes; lengths and checksum calculation |
| [`devices.py`](devices.py) | Host receive state, acknowledgement handling and router forwarding |

## Model scope

Communication is synchronous and in memory: Python objects are passed between devices. Routing and MAC tables are fixed, and normal runs do not inject packet loss or corruption. The headers illustrate protocol behaviour rather than encode standard Ethernet/IP/UDP packets; the transport uses simplified rdt2.2-style acknowledgement logic.

The final verification checks the number of characters delivered for the generated ASCII payload. The simulator does not model sockets, real network timing or production TCP/IP behaviour.

## Project and contribution

Individual **CITS3002 Computer Networks** project at the University of Western Australia, completed by **Surtaj Singh**. I implemented the four-module simulator, including protocol structures, checksum calculation, host/router behaviour, segmentation and DATA/ACK handling.
