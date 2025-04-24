"""
# Asynchronous I/O Operations
# ==========================
#
# This tutorial explores file and network I/O operations with asyncio.
# Learn how to perform I/O operations without blocking the event loop.
"""

import asyncio
import aiofiles  # pip install aiofiles
import aiohttp   # pip install aiohttp
import os
import time
from concurrent.futures import ThreadPoolExecutor


# Why Use Async I/O?
# ----------------

def why_async_io():
    print("== Why Use Async I/O? ==")
    print("Benefits of asynchronous I/O:")
    print("1. Non-blocking - Other tasks can run while waiting for I/O")
    print("2. Higher throughput - Handle more connections simultaneously")
    print("3. Better resource utilization - Keep CPU busy during I/O waits")
    print("4. Simplified code - No need for complex threading or multiprocessing")
    print("5. Lower overhead - Fewer system resources compared to threads/processes")


# Asynchronous File I/O
# -------------------
# Regular file operations in Python are blocking. 
# The aiofiles library provides asynchronous file operations.

async def file_io_example():
    print("\n== Asynchronous File I/O ==")
    
    # Create a sample file
    sample_text = "This is a sample file for async I/O operations.\n" * 100
    
    # Write to a file asynchronously
    print("Writing to file asynchronously...")
    async with aiofiles.open("async_sample.txt", "w") as file:
        await file.write(sample_text)
    
    # Read from a file asynchronously
    print("Reading from file asynchronously...")
    async with aiofiles.open("async_sample.txt", "r") as file:
        content = await file.read(100)  # Read first 100 chars
        print(f"File content (first 100 chars): {content[:50]}...")
    
    # Read file line by line
    print("\nReading file line by line:")
    async with aiofiles.open("async_sample.txt", "r") as file:
        count = 0
        async for line in file:
            count += 1
            if count <= 3:  # Only show first 3 lines
                print(f"Line {count}: {line.strip()}")
        print(f"Total lines: {count}")


# Async vs Blocking File I/O
# ------------------------

async def compare_file_io():
    print("\n== Comparing Async vs Blocking File I/O ==")
    
    # Create a large sample file
    async with aiofiles.open("large_file.txt", "w") as file:
        await file.write("This is a sample line for testing I/O performance.\n" * 10000)
    
    print("Reading large file with different methods:")
    
    # Method 1: Blocking read (in the main thread)
    start = time.time()
    with open("large_file.txt", "r") as file:
        content = file.read()
    blocking_time = time.time() - start
    print(f"1. Blocking read: {blocking_time:.4f} seconds")
    
    # Method 2: Async read (single file)
    start = time.time()
    async with aiofiles.open("large_file.txt", "r") as file:
        content = await file.read()
    async_time = time.time() - start
    print(f"2. Async read (single file): {async_time:.4f} seconds")
    
    # Method 3: Multiple async reads (concurrent)
    start = time.time()
    async def read_portion(filename, start_pos, size):
        async with aiofiles.open(filename, "r") as file:
            await file.seek(start_pos)
            return await file.read(size)
    
    # Divide the file into chunks and read concurrently
    file_size = os.path.getsize("large_file.txt")
    chunk_size = file_size // 4
    
    tasks = [
        read_portion("large_file.txt", i * chunk_size, chunk_size)
        for i in range(4)
    ]
    
    results = await asyncio.gather(*tasks)
    concurrent_time = time.time() - start
    print(f"3. Concurrent async reads: {concurrent_time:.4f} seconds")
    
    # Method 4: ThreadPoolExecutor (for comparison)
    start = time.time()
    
    def blocking_read(filename, start_pos, size):
        with open(filename, "r") as file:
            file.seek(start_pos)
            return file.read(size)
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(blocking_read, "large_file.txt", i * chunk_size, chunk_size)
            for i in range(4)
        ]
        thread_results = [future.result() for future in futures]
    
    thread_pool_time = time.time() - start
    print(f"4. ThreadPoolExecutor: {thread_pool_time:.4f} seconds")


# HTTP Requests with aiohttp
# ------------------------
# aiohttp is an async HTTP client/server framework

