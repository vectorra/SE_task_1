HTTP Request Benchmark Script
=============================

This script sends HTTP requests using:

1. Single-threaded loop
2. Python threads
3. Python processes
4. Async with asyncio

Each method sends 5 requests to https://httpbin.org/get and shows how long it takes.