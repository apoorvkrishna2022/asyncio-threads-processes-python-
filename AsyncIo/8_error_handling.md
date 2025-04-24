# Error Handling in Asynchronous Code

This README explains the concepts covered in `8_error_handling.py`, providing a detailed understanding of error handling techniques in Python's asyncio library.

## What this Tutorial Covers

This tutorial explores:
1. The unique challenges of error handling in asynchronous code
2. Basic exception handling with try/except in coroutines
3. Managing exceptions in asyncio Tasks
4. Handling errors from multiple concurrent operations
5. Dealing with task cancellation
6. Implementing proper cleanup with try/finally
7. Understanding error propagation in callbacks
8. Creating and using custom exception hierarchies
9. Best practices for robust error handling

## Key Concepts Explained

### Introduction to Error Handling in Async Code

Asynchronous code presents several unique challenges for error handling:

1. **Silent failures**: Exceptions in unawaited coroutines can be lost
2. **Cancellation**: Tasks can be cancelled externally, requiring special handling
3. **Concurrent errors**: Multiple concurrent tasks might fail independently
4. **Complex propagation**: Error flow is more complex than in synchronous code
5. **Resource cleanup**: Ensuring resources are properly released despite errors

### Basic Exception Handling

Exception handling in coroutines uses familiar try/except blocks:

```python
async def example():
    try:
        await risky_operation()
    except SomeError as e:
        # Handle the error
        print(f"Error occurred: {e}")
    finally:
        # Cleanup code that always runs
        await cleanup()
```

Key points:
- The `try/except/finally` pattern works as in synchronous code
- Exceptions from awaited coroutines propagate naturally
- You can re-raise exceptions with additional context using `raise ... from`

### Exception Handling with Tasks

Tasks require special consideration for error handling:

```python
# Method 1: Await the task (exceptions propagate normally)
task = asyncio.create_task(coroutine())
try:
    await task
except Exception as e:
    print(f"Task failed: {e}")

# Method 2: Check for exceptions explicitly
task = asyncio.create_task(coroutine())
await asyncio.sleep(0)  # Allow task to run
if task.done():
    if task.exception() is not None:
        print(f"Task failed: {task.exception()}")

# Method 3: Add a done callback
def handle_result(task):
    try:
        result = task.result()  # Raises exception if task failed
    except Exception as e:
        print(f"Task failed: {e}")

task = asyncio.create_task(coroutine())
task.add_done_callback(handle_result)
```

Key points:
- Exceptions in tasks are raised when the task is awaited
- `task.exception()` retrieves the exception without raising it
- `task.result()` raises the exception if one occurred
- Callbacks can be used to handle exceptions asynchronously

### Handling Multiple Concurrent Errors

Several strategies exist for handling errors from multiple concurrent operations:

#### 1. Using `asyncio.gather()` with `return_exceptions=True`:

```python
results = await asyncio.gather(
    task1(), task2(), task3(),
    return_exceptions=True
)

for result in results:
    if isinstance(result, Exception):
        print(f"Task failed: {result}")
    else:
        print(f"Task succeeded: {result}")
```

This collects all results and exceptions without raising them.

#### 2. Using `asyncio.wait()` with `FIRST_EXCEPTION`:

```python
tasks = [asyncio.create_task(coro) for coro in coroutines]
done, pending = await asyncio.wait(
    tasks,
    return_when=asyncio.FIRST_EXCEPTION
)

# Check done tasks for exceptions
for task in done:
    if task.exception() is not None:
        print(f"Task failed: {task.exception()}")

# Cancel pending tasks
for task in pending:
    task.cancel()
```

This stops waiting when the first exception occurs, allowing you to handle it and cancel other tasks.

#### 3. Manual exception collection:

```python
tasks = [asyncio.create_task(coro) for coro in coroutines]
await asyncio.wait(tasks)  # Wait for all to complete

results = []
exceptions = []
for task in tasks:
    if task.exception() is not None:
        exceptions.append(task.exception())
    else:
        results.append(task.result())
```

