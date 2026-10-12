"""
Configurations for the Mini Internet Protocol Stack Simulator.

Stores all fixed configuration values for the Mini Internet
Protocol Stack Simulator.
"""

# ---------------------------------------------------------
# Device names
# ---------------------------------------------------------

HOST_A_NAME = "Host A"
HOST_B_NAME = "Host B"
ROUTER_R1_NAME = "Router R1"

# ---------------------------------------------------------
# IP addresses
# ---------------------------------------------------------

HOST_A_IP = "10.0.1.10"
HOST_B_IP = "10.0.2.20"

R1_IF1_IP = "10.0.1.1"
R1_IF2_IP = "10.0.2.1"

# ---------------------------------------------------------
# MAC addresses
# ---------------------------------------------------------

HOST_A_MAC = "AA:AA:AA:AA:AA:AA"
R1_IF1_MAC = "BB:BB:BB:BB:BB:BB"
R1_IF2_MAC = "CC:CC:CC:CC:CC:CC"
HOST_B_MAC = "DD:DD:DD:DD:DD:DD"

# ---------------------------------------------------------
# Protocol constants
# ---------------------------------------------------------

ETH_TYPE_IPV4 = 0x0800
IP_PROTOCOL_UDP = 17
DEFAULT_TTL = 100

# UDP-like segment types
DATA = 0
ACK = 1

# ---------------------------------------------------------
# Header sizes in bytes
# ---------------------------------------------------------

ETHERNET_HEADER_SIZE = 14
IP_HEADER_SIZE = 12
UDP_HEADER_SIZE = 10

# ---------------------------------------------------------
# Ports
# ---------------------------------------------------------

HOST_A_PORT = 5000
HOST_B_PORT = 80

# ---------------------------------------------------------
# Segmentation
# ---------------------------------------------------------

MAX_SEGMENT_DATA_SIZE = 500

# ---------------------------------------------------------
# Interface definitions
# ---------------------------------------------------------

HOST_A_INTERFACE = {
    "eth0": {
        "ip": HOST_A_IP,
        "mac": HOST_A_MAC,
        "network": "10.0.1.0/24",
    }
}

HOST_B_INTERFACE = {
    "eth0": {
        "ip": HOST_B_IP,
        "mac": HOST_B_MAC,
        "network": "10.0.2.0/24",
    }
}

ROUTER_R1_INTERFACES = {
    "if1": {
        "ip": R1_IF1_IP,
        "mac": R1_IF1_MAC,
        "network": "10.0.1.0/24",
    },
    "if2": {
        "ip": R1_IF2_IP,
        "mac": R1_IF2_MAC,
        "network": "10.0.2.0/24",
    },
}

# ---------------------------------------------------------
# Routing tables
# Each entry maps:
# destination IP -> (outgoing interface, next-hop IP)
# ---------------------------------------------------------

HOST_A_ROUTING_TABLE = {
    HOST_B_IP: ("eth0", R1_IF1_IP),
}

HOST_B_ROUTING_TABLE = {
    HOST_A_IP: ("eth0", R1_IF2_IP),
}

ROUTER_R1_ROUTING_TABLE = {
    HOST_A_IP: ("if1", HOST_A_IP),
    HOST_B_IP: ("if2", HOST_B_IP),
}

# ---------------------------------------------------------
# MAC lookup tables
# Each entry maps:
# next-hop IP -> destination MAC address
# ---------------------------------------------------------

HOST_A_MAC_TABLE = {
    R1_IF1_IP: R1_IF1_MAC,
}

HOST_B_MAC_TABLE = {
    R1_IF2_IP: R1_IF2_MAC,
}

ROUTER_R1_MAC_TABLE = {
    HOST_A_IP: HOST_A_MAC,
    HOST_B_IP: HOST_B_MAC,
}