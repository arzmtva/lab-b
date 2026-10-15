# Practical Work 4 — Multithreading and Multiprocessing

## Objective
Compare sequential execution, multithreading, and multiprocessing in Python.

## Tasks
- Calculate the sum of one million numbers using three methods.
- Download 20 URLs sequentially, using `ThreadPoolExecutor`, and using `ProcessPoolExecutor`.
- Compare execution times using the median of three runs.
- Check how threads and processes handle shared memory.

## Results

### 1. Sum of Numbers

| Method | Median Time (seconds) |
|---|---:|
| Sequential | 0.0050 |
| 4 Threads | 0.0151 |
| 4 Processes | 0.0816 |

The sum was `500000500000` for all three methods.

### 2. Downloading URLs

| Method | Successfully Downloaded | Median Time (seconds) |
|---|---:|---:|
| Sequential | 15/20 | 13.3900 |
| ThreadPoolExecutor | 15/20 | 5.3409 |
| ProcessPoolExecutor | 15/20 | 5.3720 |

### 3. Memory Test

- **Thread:** The parent list contained `['thread']` after the thread modified it.
- **Process:** The parent list remained `[]` after the child process modified its own copy.

## Conclusion
Sequential execution was fastest for summing numbers because the calculation was simple and the overhead of threads and processes outweighed their benefits. For downloading URLs, concurrent execution was faster. Threads are useful for I/O-bound tasks, while processes provide separate memory spaces and can help with CPU-bound work. Actual performance depends on the task and system.

## Files
- `practical4.py` — Python implementation.
- `numbers.txt` — Input data containing one million numbers.Права каталога: drwxrwxr-x.

