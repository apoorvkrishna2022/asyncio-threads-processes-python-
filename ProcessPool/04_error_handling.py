#!/usr/bin/env python3
"""
04_error_handling.py - Handling errors in process pools

This file covers:
- Handling exceptions in worker processes
- Different error handling strategies
- Timeouts and cancellation
- Graceful error recovery
"""

import time
import random
import traceback
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor


def task_that_might_fail(task_id):
    """
    A function that might randomly fail to demonstrate error handling.
    
    Args:
        task_id: An identifier for the task
        
    Returns:
        A string with the task result
        
    Raises:
        ValueError: Randomly raised to simulate errors
        ZeroDivisionError: Randomly raised to simulate errors
    """
    # Simulate some work
    time.sleep(random.uniform(0.1, 0.5))
    
    # Randomly fail with different types of exceptions
    random_value = random.random()
    
    if random_value < 0.2:  # 20% chance of ValueError
        raise ValueError(f"Task {task_id} failed with ValueError")
    elif random_value < 0.3:  # 10% chance of ZeroDivisionError
        # Deliberate division by zero to demonstrate exception
        return task_id / 0
    
    # Otherwise succeed
    return f"Task {task_id} completed successfully"


def task_with_timeout(seconds):
    """
    A function that sleeps for the specified number of seconds.
    Used to demonstrate timeout handling.
    """
    time.sleep(seconds)
    return f"Slept for {seconds} seconds"


def main():
    """Main function demonstrating error handling in process pools."""
    print("=== Error Handling in Process Pools ===\n")
    
    # SECTION 1: Basic error handling with map()
    print("SECTION 1: Basic Error Handling with map()")
    print("When using map(), exceptions are raised when retrieving results.")
    
    tasks = list(range(10))  # Create 10 tasks
    
    print("\nRunning tasks with map():")
    with ProcessPoolExecutor() as executor:
        results = executor.map(task_that_might_fail, tasks)
        
        # Process results and catch exceptions
        for i, result in enumerate(results):
            try:
                print(f"  Task {i}: {result}")
            except Exception as e:
                print(f"  Task {i} failed: {type(e).__name__}: {e}")
    
    # SECTION 2: Error handling with submit() and as_completed()
    print("\nSECTION 2: Error Handling with submit() and as_completed()")
    print("When using submit(), exceptions are wrapped in the Future object.")
    
    print("\nRunning tasks with submit() and as_completed():")
    with ProcessPoolExecutor() as executor:
        # Submit all tasks
        future_to_task = {executor.submit(task_that_might_fail, i): i for i in tasks}
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_task):
            task_id = future_to_task[future]
            try:
                result = future.result()
                print(f"  Task {task_id}: {result}")
            except Exception as e:
                print(f"  Task {task_id} failed: {type(e).__name__}: {e}")
    
    # SECTION 3: Getting the full traceback
    print("\nSECTION 3: Getting the Full Traceback")
    print("ProcessPoolExecutor preserves the original exception traceback.")
    
    print("\nDisplaying full exception tracebacks:")
    with ProcessPoolExecutor() as executor:
        future = executor.submit(task_that_might_fail, 999)  # Just one task
        
        try:
            result = future.result()
            print(f"  Result: {result}")
        except Exception as e:
            print(f"  Exception type: {type(e).__name__}")
            print(f"  Exception message: {e}")
            print("\n  Full traceback:")
            traceback.print_exc()
    
    # SECTION 4: Handling timeouts
    print("\nSECTION 4: Handling Timeouts")
    print("Tasks that take too long can be timed out using result(timeout).")
    
    print("\nRunning a task with timeout handling:")
    with ProcessPoolExecutor() as executor:
        # Submit a task that will take 3 seconds
        future = executor.submit(task_with_timeout, 3)
        
        try:
            # Try to get the result with a 1 second timeout
            result = future.result(timeout=1)
            print(f"  Result: {result}")
        except concurrent.futures.TimeoutError:
            print("  Timeout occurred after 1 second")
            print("  Note: The task is still running in the worker process")
    
    # SECTION 5: Cancelling tasks
    print("\nSECTION 5: Cancelling Tasks")
    print("Futures can be cancelled if they haven't started executing yet.")
    
    print("\nTrying to cancel a task:")
    with ProcessPoolExecutor(max_workers=1) as executor:
        # Submit two tasks to a pool with only one worker
        future1 = executor.submit(task_with_timeout, 2)
        future2 = executor.submit(task_with_timeout, 1)
        
        # Try to cancel the second task
        cancel_result = future2.cancel()
        
        if cancel_result:
            print("  Successfully cancelled the task")
        else:
            print("  Could not cancel the task (it may have already started)")
            try:
                result = future2.result()
                print(f"  Result of non-cancelled task: {result}")
            except Exception as e:
                print(f"  Error in non-cancelled task: {e}")
        
        # Wait for the first task
        print(f"  Result of first task: {future1.result()}")
    
    # SECTION 6: Handling process crashes
    print("\nSECTION 6: Handling Process Crashes")
    print("ProcessPoolExecutor can recover from worker process crashes.")
    
    def crash_process():
        """A function that crashes the worker process."""
        import os
        import signal
        os.kill(os.getpid(), signal.SIGTERM)
    
    print("\nIntentionally crashing a worker process:")
    with ProcessPoolExecutor() as executor:
        # Submit a task that will crash the worker
        future1 = executor.submit(crash_process)
        
        # Submit another task that should run normally
        # (the executor will create a new worker)
        future2 = executor.submit(lambda: "I survived!")
        
        # First task will fail
        try:
            future1.result()
        except concurrent.futures.process.BrokenProcessPool:
            print("  The process pool was broken by the first task")
        except Exception as e:
            print(f"  First task failed with: {type(e).__name__}: {e}")
        
        # Second task may or may not run depending on when the pool breaks
        try:
            result = future2.result()
            print(f"  Second task result: {result}")
        except Exception as e:
            print(f"  Second task failed with: {type(e).__name__}: {e}")
    
    # SECTION 7: Error propagation strategies
    print("\nSECTION 7: Error Propagation Strategies")
    
    print("\nStrategy 1: Continue processing despite errors")
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(task_that_might_fail, i) for i in range(5)]
        
        # Process each result, ignoring failures
        successful_results = []
        failed_tasks = []
        
        for i, future in enumerate(futures):
            try:
                result = future.result()
                successful_results.append(result)
                print(f"  Task {i} succeeded: {result}")
            except Exception as e:
                failed_tasks.append(i)
                print(f"  Task {i} failed: {e}")
        
        print(f"  Successfully completed {len(successful_results)} tasks")
        print(f"  Failed tasks: {failed_tasks}")
    
    print("\nStrategy 2: Fail-fast on first error")
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(task_that_might_fail, i) for i in range(5)]
        
        try:
            # Use as_completed to get results as they finish
            for future in concurrent.futures.as_completed(futures):
                # This will raise the first exception encountered
                result = future.result()
                print(f"  Result: {result}")
        except Exception as e:
            print(f"  Stopped processing on first error: {e}")
            
            # Cancel any not-yet-running futures
            for future in futures:
                if not future.done():
                    future.cancel()
            
            print("  Cancelled remaining tasks")


if __name__ == "__main__":
    main()
    print("\nKey takeaways from this tutorial:")
    print("1. Exceptions in worker processes are re-raised in the main process")
    print("2. Use try/except blocks to handle errors gracefully")
    print("3. The result() method can take a timeout parameter to avoid waiting forever")
    print("4. Worker processes that crash are automatically replaced")
    print("5. Choose an appropriate error handling strategy based on your requirements") 