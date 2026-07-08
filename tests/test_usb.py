from src.transport.hid import HIDTransport

hid = HIDTransport()

try:

    reply = hid.send_command("QPIGS")

    print(reply)

finally:

    hid.close()