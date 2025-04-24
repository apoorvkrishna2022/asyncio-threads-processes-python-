"""
# Error Handling in Asynchronous Code
# =================================
#
# This tutorial explores error handling techniques in asyncio.
# Learn how to properly handle exceptions in async code.
"""

import asyncio
import sys
import traceback
from asyncio import CancelledError


# Introduction to Error Handling in Async Code
# -----------------------------------------

def intro_to_error_handling():
    print("== Introduction to Error Handling in Async Code ==")
    print("Error handling in async code presents unique challenges:")
    print("1. Exceptions in coroutines might be lost if not properly awaited")
    print("2. Tasks can be cancelled, requiring CancelledError handling")
    print("3. Concurrent operations need strategies for handling multiple failures")
    print("4. Error propagation works differently than in synchronous code")
    print("5. Cleanup operations require careful implementation with try/finally")


# Basic Exception Handling
# ---------------------
# Using try/except blocks in async code

async def basic_exception_handling():
    print("\n== Basic Exception Handling ==")
    
    # Example 1: Simple try/except in a coroutine
    print("Example 1: Simple try/except")
    async def handle_exception():
        try:
            print("Attempting a risky operation...")
            await asyncio.sleep(0.1)
            # Simulate an error
            raise ValueError("Something went wrong!")
        except ValueError as e:
            print(f"Caught exception: {e}")
            
    await handle_exception()
    
    # Example 2: Re-raising exceptions
    print("\nExample 2: Re-raising exceptions")
    async def re_raise():
        try:
            print("Attempting operation...")
            await asyncio.sleep(0.1)
            raise KeyError("Missing key!")
        except KeyError as e:
            print(f"Caught KeyError: {e}")
            # Re-raise a different exception
            raise RuntimeError("Couldn't complete the operation") from e
    
    try:
        await re_raise()
    except RuntimeError as e:
        print(f"Caught re-raised exception: {e}")
        # Access the original cause
        if e.__cause__:
            print(f"Original cause: {e.__cause__}")


# Exception Handling with Tasks
# --------------------------
# Handling exceptions in asyncio Tasks

async def task_exception_handling():
    print("\n== Exception Handling with Tasks ==")
    
    # Example 1: Exceptions in tasks are raised when awaited
    print("Example 1: Exceptions raised when awaited")
    
    async def failing_coroutine():
        await asyncio.sleep(0.1)
        raise ValueError("Task failure")
    
    # Create a task
    task = asyncio.create_task(failing_coroutine())
    
    try:
        # Exceptions are raised when the task is awaited
        await task
    except ValueError as e:
        print(f"Caught task exception: {e}")
    
    # Example 2: Checking for exceptions without awaiting
    print("\nExample 2: Checking exceptions without awaiting")
    
    task = asyncio.create_task(failing_coroutine())
    
    # Give the task time to complete and raise the exception
    await asyncio.sleep(0.2)
    
    if task.done():
        if task.exception() is not None:
            print(f"Task raised an exception: {task.exception()}")
        else:
            print("Task completed successfully")
    
    # Example 3: Adding a done callback to handle exceptions
    print("\nExample 3: Using done callbacks")
    
    def handle_task_result(task):
        try:
            # This will raise the exception if there was one
            task.result()
            print("Task callback: Task completed successfully")
        except Exception as e:
            print(f"Task callback: Caught exception: {e}")
    
    task = asyncio.create_task(failing_coroutine())
    task.add_done_callback(handle_task_result)
    
    # Wait for the callback to execute
    await asyncio.sleep(0.2)


# Handling Multiple Concurrent Errors
# --------------------------------
# Strategies for handling errors from multiple concurrent tasks

