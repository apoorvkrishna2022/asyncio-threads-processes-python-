# Thread Synchronization Primitives

This directory contains examples of the various synchronization primitives available in Python's `threading` module. Each file demonstrates a different primitive and includes practical examples showing how and when to use them.

## Overview of Synchronization Primitives

Synchronization primitives are tools used to coordinate the execution of multiple threads to avoid race conditions, deadlocks, and other concurrency issues.

## Files in this Directory

### 1. Locks (`01_locks.py`)

The most basic synchronization primitive. A lock ensures that a critical section of code can only be executed by one thread at a time.

**Key features:**
- Simple mutual exclusion
- Prevents race conditions
- Allows thread-safe access to shared resources
- Can be acquired with `acquire()` or using the context manager (`with` statement)

**When to use:**
- When multiple threads need to modify a shared resource
- To prevent race conditions on shared data

### 2. Reentrant Locks (`02_rlock.py`)

A specialized lock that can be acquired multiple times by the same thread without blocking.

**Key features:**
- Can be acquired multiple times by the same thread
- Each `acquire()` must be balanced by a corresponding `release()`
- Prevents deadlocks in nested function calls

**When to use:**
- When you need to call locked functions from other locked functions
- In recursive code that needs locking
- When a thread needs to acquire the same lock multiple times

### 3. Events (`03_event.py`)

A simple way for threads to signal each other that something has happened.

**Key features:**
- Binary flag (set/unset)
- Threads can wait until the flag is set
- Good for simple signaling between threads

**When to use:**
- For simple notifications between threads
- When one thread needs to signal another that a condition is true
- For basic "start" signals or "stop" flags

### 4. Conditions (`04_condition.py`)

Conditions combine a lock with the ability to wait for a specific condition to be true.

**Key features:**
- Combines a lock with wait/notify mechanisms
- Allows threads to wait efficiently until a condition is met
- Supports notifying individual threads or all waiting threads

**When to use:**
- In producer-consumer scenarios
- When threads need to wait for complex conditions
- When a thread needs to wait for another thread to change state

### 5. Semaphores (`05_semaphore.py`)

Semaphores limit the number of threads that can access a resource simultaneously.

**Key features:**
- Maintains a counter of available resources
- Blocks when no resources are available
- Can be used to limit concurrency

**When to use:**
- To limit access to a resource with limited capacity (e.g., connection pools)
- To control the maximum concurrent operations
- As a throttling mechanism

### 6. Barriers (`06_barrier.py`)

Barriers synchronize multiple threads at a specific point, allowing them to wait for each other.

**Key features:**
- Causes threads to wait until a specified number of threads have reached the barrier
- After all threads reach the barrier, they are all released simultaneously
- Can execute an action when all threads reach the barrier

**When to use:**
- In parallel algorithms where phases must be synchronized
- When multiple threads need to wait for all other threads to complete a stage
- In simulations or iterative algorithms with synchronization points

## Usage Tips

1. **Choose the Right Primitive**: Each primitive has specific use cases. Choose the one that best fits your concurrency needs.

2. **Keep Critical Sections Small**: When using locks, keep the locked sections as small as possible to maximize concurrency.

3. **Avoid Nested Locks**: When possible, avoid acquiring multiple locks to prevent deadlocks. If you must nest locks, use RLock and be consistent about the order of acquisition.

4. **Always Release Resources**: Ensure locks and semaphores are always released, preferably by using the `with` statement.

5. **Be Aware of Deadlocks**: Design your code carefully to avoid situations where threads wait for each other indefinitely.

## Examples

Each file in this directory contains working examples that demonstrate:
- Basic usage patterns
- Common pitfalls to avoid  
- Real-world applications
- Best practices

Run each file individually to see the synchronization primitive in action:

```bash
python 01_locks.py
``` 