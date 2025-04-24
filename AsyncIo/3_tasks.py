"""
# Tasks and Futures
# ================
#
# This tutorial explores Tasks and Futures in Python's asyncio library.
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor


# Tasks
# -----
# Tasks are used to schedule coroutines concurrently.
# A Task is a subclass of Future that wraps a coroutine.

async def task_basics():
    print("== Task Basics ==")
    
    async def sample_coroutine(name, delay):
        print(f"{name} starting")
        await asyncio.sleep(delay)
        print(f"{name} completed after {delay}s")
        return f"{name} result"
    
    # Create a task from a coroutine
    task1 = asyncio.create_task(
        sample_coroutine("Task 1", 1.0),
        name="task1"  # Optional name for the task
    )
    
    # Tasks start executing as soon as they're created
    print(f"Task created: {task1.get_name()}")
    print(f"Is task done? {task1.done()}")
    
    # We can await the task to get its result
    result = await task1
    print(f"Task result: {result}")
    print(f"Is task done now? {task1.done()}")


# Managing multiple tasks
async def managing_tasks():
    print("\n== Managing Multiple Tasks ==")
    
    async def work(name, delay):
        print(f"{name} starting")
        await asyncio.sleep(delay)
        print(f"{name} completed after {delay}s")
        return f"{name} result"
    
    # Create multiple tasks
    tasks = [
        asyncio.create_task(work(f"Task {i}", i * 0.5))
        for i in range(1, 5)
    ]
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)
    print(f"All tasks completed with results: {results}")
    
    # Create more tasks
    task_a = asyncio.create_task(work("Task A", 0.5))
    task_b = asyncio.create_task(work("Task B", 1.0))
    task_c = asyncio.create_task(work("Task C", 1.5))
    
    # Wait for the first task to complete
    done, pending = await asyncio.wait(
        [task_a, task_b, task_c],
        return_when=asyncio.FIRST_COMPLETED
    )
    
    print(f"Completed tasks: {len(done)}")
    print(f"Pending tasks: {len(pending)}")
    
    # Wait for remaining tasks with a timeout
    try:
        done, pending = await asyncio.wait(
            pending,
            timeout=0.6  # Wait for at most 0.6 seconds
        )
        print(f"After timeout: {len(done)} completed, {len(pending)} pending")
    except asyncio.TimeoutError:
        print("Timeout occurred")
    
    # Cancel remaining tasks
    for task in pending:
        task.cancel()
    
    # Wait for all tasks to complete (including cancelled ones)
    await asyncio.gather(*pending, return_exceptions=True)
    print("All tasks are now done or cancelled")


# Task callbacks
async def task_callbacks():
    print("\n== Task Callbacks ==")
    
    def callback(task):
        """This function is called when the task completes"""
        print(f"Callback called for {task.get_name()}")
        try:
            result = task.result()
            print(f"Task result in callback: {result}")
        except Exception as e:
            print(f"Task raised an exception: {e}")
    
    async def callback_coroutine(name, delay):
        print(f"{name} starting")
        await asyncio.sleep(delay)
        print(f"{name} completed")
        return f"{name} result"
    
    # Create a task and add a callback
    task = asyncio.create_task(
        callback_coroutine("Callback Task", 0.5),
        name="callback_task"
    )
    
    # Add callback to the task
    task.add_done_callback(callback)
    
    # Wait for the task to complete
    await task
    print("Main coroutine continued after task completion")


# Futures
# -------
# Futures represent the eventual result of an asynchronous operation.
# Tasks are a subclass of Future specifically for coroutines.

async def future_basics():
    print("\n== Future Basics ==")
    
    # Create a Future object
    future = asyncio.Future()
    
    print(f"Is future done? {future.done()}")
    
    # Schedule a coroutine to set the future's result
    asyncio.create_task(set_future_result(future, "Future result value", 0.5))
    
    # Wait for the future to have a result
    result = await future
    
    print(f"Future result: {result}")
    print(f"Is future done now? {future.done()}")


async def set_future_result(future, result, delay):
    """Helper function to set a future's result after a delay"""
    print(f"Setting future result in {delay}s")
    await asyncio.sleep(delay)
    print("Setting future result now")
    future.set_result(result)


# Working with ThreadPoolExecutor
async def thread_pool_executor():
    print("\n== Using ThreadPoolExecutor with asyncio ==")
    
    def blocking_io(delay):
        """This is a blocking function that would normally block the event loop"""
        print(f"Blocking operation starting")
        time.sleep(delay)  # This is a blocking call
        print(f"Blocking operation complete after {delay}s")
        return f"Result after {delay}s"
    
    print("Running blocking function in a thread pool")
    
    # Create a thread pool executor
    with ThreadPoolExecutor() as pool:
        # Run the blocking function in the thread pool
        # run_in_executor returns a Future that we can await
        result = await asyncio.get_event_loop().run_in_executor(
            pool, blocking_io, 1.0
        )
        
        print(f"Thread pool executor result: {result}")


# Error handling with Tasks and Futures
async def error_handling():
    print("\n== Error Handling with Tasks and Futures ==")
    
    async def successful_coroutine():
        await asyncio.sleep(0.2)
        return "Success"
    
    async def failing_coroutine():
        await asyncio.sleep(0.2)
        raise ValueError("Something went wrong")
    
    # Method 1: Try/except with await
    print("Method 1: Using try/except with await")
    try:
        task = asyncio.create_task(failing_coroutine())
        result = await task
    except ValueError as e:
        print(f"Caught exception: {e}")
    
    # Method 2: gather with return_exceptions
    print("\nMethod 2: Using gather with return_exceptions=True")
    results = await asyncio.gather(
        successful_coroutine(),
        failing_coroutine(),
        return_exceptions=True
    )
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Task {i+1} failed with: {result}")
        else:
            print(f"Task {i+1} succeeded with: {result}")
    
    # Method 3: Wait for task completion and check for exceptions
    print("\nMethod 3: Check for exceptions after task completes")
    task = asyncio.create_task(failing_coroutine())
    
    # Wait for the task to complete
    await asyncio.sleep(0.3)
    
    if task.done():
        if task.exception() is not None:
            print(f"Task failed with exception: {task.exception()}")
        else:
            print(f"Task succeeded with result: {task.result()}")


# Run all examples
if __name__ == "__main__":
    print("Tasks and Futures\n")
    
    asyncio.run(task_basics())
    asyncio.run(managing_tasks())
    asyncio.run(task_callbacks())
    asyncio.run(future_basics())
    asyncio.run(thread_pool_executor())
    asyncio.run(error_handling())
    
    print("\nNext tutorial: 4_event_loops.py - Event loops and their management") 