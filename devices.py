"""
Host and Router classes for the network simulator.

Frames are passed between Python objects instead of using real sockets.
"""

from protocol import EthernetFrame, IPPacket, UDPSegment
from config import (
    R1_IF1_MAC,
    R1_IF2_MAC,
    R1_IF1_IP,
    R1_IF2_IP,
    ETH_TYPE_IPV4,
    IP_PROTOCOL_UDP,
    DEFAULT_TTL,
    DATA,
    ACK,
)


class Host:
    """
    Represents a host in the simulated network.

    A host can:
    - send DATA segments
    - receive DATA segments
    - receive ACK segments
    - pass packets through Layer 4, Layer 3, and Layer 2
    """

    def __init__(self, name, ip_address, mac_address, local_port, routing_table, mac_table):
        self.name = name
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.local_port = local_port
        self.routing_table = routing_table
        self.mac_table = mac_table

        self.router = None
        self.router_interface = None

        # rdt2.2 receiver-side state
        self.expected_seq = 0
        self.last_ack_seq = None

        # Application-layer receive buffer
        self.received_application_data = ""

        # Learned MAC addresses for demonstration/logging
        self.learned_macs = {}

    def connect_router(self, router, router_interface):
        """
        Connect this host to a router interface.

        For this project:
        - Host A connects to Router R1 Interface 1
        - Host B connects to Router R1 Interface 2
        """
        self.router = router
        self.router_interface = router_interface

    # ---------------------------------------------------------
    # Layer 4 sending
    # ---------------------------------------------------------

    def send_data_segment(self, data, seq_num, destination_ip, destination_port):
        """
        Sends one DATA segment using the full protocol stack.

        This represents:
        Application Layer -> Layer 4 -> Layer 3 -> Layer 2
        """

        print(f"{self.name}: Layer 4: Data received from Application Layer. Data size={len(data)}")

        segment = UDPSegment(
            src_port=self.local_port,
            dst_port=destination_port,
            seg_type=DATA,
            seq_num=seq_num,
            data=data,
        )

        print(f"{self.name}: Layer 4: Checksum computed")
        print(
            f"{self.name}: Layer 4: Segment created by adding transport layer header "
            f"(DATA, seq={seq_num}) (encapsulation)"
        )
        print(f"{self.name}: Layer 4: Segment sent to Network Layer")

        return self._send_segment_to_network_layer(segment, destination_ip)

    def _send_ack_segment(self, seq_num, destination_ip, destination_port):
        """
        Sends an ACK segment back to the original sender.
        """

        ack_segment = UDPSegment(
            src_port=self.local_port,
            dst_port=destination_port,
            seg_type=ACK,
            seq_num=seq_num,
            data="",
        )

        print(
            f"{self.name}: Layer 4: Segment created by adding transport layer header "
            f"(ACK, seq={seq_num})"
        )
        print(f"{self.name}: Layer 4: Segment sent to Network Layer")

        return self._send_segment_to_network_layer(ack_segment, destination_ip)

    # ---------------------------------------------------------
    # Layer 3 sending
    # ---------------------------------------------------------

    def _send_segment_to_network_layer(self, segment, destination_ip):
        """
        Encapsulates a Layer 4 segment into a Layer 3 IP-like packet.
        """

        packet = IPPacket(
            src_ip=self.ip_address,
            dst_ip=destination_ip,
            payload=segment,
            ttl=DEFAULT_TTL,
            protocol=IP_PROTOCOL_UDP,
        )

        print(
            f"{self.name}: Layer 3: Segment received from Transport Layer: "
            f"SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}"
        )
        print(f"{self.name}: Layer 3: Destination IP read: {packet.dst_ip}")
        print(f"{self.name}: Layer 3: Routing table lookup performed")

        if destination_ip not in self.routing_table:
            print(f"{self.name}: Layer 3: No route found. Packet dropped")
            return None

        outgoing_interface, next_hop_ip = self.routing_table[destination_ip]

        print(f"{self.name}: Layer 3: Next-hop IP determined: {next_hop_ip}")
        print(f"{self.name}: Layer 3: Outgoing interface selected")
        print(f"{self.name}: Layer 3: Packet forwarded to Data Link Layer")

        return self._send_packet_to_data_link_layer(packet, next_hop_ip)

    # ---------------------------------------------------------
    # Layer 2 sending
    # ---------------------------------------------------------

    def _send_packet_to_data_link_layer(self, packet, next_hop_ip):
        """
        Encapsulates a Layer 3 packet into a Layer 2 Ethernet-like frame.
        """

        print(f"{self.name}: Layer 2: Packet received from Network Layer")

        if self.router is None or self.router_interface is None:
            print(f"{self.name}: Layer 2: No router connected. Frame dropped")
            return None

        if next_hop_ip not in self.mac_table:
            print(f"{self.name}: Layer 2: MAC address for next-hop IP not found. Frame dropped")
            return None

        destination_mac = self.mac_table[next_hop_ip]

        print(
            f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP "
            f"({next_hop_ip}) → {destination_mac}"
        )

        frame = EthernetFrame(
            dst_mac=destination_mac,
            src_mac=self.mac_address,
            payload=packet,
            eth_type=ETH_TYPE_IPV4,
        )

        print(
            f"{self.name}: Layer 2: Frame created: "
            f"SRC_MAC={frame.src_mac}, DST_MAC={frame.dst_mac}"
        )
        print(f"{self.name}: Layer 2: Frame sent")

        return self.router.receive_frame(frame, self.router_interface)

    # ---------------------------------------------------------
    # Layer 2 receiving
    # ---------------------------------------------------------

    def receive_frame(self, frame):
        """
        Receives an Ethernet-like frame from the router.
        """

        print(f"{self.name}: Layer 2: Frame received")

        self.learned_macs[frame.src_mac] = "local-link"
        print(f"{self.name}: Layer 2: Source MAC learned: {frame.src_mac}")

        if frame.dst_mac != self.mac_address:
            print(f"{self.name}: Layer 2: Frame not addressed to this host. Frame dropped")
            return None

        if frame.eth_type != ETH_TYPE_IPV4:
            print(f"{self.name}: Layer 2: Unsupported Ethernet type. Frame dropped")
            return None

        print(f"{self.name}: Layer 2: Packet delivered to Network Layer")

        return self._receive_packet_from_data_link_layer(frame.payload)

    # ---------------------------------------------------------
    # Layer 3 receiving
    # ---------------------------------------------------------

    def _receive_packet_from_data_link_layer(self, packet):
        """
        Receives an IP-like packet from Layer 2.
        """

        print(
            f"{self.name}: Layer 3: Packet received from Data Link Layer: "
            f"SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}"
        )
        print(f"{self.name}: Layer 3: Destination IP read: {packet.dst_ip}")

        if packet.dst_ip == self.ip_address:
            print(f"{self.name}: Layer 3: Packet identified as local delivery")
            print(f"{self.name}: Layer 3: Segment delivered to Transport Layer")
            return self._receive_segment_from_network_layer(packet.payload, packet.src_ip)

        print(f"{self.name}: Layer 3: Packet not for this host. Packet dropped")
        return None

    # ---------------------------------------------------------
    # Layer 4 receiving
    # ---------------------------------------------------------

    def _receive_segment_from_network_layer(self, segment, source_ip):
        """
        Receives a UDP-like segment from Layer 3.
        """

        print(f"{self.name}: Layer 4: Segment received from Network Layer")

        if not segment.is_valid():
            print(f"{self.name}: Layer 4: Segment discarded due to checksum error")

            if self.last_ack_seq is not None:
                print(f"{self.name}: Layer 4: Re-sending last ACK: seq={self.last_ack_seq}")
                return self._send_ack_segment(
                    seq_num=self.last_ack_seq,
                    destination_ip=source_ip,
                    destination_port=segment.src_port,
                )

            return None

        print(f"{self.name}: Layer 4: Checksum verified")

        if segment.is_data():
            return self._handle_data_segment(segment, source_ip)

        if segment.is_ack():
            return self._handle_ack_segment(segment)

        print(f"{self.name}: Layer 4: Unknown segment type. Segment discarded")
        return None

    def _handle_data_segment(self, segment, source_ip):
        """
        Handles a received DATA segment using rdt2.2 logic.
        """

        if segment.seq_num == self.expected_seq:
            self.received_application_data += segment.data

            print(
                f"{self.name}: Layer 4: DATA segment delivered to Application Layer. "
                f"Data size={len(segment.data)}"
            )
            print(
                f"{self.name}: Application Layer: Total data received so far="
                f"{len(self.received_application_data)} bytes"
            )

            self.last_ack_seq = segment.seq_num
            ack_seq = segment.seq_num
            self.expected_seq = 1 - self.expected_seq

            return self._send_ack_segment(
                seq_num=ack_seq,
                destination_ip=source_ip,
                destination_port=segment.src_port,
            )

        # Duplicate DATA segment
        print(
            f"{self.name}: Layer 4: Duplicate DATA segment received. "
            f"Expected seq={self.expected_seq}, received seq={segment.seq_num}"
        )

        if self.last_ack_seq is not None:
            print(f"{self.name}: Layer 4: Re-sending last ACK: seq={self.last_ack_seq}")
            return self._send_ack_segment(
                seq_num=self.last_ack_seq,
                destination_ip=source_ip,
                destination_port=segment.src_port,
            )

        return None

    def _handle_ack_segment(self, segment):
        """
        Handles a received ACK segment.
        """

        print(f"{self.name}: Layer 4: ACK received: seq={segment.seq_num}")
        return segment


