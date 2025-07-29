import asyncio
import aiohttp

urls = [
    "https://httpbin.org/get",
    "https://example.com",
    "https://www.google.com",
    "https://www.python.org",
    "https://www.wikipedia.org",
    "https://httpbin.org/uuid",
    "https://httpbin.org/ip",
    "https://httpbin.org/user-agent",
    "https://jsonplaceholder.typicode.com/posts/1",
    "https://jsonplaceholder.typicode.com/users/2",

    "https://httpbin.org/get",
    "https://example.com",
    "https://www.google.com",
    "https://www.python.org",
    "https://www.wikipedia.org",
    "https://httpbin.org/uuid",
    "https://httpbin.org/ip",
    "https://httpbin.org/user-agent",
    "https://jsonplaceholder.typicode.com/posts/1",
    "https://jsonplaceholder.typicode.com/users/2",

    "https://httpbin.org/get",
    "https://example.com",
    "https://www.google.com",
    "https://www.python.org",
    "https://www.wikipedia.org",
    "https://httpbin.org/uuid",
    "https://httpbin.org/ip",
    "https://httpbin.org/user-agent",
    "https://jsonplaceholder.typicode.com/posts/1",
    "https://jsonplaceholder.typicode.com/users/2"
]

async def publisher(queue, list_of_urls):
    for url in list_of_urls:
        print(f"Publishing URL: {url}")
        await queue.put(url)
    print("Published all URLs")

async def worker(queue):
    async with aiohttp.ClientSession() as session:
        while True:
            print("Worker waiting for URL...")
            url = await queue.get()
            print(f"Worker processing URL: {url}")
            try:
                async with session.get(url) as response:
                    content = await response.text()
                    print(f"Worker fetched {url}: Status {response.status}")
            except aiohttp.ClientError as e:
                print(f"Worker failed to fetch {url}: {e}")
            queue.task_done()

async def main():
    print("[MAIN] Starting")
    queue = asyncio.Queue()
    queue = asyncio.Queue(maxsize=3)  

    print("[MAIN] Creating publisher and workers")

    workers = [asyncio.create_task(worker(queue)) for _ in range(5)]
    publisher_task = asyncio.create_task(publisher(queue, urls))

    print("[MAIN] Awaiting queue.join()")
    await publisher_task
    await queue.join()

    print("[MAIN] Cancelling background tasks")
    publisher_task.cancel()
    for w in workers:
        w.cancel()

    print("[MAIN] All tasks completed.")

    print("All tasks completed.")

if __name__ == "__main__":
    asyncio.run(main())
