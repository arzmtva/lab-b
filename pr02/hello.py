import sys

filename = sys.argv[1]

with open(filename, "rb") as file:
    data = file.read()

print(f"File size: {len(data)} bytes")