async def concurrent_error_handling():
    print("\n== Handling Multiple Concurrent Errors ==")
    
    # Create some coroutines, some of which will fail
    async def success(name):
        await asyncio.sleep(0.2)
        print(f"{name} completed successfully")
        return f"{name} result"
    
    async def failure(name, error_type):
        await asyncio.sleep(0.1)
        print(f"{name} raising {error_type.__name__}")
        raise error_type(f"Error in {name}")
    
    # Example 1: Using asyncio.gather with return_exceptions
    print("Example 1: Using gather with return_exceptions=True")
    
    results = await asyncio.gather(
        success("Task 1"),
        failure("Task 2", ValueError),
        success("Task 3"),
        failure("Task 4", RuntimeError),
        return_exceptions=True  # Return exceptions instead of raising them
    )
    
    # Process the results and exceptions
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Task {i+1} failed with: {type(result).__name__}: {result}")
        else:
            print(f"Task {i+1} succeeded with: {result}")
    
    # Example 2: Using asyncio.wait with FIRST_EXCEPTION
    print("\nExample 2: Using wait with FIRST_EXCEPTION")
    
    tasks = [
        asyncio.create_task(success("Wait Task 1")),
        asyncio.create_task(failure("Wait Task 2", ValueError)),
        asyncio.create_task(success("Wait Task 3")),
        asyncio.create_task(failure("Wait Task 4", RuntimeError)),
    ]
    
    # Wait until first exception or all complete
    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_EXCEPTION
    )
    
    print(f"Completed tasks: {len(done)}")
    print(f"Pending tasks: {len(pending)}")
    
    # Check for exceptions in done tasks
    for task in done:
        if task.exception() is not None:
            print(f"Task failed: {task.exception()}")
        else:
            print(f"Task succeeded: {task.result()}")
    
    # Cancel pending tasks
    for task in pending:
        task.cancel()
    
    # Wait for cancelled tasks to finish
    await asyncio.gather(*pending, return_exceptions=True)
    
    # Example 3: Manual exception collection
    print("\nExample 3: Manual exception collection")
    
    async def collect_exceptions():
        coroutines = [
            success("Collect Task 1"),
            failure("Collect Task 2", ValueError),
            success("Collect Task 3"),
            failure("Collect Task 4", RuntimeError),
        ]
        
        # Create tasks
        tasks = [asyncio.create_task(coro) for coro in coroutines]
        
        # Wait for all tasks to complete
        await asyncio.wait(tasks)
        
        # Collect results and exceptions
        results = []
        exceptions = []
        
        for task in tasks:
            if task.exception() is not None:
                exceptions.append(task.exception())
            else:
                results.append(task.result())
        
        return results, exceptions
    
    results, exceptions = await collect_exceptions()
    
    print(f"Successful results: {results}")
    print(f"Exceptions ({len(exceptions)}):")
    for i, exc in enumerate(exceptions):
        print(f"  {i+1}. {type(exc).__name__}: {exc}")


# Handling Task Cancellation
# -----------------------
# Working with CancelledError and implementing cancellation

async def cancellation_handling():
    print("\n== Handling Task Cancellation ==")
    
    # Example 1: Basic cancellation
    print("Example 1: Basic cancellation")
    
    async def long_running_task():
        try:
            print("Long task started")
            for i in range(5):
                await asyncio.sleep(0.5)
                print(f"Long task step {i+1}")
        except asyncio.CancelledError:
            print("Long task was cancelled - cleaning up")
            # Perform necessary cleanup here
            await asyncio.sleep(0.1)  # Simulate cleanup
            print("Cleanup completed")
            raise  # Re-raise to properly mark as cancelled
    
    # Start the task
    task = asyncio.create_task(long_running_task())
    
    # Let it run for a bit
    await asyncio.sleep(1.2)
    
    # Cancel the task
    print("Cancelling the task...")
    task.cancel()
    
    try:
        # Wait for the task to be cancelled
        await task
    except asyncio.CancelledError:
        print("Task cancellation confirmed")
    
    # Example 2: Graceful cancellation with timeout
    print("\nExample 2: Cancellation with timeout protection")
    
    async def shielded_operation():
        # Shield prevents cancellation from propagating
        try:
            print("Starting critical operation")
            # Shield the sleep from cancellation
            await asyncio.shield(asyncio.sleep(1))
            print("Critical operation completed")
            return "Operation result"
        except asyncio.CancelledError:
            print("Cancellation detected, but critical part was protected")
            raise
    
    async def timeout_manager():
        try:
            # Set a timeout for the operation
            result = await asyncio.wait_for(shielded_operation(), timeout=0.5)
            return result
        except asyncio.TimeoutError:
            print("Operation timed out")
            return "Timeout result"
    
    result = await timeout_manager()
    print(f"Result: {result}")


# Cleanup with try/finally
# ----------------------
# Ensuring resources are properly cleaned up

async def cleanup_with_try_finally():
    print("\n== Cleanup with try/finally ==")
    
    class AsyncResource:
        """A sample resource that needs cleanup"""
        
        async def __aenter__(self):
            print("Acquiring resource")
            self.acquired = True
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            print("Releasing resource")
            self.acquired = False
        
        async def use(self):
            if not getattr(self, 'acquired', False):
                raise RuntimeError("Resource not acquired")
            print("Using resource")
    
    # Example 1: Using async context manager (recommended)
    print("Example 1: Using async context manager")
    
    async def use_with_context_manager():
        async with AsyncResource() as resource:
            await resource.use()
            # Even if an exception occurs, resource will be released
            raise ValueError("Error during resource use")
    
    try:
        await use_with_context_manager()
    except ValueError as e:
        print(f"Caught exception: {e}")
    
    # Example 2: Manual try/finally
    print("\nExample 2: Manual try/finally")
    
    async def use_with_try_finally():
        resource = AsyncResource()
        try:
            await resource.__aenter__()
            await resource.use()
            # Simulate an exception
            raise RuntimeError("Critical error")
        finally:
            # This will always run, even if an exception occurs
            await resource.__aexit__(None, None, None)
    
    try:
        await use_with_try_finally()
    except RuntimeError as e:
        print(f"Caught exception: {e}")


