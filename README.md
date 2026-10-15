# Lab B

## Practical Work 6 — Synchronization
**Variant B**

### Objective
To study synchronization using mutexes, semaphores, and condition variables.

### Tasks
1. Producer-consumer using semaphores and a mutex.
2. Producer-consumer using a mutex and condition variable.
3. Barrier synchronization for four threads and three phases.
4. Demonstration of unsafe use of if instead of while.

### Configuration
- Producers: 3
- Consumers: 2
- Buffer capacity: 5
- Items processed: 1000

### Results
- Semaphore implementation: PASS
- Condition variable implementation: PASS
- 1000 unique items consumed exactly once in both tests
- No missing or duplicate items
- Barrier test: PASS
- Unsafe if demonstration: BUG DEMONSTRATED

### Run
```bash
python3 practical6.py
