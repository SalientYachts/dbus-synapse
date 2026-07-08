from src.protocol.crc import build_command

cmd = build_command("QPIGS")

print(cmd)
print(cmd.hex())