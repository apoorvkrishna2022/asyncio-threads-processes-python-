"""
# Coroutines and Awaitables
# ========================
#
# This tutorial explores coroutines and awaitable objects in Python's asyncio.
"""

import asyncio
import inspect


# Coroutines
# ----------
# A coroutine is a specialized function that can pause execution and yield control
# back to the event loop while waiting for some operation to complete.

# Defining a coroutine with async def
async def simple_coroutine():
    """A simple coroutine that just returns a value"""
    return "I'm a coroutine!"


# Inspecting coroutines
def inspect_coroutine():
    print("== Coroutine Inspection ==")
    
    # Create a coroutine object (not executed yet)
    coro = simple_coroutine()
    
    print(f"Type of coroutine: {type(coro)}")
    print(f"Is coroutine: {inspect.iscoroutine(coro)}")
    print(f"Is coroutine function: {inspect.iscoroutinefunction(simple_coroutine)}")
    
    # Properly handle the coroutine to avoid warnings
    # Instead of calling close(), we can discard it or run it
    # Option 1: Just discard it and let Python garbage collect it
    # (This may generate a warning about a coroutine never being awaited)
    
    # Option 2: Run the coroutine immediately (better approach)
    print(f"Running the coroutine: {asyncio.run(simple_coroutine())}")
    
    # Create another coroutine for demonstration
    another_coro = simple_coroutine()
    # We need to handle this one too to avoid warnings
    asyncio.run(another_coro)


# Running a coroutine
async def run_coroutine_example():
    print("\n== Running Coroutines ==")
    
    # Three ways to run a coroutine:
    
    # 1. Using await (inside another coroutine)
    result = await simple_coroutine()
    print(f"Result from direct await: {result}")
    
    # 2. Using asyncio.create_task() to schedule it
    task = asyncio.create_task(simple_coroutine())
    result = await task
    print(f"Result from task: {result}")
    
    # 3. Using asyncio.gather() to run multiple coroutines
    results = await asyncio.gather(
        simple_coroutine(),
        simple_coroutine(),
        simple_coroutine()
    )
    print(f"Results from gather: {results}")


# Awaitables
# ----------
# Awaitable objects are objects that can be used with the await expression.
# There are three main types: coroutines, Tasks, and Futures.

async def awaitable_examples():
    print("\n== Awaitable Objects ==")
    
    # 1. Coroutine as awaitable
    print("1. Awaiting a coroutine:")
    result = await simple_coroutine()
    print(f"   Result: {result}")
    
    # 2. Task as awaitable
    print("\n2. Awaiting a task:")
    task = asyncio.create_task(simple_coroutine())
    result = await task
    print(f"   Result: {result}")
    
    # 3. Future as awaitable
    print("\n3. Awaiting a future:")
    # Create a Future object
    future = asyncio.Future()
    
    # Schedule a callback to set the future's result
    asyncio.create_task(set_future_result(future, "Future result"))
    
    # Await the future
    result = await future
    print(f"   Result: {result}")


async def set_future_result(future, result):
    """Helper function to set a future's result after a delay"""
    await asyncio.sleep(0.1)
    future.set_result(result)


# Chaining coroutines
# ------------------
# Coroutines can call other coroutines using the await keyword,
# creating a chain of operations.

async def chaining_example():
    print("\n== Chaining Coroutines ==")
    
    async def step1():
        print("Step 1 starting")
        await asyncio.sleep(0.5)
        print("Step 1 completed")
        return "Step 1 result"
    
    async def step2(step1_result):
        print("Step 2 starting with", step1_result)
        await asyncio.sleep(0.3)
        print("Step 2 completed")
        return "Step 2 result"
    
    async def step3(step2_result):
        print("Step 3 starting with", step2_result)
        await asyncio.sleep(0.2)
        print("Step 3 completed")
        return "Step 3 result"
    
    # Chain the coroutines together
    result1 = await step1()
    result2 = await step2(result1)
    final_result = await step3(result2)
    
    print(f"Final result: {final_result}")


# Common patterns
# --------------

async def common_patterns():
    print("\n== Common Coroutine Patterns ==")
    
    # 1. Sequential execution
    print("1. Sequential execution:")
    start = asyncio.get_event_loop().time()
    
    await asyncio.sleep(0.1)  # First operation
    await asyncio.sleep(0.1)  # Second operation
    await asyncio.sleep(0.1)  # Third operation
    
    print(f"   Sequential time: {asyncio.get_event_loop().time() - start:.2f}s")
    
    # 2. Concurrent execution
    print("\n2. Concurrent execution:")
    start = asyncio.get_event_loop().time()
    
    await asyncio.gather(
        asyncio.sleep(0.1),
        asyncio.sleep(0.1),
        asyncio.sleep(0.1)
    )
    
    print(f"   Concurrent time: {asyncio.get_event_loop().time() - start:.2f}s")
    
    # 3. Timeout pattern
    print("\n3. Using timeout:")
    try:
        # Try to run a coroutine with a timeout
        await asyncio.wait_for(asyncio.sleep(10), timeout=0.2)
    except asyncio.TimeoutError:
        print("   Operation timed out as expected")


# Run all examples
if __name__ == "__main__":
    print("Coroutines and Awaitables\n")
    
    # Regular function to look at coroutine properties
    inspect_coroutine()
    
    # Run all async examples
    asyncio.run(run_coroutine_example())
    asyncio.run(awaitable_examples())
    asyncio.run(chaining_example())
    asyncio.run(common_patterns())
    
    print("\nNext tutorial: 3_tasks.py - Working with Tasks and Futures") 