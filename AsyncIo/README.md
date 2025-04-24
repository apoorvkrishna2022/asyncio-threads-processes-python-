# AsyncIO Tutorial Series

Welcome to the AsyncIO Tutorial Series! This comprehensive guide will help you learn asynchronous programming in Python using the `asyncio` library, from basic concepts all the way to advanced real-world applications.

## What is AsyncIO?

AsyncIO is Python's built-in library for writing concurrent code using the `async/await` syntax. It allows your program to perform multiple operations concurrently without using threads or multiprocessing, making it perfect for I/O-bound applications like web servers, database operations, and network clients.

## Getting Started

### Prerequisites

- Python 3.7 or higher (Python 3.8+ recommended)
- Basic knowledge of Python programming

### Installation

1. Clone or download this tutorial repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## How to Use This Tutorial

This tutorial is designed to be followed sequentially, as each lesson builds upon concepts covered in previous ones. Here's how to get the most out of it:

1. Start with `main.py` to get an overview of the tutorial structure
2. Work through each file in numerical order
3. Read the code comments and docstrings carefully
4. Try modifying the examples to deepen your understanding
5. Complete any exercises mentioned in the tutorials

To run any tutorial file:

```bash
python filename.py
```

For example:
```bash
python 1_intro_to_async.py
```

## Tutorial Structure

Here's what you'll learn in each part of the tutorial:

### 1. Introduction to Asynchronous Programming (`1_intro_to_async.py`)
- What is asynchronous programming?
- Comparing synchronous vs asynchronous code
- When to use async programming
- Basic async concepts and terminology

### 2. Coroutines and Awaitables (`2_coroutines.py`)
- Creating coroutines with `async def`
- Using `await` to pause and resume execution
- Understanding the different awaitable types
- Coroutine chaining patterns

### 3. Tasks and Futures (`3_tasks.py`)
- Working with Task objects
- Creating and scheduling tasks
- Futures as a mechanism for asynchronous results
- Handling task results and exceptions

### 4. Event Loops (`4_event_loops.py`)
- Understanding the event loop
- Managing the event loop
- Creating and running tasks on the loop
- Event loop lifecycle

### 5. Asynchronous I/O Operations (`5_async_io.py`)
- Reading and writing files asynchronously
- Network operations with asyncio
- Timeouts and cancellation
- Stream readers and writers

### 6. Async Context Managers (`6_async_with.py`)
- Using `async with` statements
- Creating your own async context managers
- Resource management in async code
- Practical examples with files and connections

### 7. Synchronization Primitives (`7_sync_primitives.py`)
- Using Locks to prevent race conditions
- Semaphores for limiting concurrency
- Events for signaling between coroutines
- Conditions for more complex synchronization
- Queues for producer-consumer patterns

### 8. Error Handling (`8_error_handling.py`)
- Handling exceptions in async code
- Task exception handling
- Using try/except/finally with async/await
- Proper cleanup in async applications

### 9. Real-World Example (`9_real_world_example.py`)
- Building a complete async web crawler
- Applying all the concepts from previous tutorials
- Structuring a real async application
- Performance considerations

### 10. Advanced Use Cases (`10_advanced_use_cases.py`)
- Async generators and asynchronous iteration
- Subprocess management with AsyncIO
- Real-time communication with WebSockets
- Advanced patterns (circuit breaker, rate limiting, etc.)
- Handling backpressure in async systems

## Practice Projects

After completing the tutorial, try building these practice projects:

1. An async API client that respects rate limits
2. A simple chat server using WebSockets
3. A file processing tool that processes multiple files concurrently

## Troubleshooting Common Issues

- **"Event loop is closed"**: This usually means you're trying to use asyncio outside of an async context. Make sure you're using `asyncio.run()`.
- **"Task was destroyed but it is pending!"**: You likely created a task but didn't await it. Always await tasks or use `asyncio.gather()`.
- **Code seems to run sequentially**: Check that you're using `await` correctly and that you're creating multiple tasks for concurrent operations.

## Additional Resources

For more information about async programming in Python:

- [Python asyncio documentation](https://docs.python.org/3/library/asyncio.html)
- [PEP 492 -- Coroutines with async and await syntax](https://www.python.org/dev/peps/pep-0492/)
- [Async IO in Python: A Complete Walkthrough](https://realpython.com/async-io-python/)

## Community and Support

If you have questions while working through this tutorial:
- Check the comments in the code for explanations
- Refer to the official Python documentation
- Join Python communities on Discord or Reddit to ask questions

Happy async programming! 