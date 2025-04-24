# Introduction to Asynchronous Programming

This README explains the concepts covered in `1_intro_to_async.py`, providing a detailed overview of asynchronous programming in Python.

## What this Tutorial Covers

This tutorial introduces the fundamental difference between synchronous and asynchronous programming by comparing:

1. A synchronous function that runs tasks sequentially, blocking execution
2. An asynchronous function that runs tasks concurrently, allowing more efficient execution

## Key Concepts Explained

### Synchronous vs Asynchronous Programming

- **Synchronous Programming**: Tasks run one after another. Each task must complete before the next one starts. The program execution is blocked during operations like `time.sleep()`.

- **Asynchronous Programming**: Tasks can run concurrently. When one task is waiting (e.g., for I/O or network response), another task can execute. This improves efficiency, especially for I/O-bound operations.

### Important AsyncIO Elements

- **`asyncio.run()`**: The entry point to run an asynchronous function. It creates a new event loop, runs the coroutine, and closes the loop when done.
  ```python
  asyncio.run(async_example())
  ```

- **`asyncio.gather()`**: Runs multiple coroutines concurrently and collects their results. It's used to execute multiple tasks in parallel.
  ```python
  results = await asyncio.gather(task1(), task2(), task3())
  ```

- **`asyncio.sleep()`**: The asynchronous version of `time.sleep()`. Instead of blocking the entire program, it yields control back to the event loop, allowing other tasks to run.
  ```python
  await asyncio.sleep(2)  # Non-blocking sleep
  ```

- **`async def`**: Defines a coroutine function that can be paused and resumed.

- **`await`**: Used inside async functions to pause execution until the awaitable (coroutine, task, or future) completes.

### When to Use AsyncIO

AsyncIO is ideal for:
- I/O-bound operations (network requests, file operations)
- Concurrent operations where tasks spend time waiting
- Handling many connections simultaneously (web servers, chat applications)

AsyncIO is NOT ideal for:
- CPU-bound tasks (use multiprocessing instead)
- Simple sequential programs where concurrency isn't needed
- When synchronous code is easier to understand and maintain

## Code Example Explained

The tutorial demonstrates the difference between synchronous and asynchronous execution:

1. **Synchronous Example**: Three tasks run sequentially, taking a total time approximately equal to the sum of all task durations (~6 seconds).

2. **Asynchronous Example**: The same three tasks run concurrently, taking only as long as the longest task (~3 seconds).

This demonstrates how asynchronous programming can significantly improve performance for I/O-bound operations by utilizing waiting time efficiently.

## Key Takeaways

- Asynchronous programming improves efficiency by not blocking execution during waiting periods
- The `async`/`await` syntax makes asynchronous code more readable and easier to write
- AsyncIO is part of Python's standard library and doesn't require external dependencies
- Understanding when to use AsyncIO vs other concurrency models is crucial for effective Python programming 