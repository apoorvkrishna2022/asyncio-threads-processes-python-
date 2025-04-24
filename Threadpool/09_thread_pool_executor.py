"""
# Python Threading Tutorial - ThreadPoolExecutor
# ===========================================
#
# This file demonstrates using ThreadPoolExecutor for managing pools of threads.
"""

import concurrent.futures
import threading
import time
import random
import requests
from concurrent.futures import ThreadPoolExecutor

def thread_pool_example():
    """
    Demonstrate using ThreadPoolExecutor.
    ThreadPoolExecutor is a high-level interface for asynchronously executing callables.
    """
    print("\n=== ThreadPoolExecutor ===")
    
    def task(n):
        """A task that returns a result after a delay."""
        thread_name = threading.current_thread().name
        print(f"Task {n} running in {thread_name}")
        time.sleep(random.uniform(0.5, 2.0))
        result = n * n
        print(f"Task {n} finished with result {result}")
        return result
    
    # Create a ThreadPoolExecutor with a maximum of 3 worker threads
    print("Creating a thread pool with 3 workers")
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit tasks to the executor
        futures = [executor.submit(task, i) for i in range(5)]
        
        # Wait for tasks to complete and get results
        print("Waiting for tasks to complete")
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                print(f"Task completed with result: {result}")
            except Exception as e:
                print(f"Task raised an exception: {e}")
    
    # The executor is automatically shut down when exiting the with block
    print("All tasks completed")
    
    # Using map to process items in parallel
    print("\nUsing executor.map():")
    with ThreadPoolExecutor(max_workers=3) as executor:
        numbers = [1, 2, 3, 4, 5]
        # Map applies the function to each item in the iterable in parallel
        results = list(executor.map(task, numbers))
        
        print(f"All results: {results}")
    
    # Real-world example: Downloading multiple web pages
    print("\nReal-world example: Downloading web pages")
    
    def download_page(url):
        """Download a web page and return its size."""
        thread_name = threading.current_thread().name
        print(f"{thread_name}: Downloading {url}")
        
        try:
            # Send a GET request
            response = requests.get(url, timeout=5)
            
            # Get the page size
            page_size = len(response.content)
            
            print(f"{thread_name}: Downloaded {url} ({page_size} bytes)")
            return url, page_size
        
        except Exception as e:
            print(f"{thread_name}: Error downloading {url}: {e}")
            return url, 0
    
    # List of URLs to download
    urls = [
        "https://www.example.com",
        "https://www.python.org",
        "https://httpbin.org/get",
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://httpbin.org/status/200"
    ]
    
    # Download pages concurrently
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit download tasks
        future_to_url = {executor.submit(download_page, url): url for url in urls}
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                url, size = future.result()
                print(f"Result summary: {url} - {size} bytes")
            except Exception as e:
                print(f"Error processing result for {url}: {e}")
    
    # Combining results with callbacks
    print("\nUsing callbacks with futures:")
    
    def process_result(future):
        """Process the result of a completed future."""
        try:
            url, size = future.result()
            print(f"Callback: Processed result for {url} - {size} bytes")
        except Exception as e:
            print(f"Callback: Error processing result: {e}")
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Submit tasks and add callbacks
        for url in urls[:3]:  # Just use the first 3 URLs
            future = executor.submit(download_page, url)
            future.add_done_callback(process_result)
        
        print("Main thread continues while tasks run in background")
        time.sleep(0.5)  # Do other work in the main thread
    
    print("\nAdvantages of ThreadPoolExecutor:")
    print("1. Simple, high-level interface")
    print("2. Automatic thread management")
    print("3. Task queuing and load balancing")
    print("4. Exception handling")
    print("5. Clean resource management")
    print("6. Support for callbacks")
    print("7. Compatible with context managers (with statement)")

if __name__ == "__main__":
    thread_pool_example() 