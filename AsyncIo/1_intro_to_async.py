"""
# Introduction to Asynchronous Programming
# ========================================
#
# This tutorial introduces the core concepts of asynchronous programming in Python.
"""

import asyncio
import time

# Synchronous vs Asynchronous Programming
# ---------------------------------------

# Example of synchronous code
def sync_example():
    print("== Synchronous Example ==")
    
    def task(name, duration):
        print(f"{name}: Starting task")
        time.sleep(duration)  # This blocks the entire program
        print(f"{name}: Finished after {duration} seconds")
        return f"{name} result"
    
    start = time.time()
    
    # Tasks run sequentially, each one waiting for the previous to complete
    result1 = task("Task 1", 2)
    result2 = task("Task 2", 1)
    result3 = task("Task 3", 3)
    
    print(f"All tasks completed in {time.time() - start:.2f} seconds")
    print(f"Results: {result1}, {result2}, {result3}")


# Example of asynchronous code
async def async_example():
    print("\n== Asynchronous Example ==")
    
    async def task(name, duration):
        print(f"{name}: Starting task")
        await asyncio.sleep(duration)  # This yields control back to the event loop
        print(f"{name}: Finished after {duration} seconds")
        return f"{name} result"
    
    start = time.time()
    
    # Run tasks concurrently
    # gather() collects multiple coroutines and runs them concurrently
    results = await asyncio.gather(
        task("Task 1", 2),
        task("Task 2", 1),
        task("Task 3", 3)
    )
    
    print(f"All tasks completed in {time.time() - start:.2f} seconds")
    print(f"Results: {results}")


# Key Concepts in AsyncIO
# ----------------------
def key_concepts():
    print("\n== Key Concepts in AsyncIO ==")
    print("1. Coroutines: Functions declared with 'async def' that can be paused and resumed")
    print("2. Awaitables: Objects that can be used with 'await' (coroutines, Tasks, Futures)")
    print("3. Event Loop: The core mechanism that manages and distributes tasks")
    print("4. Tasks: Wrappers around coroutines to track their execution")
    print("5. Futures: Objects representing results that will be available in the future")
    print("6. async/await: Syntax for defining and working with asynchronous code")


# When to Use AsyncIO
# ------------------
def when_to_use():
    print("\n== When to Use AsyncIO ==")
    print("AsyncIO is ideal for:")
    print("- I/O-bound operations (network requests, file operations)")
    print("- Concurrent operations where tasks spend time waiting")
    print("- Handling many connections simultaneously (web servers, chat apps)")
    print("\nAsyncIO is NOT ideal for:")
    print("- CPU-bound tasks (use multiprocessing instead)")
    print("- Simple sequential programs where concurrency isn't needed")
    print("- When synchronous code is easier to understand and maintain")


# Run the examples
if __name__ == "__main__":
    print("Introduction to Asynchronous Programming\n")
    
    # Run synchronous example
    sync_example()
    
    # Run asynchronous example
    asyncio.run(async_example())
    
    # Show key concepts and when to use
    key_concepts()
    when_to_use()
    
    print("\nNext tutorial: 2_coroutines.py - Understanding coroutines and awaitables") 