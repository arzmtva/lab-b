
import threading
import time
from collections import Counter

TOTAL = 1000
BUFFER_SIZE = 5
PRODUCERS = 3
CONSUMERS = 2


# ==================================================
# 1A. PRODUCER-CONSUMER: SEMAPHORES + MUTEX
# ==================================================

def producer_consumer_semaphores():
    print("\n=== 1A. SEMAPHORES + MUTEX ===")

    buffer = []
    mutex = threading.Lock()
    empty = threading.Semaphore(BUFFER_SIZE)
    full = threading.Semaphore(0)

    consumed = []
    errors = []
    produced_count = 0

    def producer(producer_id):
        nonlocal produced_count

        for number in range(producer_id, TOTAL, PRODUCERS):
            empty.acquire()

            with mutex:
                if len(buffer) >= BUFFER_SIZE:
                    errors.append("Buffer overflow!")
                buffer.append(number)
                produced_count += 1

            full.release()

    def consumer():
        while True:
            full.acquire()

            with mutex:
                item = buffer.pop(0)

            empty.release()

            if item is None:
                break

            consumed.append(item)

    producer_threads = [
        threading.Thread(target=producer, args=(i,))
        for i in range(PRODUCERS)
    ]

    consumer_threads = [
        threading.Thread(target=consumer)
        for _ in range(CONSUMERS)
    ]

    for t in consumer_threads + producer_threads:
        t.start()

    for t in producer_threads:
        t.join()

    # Stop both consumers using sentinel values.
    for _ in range(CONSUMERS):
        empty.acquire()
        with mutex:
            buffer.append(None)
        full.release()

    for t in consumer_threads:
        t.join()

    counts = Counter(consumed)
    duplicates = [x for x, n in counts.items() if n > 1]
    missing = set(range(TOTAL)) - set(consumed)
    unexpected = set(consumed) - set(range(TOTAL))

    print("Produced:", produced_count)
    print("Consumed:", len(consumed))
    print("Unique items:", len(counts))
    print("Duplicates:", len(duplicates))
    print("Missing items:", len(missing))
    print("Unexpected items:", len(unexpected))
    print("Errors:", errors)

    if (len(consumed) == TOTAL and len(counts) == TOTAL
            and not missing and not unexpected and not errors):
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")


# ==================================================
# 1B. PRODUCER-CONSUMER: CONDITION + MUTEX
# ==================================================

def producer_consumer_condition():
    print("\n=== 1B. CONDITION + MUTEX ===")

    buffer = []
    condition = threading.Condition()
    consumed = []
    errors = []
    produced_count = 0

    def producer(producer_id):
        nonlocal produced_count

        for number in range(producer_id, TOTAL, PRODUCERS):
            with condition:
                while len(buffer) >= BUFFER_SIZE:
                    condition.wait()

                buffer.append(number)
                produced_count += 1
                condition.notify_all()

    def consumer():
        while True:
            with condition:
                while not buffer:
                    condition.wait()

                item = buffer.pop(0)
                condition.notify_all()

            if item is None:
                break

            consumed.append(item)

    producer_threads = [
        threading.Thread(target=producer, args=(i,))
        for i in range(PRODUCERS)
    ]

    consumer_threads = [
        threading.Thread(target=consumer)
        for _ in range(CONSUMERS)
    ]

    for t in consumer_threads + producer_threads:
        t.start()

    for t in producer_threads:
        t.join()

    with condition:
        for _ in range(CONSUMERS):
            while len(buffer) >= BUFFER_SIZE:
                condition.wait()

            buffer.append(None)
            condition.notify_all()

    for t in consumer_threads:
        t.join()

    counts = Counter(consumed)
    duplicates = [x for x, n in counts.items() if n > 1]
    missing = set(range(TOTAL)) - set(consumed)
    unexpected = set(consumed) - set(range(TOTAL))

    print("Produced:", produced_count)
    print("Consumed:", len(consumed))
    print("Unique items:", len(counts))
    print("Duplicates:", len(duplicates))
    print("Missing items:", len(missing))
    print("Unexpected items:", len(unexpected))
    print("Errors:", errors)

    if (len(consumed) == TOTAL and len(counts) == TOTAL
            and not missing and not unexpected and not errors):
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")


# ==================================================
# 2. BARRIER: FOUR THREADS, THREE PHASES
# ==================================================

def barrier_demo():
    print("\n=== 2. BARRIER: 4 THREADS, 3 PHASES ===")

    participants = 4
    barrier = threading.Condition()
    arrived = 0
    phase = 0

    def worker(worker_id):
        nonlocal arrived, phase

        for current_phase in range(1, 4):
            print(f"Thread {worker_id}: phase {current_phase} work")

            with barrier:
                my_phase = phase
                arrived += 1

                if arrived == participants:
                    arrived = 0
                    phase += 1
                    barrier.notify_all()
                else:
                    while phase == my_phase:
                        barrier.wait()

            print(f"Thread {worker_id}: passed phase {current_phase}")

    threads = [
        threading.Thread(target=worker, args=(i,))
        for i in range(1, participants + 1)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print("Barrier test completed: PASS")


# ==================================================
# 3. DEMONSTRATE WHY IF INSTEAD OF WHILE IS UNSAFE
# ==================================================

def lost_wakeup_demo():
    print("\n=== 3. UNSAFE IF INSTEAD OF WHILE ===")

    condition = threading.Condition()
    buffer = []
    errors = []

    def unsafe_consumer(consumer_id):
        with condition:
            # INTENTIONALLY WRONG: should use while, not if.
            if not buffer:
                condition.wait()

            # Another consumer may already have removed the item.
            if not buffer:
                errors.append(
                    f"Consumer {consumer_id}: woke up, but buffer is empty!"
                )
                print(errors[-1])
                return

            item = buffer.pop(0)
            print(f"Consumer {consumer_id} consumed {item}")

    # Both consumers wait for an item.
    consumers = [
        threading.Thread(target=unsafe_consumer, args=(i,))
        for i in (1, 2)
    ]

    for t in consumers:
        t.start()

    time.sleep(0.2)

    # Add only one item and wake both consumers.
    with condition:
        buffer.append(42)
        condition.notify_all()

    for t in consumers:
        t.join()

    if errors:
        print("BUG DEMONSTRATED: if is unsafe.")
    else:
        print("No error observed this time; scheduling can vary.")


# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":
    producer_consumer_semaphores()
    producer_consumer_condition()
    barrier_demo()
    lost_wakeup_demo()
