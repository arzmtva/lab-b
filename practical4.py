import time
import statistics
import threading
import multiprocessing
import urllib.request
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def split_data(data):
    n = len(data)
    return [data[i*n//4:(i+1)*n//4] for i in range(4)]

def sequential_sum(data):
    return sum(data)

def threaded_sum(data):
    parts = split_data(data)
    results = [0] * 4
    def worker(i):
        results[i] = sum(parts[i])
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return sum(results)

def process_worker(data):
    return sum(data)

def process_sum(data):
    with multiprocessing.Pool(4) as pool:
        return sum(pool.map(process_worker, split_data(data)))

URLS = [
    "https://example.com", "https://www.python.org",
    "https://www.wikipedia.org", "https://www.github.com",
    "https://www.mozilla.org", "https://www.gnu.org",
    "https://pypi.org", "https://www.ubuntu.com",
    "https://www.nasa.gov", "https://www.w3.org",
    "https://www.apple.com", "https://www.microsoft.com",
    "https://www.djangoproject.com", "https://www.linux.org",
    "https://www.google.com", "https://www.bbc.com",
    "https://www.reddit.com", "https://stackoverflow.com",
    "https://www.python.org", "https://example.com"
]

def download(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            return len(response.read())
    except Exception:
        return 0

def sequential_download(urls):
    return [download(url) for url in urls]

def threaded_download(urls):
    with ThreadPoolExecutor(max_workers=4) as executor:
        return list(executor.map(download, urls))

def process_download(urls):
    with ProcessPoolExecutor(max_workers=4) as executor:
        return list(executor.map(download, urls))

def measure(name, function, data, is_sum=False):
    times = []
    result = None
    for _ in range(3):
        start = time.perf_counter()
        result = function(data)
        times.append(time.perf_counter() - start)
    print("\n" + name)
    if is_sum:
        print("Сумма:", result)
    else:
        print("Успешно загружено:", sum(x > 0 for x in result), "/20")
    print("3 измерения:", [round(x, 4) for x in times])
    print("Медиана:", round(statistics.median(times), 4), "секунд")

shared_list = []

def thread_change():
    shared_list.append("thread")

def process_change(data):
    data.append("process")

if __name__ == "__main__":
    print("ПРАКТИЧЕСКАЯ РАБОТА №4")
    with open("numbers.txt") as f:
        numbers = [int(x.strip()) for x in f if x.strip()]
    print("Количество чисел:", len(numbers))

    print("\n1. СУММА ЧИСЕЛ")
    measure("Последовательно", sequential_sum, numbers, True)
    measure("4 потока", threaded_sum, numbers, True)
    measure("4 процесса", process_sum, numbers, True)

    print("\n2. ЗАГРУЗКА 20 URL")
    measure("Последовательно", sequential_download, URLS)
    measure("ThreadPoolExecutor", threaded_download, URLS)
    measure("ProcessPoolExecutor", process_download, URLS)

    print("\n4. ПРОВЕРКА ПАМЯТИ")
    shared_list.clear()
    t = threading.Thread(target=thread_change)
    t.start()
    t.join()
    print("После потока:", shared_list)

    shared_list.clear()
    p = multiprocessing.Process(target=process_change, args=(shared_list,))
    p.start()
    p.join()
    print("После процесса:", shared_list)
    print("\nРАБОТА ЗАВЕРШЕНА")
