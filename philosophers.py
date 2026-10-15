
import threading
import time
import random

N = 5
MEALS = 5


def run_philosophers(mode):
    forks = [threading.Lock() for _ in range(N)]
    meals = [0] * N
    barrier = threading.Barrier(N) if mode == "deadlock" else None
    room = threading.Semaphore(N - 1)

    def philosopher(i):
        left = i
        right = (i + 1) % N

        for _ in range(MEALS):
            time.sleep(random.uniform(0.001, 0.01))

            if mode == "limit":
                room.acquire()

            # Force the deadlock scenario for demonstration.
            if mode == "deadlock":
                forks[left].acquire()
                print(f"Philosopher {i} took fork {left}")
                barrier.wait()
                forks[right].acquire()

            elif mode == "numbering":
                first, second = sorted((left, right))
                forks[first].acquire()
                forks[second].acquire()

            elif mode == "limit":
                forks[left].acquire()
                forks[right].acquire()

            meals[i] += 1
            print(f"Philosopher {i} ate meal {meals[i]}")

            forks[left].release() if mode != "numbering" else None

            if mode == "numbering":
                forks[max(left, right)].release()
                forks[min(left, right)].release()
            else:
                forks[right].release()

            if mode == "limit":
                room.release()

    threads = [
        threading.Thread(target=philosopher, args=(i,))
        for i in range(N)
    ]

    for t in threads:
        t.start()

    if mode == "deadlock":
        for t in threads:
            t.join(timeout=2)
        print("\nDeadlock demonstration: threads may remain blocked.")
        print("Meals:", meals)
        return

    for t in threads:
        t.join()

    print("\nStatistics:", mode)
    for i, count in enumerate(meals):
        print(f"Philosopher {i}: ate {count} times")


if __name__ == "__main__":
    print("1 - Original deadlock")
    print("2 - Fork numbering solution")
    print("3 - Limit philosophers at table")

    choice = input("Choose 1, 2, or 3: ").strip()

    if choice == "1":
        run_philosophers("deadlock")
    elif choice == "2":
        run_philosophers("numbering")
    elif choice == "3":
        run_philosophers("limit")
    else:
        print("Invalid choice")
