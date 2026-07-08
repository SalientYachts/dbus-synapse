"""
PI30 CRC16 implementation used by Voltronic / Synapse inverters.
"""

CRC_POLY = 0x1021


def crc16(data: bytes) -> bytes:
    """
    Calculate the PI30 CRC.

    Returns:
        Two-byte CRC suitable for appending to a PI30 command.
    """

    crc = 0

    for byte in data:
        crc ^= byte << 8

        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ CRC_POLY
            else:
                crc <<= 1

            crc &= 0xFFFF

    hi = (crc >> 8) & 0xFF
    lo = crc & 0xFF

    #
    # PI30 escapes reserved characters
    #
    if hi in (0x28, 0x0D, 0x0A):
        hi += 1

    if lo in (0x28, 0x0D, 0x0A):
        lo += 1

    return bytes([hi, lo])


def build_command(command: str) -> bytes:
    """
    Build a complete PI30 command.

    Example:

        build_command("QPIGS")
    """

    cmd = command.encode("ascii")

    return cmd + crc16(cmd) + b"\r"