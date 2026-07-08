import os
import time

DEVICE = "/dev/hidraw0"

class HIDTransport:

    def __init__(self):
        self.fd = os.open(DEVICE, os.O_RDWR)

    def flush(self):
        pass

    def send_command(self, command):

        payload = command.encode() + b"\r"

        for i in range(0, len(payload), 8):
            chunk = payload[i:i+8]
            chunk = chunk.ljust(8, b"\x00")
            os.write(self.fd, chunk)

        time.sleep(0.1)

        response = bytearray()

        while True:
            packet = os.read(self.fd, 8)
            response.extend(packet)

            if 0x0D in packet:
                break

        response = bytes(response)

        response = response[:response.index(0x0D)]
        response = response.replace(b"\x00", b"")

        if len(response) > 2:
            response = response[:-2]

        return response.decode(errors="ignore")

    def close(self):
        os.close(self.fd)