class Router:
    """
    Represents Router R1 in the fixed topology.

    The router forwards IP packets between its two interfaces and
    creates a new Ethernet-like frame for each outgoing hop.
    """

    def __init__(self, name, routing_table, mac_table):
        self.name = name
        self.routing_table = routing_table
        self.mac_table = mac_table

        self.interfaces = {
            "if1": {
                "label": "Interface 1",
                "ip": R1_IF1_IP,
                "mac": R1_IF1_MAC,
            },
            "if2": {
                "label": "Interface 2",
                "ip": R1_IF2_IP,
                "mac": R1_IF2_MAC,
            },
        }

        # Used to demonstrate MAC learning
        self.mac_learning_table = {}

        self.host_a = None
        self.host_b = None

    def connect_hosts(self, host_a, host_b):
        """
        Connects Host A and Host B to the router.
        """
        self.host_a = host_a
        self.host_b = host_b

    # ---------------------------------------------------------
    # Layer 2 receiving
    # ---------------------------------------------------------

    def receive_frame(self, frame, incoming_interface):
        """
        Receives an Ethernet-like frame on a router interface.
        """

        if incoming_interface not in self.interfaces:
            print(f"{self.name}: Layer 2: Unknown incoming interface. Frame dropped")
            return None

        interface_label = self.interfaces[incoming_interface]["label"]

        print(f"{self.name}: Layer 2: Frame received on {interface_label}")

        expected_mac = self.interfaces[incoming_interface]["mac"]

        if frame.dst_mac != expected_mac:
            print(f"{self.name}: Layer 2: Frame not addressed to this interface. Frame dropped")
            return None

        if frame.eth_type != ETH_TYPE_IPV4:
            print(f"{self.name}: Layer 2: Unsupported Ethernet type. Frame dropped")
            return None

        self.mac_learning_table[frame.src_mac] = incoming_interface
        print(
            f"{self.name}: Layer 2: Source MAC learned: "
            f"{frame.src_mac} on {interface_label}"
        )

        print(f"{self.name}: Layer 2: Packet delivered to Network Layer")

        return self._receive_packet_from_data_link_layer(frame.payload)

    # ---------------------------------------------------------
    # Layer 3 receiving / forwarding
    # ---------------------------------------------------------

    def _receive_packet_from_data_link_layer(self, packet):
        """
        Receives an IP-like packet from Layer 2 and forwards it.
        """

        print(
            f"{self.name}: Layer 3: Packet received from Data Link Layer: "
            f"SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}"
        )
        print(f"{self.name}: Layer 3: Destination IP read: {packet.dst_ip}")

        old_ttl, new_ttl = packet.decrement_ttl()
        print(f"{self.name}: Layer 3: TTL decremented: {old_ttl} → {new_ttl}")

        if packet.is_expired():
            print(f"{self.name}: Layer 3: Packet dropped due to TTL expiry")
            return None

        print(f"{self.name}: Layer 3: Routing table lookup performed")

        if packet.dst_ip not in self.routing_table:
            print(f"{self.name}: Layer 3: No route found. Packet dropped")
            return None

        outgoing_interface, next_hop_ip = self.routing_table[packet.dst_ip]
        interface_label = self.interfaces[outgoing_interface]["label"]

        print(f"{self.name}: Layer 3: Next-hop IP determined: {next_hop_ip}")
        print(f"{self.name}: Layer 3: Outgoing interface selected ({interface_label})")
        print(f"{self.name}: Layer 3: Packet forwarded to Data Link Layer")

        return self._send_packet_to_data_link_layer(
            packet=packet,
            outgoing_interface=outgoing_interface,
            next_hop_ip=next_hop_ip,
        )

    # ---------------------------------------------------------
    # Layer 2 forwarding
    # ---------------------------------------------------------

    def _send_packet_to_data_link_layer(self, packet, outgoing_interface, next_hop_ip):
        """
        Encapsulates the packet into a new frame and forwards it.
        """

        print(f"{self.name}: Layer 2: Packet received from Network Layer")

        if outgoing_interface not in self.interfaces:
            print(f"{self.name}: Layer 2: Unknown outgoing interface. Frame dropped")
            return None

        if next_hop_ip not in self.mac_table:
            print(f"{self.name}: Layer 2: MAC address for next-hop IP not found. Frame dropped")
            return None

        destination_mac = self.mac_table[next_hop_ip]
        source_mac = self.interfaces[outgoing_interface]["mac"]
        interface_label = self.interfaces[outgoing_interface]["label"]

        print(
            f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP "
            f"({next_hop_ip}) → {destination_mac}"
        )

        frame = EthernetFrame(
            dst_mac=destination_mac,
            src_mac=source_mac,
            payload=packet,
            eth_type=ETH_TYPE_IPV4,
        )

        print(
            f"{self.name}: Layer 2: Frame created: "
            f"SRC_MAC={frame.src_mac}, DST_MAC={frame.dst_mac}"
        )
        print(f"{self.name}: Layer 2: Frame forwarded on {interface_label}")

        if outgoing_interface == "if1":
            if self.host_a is None:
                print(f"{self.name}: Layer 2: Host A not connected. Frame dropped")
                return None
            return self.host_a.receive_frame(frame)

        if outgoing_interface == "if2":
            if self.host_b is None:
                print(f"{self.name}: Layer 2: Host B not connected. Frame dropped")
                return None
            return self.host_b.receive_frame(frame)

        print(f"{self.name}: Layer 2: Unknown outgoing interface. Frame dropped")
        return None