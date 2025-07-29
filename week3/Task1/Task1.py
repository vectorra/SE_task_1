import threading
import time
import requests
import multiprocessing
import asyncio

async def request_URL_async():
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, requests.get, "https://httpbin.org/get")
    return f"Async Process: Status {response.status_code}"

async def run_async_tasks(num_tasks):
    tasks = [request_URL_async() for _ in range(num_tasks)]
    return await asyncio.gather(*tasks)


def request_URL(i):
    response = requests.get("https://httpbin.org/get")
    return f"Process {i}: Status {response.status_code}"

def run_processes(num_processes):
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.map(request_URL, range(num_processes))
    return results


def run_threads(num_threads):
    threads = []
    results = [None] * num_threads

    def thread_target(i):
        result = request_URL(i)
        results[i] = result

    for i in range(num_threads):
        thread = threading.Thread(target=thread_target, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return results


if __name__ == "__main__":
    num_tasks = 5


    # --- Single-threaded (blocking) ---
    print("Single-threaded Results:")
    num_requests = 5
    time_start = time.time()
    for _ in range(num_requests):
        response = requests.get("https://httpbin.org/get")
        print(f"Single-threaded: Status {response.status_code}")
    time_end = time.time()
    print(f"Single-threaded: {num_requests} requests completed in {time_end - time_start:.2f} seconds\n")
    # --- Threading ---
    print("Threading Results:")
    time_start = time.time()
    thread_results = run_threads(num_tasks)
    time_end = time.time()
    print("\n".join(thread_results))
    print(f"Threads: {len(thread_results)} results in {time_end - time_start:.2f} seconds\n")

    # --- Multiprocessing ---
    print("Multiprocessing Results:")
    time_start = time.time()
    process_results = run_processes(num_tasks)
    time_end = time.time()
    print("\n".join(process_results))
    print(f"Processes: {len(process_results)} results in {time_end - time_start:.2f} seconds\n")

    # --- Async ---
    print("Async Results:")
    time_start = time.time()
    async_results = asyncio.run(run_async_tasks(num_tasks))
    time_end = time.time()
    print("\n".join(async_results))
    print(f"Async: {len(async_results)} tasks completed in {time_end - time_start:.2f} seconds")
