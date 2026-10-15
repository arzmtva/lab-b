
import json
import sys


def is_safe(available, allocation, need):
    work = available[:]
    finished = [False] * len(allocation)
    sequence = []

    while True:
        found = False

        for i in range(len(allocation)):
            if not finished[i] and all(
                need[i][j] <= work[j]
                for j in range(len(work))
            ):
                work = [
                    work[j] + allocation[i][j]
                    for j in range(len(work))
                ]
                finished[i] = True
                sequence.append(i)
                found = True

        if not found:
            break

    return all(finished), sequence


def main():
    # Read initial system state from a JSON file.
    filename = sys.argv[1] if len(sys.argv) > 1 else "banker.json"

    with open(filename, encoding="utf-8") as file:
        data = json.load(file)

    available = data["available"]
    allocation = data["allocation"]
    maximum = data["maximum"]

    need = [
        [maximum[i][j] - allocation[i][j]
         for j in range(len(available))]
        for i in range(len(allocation))
    ]

    safe, sequence = is_safe(available, allocation, need)

    if safe:
        print("Initial state is SAFE.")
        print("Safe sequence:", " -> ".join(f"P{i}" for i in sequence))
    else:
        print("Initial state is UNSAFE.")

    # Requests are read from standard input:
    # one JSON object per line, e.g. {"pid": 1, "request": [1, 0, 2]}
    for line in sys.stdin:
        if not line.strip():
            continue

        request_data = json.loads(line)
        pid = request_data["pid"]
        request = request_data["request"]

        if not 0 <= pid < len(allocation):
            print("DENIED: invalid process ID")
            continue

        if len(request) != len(available) or any(x < 0 for x in request):
            print("DENIED: invalid request vector")
            continue

        if any(request[j] > need[pid][j]
               for j in range(len(available))):
            print("DENIED: request exceeds remaining need")
            continue

        if any(request[j] > available[j]
               for j in range(len(available))):
            print("WAIT: resources are not currently available")
            continue

        # Temporarily grant the request.
        old_available = available[:]
        old_allocation = [row[:] for row in allocation]
        old_need = [row[:] for row in need]

        available = [
            available[j] - request[j]
            for j in range(len(available))
        ]
        allocation[pid] = [
            allocation[pid][j] + request[j]
            for j in range(len(available))
        ]
        need[pid] = [
            need[pid][j] - request[j]
            for j in range(len(available))
        ]

        safe, sequence = is_safe(available, allocation, need)

        if safe:
            print("GRANTED: request is safe")
            print("Safe sequence:", " -> ".join(f"P{i}" for i in sequence))
        else:
            # Roll back all temporary changes.
            available = old_available
            allocation = old_allocation
            need = old_need
            print("DENIED: unsafe state; request rolled back")


if __name__ == "__main__":
    main()
