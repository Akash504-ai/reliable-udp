import socket


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000

TIMEOUT = 2
MAX_RETRIES = 5

client = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

client.settimeout(TIMEOUT)

messages = [
    "Hello",
    "This is UDP",
    "But we are making it reliable"
]

try:

    for sequence_number, message in enumerate(messages, start=1):

        packet = f"{sequence_number}|{message}"

        retries = 0

        while retries < MAX_RETRIES:

            print(
                f"Sending packet #{sequence_number}: "
                f"{message}"
            )

            client.sendto(
                packet.encode(),
                (SERVER_HOST, SERVER_PORT)
            )

            try:

                data, address = client.recvfrom(1024)

                response = data.decode()

                ack_type, ack_number = response.split("|", 1)

                ack_number = int(ack_number)

                if (
                    ack_type == "ACK"
                    and ack_number == sequence_number
                ):

                    print(
                        f"ACK received for "
                        f"#{sequence_number}\n"
                    )

                    break

                else:

                    print(
                        f"Unexpected ACK received: "
                        f"{response}"
                    )

            except socket.timeout:

                retries += 1

                print(
                    f"Timeout for packet "
                    f"#{sequence_number}"
                )

                print(
                    f"Retrying "
                    f"({retries}/{MAX_RETRIES})...\n"
                )

        if retries == MAX_RETRIES:

            print(
                f"Failed to deliver "
                f"packet #{sequence_number}"
            )

            print(
                "Maximum retries reached."
            )

            break


    print("Transfer completed.")

except KeyboardInterrupt:

    print("\nClient stopped by user.")


finally:

    client.close()

    print("Socket closed.")