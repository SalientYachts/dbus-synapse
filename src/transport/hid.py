import time
import usb.core
import usb.util

VENDOR_ID = 0x0665
PRODUCT_ID = 0x5161

HID_SET_REPORT = 0x09
HID_REPORT_TYPE_OUTPUT = 0x02
BM_REQUEST_TYPE = 0x21

CHUNK_SIZE = 8
READ_ENDPOINT = 0x81


class HIDTransport:

    def __init__(self):
        self.dev = usb.core.find(
            idVendor=VENDOR_ID,
            idProduct=PRODUCT_ID
        )

        if self.dev is None:
            raise RuntimeError("Synapse inverter not found")

        if self.dev.is_kernel_driver_active(0):
            self.dev.detach_kernel_driver(0)

        self.dev.set_configuration()
        usb.util.claim_interface(self.dev, 0)

    def flush(self):

        while True:
            try:
                self.dev.read(
                    READ_ENDPOINT,
                    CHUNK_SIZE,
                    timeout=20
                )
            except usb.core.USBError:
                break

    def send_command(self, command):

        self.flush()

        payload = command.encode() + b"\r"

        for i in range(0, len(payload), 8):

            chunk = payload[i:i + 8]
            chunk = chunk.ljust(8, b"\x00")

            self.dev.ctrl_transfer(
                BM_REQUEST_TYPE,
                HID_SET_REPORT,
                (HID_REPORT_TYPE_OUTPUT << 8),
                0,
                chunk
            )

        time.sleep(0.1)

        response = bytearray()

        while True:

            packet = self.dev.read(
                READ_ENDPOINT,
                CHUNK_SIZE,
                timeout=1000
            )

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

        usb.util.release_interface(self.dev, 0)
        usb.util.dispose_resources(self.dev)