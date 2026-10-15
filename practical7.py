
import os
import time
import json
import ast
import operator
import socket
import multiprocessing as mp
from multiprocessing import shared_memory
from array import array

BASE = "/tmp"
REQ = BASE + "/pr7_requests.fifo"
SOCK = BASE + "/pr7_server.sock"

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def evaluate(expression):
    tree = ast.parse(expression, mode="eval")

    def calc(node):
        if isinstance(node, ast.Expression):
            return calc(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            return OPS[type(node.op)](calc(node.left), calc(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
            return OPS[type(node.op)](calc(node.operand))
        raise ValueError("Unsupported expression")

    return str(calc(tree))


# PART 1: FIFO CLIENT-SERVER

def fifo_server(count):
    print("FIFO server ready", flush=True)

    for _ in range(count):
        with open(REQ, "r") as f:
            data = json.loads(f.readline())

        answer = evaluate(data["expression"])

        with open(data["response"], "w") as f:
            f.write(answer + "\n")

    print("FIFO server finished", flush=True)


def fifo_client(expression, index):
    response = f"{BASE}/pr7_response_{os.getpid()}_{index}.fifo"
    os.mkfifo(response)

    fd = os.open(response, os.O_RDONLY | os.O_NONBLOCK)

    try:
        with open(REQ, "w") as f:
            f.write(json.dumps({
                "expression": expression,
                "response": response
            }) + "\n")

        result = ""
        deadline = time.monotonic() + 10

        while time.monotonic() < deadline:
            try:
                chunk = os.read(fd, 4096)
                if chunk:
                    result += chunk.decode()
                    if "\n" in result:
                        break
            except BlockingIOError:
                pass
            time.sleep(0.01)

        if "\n" not in result:
            raise TimeoutError("FIFO response timed out")

        print(f"FIFO: {expression} = {result.strip()}")

    finally:
        os.close(fd)
        os.unlink(response)


def run_fifo():
    if os.path.exists(REQ):
        os.unlink(REQ)
    os.mkfifo(REQ)

    server = mp.Process(target=fifo_server, args=(3,))
    server.start()
    time.sleep(0.3)

    try:
        for i, expression in enumerate(["12 + 8", "7 * 6", "100 / 4"]):
            fifo_client(expression, i)
    finally:
        server.join(timeout=12)
        if server.is_alive():
            server.terminate()
            server.join()
        if os.path.exists(REQ):
            os.unlink(REQ)

    print("FIFO test finished\n")


# PART 2: UNIX SOCKETS WITH MULTIPLE CLIENTS

def socket_handler(conn):
    try:
        data = conn.recv(4096).decode()
        expression = json.loads(data)["expression"]
        answer = evaluate(expression)
        conn.sendall(answer.encode())
    except Exception as error:
        conn.sendall(f"Error: {error}".encode())
    finally:
        conn.close()


def socket_server(count):
    if os.path.exists(SOCK):
        os.unlink(SOCK)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCK)
    server.listen(count)
    processes = []

    for _ in range(count):
        conn, _ = server.accept()
        process = mp.Process(target=socket_handler, args=(conn,))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

    server.close()
    if os.path.exists(SOCK):
        os.unlink(SOCK)


def socket_client(expression):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(SOCK)
    client.sendall(json.dumps({"expression": expression}).encode())
    answer = client.recv(4096).decode()
    print(f"Socket: {expression} = {answer}")
    client.close()


def run_socket():
    expressions = ["20 + 22", "9 * 9", "81 / 3"]

    server = mp.Process(target=socket_server, args=(len(expressions),))
    server.start()
    time.sleep(0.3)

    clients = []
    for expression in expressions:
        process = mp.Process(target=socket_client, args=(expression,))
        process.start()
        clients.append(process)

    for process in clients:
        process.join()

    server.join()
    print("Socket test finished\n")


# PART 3: SHARED MEMORY VS PIPE

def shared_memory_reader(name, count, result_queue):
    shm = shared_memory.SharedMemory(name=name)
    try:
        numbers = memoryview(shm.buf).cast("q")
        result_queue.put(sum(numbers[:count]))
        numbers.release()
    finally:
        shm.close()


def pipe_reader(conn):
    data = conn.recv_bytes()
    numbers = array("q")
    numbers.frombytes(data)
    conn.send(sum(numbers))
    conn.close()


def run_memory_test():
    count = 10**7
    numbers = array("q", range(count))
    expected = count * (count - 1) // 2
    print(f"Array size: {count:,} numbers")

    shm = shared_memory.SharedMemory(create=True, size=len(numbers) * numbers.itemsize)
    queue = mp.Queue()

    start = time.perf_counter()
    shm.buf[:] = memoryview(numbers).cast("B")
    process = mp.Process(
        target=shared_memory_reader,
        args=(shm.name, count, queue)
    )
    process.start()
    shm_result = queue.get()
    process.join()
    shm_time = time.perf_counter() - start
    shm.close()
    shm.unlink()

    parent, child = mp.Pipe()
    process = mp.Process(target=pipe_reader, args=(child,))

    start = time.perf_counter()
    process.start()
    child.close()
    parent.send_bytes(numbers.tobytes())
    pipe_result = parent.recv()
    process.join()
    pipe_time = time.perf_counter() - start
    parent.close()

    print(f"Expected sum: {expected}")
    print(f"Shared memory sum: {shm_result}, time: {shm_time:.4f} seconds")
    print(f"Pipe sum: {pipe_result}, time: {pipe_time:.4f} seconds")

    print("\nCOMPARISON TABLE")
    print("-" * 65)
    print(f"{'Mechanism':<20}{'Synchronization':<18}{'Data size':<12}{'Time (s)'}")
    print("-" * 65)
    print(f"{'FIFO':<20}{'No (basic)':<18}{'Small':<12}{'N/A'}")
    print(f"{'Unix socket':<20}{'No (basic)':<18}{'Small':<12}{'N/A'}")
    print(f"{'Shared memory':<20}{'Yes, if shared writes':<25}{'80 MB':<12}{shm_time:.4f}")print(f"{'Shared memory':<20}{'Yes, if shared writes':<18}{'80 MB':<12}{shm_time:.4f}")
    print(f"{'Pipe':<20}{'No (built-in)':<18}{'80 MB':<12}{pipe_time:.4f}")


if __name__ == "__main__":
    print("=== PRACTICAL WORK 7 — VARIANT B ===\n")
    run_fifo()
    run_socket()
    run_memory_test()
    print("\nPRACTICAL WORK 7 COMPLETED")
