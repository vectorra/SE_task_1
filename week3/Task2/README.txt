Async URL Publisher-Worker Pipeline
===================================

This script demonstrates an asynchronous producer-consumer model using Python's asyncio and aiohttp libraries.

Overview
--------
- A `publisher()` coroutine puts a list of URLs into an asyncio queue.
- Multiple `worker()` coroutines consume URLs from the queue, fetch their content using aiohttp, and print the HTTP status.
- The queue uses a `maxsize` to simulate backpressure and enforce concurrency.

Features
--------
- True concurrency between publisher and consumers.
- Bounded queue size to prevent publisher from flooding the queue.
- Multiple asynchronous workers handle requests concurrently.
- Designed to demonstrate async I/O for real-time or streaming data pipelines.