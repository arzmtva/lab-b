
import threading


class DeadlockError(Exception):
    pass


class TrackedLock:
    graph = {}
    graph_lock = threading.Lock()

    def __init__(self):
        self.lock = threading.Lock()
        self.owner = None

    def acquire(self):
        current = threading.current_thread()

        with TrackedLock.graph_lock:
            if self.owner is not None and self.owner != current:
                TrackedLock.graph.setdefault(current, set()).add(self.owner)

                if self.has_cycle():
                    TrackedLock.graph[current].discard(self.owner)
                    raise DeadlockError(
                        f"Deadlock detected: {current.name} "
                        f"waits for {self.owner.name}"
                    )

        self.lock.acquire()
        self.owner = current

        with TrackedLock.graph_lock:
            TrackedLock.graph.pop(current, None)

    def release(self):
        self.owner = None
        self.lock.release()

    @classmethod
    def has_cycle(cls):
        visited = set()
        active = set()

        def dfs(node):
            visited.add(node)
            active.add(node)

            for neighbor in cls.graph.get(node, set()):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in active:
                    return True

            active.remove(node)
            return False

        return any(
            dfs(node) for node in list(cls.graph)
            if node not in visited
        )


if __name__ == "__main__":
    lock1 = TrackedLock()
    lock2 = TrackedLock()
    barrier = threading.Barrier(2)

    def worker(first, second):
        first.acquire()
        print(threading.current_thread().name, "acquired first lock")

        barrier.wait()

        try:
            second.acquire()
            print(threading.current_thread().name, "acquired second lock")
            second.release()
        except DeadlockError as error:
            print("CAUGHT:", error)
        finally:
            first.release()

    t1 = threading.Thread(
        target=worker, args=(lock1, lock2), name="Thread-1"
    )
    t2 = threading.Thread(
        target=worker, args=(lock2, lock1), name="Thread-2"
    )

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    print("Test finished")