This approach gives you full control over how to handle the collected exceptions.

### Handling Task Cancellation

Task cancellation is a common occurrence in asyncio applications:

```python
async def cancellable_operation():
    try:
        while True:
            await asyncio.sleep(1)
            # Do work...
    except asyncio.CancelledError:
        # Perform cleanup
        print("Operation was cancelled, cleaning up...")
        await cleanup()
        # Re-raise to propagate cancellation or not
        raise  # Propagate cancellation
        # or return/pass to suppress
```

Key points:
- `asyncio.CancelledError` is raised when a task is cancelled
- You should catch it to perform proper cleanup
- Whether to re-raise or suppress depends on your application needs
- `asyncio.shield()` can protect operations from cancellation

### Cleanup with try/finally

The `try/finally` pattern ensures resources are properly cleaned up:

```python
async def use_resource():
    resource = await acquire_resource()
    try:
        await use(resource)
    finally:
        # This runs even if cancelled or exception occurs
        await release(resource)
```

Async context managers are often cleaner:

```python
async def use_resource():
    async with ResourceManager() as resource:
        await use(resource)
    # Resource is automatically released here
```

### Error Propagation in Callbacks

Errors in callbacks require special handling:

```python
def callback_with_error():
    # Errors here won't be caught in normal try/except
    raise ValueError("Error in callback")

# Use a custom exception handler
def custom_exception_handler(loop, context):
    exception = context.get('exception')
    message = context.get('message')
    print(f"Caught callback error: {message}")
    print(f"Exception: {exception}")

# Set the handler
loop = asyncio.get_running_loop()
loop.set_exception_handler(custom_exception_handler)
```

### Custom Exception Hierarchies

Creating a custom exception hierarchy helps with structured error handling:

```python
class AsyncOperationError(Exception):
    """Base class for async operation errors"""

class ConnectionError(AsyncOperationError):
    """Error in network connection"""

class TimeoutError(AsyncOperationError):
    """Operation timed out"""

class RetryableError(AsyncOperationError):
    """Error that can be retried"""
    def __init__(self, message, retry_after=1):
        super().__init__(message)
        self.retry_after = retry_after

# Usage
try:
    await operation()
except ConnectionError:
    # Handle connection issues
except TimeoutError:
    # Handle timeouts
except RetryableError as e:
    # Schedule retry after e.retry_after seconds
except AsyncOperationError:
    # Handle other operation errors
```

### Best Practices for Error Handling

1. **Never ignore exceptions** in asynchronous code - they can cause silent failures
2. **Explicitly handle cancellation** with `try/except asyncio.CancelledError`
3. **Use `return_exceptions=True`** with `gather()` when you need all results regardless of errors
4. **Always implement proper cleanup** using `try/finally` or async context managers
5. **Set a global exception handler** for the event loop to catch unhandled exceptions
6. **Use custom exception hierarchies** for structured error handling
7. **Be careful with exception suppression** - it can mask important errors
8. **Log exceptions appropriately** for debugging and monitoring
9. **Consider timeout handling** for operations that might hang
10. **Use `asyncio.shield()`** to protect critical cleanup operations from cancellation

## Practical Applications

Robust error handling is essential for:

- Web servers and API clients
- Database operations
- File I/O and network operations
- Long-running services
- User-facing applications
- Workflows with multiple dependent steps
- Any application where reliability is important

## Key Takeaways

- Asynchronous error handling requires special consideration for task cancellation, multiple concurrent errors, and resource cleanup
- Use `try/except/finally` blocks for basic error handling in coroutines
- Consider multiple strategies for handling exceptions in concurrent tasks
- Always handle `CancelledError` and implement proper cleanup
- Use async context managers for cleaner resource management
- Create custom exception hierarchies for more structured error handling
- Set a global exception handler for the event loop to catch unhandled exceptions
- Follow best practices to create robust, reliable asynchronous applications 