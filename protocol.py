"""
Protocol classes used by the simulator.

The classes represent simplified Layer 2, Layer 3, and Layer 4 headers.
"""

from config import (
    ETH_TYPE_IPV4,
    IP_PROTOCOL_UDP,
    DEFAULT_TTL,
    DATA,
    ACK,
    ETHERNET_HEADER_SIZE,
    IP_HEADER_SIZE,
    UDP_HEADER_SIZE,
)


class EthernetFrame:
    """
    Represents a simplified Ethernet-like Layer 2 frame.

    Header fields:
    - Destination MAC address
    - Source MAC address
    - Type field
    - Payload containing an IPPacket
    """

    HEADER_SIZE = ETHERNET_HEADER_SIZE

    def __init__(self, dst_mac, src_mac, payload, eth_type=ETH_TYPE_IPV4):
        self.dst_mac = dst_mac
        self.src_mac = src_mac
        self.eth_type = eth_type
        self.payload = payload

    def total_size(self):
        """
        Returns the logical size of the frame in bytes.
        """
        payload_size = self.payload.total_size() if hasattr(self.payload, "total_size") else 0
        return self.HEADER_SIZE + payload_size

    def __repr__(self):
        return (
            f"EthernetFrame(src_mac={self.src_mac}, "
            f"dst_mac={self.dst_mac}, eth_type={hex(self.eth_type)})"
        )


class IPPacket:
    """
    Represents a simplified IP-like Layer 3 packet.

    Header fields:
    - Source IP
    - Destination IP
    - TTL
    - Protocol
    - Total length
    - Payload containing a UDPSegment
    """

    HEADER_SIZE = IP_HEADER_SIZE

    def __init__(self, src_ip, dst_ip, payload, ttl=DEFAULT_TTL, protocol=IP_PROTOCOL_UDP):
        if ttl < 0:
            raise ValueError("TTL cannot be negative")

        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.ttl = ttl
        self.protocol = protocol
        self.payload = payload
        self.total_length = self.total_size()

    def total_size(self):
        """
        Returns the logical size of the IP packet in bytes.
        """
        payload_size = self.payload.total_size() if hasattr(self.payload, "total_size") else 0
        return self.HEADER_SIZE + payload_size

    def decrement_ttl(self):
        """
        Decrements TTL by one when the packet passes through a router.
        Returns the old and new TTL values for logging.
        """
        old_ttl = self.ttl
        self.ttl -= 1
        return old_ttl, self.ttl

    def is_expired(self):
        """
        Returns True if TTL has reached zero or below.
        """
        return self.ttl <= 0

    def __repr__(self):
        return (
            f"IPPacket(src_ip={self.src_ip}, dst_ip={self.dst_ip}, "
            f"ttl={self.ttl}, protocol={self.protocol}, length={self.total_length})"
        )


class UDPSegment:
    """
    Represents a simplified UDP-like Layer 4 segment with ACK support.

    Header fields:
    - Source port
    - Destination port
    - Length
    - Checksum
    - Type: DATA or ACK
    - Sequence number: 0 or 1
    - Data
    """

    HEADER_SIZE = UDP_HEADER_SIZE

    def __init__(self, src_port, dst_port, seg_type, seq_num, data=""):
        if seg_type not in (DATA, ACK):
            raise ValueError("Segment type must be DATA or ACK")

        if seq_num not in (0, 1):
            raise ValueError("Sequence number must be 0 or 1")

        self.src_port = src_port
        self.dst_port = dst_port
        self.seg_type = seg_type
        self.seq_num = seq_num
        self.data = data
        self.length = self.total_size()

        self.checksum = 0
        self.checksum = self.compute_checksum()

    def total_size(self):
        """
        Returns the logical size of the UDP-like segment in bytes.
        """
        return self.HEADER_SIZE + len(self._data_bytes())

    def _data_bytes(self):
        """
        Converts the data field into bytes for checksum calculation.
        """
        if isinstance(self.data, bytes):
            return self.data
        return str(self.data).encode("utf-8")

    def _bytes_for_checksum(self):
        """
        Creates a byte representation of the segment fields for checksum calculation.

        The checksum field itself is treated as zero while calculating the checksum.
        """
        header_string = (
            f"{self.src_port}|"
            f"{self.dst_port}|"
            f"{self.length}|"
            f"0|"
            f"{self.seg_type}|"
            f"{self.seq_num}|"
        )

        return header_string.encode("utf-8") + self._data_bytes()

    def compute_checksum(self):
        """
        Computes a 16-bit one's complement checksum.

        This follows the same idea as the Internet/UDP checksum:
        - split data into 16-bit words
        - add them using wraparound carry
        - return one's complement of the final sum
        """
        data = self._bytes_for_checksum()

        if len(data) % 2 == 1:
            data += b"\x00"

        total = 0

        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i + 1]
            total += word

            while total > 0xFFFF:
                total = (total & 0xFFFF) + (total >> 16)

        return ~total & 0xFFFF

    def is_valid(self):
        """
        Verifies whether the segment checksum is correct.
        """
        return self.checksum == self.compute_checksum()

    def is_data(self):
        """
        Returns True if this is a DATA segment.
        """
        return self.seg_type == DATA

    def is_ack(self):
        """
        Returns True if this is an ACK segment.
        """
        return self.seg_type == ACK

    def type_name(self):
        """
        Returns a readable segment type name for logging.
        """
        if self.seg_type == DATA:
            return "DATA"
        if self.seg_type == ACK:
            return "ACK"
        return "UNKNOWN"

    def __repr__(self):
        return (
            f"UDPSegment(type={self.type_name()}, seq={self.seq_num}, "
            f"src_port={self.src_port}, dst_port={self.dst_port}, length={self.length})"
        )