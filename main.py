"""
Main entry point for the protocol stack simulator.

The program creates the network topology, sends application data from
Host A to Host B, and verifies that the full message is delivered.
"""

import sys

from devices import Host, Router
from config import (
    HOST_A_NAME,
    HOST_B_NAME,
    ROUTER_R1_NAME,
    HOST_A_IP,
    HOST_B_IP,
    HOST_A_MAC,
    HOST_B_MAC,
    HOST_A_PORT,
    HOST_B_PORT,
    MAX_SEGMENT_DATA_SIZE,
    HOST_A_ROUTING_TABLE,
    HOST_B_ROUTING_TABLE,
    ROUTER_R1_ROUTING_TABLE,
    HOST_A_MAC_TABLE,
    HOST_B_MAC_TABLE,
    ROUTER_R1_MAC_TABLE,
)


def validate_message_size(args):
    """
    Validates the command-line message size.

    Expected usage:
        python main.py 100
    """

    if len(args) != 2:
        print("Usage: python main.py <message_size_in_bytes>")
        return None

    try:
        message_size = int(args[1])
    except ValueError:
        print("Error: message size must be an integer.")
        return None

    if message_size <= 0:
        print("Error: message size must be a positive integer.")
        return None

    return message_size


def split_application_data(application_data):
    """
    Splits application data into chunks of at most MAX_SEGMENT_DATA_SIZE bytes.
    """

    chunks = []

    for i in range(0, len(application_data), MAX_SEGMENT_DATA_SIZE):
        chunk = application_data[i:i + MAX_SEGMENT_DATA_SIZE]
        chunks.append(chunk)

    return chunks


def build_network():
    """
    Creates Host A, Router R1, and Host B, then connects them logically.
    """

    host_a = Host(
        name=HOST_A_NAME,
        ip_address=HOST_A_IP,
        mac_address=HOST_A_MAC,
        local_port=HOST_A_PORT,
        routing_table=HOST_A_ROUTING_TABLE,
        mac_table=HOST_A_MAC_TABLE,
    )

    host_b = Host(
        name=HOST_B_NAME,
        ip_address=HOST_B_IP,
        mac_address=HOST_B_MAC,
        local_port=HOST_B_PORT,
        routing_table=HOST_B_ROUTING_TABLE,
        mac_table=HOST_B_MAC_TABLE,
    )

    router_r1 = Router(
        name=ROUTER_R1_NAME,
        routing_table=ROUTER_R1_ROUTING_TABLE,
        mac_table=ROUTER_R1_MAC_TABLE,
    )

    host_a.connect_router(router_r1, "if1")
    host_b.connect_router(router_r1, "if2")
    router_r1.connect_hosts(host_a, host_b)

    return host_a, router_r1, host_b


def main():
    """
    Runs the simulation.
    """

    message_size = validate_message_size(sys.argv)

    if message_size is None:
        return

    print("Mini Internet Protocol Stack Simulator")
    print("--------------------------------------")
    print(f"Message size: {message_size} bytes")
    print()

    host_a, _, host_b = build_network()

    # Create a test payload of the requested size.
    # Since "X" is one ASCII character, len(application_data) equals the byte size.
    application_data = "X" * message_size

    chunks = split_application_data(application_data)

    print("Starting transmission: Host A → Router R1 → Host B")
    print(f"Total segments required: {len(chunks)}")
    print()

    seq_num = 0
    all_segments_delivered = True
    max_retries = 3

    for index, chunk in enumerate(chunks, start=1):
        print("=" * 70)
        print(
            f"Sending segment {index}/{len(chunks)} "
            f"| Data size={len(chunk)} bytes "
            f"| seq={seq_num}"
        )
        print("=" * 70)

        segment_delivered = False

        for attempt in range(1, max_retries + 1):
            if attempt > 1:
                print(
                    f"Host A: Layer 4: Retransmitting segment {index}/{len(chunks)} "
                    f"due to incorrect or missing ACK"
                )

            ack_segment = host_a.send_data_segment(
                data=chunk,
                seq_num=seq_num,
                destination_ip=HOST_B_IP,
                destination_port=HOST_B_PORT,
            )

            print()

            if ack_segment is not None and ack_segment.is_ack() and ack_segment.seq_num == seq_num:
                print(f"Host A: Layer 4: Correct ACK received for seq={seq_num}")
                print(f"Host A: Layer 4: Segment {index}/{len(chunks)} completed")
                seq_num = 1 - seq_num
                segment_delivered = True
                print()
                break

            print(f"Host A: Layer 4: Correct ACK not received for seq={seq_num}")

        if not segment_delivered:
            print(
                f"Host A: Layer 4: Segment {index}/{len(chunks)} failed "
                f"after {max_retries} attempts"
            )
            all_segments_delivered = False
            break

    print("=" * 70)

    if all_segments_delivered:
        actual_delivered = len(host_b.received_application_data)

        print("Simulation completed successfully.")
        print(f"Total application data requested: {message_size} bytes")
        print(f"Total application data delivered to Host B: {actual_delivered} bytes")
        print(f"Total DATA segments sent: {len(chunks)}")

        if actual_delivered == message_size:
            print("End-to-end data verification: PASSED")
        else:
            print("End-to-end data verification: FAILED")
    else:
        print("Simulation failed.")


if __name__ == "__main__":
    main()