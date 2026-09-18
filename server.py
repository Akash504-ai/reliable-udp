import socket

HOST = "127.0.0.1"
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server.bind((HOST, PORT))

print(f"Server started on {HOST}:{PORT}")

received_packets = set()

while True:

    data, address = server.recvfrom(1024)

    message = data.decode()

    sequence_number, content = message.split("|", 1)

    sequence_number = int(sequence_number)

    if sequence_number in received_packets:
        print(f"Duplicate packet received: #{sequence_number}")

    else:
        received_packets.add(sequence_number)

        print(f"Received #{sequence_number}: {content}")

    ack = f"ACK|{sequence_number}"

    server.sendto(ack.encode(), address)

    print(f"Sent ACK for #{sequence_number}")