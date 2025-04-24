# Coroutines and Awaitables

This README explains the concepts covered in `2_coroutines.py`, providing a detailed understanding of coroutines and awaitables in Python's asyncio framework.

## What this Tutorial Covers

This tutorial explores:
1. What coroutines are and how to define them
2. Different types of awaitable objects
3. How to chain coroutines together
4. Common coroutine patterns and usage

## Key Concepts Explained

### Coroutines

A coroutine is a specialized function defined with `async def` that can pause execution and yield control back to the event loop while waiting for some operation to complete.

- **Creating a Coroutine**: Use `async def` to define a coroutine function
  ```python
  async def simple_coroutine():
      return "I'm a coroutine!"
  ```

- **Coroutine State**: When you call a coroutine function, it returns a coroutine object but doesn't execute the function body yet

- **Coroutine Inspection**: You can inspect coroutines using the `inspect` module:
  ```python
  print(f"Is coroutine: {inspect.iscoroutine(coro)}")
  print(f"Is coroutine function: {inspect.iscoroutinefunction(func)}")
  ```

### Running Coroutines

Coroutines must be run using one of these methods:

1. **Using `await`**: Can only be done inside another coroutine
   ```python
   result = await simple_coroutine()
   ```

2. **Using `asyncio.create_task()`**: Schedule the coroutine as a Task
   ```python
   task = asyncio.create_task(simple_coroutine())
   result = await task
   ```

3. **Using `asyncio.gather()`**: Run multiple coroutines concurrently
   ```python
   results = await asyncio.gather(coro1(), coro2(), coro3())
   ```

4. **Using `asyncio.run()`**: Top-level function to run a coroutine
   ```python
   asyncio.run(main())
   ```

### Awaitable Objects

An awaitable is any object that can be used with the `await` keyword. There are three main types:

1. **Coroutines**: Functions defined with `async def`
   ```python
   await simple_coroutine()
   ```

2. **Tasks**: Wrappers around coroutines that track their execution
   ```python
   task = asyncio.create_task(simple_coroutine())
   await task
   ```

3. **Futures**: Low-level awaitable objects representing an eventual result
   ```python
   future = asyncio.Future()
   future.set_result("Result")
   await future
   ```

### Chaining Coroutines

Coroutines can call other coroutines using the `await` keyword, creating a chain of operations:

```python
async def workflow():
    result1 = await step1()
    result2 = await step2(result1)
    final_result = await step3(result2)
    return final_result
```

This creates a sequential execution where each step depends on the result of the previous step.

### Common Coroutine Patterns

1. **Sequential Execution**: Operations run one after another
   ```python
   result1 = await operation1()
   result2 = await operation2()
   ```

2. **Concurrent Execution**: Operations run in parallel
   ```python
   results = await asyncio.gather(operation1(), operation2())
   ```

3. **Timeout Pattern**: Limit the time allowed for an operation
   ```python
   try:
       await asyncio.wait_for(long_operation(), timeout=1.0)
   except asyncio.TimeoutError:
       print("Operation timed out")
   ```

## Practical Application

The tutorial demonstrates multiple ways to work with coroutines, including:
- Inspecting coroutine objects
- Running coroutines with different approaches
- Working with different awaitable types
- Chaining coroutines to create workflows
- Comparing sequential vs concurrent execution
- Implementing timeouts for operations

## Key Takeaways

- Coroutines are the foundation of asyncio programming
- The `await` keyword pauses execution until an awaitable completes
- Tasks are higher-level abstractions that manage coroutines
- Futures represent eventual results of asynchronous operations
- Proper chaining of coroutines creates efficient asynchronous workflows
- Using concurrent execution can significantly improve performance for I/O-bound operations 