# Python Network Simulator

A Python simulation of data travelling from Host A through a router to Host B. It models encapsulation, routing and reliable delivery through simplified Ethernet, IP and UDP-like protocol objects.

## Implementation

- Ethernet-like frames with source and destination MAC addresses.
- IP-like packets with routing tables, next-hop selection and time-to-live checks.
- UDP-like segments with a 16-bit checksum, DATA/ACK messages and alternating sequence numbers.
- Application payload segmentation, acknowledgements, retransmission attempts and duplicate-delivery suppression.
- Layer-by-layer logs and end-to-end payload verification.

The simulation passes objects between devices in memory. Its simplified headers and transport protocol are intended for learning and do not implement a production TCP/IP stack.

## Run

Use Python 3.9 or newer. There are no third-party dependencies.

```bash
python -X utf8 main.py 1501
```

The argument is the positive message size in bytes. A successful run ends with `End-to-end data verification: PASSED`. The UTF-8 option supports the arrow characters in the logs on Windows.

## Source files

| File | Purpose |
| --- | --- |
| `main.py` | Builds the topology, splits the message and drives transmission. |
| `devices.py` | Implements hosts, router forwarding, ACK handling and receiver state. |
| `protocol.py` | Defines frames, packets, segments and checksum calculation. |
| `config.py` | Defines addresses, interfaces, routing tables and protocol constants. |

## Validation

Before publication, delivery checks passed for 1, 499, 500, 501, 1,501 and 65,000 bytes. Additional checks covered missing or invalid input, corrupted checksums, duplicate delivery and expired TTLs.

## Project context

An educational networking project by Surtaj Singh. The repository contains the complete four-module implementation.
