
def detect_deadlock(events):
    # Graph: process -> process it is waiting for
    graph = {}
    waiting = {}
    owners = {}

    for event in events:
        parts = event.split()

        if len(parts) != 2:
            continue

        action, resource = parts
        process = None

        # Events: acquire P1 R1, release P1 R1, wait P1 R1
        if action in ("acquire", "release", "wait"):
            # Correct format has three fields, handled below
            continue

    graph = {}
    owners = {}
    waiting = {}

    for event in events:
        parts = event.split()

        if len(parts) != 3:
            continue

        action, process, resource = parts

        if action == "acquire":
            if resource not in owners:
                owners[resource] = process
            elif owners[resource] != process:
                waiting[process] = resource

        elif action == "wait":
            waiting[process] = resource

        elif action == "release":
            if owners.get(resource) == process:
                del owners[resource]
                waiting.pop(process, None)

    for process, resource in waiting.items():
        owner = owners.get(resource)
        if owner is not None and owner != process:
            graph.setdefault(process, []).append(owner)

    visited = set()
    active = set()
    path = []

    def dfs(process):
        visited.add(process)
        active.add(process)
        path.append(process)

        for neighbor in graph.get(process, []):
            if neighbor not in visited:
                result = dfs(neighbor)
                if result:
                    return result
            elif neighbor in active:
                index = path.index(neighbor)
                return path[index:] + [neighbor]

        path.pop()
        active.remove(process)
        return None

    for process in graph:
        if process not in visited:
            cycle = dfs(process)
            if cycle:
                print("DEADLOCK DETECTED!")
                print("Cycle:", " -> ".join(cycle))
                print("Participants:", ", ".join(cycle[:-1]))
                return

    print("No deadlock detected.")


if __name__ == "__main__":
    print("Enter events: acquire/release/wait PROCESS RESOURCE")
    print("Example: acquire P1 R1")
    print("Type END to finish input.")

    events = []
    while True:
        try:
            line = input()
        except EOFError:
            break

        if line.strip().upper() == "END":
            break

        if line.strip():
            events.append(line.strip())

    detect_deadlock(events)