async def http_requests_example():
    print("\n== Asynchronous HTTP Requests ==")
    
    # Make a single HTTP request
    print("Making a single HTTP request...")
    async with aiohttp.ClientSession() as session:
        async with session.get("https://httpbin.org/get") as response:
            print(f"Status: {response.status}")
            data = await response.json()
            print(f"Response headers: {list(data['headers'].keys())}")
    
    # Make multiple concurrent HTTP requests
    print("\nMaking multiple concurrent HTTP requests...")
    urls = [
        f"https://httpbin.org/delay/{i}"  # This endpoint delays the response
        for i in range(1, 4)
    ]
    
    async def fetch_url(session, url):
        start = time.time()
        async with session.get(url) as response:
            data = await response.json()
            duration = time.time() - start
            return {
                "url": url,
                "status": response.status,
                "duration": duration
            }
    
    # Sequential requests
    print("Sequential requests:")
    start = time.time()
    async with aiohttp.ClientSession() as session:
        results = []
        for url in urls:
            result = await fetch_url(session, url)
            results.append(result)
            print(f"  {result['url']} - {result['duration']:.2f}s")
        print(f"Total sequential time: {time.time() - start:.2f}s")
    
    # Concurrent requests
    print("\nConcurrent requests:")
    start = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        for result in results:
            print(f"  {result['url']} - {result['duration']:.2f}s")
        print(f"Total concurrent time: {time.time() - start:.2f}s")


# Streaming with aiohttp
# --------------------

async def streaming_example():
    print("\n== Streaming with aiohttp ==")
    
    # Download a large file, processing it in chunks
    print("Downloading and processing in chunks...")
    url = "https://httpbin.org/bytes/1024000"  # 1MB of random bytes
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                # Get total size if available
                content_length = response.headers.get("Content-Length")
                if content_length:
                    total_size = int(content_length)
                    print(f"Total size to download: {total_size} bytes")
                
                # Process the response in chunks
                chunk_size = 8192
                bytes_read = 0
                start = time.time()
                
                # Stream the response
                async for chunk in response.content.iter_chunked(chunk_size):
                    bytes_read += len(chunk)
                    # Simulate processing each chunk
                    if bytes_read % (chunk_size * 16) == 0:
                        print(f"Processed {bytes_read} bytes "
                              f"({bytes_read / total_size * 100:.1f}%)")
                
                duration = time.time() - start
                print(f"Download complete: {bytes_read} bytes in {duration:.2f}s "
                      f"({bytes_read / duration / 1024:.1f} KB/s)")


# Combining File and Network I/O
# ----------------------------

async def combined_io_example():
    print("\n== Combining File and Network I/O ==")
    
    # Download a file and save it asynchronously
    url = "https://httpbin.org/image/jpeg"  # Sample image
    filename = "downloaded_image.jpg"
    
    print(f"Downloading image from {url} and saving to {filename}...")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                # Open file for writing
                async with aiofiles.open(filename, "wb") as file:
                    # Stream directly from response to file
                    async for chunk in response.content.iter_chunked(8192):
                        await file.write(chunk)
                
                # Get file info
                file_size = os.path.getsize(filename)
                print(f"Download complete: {file_size} bytes saved to {filename}")
                
                # Read some metadata from the file
                async with aiofiles.open(filename, "rb") as file:
                    # Read the first 24 bytes (typically JPEG header)
                    header = await file.read(24)
                    print(f"File header (hex): {header.hex()[:20]}...")
            else:
                print(f"Error downloading file: {response.status}")


# Best Practices for Async I/O
# --------------------------

def best_practices():
    print("\n== Best Practices for Async I/O ==")
    
    print("1. Use appropriate libraries (aiofiles, aiohttp, etc.)")
    print("2. Don't mix blocking I/O with async code")
    print("3. For CPU-bound tasks, use executors (ThreadPoolExecutor, ProcessPoolExecutor)")
    print("4. Handle errors properly with try/except blocks")
    print("5. Use streaming for large files/responses")
    print("6. Be mindful of memory usage when working with large files")
    print("7. Set appropriate timeouts for network operations")
    print("8. Use connection pooling for multiple HTTP requests")
    print("9. Don't forget to close resources (use async with when possible)")


# Clean up
async def cleanup():
    """Clean up sample files created during the tutorial"""
    try:
        for filename in ["async_sample.txt", "large_file.txt", "downloaded_image.jpg"]:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"Removed {filename}")
    except Exception as e:
        print(f"Error during cleanup: {e}")


# Run all examples
if __name__ == "__main__":
    print("Asynchronous I/O Operations\n")
    
    # Regular function
    why_async_io()
    
    # Install required packages if not already installed
    print("\nNote: This tutorial requires the aiofiles and aiohttp packages.")
    print("If not installed, run: pip install aiofiles aiohttp\n")
    
    # Run async examples
    try:
        asyncio.run(file_io_example())
        asyncio.run(compare_file_io())
        asyncio.run(http_requests_example())
        asyncio.run(streaming_example())
        asyncio.run(combined_io_example())
        
        # Clean up sample files
        asyncio.run(cleanup())
    except ImportError as e:
        print(f"Error: {e}")
        print("Please install the required packages with: pip install aiofiles aiohttp")
    
    # Show best practices
    best_practices()
    
    print("\nNext tutorial: 6_async_with.py - Context managers with async/await") 