# Tasks and Futures

This README explains the concepts covered in `3_tasks.py`, providing a detailed understanding of Tasks and Futures in Python's asyncio library.

## What this Tutorial Covers

This tutorial explores:
1. Working with Tasks to schedule coroutines concurrently
2. Understanding and managing Futures
3. Managing multiple tasks with various control patterns
4. Using callbacks with Tasks
5. Error handling strategies with Tasks and Futures
6. Integrating with thread pools for blocking operations

## Key Concepts Explained

### Tasks

A Task is a wrapper around a coroutine that schedules it for execution on the event loop. Tasks are a subclass of Future that specifically wrap coroutines.

- **Creating Tasks**: Use `asyncio.create_task()` to create a Task from a coroutine
  ```python
  task = asyncio.create_task(
      my_coroutine("Task 1", 1.0),
      name="my_task"  # Optional name
  )
  ```

- **Task Execution**: Tasks start executing as soon as they are created

- **Task States**: Check if a task is done with the `.done()` method
  ```python
  print(f"Is task done? {task.done()}")
  ```

- **Task Results**: Get a task's result by awaiting it
  ```python
  result = await task
  ```

### Managing Multiple Tasks

Several methods exist for working with multiple tasks simultaneously:

1. **`asyncio.gather()`**: Runs multiple coroutines/tasks concurrently and collects their results
   ```python
   results = await asyncio.gather(task1, task2, task3)
   ```

2. **`asyncio.wait()`**: Provides more control over waiting for task completion
   ```python
   # Wait for the first task to complete
   done, pending = await asyncio.wait(
       [task1, task2, task3],
       return_when=asyncio.FIRST_COMPLETED
   )
   
   # Wait with a timeout
   done, pending = await asyncio.wait(
       [task1, task2, task3],
       timeout=2.0
   )
   ```

3. **Cancelling Tasks**: Tasks can be cancelled if they're no longer needed
   ```python
   task.cancel()
   ```

### Task Callbacks

You can attach callback functions to tasks that will be called when the task completes:

```python
def callback(task):
    print(f"Task {task.get_name()} completed")
    
    try:
        result = task.result()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Task failed with: {e}")

task = asyncio.create_task(my_coroutine())
task.add_done_callback(callback)
```

The callback is executed in the event loop thread when the task completes, raises an exception, or is cancelled.

### Futures

Futures represent the eventual result of an asynchronous operation:

- **Creating Futures**: Create with `asyncio.Future()`
  ```python
  future = asyncio.Future()
  ```

- **Setting Results**: Set a future's result when available
  ```python
  future.set_result("result value")
  ```

- **Getting Results**: Await the future to get its result
  ```python
  result = await future
  ```

- **Future States**: Check if a future is done with `.done()`
  ```python
  print(f"Is future done? {future.done()}")
  ```

### Working with ThreadPoolExecutor

For CPU-bound or blocking I/O operations, you can use a ThreadPoolExecutor with asyncio:

```python
with ThreadPoolExecutor() as pool:
    result = await asyncio.get_event_loop().run_in_executor(
        pool, blocking_function, arg1, arg2
    )
```

This runs the blocking function in a separate thread, returning a Future that can be awaited without blocking the event loop.

### Error Handling with Tasks and Futures

There are several approaches to handle errors in asyncio tasks:

1. **Try/Except with await**:
   ```python
   try:
       result = await task
   except Exception as e:
       print(f"Task failed: {e}")
   ```

2. **Using `gather()` with `return_exceptions=True`**:
   ```python
   results = await asyncio.gather(
       task1, task2, task3,
       return_exceptions=True
   )
   # Results will contain either successful results or exception objects
   ```

3. **Checking for exceptions directly**:
   ```python
   if task.done():
       if task.exception() is not None:
           print(f"Task failed: {task.exception()}")
       else:
           print(f"Task succeeded: {task.result()}")
   ```

## Practical Applications

Tasks and Futures enable several common asynchronous patterns:

- Running multiple operations concurrently
- Handling timeouts for operations that might hang
- Setting up callbacks for asynchronous operations
- Properly managing resources and error handling
- Integrating blocking code with asyncio's event loop

## Key Takeaways

- Tasks are the primary way to schedule coroutines for concurrent execution
- Futures represent eventual results of asynchronous operations
- Multiple tasks can be managed with tools like `gather()` and `wait()`
- Callbacks provide a way to respond to task completion without awaiting
- Error handling requires special consideration in asynchronous code
- ThreadPoolExecutor bridges synchronous blocking code with asyncio
- Proper task management includes handling exceptions and cancellation 