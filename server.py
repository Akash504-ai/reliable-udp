import socket
import random

HOST = "127.0.0.1"
PORT = 5000

# Percentage of packets/ACKs we intentionally drop
PACKET_LOSS_RATE = 0.20
ACK_LOSS_RATE = 0.30


server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server.bind((HOST, PORT))

print("=" * 50)
print("Reliable UDP Server")
print("=" * 50)
print(f"Server running on {HOST}:{PORT}")
print(f"Packet loss simulation : {PACKET_LOSS_RATE * 100:.0f}%")
print(f"ACK loss simulation    : {ACK_LOSS_RATE * 100:.0f}%")
print("Waiting for packets...\n")


received_packets = set()

# The next packet we expect
expected_sequence_number = 1

try:

    while True:

        data, address = server.recvfrom(1024)

        if random.random() < PACKET_LOSS_RATE:

            # Try to extract sequence number
            try:
                message = data.decode()
                sequence_number = int(message.split("|", 1)[0])

                print(
                    f"Packet #{sequence_number} "
                    f"dropped by network simulation"
                )

            except (ValueError, UnicodeDecodeError):

                print("Invalid packet dropped")

            continue


        try:

            message = data.decode()

            sequence_number, content = message.split("|", 1)

            sequence_number = int(sequence_number)

        except (ValueError, UnicodeDecodeError):

            print("Invalid packet received")
            continue


        print(f"Packet #{sequence_number} received")


        if sequence_number in received_packets:

            print(
                f"Duplicate packet detected: "
                f"#{sequence_number}"
            )


        elif sequence_number == expected_sequence_number:

            received_packets.add(sequence_number)

            print(f"Processing #{sequence_number}: {content}")

            expected_sequence_number += 1



        elif sequence_number > expected_sequence_number:

            received_packets.add(sequence_number)

            print(
                f"Out-of-order packet #{sequence_number}"
            )

            print(
                f"   Expected packet #{expected_sequence_number}"
            )

            print(
                f"   Buffering packet #{sequence_number}"
            )


        else:

            received_packets.add(sequence_number)

            print(
                f"Old packet received: "
                f"#{sequence_number}"
            )


        if random.random() < ACK_LOSS_RATE:

            print(
                f"ACK for #{sequence_number} "
                f"dropped by network simulation\n"
            )

            continue


        ack = f"ACK|{sequence_number}"

        server.sendto(
            ack.encode(),
            address
        )

        print(
            f"ACK sent for #{sequence_number}\n"
        )


except KeyboardInterrupt:

    print("\n\nServer shutting down...")

finally:

    server.close()

    print("Socket closed.")