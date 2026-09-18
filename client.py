import socket

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

TIMEOUT = 2

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client.settimeout(TIMEOUT)

messages = [
    "Hello",
    "This is UDP",
    "But we are making it reliable"
]

for sequence_number, message in enumerate(messages, start=1):

    packet = f"{sequence_number}|{message}"

    while True:

        print(f"Sending packet #{sequence_number}")

        client.sendto(
            packet.encode(),
            (SERVER_HOST, SERVER_PORT)
        )

        try:

            data, address = client.recvfrom(1024)

            response = data.decode()

            ack_type, ack_number = response.split("|")

            ack_number = int(ack_number)

            if ack_type == "ACK" and ack_number == sequence_number:

                print(f"ACK received for #{sequence_number}\n")

                break

        except socket.timeout:

            print(f"Timeout! Resending packet #{sequence_number}\n")

client.close()