# Error Propagation in Callbacks
# ---------------------------
# Handling errors in callbacks, where they can be easily lost

def error_propagation_in_callbacks():
    print("\n== Error Propagation in Callbacks ==")
    
    # Example: Using call_exception_handler
    loop = asyncio.get_event_loop()
    
    def callback_with_error():
        try:
            # Simulate an error in a callback
            raise ValueError("Error in callback")
        except Exception as e:
            # Get the current exception details
            exc_type, exc_value, exc_traceback = sys.exc_info()
            
            # Create a context with error details
            context = {
                'message': 'Error in callback',
                'exception': exc_value,
                'task': asyncio.current_task(),
            }
            
            # Report the error to the event loop
            loop.call_exception_handler(context)
    
    # Set a custom exception handler
    def custom_exception_handler(loop, context):
        print(f"Custom exception handler caught an error: {context['message']}")
        if 'exception' in context:
            print(f"Exception: {context['exception']}")
        
        # Optionally print a traceback
        if 'exception' in context and hasattr(context['exception'], '__traceback__'):
            traceback.print_tb(context['exception'].__traceback__)
    
    # Register the custom handler
    loop.set_exception_handler(custom_exception_handler)
    
    # Schedule the callback
    loop.call_soon(callback_with_error)
    
    # Run the loop briefly to execute the callback
    asyncio.run(asyncio.sleep(0.1))


# Custom Exception Types
# -------------------
# Creating and using custom exception types for better error handling

class AsyncOperationError(Exception):
    """Base exception for async operations"""
    pass

class ConnectionError(AsyncOperationError):
    """Error when establishing connection"""
    pass

class TimeoutError(AsyncOperationError):
    """Operation timed out"""
    pass

class RetryableError(AsyncOperationError):
    """Error that allows retrying the operation"""
    
    def __init__(self, message, retry_after=1):
        super().__init__(message)
        self.retry_after = retry_after


async def custom_exception_handling():
    print("\n== Custom Exception Types ==")
    
    async def perform_operation(fail_type=None):
        print("Starting operation")
        
        await asyncio.sleep(0.1)
        
        if fail_type == "connection":
            raise ConnectionError("Failed to connect to server")
        elif fail_type == "timeout":
            raise TimeoutError("Operation timed out after 5 seconds")
        elif fail_type == "retry":
            raise RetryableError("Service unavailable, try again", retry_after=2)
        
        print("Operation successful")
        return "Operation result"
    
    # Example 1: Handling different exception types
    print("Example 1: Handling different exception types")
    
    async def handle_different_exceptions():
        for fail_type in [None, "connection", "timeout", "retry"]:
            try:
                result = await perform_operation(fail_type)
                print(f"Result: {result}")
            except ConnectionError as e:
                print(f"Connection error: {e}")
            except TimeoutError as e:
                print(f"Timeout: {e}")
            except RetryableError as e:
                print(f"Retryable error: {e}")
                print(f"Retrying in {e.retry_after} seconds...")
                await asyncio.sleep(e.retry_after)
                print("Retry now")
            except AsyncOperationError as e:
                # Catch any other operation errors
                print(f"Operation error: {e}")
    
    await handle_different_exceptions()


# Best Practices for Error Handling
# ------------------------------

def best_practices():
    print("\n== Best Practices for Error Handling in Async Code ==")
    
    print("1. Always await coroutines and tasks to propagate exceptions")
    print("2. Use try/except/finally blocks for proper cleanup")
    print("3. Prefer async context managers for resource management")
    print("4. Handle CancelledError for graceful cancellation")
    print("5. Use asyncio.gather with return_exceptions for concurrent error handling")
    print("6. Create custom exception types for different error scenarios")
    print("7. Log exceptions with context for better debugging")
    print("8. Don't suppress exceptions unless you have a good reason")
    print("9. Set a global exception handler for uncaught exceptions")
    print("10. Be careful with error handling in callbacks")


# Run all examples
if __name__ == "__main__":
    print("Error Handling in Asynchronous Code\n")
    
    # Regular function examples
    intro_to_error_handling()
    
    # Run async examples
    asyncio.run(basic_exception_handling())
    asyncio.run(task_exception_handling())
    asyncio.run(concurrent_error_handling())
    asyncio.run(cancellation_handling())
    asyncio.run(cleanup_with_try_finally())
    
    # Examples with callbacks
    error_propagation_in_callbacks()
    
    # Custom exception handling
    asyncio.run(custom_exception_handling())
    
    # Best practices
    best_practices()
    
    print("\nNext tutorial: 9_real_world_example.py - A comprehensive real-world application") 