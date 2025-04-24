"""
# Event Loops
# ==========
#
# This tutorial explores event loops in Python's asyncio library.
# The event loop is the core of every asyncio application.
"""

import asyncio
import threading
import time


# What is an Event Loop?
# --------------------
# An event loop is the core component that executes asynchronous tasks and callbacks,
# handles network IO operations, and runs subprocesses.

def event_loop_overview():
    print("== Event Loop Overview ==")
    print("An event loop:")
    print("1. Manages and distributes the execution of different tasks")
    print("2. Handles I/O operations asynchronously")
    print("3. Executes callbacks when operations complete")
    print("4. Ensures tasks run in the correct order based on priorities and dependencies")
    print("5. Provides a way to schedule functions to run at a specific time")


# Getting the Event Loop
# --------------------

async def get_event_loop_example():
    print("\n== Getting the Event Loop ==")
    
    # In Python 3.7+, asyncio.get_event_loop() gets the running event loop
    # when called from a coroutine
    loop = asyncio.get_event_loop()
    print(f"Current event loop: {loop}")
    print(f"Is loop running: {loop.is_running()}")
    
    # You can also get the running loop with asyncio.get_running_loop()
    # (Python 3.7+)
    running_loop = asyncio.get_running_loop()
    print(f"Running loop: {running_loop}")
    print(f"Are they the same loop? {loop is running_loop}")


# Running the Event Loop
# --------------------

def run_event_loop_example():
    print("\n== Running the Event Loop ==")
    
    async def example_coroutine():
        print("Coroutine started")
        await asyncio.sleep(0.1)
        print("Coroutine finished")
        return "Coroutine result"
    
    print("Method 1: Using asyncio.run() (recommended for main entry point)")
    result = asyncio.run(example_coroutine())
    print(f"Result: {result}")
    
    print("\nMethod 2: Manually running the event loop (lower-level control)")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        print("Starting the event loop")
        result = loop.run_until_complete(example_coroutine())
        print(f"Result: {result}")
    finally:
        print("Closing the event loop")
        loop.close()


# Event Loop Methods
# ----------------

async def event_loop_methods():
    print("\n== Event Loop Methods ==")
    loop = asyncio.get_running_loop()
    
    # 1. Scheduling a callback
    print("1. Scheduling a callback to run soon")
    loop.call_soon(lambda: print("Callback executed"))
    
    # 2. Scheduling a callback with a delay
    print("2. Scheduling a delayed callback (0.5s)")
    loop.call_later(0.5, lambda: print("Delayed callback executed"))
    
    # 3. Scheduling a callback at a specific time
    now = loop.time()
    print(f"3. Scheduling a callback at a specific time ({now + 1.0})")
    loop.call_at(now + 1.0, lambda: print("Time-based callback executed"))
    
    # Wait for all scheduled callbacks to run
    await asyncio.sleep(1.1)


# Creating Tasks with the Event Loop
# --------------------------------

async def create_tasks_with_loop():
    print("\n== Creating Tasks with the Event Loop ==")
    loop = asyncio.get_running_loop()
    
    async def sample_coroutine(name, delay):
        print(f"{name} started")
        await asyncio.sleep(delay)
        print(f"{name} completed")
        return f"{name} result"
    
    # Create a task using the event loop directly (lower-level API)
    task = loop.create_task(sample_coroutine("Loop Task", 0.5))
    print(f"Task created: {task}")
    
    # Wait for the task to complete
    result = await task
    print(f"Task result: {result}")


# Event Loop and Threads
# --------------------
# The event loop runs in a single thread by default.
# Running event loops in different threads requires careful coordination.

def event_loop_in_thread():
    print("\n== Event Loop in Threads ==")
    
    def run_event_loop_in_thread():
        """Function to run an event loop in a separate thread"""
        print(f"Thread {threading.current_thread().name} starting")
        
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def thread_coroutine():
            print(f"Coroutine running in {threading.current_thread().name}")
            await asyncio.sleep(0.5)
            print(f"Coroutine in {threading.current_thread().name} completed")
            return "Thread coroutine result"
        
        # Run the coroutine in this thread's event loop
        result = loop.run_until_complete(thread_coroutine())
        print(f"Result in thread: {result}")
        
        # Clean up
        loop.close()
        print(f"Thread {threading.current_thread().name} ending")
    
    # Create and start a thread with its own event loop
    thread = threading.Thread(name="EventLoopThread", target=run_event_loop_in_thread)
    thread.start()
    
    # Wait for the thread to complete
    thread.join()
    print("Main thread continues after thread completes")


# Stopping and Closing Event Loops
# ------------------------------

def stopping_event_loop():
    print("\n== Stopping and Closing Event Loops ==")
    
    async def long_running_task():
        try:
            print("Long-running task started")
            while True:
                print("Task still running...")
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            print("Task was cancelled")
            raise
    
    async def stop_loop_after_delay(loop, delay):
        """Stops the event loop after a delay"""
        await asyncio.sleep(delay)
        print(f"Stopping the event loop after {delay}s")
        loop.stop()
    
    # Create a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Schedule the long-running task
    task = loop.create_task(long_running_task())
    
    # Schedule stopping the loop after a delay
    loop.create_task(stop_loop_after_delay(loop, 2.0))
    
    try:
        print("Starting the event loop")
        # run_forever() runs until loop.stop() is called
        loop.run_forever()
    finally:
        # Cancel any pending tasks
        print("Cancelling pending tasks...")
        task.cancel()
        
        # Run the event loop until the task is cancelled
        loop.run_until_complete(asyncio.gather(task, return_exceptions=True))
        
        print("Closing the event loop")
        loop.close()


# Debugging Event Loops
# -------------------

def debug_event_loop():
    print("\n== Debugging Event Loops ==")
    
    # Enable debug mode
    print("Enabling debug mode for asyncio")
    asyncio.get_event_loop().set_debug(True)
    
    # Show the effect of debug mode
    async def debug_example():
        # In debug mode, warnings are emitted for slow callbacks
        await asyncio.sleep(0.1)
        
        # Create a task that's never awaited (debug mode will warn about this)
        asyncio.create_task(asyncio.sleep(1.0))
        
        # Debug mode also enables more verbose exception handling
        await asyncio.sleep(0.1)
    
    print("Running with debug enabled (may show warnings)")
    asyncio.run(debug_example())
    
    print("\nDebug features include:")
    print("1. Warnings for slow callbacks (>100ms)")
    print("2. Resource tracking (detect unclosed resources)")
    print("3. Warnings for tasks destroyed while pending")
    print("4. More detailed logging information")


# Best Practices
# ------------

def best_practices():
    print("\n== Event Loop Best Practices ==")
    
    print("1. Use asyncio.run() as the main entry point for your application")
    print("2. Avoid creating multiple event loops in the same thread")
    print("3. Don't call blocking functions directly in coroutines")
    print("4. Use loop.run_in_executor() for CPU-bound or blocking operations")
    print("5. Always clean up resources with try/finally blocks")
    print("6. Enable debug mode during development to catch common mistakes")
    print("7. Be careful with synchronization between different event loops")


# Run all examples
if __name__ == "__main__":
    print("Event Loops\n")
    
    # Regular function examples
    event_loop_overview()
    run_event_loop_example()
    event_loop_in_thread()
    stopping_event_loop()
    debug_event_loop()
    best_practices()
    
    # Async function examples
    asyncio.run(get_event_loop_example())
    asyncio.run(event_loop_methods())
    asyncio.run(create_tasks_with_loop())
    
    print("\nNext tutorial: 5_async_io.py - File and network I/O operations") 